#!/usr/bin/env python3
"""
check-duplicate-names.py — Find duplicate filenames within the same directory while ignoring extensions.

Usage:
    python3 scripts/check-duplicate-names.py
    python3 scripts/check-duplicate-names.py --dir wallpapers
"""

from __future__ import annotations

import argparse
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


def collect_images(directory: Path) -> list[Path]:
    """Recursively collect supported image files under a directory."""
    return sorted(
        f
        for f in directory.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def basename_without_suffix(path: Path) -> str:
    """Return the filename without its last extension."""
    return path.stem


def find_duplicate_names(files: list[Path]) -> dict[tuple[Path, str], list[Path]]:
    """Group files by parent directory and filename stem, then return only duplicate groups."""
    groups: dict[tuple[Path, str], list[Path]] = defaultdict(list)
    for file_path in files:
        groups[(file_path.parent, basename_without_suffix(file_path))].append(file_path)

    return {
        key: paths
        for key, paths in sorted(groups.items(), key=lambda item: (str(item[0][0]), item[0][1]))
        if len(paths) > 1
    }


def run(directory: Path) -> int:
    files = collect_images(directory)
    if not files:
        print("No image files found.")
        return 0

    duplicate_groups = find_duplicate_names(files)
    if not duplicate_groups:
        print("No duplicate names found.")
        return 0

    print(f"Found {len(duplicate_groups)} duplicate name group(s) in the same directory:\n")

    duplicate_file_count = 0
    for index, ((parent_dir, name), paths) in enumerate(duplicate_groups.items(), start=1):
        duplicate_file_count += len(paths)
        print(f"[{index}] {name}")
        print(f"  Directory: {parent_dir.relative_to(directory.parent)}")
        for path in paths:
            print(f"  - {path.relative_to(directory.parent)}")
        print()

    print(f"Duplicate groups: {len(duplicate_groups)}")
    print(f"Files involved: {duplicate_file_count}")
    return 1


def main() -> None:
    default_dir = Path(__file__).resolve().parent.parent / "wallpapers"

    parser = argparse.ArgumentParser(
        description="Find duplicate filenames within the same directory while ignoring file extensions.",
    )
    parser.add_argument(
        "--dir",
        "-d",
        type=Path,
        default=default_dir,
        metavar="PATH",
        help=f"Directory to scan (default: {default_dir})",
    )
    args = parser.parse_args()

    if not args.dir.is_dir():
        print(f"Directory not found: {args.dir}", file=sys.stderr)
        sys.exit(2)

    sys.exit(run(args.dir))


if __name__ == "__main__":
    main()
