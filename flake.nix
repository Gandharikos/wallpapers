{
  description = ''
    Personal collection of wallpapers organized by theme, installable via Nix.
  '';

  outputs = _: let
    lib = import ./lib;
  in {
    # Wallpapers output - organized by theme
    # Access via: inputs.wallpapers.wallpapers.tokyonight-street-01
    # Or filter by tags: builtins.filter (w: builtins.elem "catppuccin" w.tags)
    wallpapers = lib.toWallpkgs ./wallpapers ["png" "jpg" "jpeg" "gif" "webp"];
  };
}
