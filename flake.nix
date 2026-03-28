{
  description = ''
    Personal collection of wallpapers organized by theme, installable via Nix.
  '';

  outputs = _: let
    lib = import ./lib;
  in
    # Wallpapers output - organized by theme
    # Access via: inputs.wallpapers.tokyonight.anime-girl.path
    # Or filter by tags: builtins.filter (w: builtins.elem "catppuccin" w.tags)
    lib.toWallpkgs ./wallpapers ["png" "jpg" "jpeg" "gif" "webp"];
}
