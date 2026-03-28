# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a personal wallpaper collection organized by color scheme and theme. It contains 600+ wallpaper images categorized into theme-based directories.

## Directory Structure

```
├── wallpapers/           # All wallpaper files organized by theme
│   ├── catppuccin/      # ~143 images
│   ├── tokyonight/      # ~105 images
│   ├── nordic/          # ~115 images
│   ├── gruvbox/         # ~40 images
│   ├── rosepine/        # ~35 images
│   ├── dracula/         # ~20 images
│   ├── cyberdream/
│   ├── decay/
│   ├── graphite/
│   ├── kanagawa/
│   ├── solarized/
│   └── unorganized/     # Uncategorized wallpapers
├── lib/                 # Nix library functions
│   └── default.nix      # Core toWallpkgs implementation
├── flake.nix            # Nix flake entry point
├── example.nix          # Usage examples
└── CLAUDE.md            # This file
```

## Nix Flake Structure

This repository is a Nix flake that exposes wallpapers as structured attributes:

- `flake.nix` - Main flake definition, exports `wallpapers` output (scans `./wallpapers`)
- `lib/default.nix` - Core library implementing `toWallpkgs` function (auto-generates tags from filenames)
- `wallpapers/` - All theme directories with wallpaper files
- `wallpapers-manual.nix.example` - Optional: Manual tag configuration template (like yunfachi/nix-config-wallpapers)

### How toWallpkgs Works

The `toWallpkgs` function scans directories and creates attributes for each wallpaper:
- **path**: Full file path to the wallpaper
- **tags**: List derived from filename by splitting on `-` (e.g., `catppuccin-anime-girl.png` → `["catppuccin" "anime" "girl"]`)
- **hash**: MD5 hash for file verification

### Two Approaches for Tags

**Approach 1: Automatic (current)** - Tags auto-generated from filenames
- Files split by `-` to create tags: `catppuccin-anime-cafe.png` → `["catppuccin", "anime", "cafe"]`
- Quick and automatic, no manual maintenance
- Current default in `flake.nix`

**Approach 2: Manual (optional)** - Manually curated tags (like yunfachi/nix-config-wallpapers)
- Use `wallpapers-manual.nix.example` as template
- Precise, descriptive tags for each wallpaper
- Better for curated collections
- Example: `"catppuccin/anime" = ["catppuccin" "anime" "girl" "colorful" "detailed"];`

For manual approach, copy `wallpapers-manual.nix.example` to `wallpapers-manual.nix` and update `flake.nix` to use it.

## Common Tasks

### Adding New Wallpapers

1. Determine the appropriate theme directory based on the wallpaper's color scheme
2. Use descriptive filenames with hyphens: `theme-subject-style.ext`
3. Place the file in `wallpapers/<theme>/`
4. If the theme is unclear or doesn't match existing themes, use `wallpapers/unorganized/`

### Organizing Wallpapers

- When moving wallpapers from `wallpapers/unorganized/` to theme directories, consider the dominant colors and aesthetic style
- Rename files to follow hyphen-separated convention for better Nix tag generation
- Keep filenames descriptive (e.g., `tokyonight-anime-cafe.png`, `gruvbox-forest-winter.jpg`)
- Supported image formats: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- All wallpapers must be inside the `wallpapers/` directory

### Testing Nix Flake

```bash
# Show all wallpapers
nix eval .#wallpapers --apply builtins.attrNames

# Check a specific wallpaper
nix eval .#wallpapers.catppuccin-01 --json

# Filter wallpapers by tag
nix eval .#wallpapers --apply 'w: builtins.filter (x: builtins.elem "catppuccin" x.tags) (builtins.attrValues w)'
```

## Git Workflow

Use conventional commit format:
- `feat:` when adding new wallpapers (e.g., "feat: add more tokyo night street photos")
- `chore:` when reorganizing or moving files
- `docs:` when updating documentation

Example: `feat: add cyberpunk wallpapers to gruvbox collection`
