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

**Total wallpapers: 654**

### catppuccin (141 wallpapers)

|||
|-|-|
|![](wallpapers/catppuccin/angel.jpg)<br>**angel.jpg**|![](wallpapers/catppuccin/anime-2b.png)<br>**anime-2b.png**|
|![](wallpapers/catppuccin/anime-4k-uvwsx2m7duh51ale.jpg)<br>**anime-4k-uvwsx2m7duh51ale.jpg**|![](wallpapers/catppuccin/anime-angel.png)<br>**anime-angel.png**|
|![](wallpapers/catppuccin/anime-cafe-tokyonight.png)<br>**anime-cafe-tokyonight.png**|![](wallpapers/catppuccin/anime-cat-girl.png)<br>**anime-cat-girl.png**|

### cyberdream (15 wallpapers)

|||
|-|-|
|![](wallpapers/cyberdream/acrylic.jpg)<br>**acrylic.jpg**|![](wallpapers/cyberdream/alien-planet.jpeg)<br>**alien-planet.jpeg**|
|![](wallpapers/cyberdream/beach.jpg)<br>**beach.jpg**|![](wallpapers/cyberdream/cliff-edge.jpg)<br>**cliff-edge.jpg**|
|![](wallpapers/cyberdream/cyber-girl.jpg)<br>**cyber-girl.jpg**|![](wallpapers/cyberdream/cyberpunk-car.png)<br>**cyberpunk-car.png**|

### decay (12 wallpapers)

|||
|-|-|
|![](wallpapers/decay/abandoned.jpg)<br>**abandoned.jpg**|![](wallpapers/decay/abstract.jpg)<br>**abstract.jpg**|
|![](wallpapers/decay/arcade-red.png)<br>**arcade-red.png**|![](wallpapers/decay/beach-landscape.png)<br>**beach-landscape.png**|
|![](wallpapers/decay/black-white-girl.png)<br>**black-white-girl.png**|![](wallpapers/decay/blue-swirl.png)<br>**blue-swirl.png**|

### dracula (20 wallpapers)

|||
|-|-|
|![](wallpapers/dracula/cristina.png)<br>**cristina.png**|![](wallpapers/dracula/evangelion-end.jpg)<br>**evangelion-end.jpg**|
|![](wallpapers/dracula/evangelion-grey.jpg)<br>**evangelion-grey.jpg**|![](wallpapers/dracula/evangelion-hot.jpg)<br>**evangelion-hot.jpg**|
|![](wallpapers/dracula/evangelion-night.jpg)<br>**evangelion-night.jpg**|![](wallpapers/dracula/evangelion-red.jpg)<br>**evangelion-red.jpg**|

### graphite (12 wallpapers)

|||
|-|-|
|![](wallpapers/graphite/chainsawman-sketch.png)<br>**chainsawman-sketch.png**|![](wallpapers/graphite/cybergirl.jpg)<br>**cybergirl.jpg**|
|![](wallpapers/graphite/gojo.png)<br>**gojo.png**|![](wallpapers/graphite/japan-lake.jpg)<br>**japan-lake.jpg**|
|![](wallpapers/graphite/limbo.jpg)<br>**limbo.jpg**|![](wallpapers/graphite/min-mountain.jpg)<br>**min-mountain.jpg**|

### gruvbox (40 wallpapers)

|||
|-|-|
|![](wallpapers/gruvbox/astronaut.jpg)<br>**astronaut.jpg**|![](wallpapers/gruvbox/autumn-leaves.jpg)<br>**autumn-leaves.jpg**|
|![](wallpapers/gruvbox/beige-tree.png)<br>**beige-tree.png**|![](wallpapers/gruvbox/berserkdrac.png)<br>**berserkdrac.png**|
|![](wallpapers/gruvbox/bici.jpg)<br>**bici.jpg**|![](wallpapers/gruvbox/blackhole.jpeg)<br>**blackhole.jpeg**|

### kanagawa (3 wallpapers)

|||
|-|-|
|![](wallpapers/kanagawa/kanagawa-inverted-darker.jpg)<br>**kanagawa-inverted-darker.jpg**|![](wallpapers/kanagawa/mountain-dragon.jpg)<br>**mountain-dragon.jpg**|
|![](wallpapers/kanagawa/sunset-dragon.jpg)<br>**sunset-dragon.jpg**||

### nordic (113 wallpapers)

|||
|-|-|
|![](wallpapers/nordic/anime-eye.png)<br>**anime-eye.png**|![](wallpapers/nordic/anime-girl-sky.jpg)<br>**anime-girl-sky.jpg**|
|![](wallpapers/nordic/antman.jpg)<br>**antman.jpg**|![](wallpapers/nordic/astronaut-balloons.jpg)<br>**astronaut-balloons.jpg**|
|![](wallpapers/nordic/astronaut-nord.png)<br>**astronaut-nord.png**|![](wallpapers/nordic/astronaut-planet.jpg)<br>**astronaut-planet.jpg**|

### rosepine (34 wallpapers)

|||
|-|-|
|![](wallpapers/rosepine/anime-blood.jpg)<br>**anime-blood.jpg**|![](wallpapers/rosepine/awesome-landscape.png)<br>**awesome-landscape.png**|
|![](wallpapers/rosepine/bg_13.jpg)<br>**bg_13.jpg**|![](wallpapers/rosepine/blade3.png)<br>**blade3.png**|
|![](wallpapers/rosepine/blood-jungles.jpg)<br>**blood-jungles.jpg**|![](wallpapers/rosepine/burning-cherry.jpeg)<br>**burning-cherry.jpeg**|

### solarized (11 wallpapers)

|||
|-|-|
|![](wallpapers/solarized/chinatown.png)<br>**chinatown.png**|![](wallpapers/solarized/city-buildings.png)<br>**city-buildings.png**|
|![](wallpapers/solarized/crane.jpg)<br>**crane.jpg**|![](wallpapers/solarized/crow.png)<br>**crow.png**|
|![](wallpapers/solarized/darkness.jpg)<br>**darkness.jpg**|![](wallpapers/solarized/judy.png)<br>**judy.png**|

### tokyonight (128 wallpapers)

|||
|-|-|
|![](wallpapers/tokyonight/alfa.png)<br>**alfa.png**|![](wallpapers/tokyonight/anglerfish.jpg)<br>**anglerfish.jpg**|
|![](wallpapers/tokyonight/anime-chick.jpg)<br>**anime-chick.jpg**|![](wallpapers/tokyonight/anime-city.png)<br>**anime-city.png**|
|![](wallpapers/tokyonight/anime-girl-flowers-variant-2.jpg)<br>**anime-girl-flowers-variant-2.jpg**|![](wallpapers/tokyonight/anime-girl-flowers-variant.jpg)<br>**anime-girl-flowers-variant.jpg**|

### unorganized (125 wallpapers)

|||
|-|-|
|![](wallpapers/unorganized/abstract.jpg)<br>**abstract.jpg**|![](wallpapers/unorganized/alien-planet.jpeg)<br>**alien-planet.jpeg**|
|![](wallpapers/unorganized/android-dark-lines.jpg)<br>**android-dark-lines.jpg**|![](wallpapers/unorganized/android-sakura.jpg)<br>**android-sakura.jpg**|
|![](wallpapers/unorganized/anime-nord.png)<br>**anime-nord.png**|![](wallpapers/unorganized/arch-eagle.png)<br>**arch-eagle.png**|


## Credits

Special thanks to every wallpaper creator. If you are the creator of any wallpaper here and would like attribution or removal, please [open an issue](https://github.com/yourusername/wallpapers/issues).

## License

MIT License - See [LICENSE](LICENSE) file for details.
