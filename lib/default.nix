# Wallpaper library - converts directory structure to Nix attributes
# Based on wallpkgs by NotAShelf: https://github.com/NotAShelf/wallpkgs
let
  splitString =
    separator: str:
    let
      loop =
        str: acc: currentPos: currentSegment:
        if currentPos == builtins.stringLength str then
          # end of string: add the current segment (even if it's empty)
          acc ++ [ currentSegment ]
        else
          let
            char = builtins.substring currentPos 1 str;
          in
          if char == separator then
            # separator; add the current segment to acc and start a new segment
            loop str (acc ++ [ currentSegment ]) (currentPos + 1) ""
          else
            loop str acc (currentPos + 1) (currentSegment + char);
    in
    loop str [ ] 0 "";

  filterAttrs =
    f: attrs:
    let
      names = builtins.attrNames attrs;
      filteredNames = builtins.filter (name: f name attrs.${name}) names;
    in
    builtins.listToAttrs (
      map (name: {
        inherit name;
        value = attrs.${name};
      }) filteredNames
    );

  genAttrs =
    names: f:
    builtins.listToAttrs (
      map (name: {
        inherit name;
        value = f name;
      }) names
    );

  hasSuffix =
    suffix: content:
    let
      lenContent = builtins.stringLength content;
      lenSuffix = builtins.stringLength suffix;
    in
    lenContent >= lenSuffix && builtins.substring (lenContent - lenSuffix) lenContent content == suffix;

  concatMapAttrs =
    f: attrs: builtins.foldl' (it: ac: it // ac) { } (builtins.attrValues (builtins.mapAttrs f attrs));

  # Main function: converts a directory of wallpapers into a structured attribute set
  # Each wallpaper gets: path (file location), tags (from filename), hash (for verification)
  toWallpkgs =
    path: extensions:
    let
      hasValidExtension =
        file: builtins.foldl' (acc: elem: (hasSuffix elem "${file}") || acc) false extensions;

      fetchPath =
        path:
        filterAttrs (n: t: t == "directory" || (t == "regular" && hasValidExtension n)) (
          builtins.readDir path
        );

      getFiles =
        path:
        concatMapAttrs (
          n: v:
          if v == "directory" then
            {
              ${n} = getFiles "${path}/${n}";
            }
          else
            let
              name = builtins.head (splitString "." n);
            in
            {
              ${name} = {
                path = "${path}/${n}";
                tags = splitString "-" name;
                hash = builtins.hashFile "md5" "${path}/${n}";
              };
            }
        ) (fetchPath path);
    in
    getFiles path;
in
{
  inherit splitString filterAttrs genAttrs;
  inherit toWallpkgs;
}
