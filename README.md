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

**Total wallpapers: 638**

### catppuccin (143 wallpapers)

|||
|-|-|
|![](wallpapers/catppuccin/2b.png)<br>**2b.png**|![](wallpapers/catppuccin/4k-ai-mountain.jpg)<br>**4k-ai-mountain.jpg**|
|![](wallpapers/catppuccin/aesthetic_deer.png)<br>**aesthetic_deer.png**|![](wallpapers/catppuccin/aesthetic-japan.jpg)<br>**aesthetic-japan.jpg**|
|![](wallpapers/catppuccin/anime1.jpeg)<br>**anime1.jpeg**|![](wallpapers/catppuccin/anime-4k-uvwsx2m7duh51ale.jpg)<br>**anime-4k-uvwsx2m7duh51ale.jpg**|

### cyberdream (16 wallpapers)

|||
|-|-|
|![](wallpapers/cyberdream/acrylic.jpg)<br>**acrylic.jpg**|![](wallpapers/cyberdream/alien_planet.jpeg)<br>**alien_planet.jpeg**|
|![](wallpapers/cyberdream/beach.jpg)<br>**beach.jpg**|![](wallpapers/cyberdream/cliff-edge.jpg)<br>**cliff-edge.jpg**|
|![](wallpapers/cyberdream/cyber-girl.jpg)<br>**cyber-girl.jpg**|![](wallpapers/cyberdream/cyberpunk_car.png)<br>**cyberpunk_car.png**|

### decay (12 wallpapers)

|||
|-|-|
|![](wallpapers/decay/abandoned.jpg)<br>**abandoned.jpg**|![](wallpapers/decay/abstract.jpg)<br>**abstract.jpg**|
|![](wallpapers/decay/arcade_decay_red.png)<br>**arcade_decay_red.png**|![](wallpapers/decay/beach_landscape.png)<br>**beach_landscape.png**|
|![](wallpapers/decay/black-white-girl.png)<br>**black-white-girl.png**|![](wallpapers/decay/blue_swirl.png)<br>**blue_swirl.png**|

### dracula (20 wallpapers)

|||
|-|-|
|![](wallpapers/dracula/Cristina.png)<br>**Cristina.png**|![](wallpapers/dracula/evangelion-dracula+.png)<br>**evangelion-dracula+.png**|
|![](wallpapers/dracula/evangelion-end.jpg)<br>**evangelion-end.jpg**|![](wallpapers/dracula/evangelion-grey.jpg)<br>**evangelion-grey.jpg**|
|![](wallpapers/dracula/evangelion-hot.jpg)<br>**evangelion-hot.jpg**|![](wallpapers/dracula/evangelion-night.jpg)<br>**evangelion-night.jpg**|

### graphite (12 wallpapers)

|||
|-|-|
|![](wallpapers/graphite/chainsawman_sketch.png)<br>**chainsawman_sketch.png**|![](wallpapers/graphite/cybergirl.jpg)<br>**cybergirl.jpg**|
|![](wallpapers/graphite/gojo.png)<br>**gojo.png**|![](wallpapers/graphite/japan_lake.jpg)<br>**japan_lake.jpg**|
|![](wallpapers/graphite/limbo.jpg)<br>**limbo.jpg**|![](wallpapers/graphite/min_mountain.jpg)<br>**min_mountain.jpg**|

### gruvbox (40 wallpapers)

|||
|-|-|
|![](wallpapers/gruvbox/astronaut.jpg)<br>**astronaut.jpg**|![](wallpapers/gruvbox/autumn_leaves.jpg)<br>**autumn_leaves.jpg**|
|![](wallpapers/gruvbox/beige_tree.png)<br>**beige_tree.png**|![](wallpapers/gruvbox/berserkdrac.png)<br>**berserkdrac.png**|
|![](wallpapers/gruvbox/bg_19.jpg)<br>**bg_19.jpg**|![](wallpapers/gruvbox/bg_20.jpg)<br>**bg_20.jpg**|

### kanagawa (3 wallpapers)

|||
|-|-|
|![](wallpapers/kanagawa/kanagawa-inverted-darker.jpg)<br>**kanagawa-inverted-darker.jpg**|![](wallpapers/kanagawa/mountain_kanagawa-dragon.jpg)<br>**mountain_kanagawa-dragon.jpg**|
|![](wallpapers/kanagawa/sunset_kanagawa-dragon.jpg)<br>**sunset_kanagawa-dragon.jpg**||

### nordic (115 wallpapers)

|||
|-|-|
|![](wallpapers/nordic/anime-eye-nord.png)<br>**anime-eye-nord.png**|![](wallpapers/nordic/Antman.jpg)<br>**Antman.jpg**|
|![](wallpapers/nordic/arch-chan_to.png)<br>**arch-chan_to.png**|![](wallpapers/nordic/astronaut-balloons.jpg)<br>**astronaut-balloons.jpg**|
|![](wallpapers/nordic/astronaut-nord.png)<br>**astronaut-nord.png**|![](wallpapers/nordic/astronaut-planet.jpg)<br>**astronaut-planet.jpg**|

### rosepine (35 wallpapers)

|||
|-|-|
|![](wallpapers/rosepine/anime_blood.jpg)<br>**anime_blood.jpg**|![](wallpapers/rosepine/awesome-landscape.png)<br>**awesome-landscape.png**|
|![](wallpapers/rosepine/bg_13.jpg)<br>**bg_13.jpg**|![](wallpapers/rosepine/blade3.png)<br>**blade3.png**|
|![](wallpapers/rosepine/BloodJungles.jpg)<br>**BloodJungles.jpg**|![](wallpapers/rosepine/burning_cherry.jpeg)<br>**burning_cherry.jpeg**|

### solarized (11 wallpapers)

|||
|-|-|
|![](wallpapers/solarized/chinatown.png)<br>**chinatown.png**|![](wallpapers/solarized/city-buildings.png)<br>**city-buildings.png**|
|![](wallpapers/solarized/crane.jpg)<br>**crane.jpg**|![](wallpapers/solarized/crow.png)<br>**crow.png**|
|![](wallpapers/solarized/darkness.jpg)<br>**darkness.jpg**|![](wallpapers/solarized/judy.png)<br>**judy.png**|

### tokyonight (105 wallpapers)

|||
|-|-|
|![](wallpapers/tokyonight/aesthetic-hollow-knight-purple-desktop-wallpaper.jpg)<br>**aesthetic-hollow-knight-purple-desktop-wallpaper.jpg**|![](wallpapers/tokyonight/Aesthetic_Japan_Wallpapers.jpg)<br>**Aesthetic_Japan_Wallpapers.jpg**|
|![](wallpapers/tokyonight/alex-knight-5-GNa303REg-unsplash.jpg)<br>**alex-knight-5-GNa303REg-unsplash.jpg**|![](wallpapers/tokyonight/alfa.png)<br>**alfa.png**|
|![](wallpapers/tokyonight/amilia.jpg)<br>**amilia.jpg**|![](wallpapers/tokyonight/anime-chick.jpg)<br>**anime-chick.jpg**|

### unorganized (126 wallpapers)

|||
|-|-|
|![](wallpapers/unorganized/abstract.jpg)<br>**abstract.jpg**|![](wallpapers/unorganized/android-dark-lines.jpg)<br>**android-dark-lines.jpg**|
|![](wallpapers/unorganized/android-sakura.jpg)<br>**android-sakura.jpg**|![](wallpapers/unorganized/anime-nord.png)<br>**anime-nord.png**|
|![](wallpapers/unorganized/arch-eagle.png)<br>**arch-eagle.png**|![](wallpapers/unorganized/arch-nord-dark.png)<br>**arch-nord-dark.png**|


## Credits

Special thanks to every wallpaper creator. If you are the creator of any wallpaper here and would like attribution or removal, please [open an issue](https://github.com/yourusername/wallpapers/issues).

## License

MIT License - See [LICENSE](LICENSE) file for details.
