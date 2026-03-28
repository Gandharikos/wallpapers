#!/usr/bin/env bash
# Generate README.md preview section with 6 sample wallpapers per theme

set -e

OUTPUT_FILE="README.md.new"
WALLPAPERS_DIR="wallpapers"

# Start building the new README
cat > "$OUTPUT_FILE" << 'EOF'
# wallpapers

Personal collection of 600+ wallpapers organized by theme and color scheme, installable via Nix.

## Directory Structure

```
wallpapers/
├── catppuccin/     # Catppuccin color scheme (~143 wallpapers)
├── tokyonight/     # Tokyo Night theme (~105 wallpapers)
├── nordic/         # Nordic/Nord theme (~115 wallpapers)
├── gruvbox/        # Gruvbox color scheme (~40 wallpapers)
├── rosepine/       # Rosé Pine theme (~35 wallpapers)
├── dracula/        # Dracula theme (~20 wallpapers)
├── cyberdream/     # Cyberdream theme
├── decay/          # Decay theme
├── graphite/       # Graphite theme
├── kanagawa/       # Kanagawa theme
├── solarized/      # Solarized theme
└── unorganized/    # Unsorted wallpapers
```

## Usage with Nix

This repository is a Nix flake. Add it to your flake inputs:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    wallpapers.url = "github:yourusername/wallpapers";
  };

  outputs = {nixpkgs, wallpapers, ...}: {
    # Example: Use a specific wallpaper
    # wallpapers.wallpapers.tokyonight.anime.path

    # Example: Filter wallpapers by tag
    homeConfigurations.youruser = {
      home.file."Pictures/catppuccin-walls" = {
        source = let
          catppuccinWalls = builtins.filter
            (wall: builtins.elem "catppuccin" wall.tags)
            (builtins.attrValues wallpapers.wallpapers);
        in catppuccinWalls;
      };
    };
  };
}
```

### Accessing Wallpapers

Each wallpaper has the following attributes:
- `path` - Full path to the wallpaper file
- `tags` - List of tags derived from filename (split by `-`)
- `hash` - MD5 hash for verification

Example:
```nix
# Access: wallpapers.wallpapers.catppuccin.anime-girl
# Returns: { path = "..."; tags = ["anime", "girl"]; hash = "..."; }
```

## Preview

EOF

# Count total wallpapers
TOTAL=$(find "$WALLPAPERS_DIR" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" \) | wc -l | tr -d ' ')
echo "**Total wallpapers: $TOTAL**" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Process each theme directory (in sorted order)
for theme_dir in $(find "$WALLPAPERS_DIR" -mindepth 1 -maxdepth 1 -type d | sort); do
    theme=$(basename "$theme_dir")
    echo "Processing theme: $theme"

    # Count wallpapers in this theme
    count=$(find "$theme_dir" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" \) | wc -l | tr -d ' ')

    # Get up to 6 sample wallpapers
    samples=()
    while IFS= read -r file; do
        samples+=("$file")
        if [ ${#samples[@]} -ge 6 ]; then
            break
        fi
    done < <(find "$theme_dir" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" \) | sort | head -6)

    if [ ${#samples[@]} -eq 0 ]; then
        continue
    fi

    # Add theme header
    echo "### $theme ($count wallpapers)" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    # Create table header
    echo "|||" >> "$OUTPUT_FILE"
    echo "|-|-|" >> "$OUTPUT_FILE"

    # Add wallpapers in pairs (2 per row)
    for ((i=0; i<${#samples[@]}; i+=2)); do
        file1="${samples[$i]}"
        filename1=$(basename "$file1")

        if [ $((i+1)) -lt ${#samples[@]} ]; then
            file2="${samples[$((i+1))]}"
            filename2=$(basename "$file2")
            echo "|![]($file1)<br>**$filename1**|![]($file2)<br>**$filename2**|" >> "$OUTPUT_FILE"
        else
            echo "|![]($file1)<br>**$filename1**||" >> "$OUTPUT_FILE"
        fi
    done

    echo "" >> "$OUTPUT_FILE"
done

# Add footer
cat >> "$OUTPUT_FILE" << 'EOF'

## Credits

Special thanks to every wallpaper creator. If you are the creator of any wallpaper here and would like attribution or removal, please [open an issue](https://github.com/yourusername/wallpapers/issues).

## License

MIT License - See [LICENSE](LICENSE) file for details.
EOF

echo ""
echo "✅ Generated $OUTPUT_FILE"
echo "Review it and then: mv $OUTPUT_FILE README.md"
