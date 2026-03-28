#!/usr/bin/env python3
"""
dedup.py — Detect and remove duplicate images in the wallpapers/wallpapers directory.

Usage:
    python3 dedup.py                  # Dry-run: scan the default wallpapers/ directory, no deletions
    python3 dedup.py --delete         # Actually delete duplicates (keeps the oldest file in each group)
    python3 dedup.py --dir /path/to   # Scan a custom directory
    python3 dedup.py --dir /path/to --delete

Deduplication strategy:
    - Content is verified by MD5 hash (file name and path are irrelevant)
    - Within each duplicate group, the file with the earliest modification time is kept
    - Works across subdirectories (e.g. the same image in catppuccin/ and gruvbox/ will be detected)
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".heic",
    ".tiff",
    ".tif",
    ".bmp",
    ".raw",
    ".cr2",
    ".nef",
}


# ── Utilities ───────────────────────────────────────────────────────────────


def md5_file(path: Path, chunk_size: int = 65536) -> str:
    """Read a file in chunks and return its MD5 hex digest (avoids loading the whole file into memory)."""
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def human_size(n_bytes: int) -> str:
    """Format a byte count as a human-readable string, e.g. '1.2 MB'."""
    for unit in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} TB"


# ── Core logic ──────────────────────────────────────────────────────────────


def collect_images(directory: Path) -> list[Path]:
    """Recursively collect all image files with supported extensions under a directory."""
    return [
        f
        for f in directory.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]


def build_hash_groups(files: list[Path]) -> dict[str, list[Path]]:
    """
    Compute the MD5 hash of each file and group files by hash value.
    Only groups with 2 or more members (true duplicates) are returned.
    """
    groups: dict[str, list[Path]] = defaultdict(list)
    total = len(files)
    for i, f in enumerate(files, 1):
        print(f"\r  Hashing... {i}/{total}", end="", flush=True)
        try:
            groups[md5_file(f)].append(f)
        except (OSError, PermissionError) as e:
            print(f"\n  ⚠️  Skipped (unreadable): {f}  ({e})")
    print()  # newline after progress indicator
    return {h: paths for h, paths in groups.items() if len(paths) > 1}


def choose_keeper(paths: list[Path]) -> Path:
    """
    Select the file to keep from a duplicate group.
    Prefers the file with the earliest modification time (treated as the original).
    Falls back to lexicographic path order for determinism when timestamps are equal.
    """
    return min(paths, key=lambda p: (p.stat().st_mtime, str(p)))


# ── Main flow ───────────────────────────────────────────────────────────────


def run(directory: Path, delete: bool) -> None:
    mode_label = "[DELETE MODE]" if delete else "[DRY RUN — no files will be deleted]"
    print(f"\n{'=' * 60}")
    print(f"  dedup.py  {mode_label}")
    print(f"  Scanning: {directory}")
    print(f"{'=' * 60}\n")

    # 1. Collect files
    files = collect_images(directory)
    if not files:
        print("No image files found. Exiting.")
        return
    print(f"Images found: {len(files)}\n")

    # 2. Hash and group
    dup_groups = build_hash_groups(files)
    if not dup_groups:
        print("✅ No duplicates found — the directory is already clean.")
        return

    # 3. Report
    total_to_delete = 0
    total_bytes_saved = 0
    all_to_delete: list[Path] = []

    print(f"Found {len(dup_groups)} duplicate group(s):\n")
    for i, (hash_val, paths) in enumerate(dup_groups.items(), 1):
        keeper = choose_keeper(paths)
        to_delete = [p for p in paths if p != keeper]
        size = keeper.stat().st_size
        saved = size * len(to_delete)
        total_to_delete += len(to_delete)
        total_bytes_saved += saved
        all_to_delete.extend(to_delete)

        print(f"  [{i}] MD5: {hash_val[:12]}...  ({human_size(size)} each)")
        print(f"      ✅ Keep:   {keeper.relative_to(directory.parent)}")
        for p in to_delete:
            print(
                f"      🗑️  {'Delete' if delete else 'Would delete'}: {p.relative_to(directory.parent)}"
            )
        print()

    print(f"{'─' * 60}")
    print(f"  Redundant files: {total_to_delete}")
    print(f"  Space to free:   {human_size(total_bytes_saved)}")
    print(f"{'─' * 60}\n")

    # 4. Delete (only when --delete is passed)
    if not delete:
        print("ℹ️  Dry-run complete — nothing was deleted.")
        print("   Re-run with --delete to actually remove the duplicates.\n")
        return

    deleted_count = 0
    failed: list[tuple[Path, str]] = []
    for p in all_to_delete:
        try:
            p.unlink()
            deleted_count += 1
            print(f"  🗑️  Deleted: {p.relative_to(directory.parent)}")
        except (OSError, PermissionError) as e:
            failed.append((p, str(e)))
            print(f"  ❌ Failed to delete: {p}  ({e})")

    print(
        f"\n✅ Done. Deleted {deleted_count} file(s), freed {human_size(total_bytes_saved)}."
    )
    if failed:
        print(f"⚠️  {len(failed)} file(s) could not be deleted — check permissions.")


# ── Entry point ─────────────────────────────────────────────────────────────


def main() -> None:
    # Default target: the wallpapers/ subdirectory one level above this script
    default_dir = Path(__file__).resolve().parent.parent / "wallpapers"

    parser = argparse.ArgumentParser(
        description="Detect and remove duplicate images using MD5 content hashing (file names are ignored).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--dir",
        "-d",
        type=Path,
        default=default_dir,
        metavar="PATH",
        help=f"Directory to scan (default: {default_dir})",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete duplicate files (omit for dry-run preview)",
    )
    args = parser.parse_args()

    if not args.dir.is_dir():
        print(f"❌ Directory not found: {args.dir}", file=sys.stderr)
        sys.exit(1)

    run(directory=args.dir, delete=args.delete)


if __name__ == "__main__":
    main()
