#!/usr/bin/env python3

from __future__ import annotations

import argparse
import gzip
import html
import json
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

import numpy as np
from PIL import Image

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
THEME_TOKENS = {
    "catppuccin",
    "cyberdream",
    "decay",
    "dracula",
    "graphite",
    "gruvbox",
    "kanagawa",
    "nord",
    "nordic",
    "rosepine",
    "solarized",
    "tokyonight",
    "unorganized",
}
GENERIC_TOKENS = {
    "a",
    "about",
    "after",
    "all",
    "an",
    "and",
    "app",
    "as",
    "at",
    "background",
    "best",
    "by",
    "cc",
    "centered",
    "desktop",
    "download",
    "duck",
    "free",
    "female",
    "from",
    "gallery",
    "go",
    "here",
    "hd",
    "high",
    "homepage",
    "human",
    "image",
    "images",
    "in",
    "inside",
    "into",
    "it",
    "its",
    "of",
    "on",
    "online",
    "or",
    "out",
    "over",
    "page",
    "person",
    "people",
    "per",
    "photo",
    "photography",
    "picture",
    "pictures",
    "quality",
    "result",
    "results",
    "resolution",
    "re",
    "royalty",
    "sfw",
    "search",
    "sure",
    "standing",
    "stock",
    "sitting",
    "that",
    "the",
    "this",
    "title",
    "to",
    "verify",
    "walking",
    "unsplash",
    "wallhaven",
    "wallpaper",
    "wallpapers",
    "with",
    "you",
    "your",
    "body",
    "browser",
    "continue",
    "enable",
    "javascript",
    "making",
    "down",
    "during",
    "low",
    "male",
    "near",
    "poster",
}
KEEPABLE_GENERIC_TOKENS = {
    "anime",
    "beach",
    "bridge",
    "building",
    "buildings",
    "car",
    "cat",
    "city",
    "clouds",
    "coast",
    "deer",
    "forest",
    "girl",
    "japan",
    "lake",
    "lantern",
    "lights",
    "market",
    "moon",
    "mountain",
    "mountains",
    "neon",
    "night",
    "ocean",
    "pagoda",
    "planet",
    "portrait",
    "rain",
    "river",
    "road",
    "sea",
    "shore",
    "sign",
    "sky",
    "street",
    "streets",
    "sunset",
    "temple",
    "tokyo",
    "tower",
    "train",
    "tree",
    "trees",
    "water",
    "waves",
}
SOURCE_TOKENS = {
    "getty",
    "images",
    "wallhaven",
    "unsplash",
}


@dataclass
class Candidate:
    path: Path
    source: str
    source_id: str | None
    author_slug: str | None


@dataclass
class PlannedRename:
    source: Path
    target: Path
    reason: str
    url: str | None


class MetaHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.metas: dict[str, list[str]] = {}
        self.title_parts: list[str] = []
        self.scripts: list[str] = []
        self._in_title = False
        self._in_script = False
        self._current_script: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name.lower(): value or "" for name, value in attrs}
        if tag.lower() == "meta":
            key = (attributes.get("property") or attributes.get("name") or attributes.get("itemprop") or "").lower()
            value = attributes.get("content", "")
            if key and value:
                self.metas.setdefault(key, []).append(html.unescape(value))
        elif tag.lower() == "title":
            self._in_title = True
        elif tag.lower() == "script":
            self._in_script = True
            self._current_script = []

    def handle_endtag(self, tag: str) -> None:
        lower = tag.lower()
        if lower == "title":
            self._in_title = False
        elif lower == "script":
            self._in_script = False
            script = "".join(self._current_script).strip()
            if script:
                self.scripts.append(script)
            self._current_script = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_script:
            self._current_script.append(data)

    @property
    def title(self) -> str:
        return " ".join(part.strip() for part in self.title_parts if part.strip())


def normalize_text(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text)
    return "".join(char for char in folded if not unicodedata.combining(char))


def tokenize(text: str) -> list[str]:
    normalized = normalize_text(text)
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", normalized)
    normalized = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", normalized)
    lowered = normalized.lower()
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return [token for token in lowered.split() if token]


def dedupe(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rename source-named wallpapers using Unsplash/Wallhaven page metadata."
    )
    parser.add_argument("--root", default="wallpapers", help="wallpaper root directory")
    parser.add_argument("--apply", action="store_true", help="rename files in place")
    parser.add_argument("--theme", action="append", default=[], help="limit to one or more themes")
    parser.add_argument(
        "--source",
        action="append",
        choices=["unsplash", "wallhaven"],
        default=[],
        help="limit to one or more source types",
    )
    parser.add_argument("--offline", action="store_true", help="skip network fetch and only use local fallback")
    return parser.parse_args()


def enumerate_candidates(root: Path, themes: set[str], sources: set[str]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        theme = path.parent.name.lower()
        if themes and theme not in themes:
            continue

        basename = path.stem
        unsplash = extract_unsplash_source(basename)
        if unsplash and (not sources or "unsplash" in sources):
            source_id, author_slug = unsplash
            candidates.append(Candidate(path=path, source="unsplash", source_id=source_id, author_slug=author_slug))
            continue

        wallhaven = extract_wallhaven_source(basename)
        if wallhaven is not None and (not sources or "wallhaven" in sources):
            source_id = wallhaven or None
            candidates.append(Candidate(path=path, source="wallhaven", source_id=source_id, author_slug=None))

    return candidates


def extract_unsplash_source(basename: str) -> tuple[str, str | None] | None:
    match = re.fullmatch(r"(.+?)-unsplash(?:_\d+)?(?:-variant(?:-\d+)?)?", basename)
    if not match:
        return None

    stem = match.group(1)
    parts = stem.split("-")
    if len(parts) < 2:
        return None

    id_parts = [parts[-1]]
    index = len(parts) - 2
    while index >= 0:
        token = parts[index]
        if re.search(r"[A-Z0-9_]", token):
            id_parts.insert(0, token)
            index -= 1
            continue
        if len(token) == 1:
            id_parts.insert(0, token)
            index -= 1
            continue
        break

    author_parts = parts[: index + 1]
    source_id = "-".join(id_parts)
    author_slug = "-".join(author_parts) if author_parts else None
    return source_id, author_slug


def extract_wallhaven_source(basename: str) -> str | None:
    match = re.fullmatch(r"wallhaven(?:-([a-z0-9]+))?", basename)
    if not match:
        return None
    return match.group(1) or ""


def fetch_text(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Encoding": "gzip",
        },
    )
    with urlopen(request, timeout=20) as response:
        data = response.read()
        encoding = response.headers.get("Content-Encoding", "")
        if "gzip" in encoding:
            data = gzip.decompress(data)
        charset = response.headers.get_content_charset() or "utf-8"
        return data.decode(charset, errors="replace")


def fetch_json(url: str) -> dict[str, object]:
    payload = fetch_text(url)
    return json.loads(payload)


def fetch_reader_text(url: str) -> str:
    stripped = re.sub(r"^https?://", "", url)
    return fetch_text(f"https://r.jina.ai/http://{stripped}")


def parse_document(text: str) -> MetaHTMLParser:
    parser = MetaHTMLParser()
    parser.feed(text)
    return parser


def decode_json_string(value: str) -> str:
    try:
        return json.loads(f'"{value}"')
    except json.JSONDecodeError:
        return value


def extract_unsplash_texts(document: MetaHTMLParser, author_slug: str | None) -> list[str]:
    texts: list[str] = []
    for key in ("twitter:image:alt", "og:title", "og:description", "description", "keywords"):
        texts.extend(document.metas.get(key, []))
    if document.title:
        texts.append(document.title)

    patterns = [
        r'"alt_description":"((?:\\.|[^"\\])*)"',
        r'"description":"((?:\\.|[^"\\])*)"',
        r'"slug":"((?:\\.|[^"\\])*)"',
        r'"title":"((?:\\.|[^"\\])*)"',
    ]
    for script in document.scripts:
        for pattern in patterns:
            for match in re.finditer(pattern, script):
                value = decode_json_string(match.group(1))
                if value:
                    texts.append(value)

    if author_slug:
        author_tokens = set(tokenize(author_slug))
        filtered: list[str] = []
        for text in texts:
            tokens = tokenize(text)
            if tokens and all(token in author_tokens for token in tokens):
                continue
            filtered.append(text)
        texts = filtered

    return dedupe(texts)


def fetch_unsplash_oembed_texts(source_id: str, author_slug: str | None) -> list[str]:
    url = f"https://unsplash.com/oembed?url=https://unsplash.com/photos/{source_id}"
    payload = fetch_json(url)
    texts: list[str] = []
    for key in ("title", "author_name", "provider_name"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            texts.append(value.strip())

    if author_slug:
        author_tokens = set(tokenize(author_slug))
        filtered: list[str] = []
        for text in texts:
            tokens = tokenize(text)
            if tokens and all(token in author_tokens for token in tokens):
                continue
            filtered.append(text)
        texts = filtered

    return dedupe(texts)


def strip_tags(text: str) -> str:
    unescaped = html.unescape(text)
    stripped = re.sub(r"<[^>]+>", " ", unescaped)
    return re.sub(r"\s+", " ", stripped).strip()


def fetch_search_texts(query: str) -> list[str]:
    url = f"https://lite.duckduckgo.com/lite/?q={quote_plus(query)}"
    text = fetch_text(url)
    chunks = re.findall(
        r"""<a[^>]*class=['"][^'"]*result-link[^'"]*['"][^>]*>(.*?)</a>""",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not chunks:
        chunks = re.findall(r"<a[^>]+>(.*?)</a>", text, flags=re.IGNORECASE | re.DOTALL)
    texts = [strip_tags(chunk) for chunk in chunks]
    return [text for text in texts if text]


def extract_reader_texts(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.lower().startswith(("url source:", "markdown content:", "warning:", "status:")):
            continue
        lines.append(stripped)
    return dedupe(lines[:40])


def search_fallback_texts(candidate: Candidate) -> list[str]:
    if candidate.source == "unsplash" and candidate.source_id:
        query = f'{candidate.source_id} site:unsplash.com/photos'
        if candidate.author_slug:
            query = f"{candidate.author_slug} {query}"
        return fetch_search_texts(query)
    if candidate.source == "wallhaven" and candidate.source_id:
        return fetch_search_texts(f"{candidate.source_id} wallhaven")
    return []


def extract_wallhaven_texts(document: MetaHTMLParser) -> list[str]:
    texts: list[str] = []
    for key in ("og:title", "og:description", "description", "keywords"):
        texts.extend(document.metas.get(key, []))
    if document.title:
        texts.append(document.title)

    for script in document.scripts:
        for pattern in (
            r'"label":"((?:\\.|[^"\\])*)"',
            r'"tag":"((?:\\.|[^"\\])*)"',
            r'"title":"((?:\\.|[^"\\])*)"',
        ):
            for match in re.finditer(pattern, script):
                value = decode_json_string(match.group(1))
                if value:
                    texts.append(value)

    return dedupe(texts)


def clean_tokens(texts: Iterable[str], theme: str, author_slug: str | None = None) -> list[str]:
    author_tokens = set(tokenize(author_slug or ""))
    tokens: list[str] = []
    for text in texts:
        for token in tokenize(text):
            if token in THEME_TOKENS or token == theme:
                continue
            if token in GENERIC_TOKENS and token not in KEEPABLE_GENERIC_TOKENS:
                continue
            if re.fullmatch(r"\d+x\d+", token):
                continue
            if token in SOURCE_TOKENS:
                continue
            if token in author_tokens:
                continue
            if token.isdigit():
                continue
            tokens.append(token)

    return dedupe(tokens)


def build_basename(tokens: list[str]) -> str | None:
    if not tokens:
        return None
    compact = []
    for token in tokens:
        if token in {"wallpaper", "wallpapers", "photo", "image"}:
            continue
        compact.append(token)
    compact = dedupe(compact)
    if not compact:
        return None
    return "-".join(compact[:5])


def image_feature(image_path: Path) -> np.ndarray:
    with Image.open(image_path) as image:
        rgb = image.convert("RGB").resize((12, 8), Image.Resampling.LANCZOS)
        gray = image.convert("L").resize((12, 8), Image.Resampling.LANCZOS)

    rgb_array = np.asarray(rgb, dtype=np.float32) / 255.0
    gray_array = np.asarray(gray, dtype=np.float32) / 255.0
    grad_x = np.abs(np.diff(gray_array, axis=1, append=gray_array[:, -1:]))
    grad_y = np.abs(np.diff(gray_array, axis=0, append=gray_array[-1:, :]))
    edge_array = grad_x + grad_y

    vector = np.concatenate(
        [
            rgb_array.reshape(-1),
            gray_array.reshape(-1),
            edge_array.reshape(-1),
        ]
    )
    norm = np.linalg.norm(vector)
    if norm:
        vector = vector / norm
    return vector


def similarity_fallback(candidate: Candidate, root: Path, feature_cache: dict[Path, np.ndarray]) -> str | None:
    theme = candidate.path.parent.name
    named_files = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if path == candidate.path:
            continue
        if path.parent.name != theme:
            continue
        if extract_unsplash_source(path.stem) or extract_wallhaven_source(path.stem):
            continue
        named_files.append(path)

    try:
        target_feature = feature_cache.setdefault(candidate.path, image_feature(candidate.path))
    except Exception:
        return None

    best_name: str | None = None
    best_distance = float("inf")
    for path in named_files:
        try:
            named_feature = feature_cache.setdefault(path, image_feature(path))
            distance = float(np.linalg.norm(target_feature - named_feature))
        except Exception:
            continue
        if distance < best_distance:
            best_distance = distance
            best_name = path.stem

    if best_name:
        return f"{best_name}-variant"
    return None


def reserve_target(path: Path, basename: str, reserved: set[Path]) -> Path:
    candidate = path.with_name(f"{basename}{path.suffix.lower()}")
    counter = 2
    while candidate in reserved:
        candidate = path.with_name(f"{basename}-{counter}{path.suffix.lower()}")
        counter += 1
    reserved.add(candidate)
    return candidate


def source_url(candidate: Candidate) -> str | None:
    if candidate.source == "unsplash" and candidate.source_id:
        return f"https://unsplash.com/photos/{candidate.source_id}"
    if candidate.source == "wallhaven" and candidate.source_id:
        return f"https://wallhaven.cc/w/{candidate.source_id}"
    return None


def plan_renames(candidates: list[Candidate], root: Path, offline: bool) -> list[PlannedRename]:
    reserved = {candidate.path for candidate in candidates}
    feature_cache: dict[Path, np.ndarray] = {}
    for path in root.rglob("*"):
        if path.is_file():
            reserved.add(path)

    planned: list[PlannedRename] = []
    for candidate in candidates:
        reserved.discard(candidate.path)
        theme = candidate.path.parent.name.lower()
        url = source_url(candidate)
        tokens: list[str] = []
        reason = "metadata"

        if url and not offline:
            try:
                if candidate.source == "unsplash":
                    texts = fetch_unsplash_oembed_texts(candidate.source_id or "", candidate.author_slug)
                else:
                    document = parse_document(fetch_text(url))
                    texts = extract_wallhaven_texts(document)
                tokens = clean_tokens(texts, theme=theme, author_slug=candidate.author_slug)
            except (HTTPError, URLError, TimeoutError, ValueError) as error:
                print(f"warn: failed to fetch metadata for {candidate.path}: {error}", file=sys.stderr)
                if url:
                    try:
                        reader_texts = extract_reader_texts(fetch_reader_text(url))
                        if reader_texts:
                            tokens = clean_tokens(reader_texts, theme=theme, author_slug=candidate.author_slug)
                            reason = "reader"
                    except (HTTPError, URLError, TimeoutError, ValueError) as reader_error:
                        print(f"warn: reader fallback failed for {candidate.path}: {reader_error}", file=sys.stderr)
                if not tokens:
                    try:
                        search_texts = search_fallback_texts(candidate)
                        if search_texts:
                            tokens = clean_tokens(search_texts, theme=theme, author_slug=candidate.author_slug)
                            reason = "search"
                    except (HTTPError, URLError, TimeoutError, ValueError) as search_error:
                        print(f"warn: search fallback failed for {candidate.path}: {search_error}", file=sys.stderr)

        basename = build_basename(tokens)
        if not basename:
            basename = similarity_fallback(candidate, root, feature_cache)
            reason = "similarity"

        if not basename:
            print(f"warn: no rename candidate for {candidate.path}", file=sys.stderr)
            reserved.add(candidate.path)
            continue

        target = reserve_target(candidate.path, basename, reserved)
        if target == candidate.path:
            reserved.add(candidate.path)
            continue

        planned.append(PlannedRename(source=candidate.path, target=target, reason=reason, url=url))

    return planned


def apply_renames(planned: list[PlannedRename]) -> None:
    temporary_moves: list[tuple[Path, Path]] = []
    for rename in planned:
        if not rename.source.exists():
            print(f"warn: skipping missing source during apply: {rename.source}", file=sys.stderr)
            continue
        temporary = rename.source.with_name(f".codex-source-rename-{rename.source.name}")
        counter = 2
        while temporary.exists():
            temporary = rename.source.with_name(f".codex-source-rename-{counter}-{rename.source.name}")
            counter += 1
        rename.source.rename(temporary)
        temporary_moves.append((temporary, rename.target))

    for temporary, target in temporary_moves:
        temporary.rename(target)


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    themes = {theme.lower() for theme in args.theme}
    sources = {source.lower() for source in args.source}

    if not root.exists():
        print(f"error: missing root directory: {root}", file=sys.stderr)
        return 1

    candidates = enumerate_candidates(root, themes=themes, sources=sources)
    if not candidates:
        print("No source-named wallpapers found.")
        return 0

    planned = plan_renames(candidates, root=root, offline=args.offline)
    if not planned:
        print("No renames planned.")
        return 0

    cwd = Path.cwd().resolve()
    for rename in planned:
        source = rename.source.relative_to(cwd)
        target = rename.target.relative_to(cwd)
        suffix = f" [{rename.reason}]"
        if rename.url:
            suffix += f" {rename.url}"
        print(f"{source} -> {target}{suffix}")

    print()
    print(f"Planned renames: {len(planned)}")

    if args.apply:
        apply_renames(planned)
        print("Applied renames.")
    else:
        print("Dry run only. Re-run with --apply to rename files.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
