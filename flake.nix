{
  description = ''
    Personal collection of wallpapers organized by theme, installable via Nix.
  '';

  outputs = _:
    let
      lib = import ./lib;
      wallpapers = lib.toWallpkgs ./wallpapers [
        "png"
        "jpg"
        "jpeg"
        "gif"
        "webp"
      ];
    in
    wallpapers;
}
