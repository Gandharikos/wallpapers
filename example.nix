# Example usage in Home Manager or NixOS configuration
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    wallpapers.url = "github:yourusername/wallpapers";
  };

  outputs = {nixpkgs, wallpapers, ...}: {
    # Example 1: Use a specific wallpaper
    homeConfigurations.example = {
      home.file."Pictures/wallpaper.jpg".source = wallpapers.wallpapers.tokyonight.anime_cafe_tokyonight.path;
    };

    # Example 2: Filter wallpapers by tag (catppuccin theme)
    homeConfigurations.catppuccin-user = let
      catppuccinWalls = builtins.filter
        (wall: builtins.elem "catppuccin" wall.tags)
        (builtins.concatLists (builtins.map
          (dir: builtins.attrValues wallpapers.wallpapers.${dir})
          ["catppuccin"]));
    in {
      # Copy all catppuccin wallpapers
      home.file."Pictures/catppuccin" = {
        source = builtins.path {
          path = wallpapers.wallpapers.catppuccin;
          recursive = true;
        };
      };
    };

    # Example 3: Set as system wallpaper (Hyprland)
    homeConfigurations.hyprland-user = {
      wayland.windowManager.hyprland.settings = {
        exec-once = [
          "swaybg -i ${wallpapers.wallpapers.tokyonight.anime.path}"
        ];
      };
    };

    # Example 4: Random wallpaper selector
    homeConfigurations.random-wall = let
      tokyoWalls = builtins.attrValues wallpapers.wallpapers.tokyonight;
      randomWall = builtins.elemAt tokyoWalls 0; # Use your own randomization logic
    in {
      home.file."Pictures/current-wallpaper".source = randomWall.path;
    };

    # Example 5: Access wallpaper metadata
    homeConfigurations.metadata-example = let
      wall = wallpapers.wallpapers.catppuccin.anime;
    in {
      # wall.path - Full path to wallpaper
      # wall.tags - ["anime"]
      # wall.hash - MD5 hash
      home.file."wallpaper-info.txt".text = ''
        Path: ${wall.path}
        Tags: ${builtins.toString wall.tags}
        Hash: ${wall.hash}
      '';
    };
  };
}
