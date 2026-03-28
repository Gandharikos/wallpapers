#!/usr/bin/env swift

import Foundation
import ImageIO
import Vision

struct Options {
  var root = URL(fileURLWithPath: "wallpapers", isDirectory: true)
  var apply = false
  var themes: Set<String> = []
  var inspectPath: String?
}

struct PlannedRename {
  let source: URL
  let target: URL
  let reason: String
}

enum RenameError: Error, CustomStringConvertible {
  case invalidArguments(String)
  case imageLoadFailed(URL)
  case visionFailed(URL, String)
  case renameConflict(URL)

  var description: String {
    switch self {
    case .invalidArguments(let message):
      return message
    case .imageLoadFailed(let url):
      return "Failed to load image data for \(url.path)"
    case .visionFailed(let url, let reason):
      return "Vision failed for \(url.path): \(reason)"
    case .renameConflict(let url):
      return "Multiple files resolved to the same target: \(url.path)"
    }
  }
}

let supportedExtensions: Set<String> = ["jpg", "jpeg", "png", "gif", "webp"]

let themeTokens: Set<String> = [
  "catppuccin", "cyberdream", "decay", "dracula", "graphite", "gruvbox",
  "kanagawa", "nord", "nordic", "rosepine", "solarized", "tokyonight", "unorganized",
]

let noiseTokens: Set<String> = [
  "a", "an", "and", "at", "by", "for", "from", "in", "of", "on", "the", "to", "with",
  "bg", "wall", "wallpaper", "wallpapers", "wallhaven", "unknown", "sample", "image", "photo",
  "desktop", "mobile", "wide", "final", "flipped", "live", "old", "new", "original",
  "k", "ps", "4k", "3k", "2k", "8k", "hd", "uhd", "ps4", "v1", "v2", "v3", "v4", "v5", "v6", "v7",
  "01", "02", "03", "04", "05", "06", "07", "08", "09",
  "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
  "jpeg", "jpg", "png", "gif", "webp",
]

let genericClassifierTokens: Set<String> = [
  "art", "artwork", "background", "blur", "bright", "close", "color", "colorful",
  "dark", "day", "design", "graphic", "illustration", "indoors", "light", "lighting",
  "modern", "night", "outdoor", "outside", "pattern", "picture", "scenery", "scene",
  "sky", "style", "texture", "visual",
]

let semanticKeepTokens: Set<String> = [
  "2b", "angel", "anime", "arch", "astronaut", "beach", "bebop", "cat", "castle", "city",
  "cyberpunk", "deer", "dragon", "earth", "evangelion", "forest", "fox", "fuji", "girl",
  "gojo", "japan", "kiryu", "lake", "landscape", "lofi", "mario", "mask", "mecha", "moon",
  "mountain", "naruto", "neon", "nier", "nix", "nixos", "ocean", "pagoda", "planet", "portrait",
  "retro", "river", "robot", "samurai", "sea", "shrine", "street", "sunset", "tokyo", "torii",
  "tree", "witcher", "woman", "wolf",
]

func usage() -> String {
  """
  Usage: scripts/semantic-rename.swift [--apply] [--root PATH] [--theme NAME ...]

    --apply      Rename files in place. Without this flag the script prints a dry run.
    --root PATH  Root wallpaper directory. Defaults to ./wallpapers
    --theme NAME Limit processing to one or more theme subdirectories.
    --inspect    Print token/debug information for a single file.
  """
}

func parseArgs() throws -> Options {
  var options = Options()
  var index = 1
  let arguments = CommandLine.arguments

  while index < arguments.count {
    let argument = arguments[index]
    switch argument {
    case "--apply":
      options.apply = true
    case "--root":
      index += 1
      guard index < arguments.count else {
        throw RenameError.invalidArguments("--root requires a value\n\(usage())")
      }
      options.root = URL(fileURLWithPath: arguments[index], isDirectory: true)
    case "--theme":
      index += 1
      guard index < arguments.count else {
        throw RenameError.invalidArguments("--theme requires a value\n\(usage())")
      }
      options.themes.insert(arguments[index].lowercased())
    case "--inspect":
      index += 1
      guard index < arguments.count else {
        throw RenameError.invalidArguments("--inspect requires a value\n\(usage())")
      }
      options.inspectPath = arguments[index]
    case "--help", "-h":
      throw RenameError.invalidArguments(usage())
    default:
      throw RenameError.invalidArguments("Unknown argument: \(argument)\n\(usage())")
    }
    index += 1
  }

  return options
}

func insertingSpacesForCamelCase(_ input: String) -> String {
  let firstPass = input.replacingOccurrences(
    of: "([a-z0-9])([A-Z])",
    with: "$1 $2",
    options: .regularExpression
  )
  return firstPass.replacingOccurrences(
    of: "([A-Z]+)([A-Z][a-z])",
    with: "$1 $2",
    options: .regularExpression
  )
}

func tokenize(_ input: String) -> [String] {
  let camelSpaced = insertingSpacesForCamelCase(input)
  let folded = camelSpaced.folding(
    options: [.diacriticInsensitive, .caseInsensitive, .widthInsensitive],
    locale: .current
  )
  let normalized = folded
    .lowercased()
    .replacingOccurrences(of: #"[^a-z0-9]+"#, with: " ", options: .regularExpression)

  let rawTokens = normalized
    .split(separator: " ")
    .map(String.init)

  return rawTokens.flatMap { token -> [String] in
    guard let match = token.range(of: #"^([a-z]{2,})(\d+)$"#, options: .regularExpression) else {
      return [token]
    }

    let tokenString = String(token[match])
    let prefix = tokenString.replacingOccurrences(
      of: #"^([a-z]{2,})(\d+)$"#,
      with: "$1",
      options: .regularExpression
    )
    let digits = tokenString.replacingOccurrences(
      of: #"^([a-z]{2,})(\d+)$"#,
      with: "$2",
      options: .regularExpression
    )

    return [prefix, digits]
  }
}

func dedupe(_ tokens: [String]) -> [String] {
  var seen = Set<String>()
  var result: [String] = []

  for token in tokens where !token.isEmpty {
    if seen.insert(token).inserted {
      result.append(token)
    }
  }

  return result
}

func isNumeric(_ token: String) -> Bool {
  token.allSatisfy(\.isNumber)
}

func isVersionToken(_ token: String) -> Bool {
  token.range(of: #"^v0*\d+$"#, options: .regularExpression) != nil
}

func looksRandomBasename(_ basename: String) -> Bool {
  basename.range(of: #"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9]{6,}$"#, options: .regularExpression) != nil
}

func isKebabCase(_ basename: String) -> Bool {
  basename.range(of: #"^[a-z0-9]+(?:-[a-z0-9]+)*$"#, options: .regularExpression) != nil
}

func looksOpaque(_ basename: String) -> Bool {
  let lowered = basename.lowercased()
  let opaquePatterns = [
    #"^bg[_-]?\d+$"#,
    #"^wallhaven(?:[-_][a-z0-9]+)?$"#,
    #"^wallpaper(?:[-_]?\d+)?(?:[-_].+)?$"#,
    #"^unknown(?:[-_].+)?$"#,
    #"^img[-_].+$"#,
    #"^dsc[-_].+$"#,
    #".+-unsplash$"#,
    #"^melissa[_ -]?wall[_ -]?\d+$"#,
  ]

  return opaquePatterns.contains {
    lowered.range(of: $0, options: .regularExpression) != nil
  }
}

func hasSourceNoise(_ basename: String) -> Bool {
  let lowered = basename.lowercased()
  return lowered.contains("unsplash")
    || lowered.contains("getty")
    || lowered.contains("wallhaven")
}

func hasTrailingOrdinalNoise(_ basename: String) -> Bool {
  basename.lowercased().range(of: #"(?:^|[_-])\d+$"#, options: .regularExpression) != nil
}

func trailingOrdinalToken(from basename: String) -> String? {
  let lowered = basename.lowercased()
  guard hasTrailingOrdinalNoise(lowered) else {
    return nil
  }

  let extracted = lowered.replacingOccurrences(
    of: #".*(?:^|[_-])(\d+)$"#,
    with: "$1",
    options: .regularExpression
  )

  return extracted.isEmpty ? nil : extracted
}

func cleanedExistingTokens(from basename: String, theme: String) -> [String] {
  if hasSourceNoise(basename) {
    return []
  }

  let themeParts = Set(tokenize(theme))
  let filtered = tokenize(basename).map { token -> String in
    switch token {
    case "win":
      return "windows"
    default:
      return token
    }
  }.filter { token in
    !noiseTokens.contains(token)
      && !themeParts.contains(token)
      && !isNumeric(token)
      && !isVersionToken(token)
  }

  return dedupe(filtered)
}

func classifierTokens(from identifier: String) -> [String] {
  let simplified = identifier
    .split(separator: ",")
    .prefix(2)
    .map(String.init)
    .joined(separator: " ")

  var tokens = tokenize(simplified).map { token -> String in
    switch token {
    case "cartoon", "comic", "manga", "anime":
      return "anime"
    case "automobile", "auto":
      return "car"
    case "metropolis":
      return "city"
    case "seashore":
      return "coast"
    case "woodland":
      return "forest"
    case "valley":
      return "valley"
    case "volcano":
      return "volcano"
    case "spaceship":
      return "spacecraft"
    default:
      return token
    }
  }

  tokens = tokens.filter { token in
    !noiseTokens.contains(token)
      && !genericClassifierTokens.contains(token)
      && !isNumeric(token)
      && !isVersionToken(token)
  }

  return dedupe(tokens)
}

func loadImage(at url: URL) throws -> CGImage {
  guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
        let image = CGImageSourceCreateImageAtIndex(source, 0, nil)
  else {
    throw RenameError.imageLoadFailed(url)
  }

  return image
}

func detectFace(in image: CGImage, fileURL: URL) throws -> Bool {
  let request = VNDetectFaceRectanglesRequest()
  let handler = VNImageRequestHandler(cgImage: image, options: [:])

  do {
    try handler.perform([request])
    return !(request.results ?? []).isEmpty
  } catch {
    throw RenameError.visionFailed(fileURL, error.localizedDescription)
  }
}

func classifyImage(at url: URL) throws -> [String] {
  let image = try loadImage(at: url)
  let request = VNClassifyImageRequest()
  let handler = VNImageRequestHandler(cgImage: image, options: [:])

  do {
    try handler.perform([request])
  } catch {
    throw RenameError.visionFailed(url, error.localizedDescription)
  }

  let observations = request.results ?? []

  var tokens: [String] = []
  for observation in observations.prefix(8) where observation.confidence >= 0.12 {
    tokens.append(contentsOf: classifierTokens(from: observation.identifier))
  }

  if try detectFace(in: image, fileURL: url) && !tokens.contains("portrait") {
    tokens.append("portrait")
  }

  return dedupe(tokens)
}

func mergeTokens(existing: [String], classified: [String]) -> [String] {
  var merged: [String] = []
  let existingPreferred = existing.filter { semanticKeepTokens.contains($0) || existing.count <= 3 }
  merged.append(contentsOf: existingPreferred)
  merged.append(contentsOf: classified)
  merged.append(contentsOf: existing)

  let filtered = dedupe(merged).filter { token in
    !noiseTokens.contains(token)
      && !isVersionToken(token)
  }

  return Array(filtered.prefix(4))
}

func candidateBasename(for file: URL, theme: String) throws -> (String, String)? {
  let basename = file.deletingPathExtension().lastPathComponent
  let existing = cleanedExistingTokens(from: basename, theme: theme)
  let requiresNormalization = !isKebabCase(basename)
  let needsSemanticRecovery = looksOpaque(basename)
    || hasSourceNoise(basename)
    || existing.isEmpty
  let wantsSemanticSupplement = hasTrailingOrdinalNoise(basename)
    || (requiresNormalization && existing.count == 1)
  let shouldTryVision = needsSemanticRecovery || wantsSemanticSupplement

  if !requiresNormalization && !shouldTryVision {
    return nil
  }

  var classified: [String] = []
  var usedVision = false
  if shouldTryVision {
    do {
      classified = try classifyImage(at: file)
      usedVision = !classified.isEmpty
    } catch {
      if needsSemanticRecovery && existing.isEmpty {
        return nil
      }
    }
  }

  var tokens = usedVision ? mergeTokens(existing: existing, classified: classified) : existing

  if !usedVision && looksRandomBasename(basename) {
    return nil
  }

  if !usedVision && hasTrailingOrdinalNoise(basename) {
    if let trailingOrdinal = trailingOrdinalToken(from: basename), !tokens.contains(trailingOrdinal) {
      tokens.append(trailingOrdinal)
    }
  }

  if tokens.isEmpty {
    tokens = Array(classified.prefix(4))
  }

  if tokens.isEmpty {
    tokens = tokenize(basename).filter { !$0.isEmpty && !$0.allSatisfy(\.isNumber) }
  }

  tokens = dedupe(tokens)

  guard !tokens.isEmpty else {
    return nil
  }

  let newBasename = tokens.joined(separator: "-")
  guard newBasename != basename else {
    return nil
  }

  let reason = usedVision ? "semantic" : "normalize"
  return (newBasename, reason)
}

func enumerateImageFiles(root: URL, themes: Set<String>) throws -> [URL] {
  let resourceKeys: [URLResourceKey] = [.isRegularFileKey, .isDirectoryKey]
  guard let enumerator = FileManager.default.enumerator(
    at: root,
    includingPropertiesForKeys: resourceKeys,
    options: [.skipsHiddenFiles]
  ) else {
    return []
  }

  var files: [URL] = []

  for case let fileURL as URL in enumerator {
    let values = try fileURL.resourceValues(forKeys: Set(resourceKeys))
    if values.isDirectory == true {
      if fileURL.pathExtension == "git" {
        enumerator.skipDescendants()
      }
      continue
    }

    guard values.isRegularFile == true else {
      continue
    }

    let ext = fileURL.pathExtension.lowercased()
    guard supportedExtensions.contains(ext) else {
      continue
    }

    let theme = fileURL.deletingLastPathComponent().lastPathComponent.lowercased()
    if !themes.isEmpty && !themes.contains(theme) {
      continue
    }

    files.append(fileURL)
  }

  return files.sorted { $0.path < $1.path }
}

func disambiguatedTarget(
  directory: URL,
  basename: String,
  ext: String,
  reserved: inout Set<String>
) -> URL {
  var candidate = basename
  var attempt = 2

  while reserved.contains("\(directory.path)/\(candidate).\(ext)") {
    candidate = "\(basename)-\(attempt)"
    attempt += 1
  }

  let target = directory.appendingPathComponent(candidate).appendingPathExtension(ext)
  reserved.insert(target.path)
  return target
}

func planRenames(root: URL, themes: Set<String>) throws -> [PlannedRename] {
  let files = try enumerateImageFiles(root: root, themes: themes)
  var reserved = Set(files.map(\.path))
  var planned: [PlannedRename] = []

  for file in files {
    let theme = file.deletingLastPathComponent().lastPathComponent
    guard let (newBasename, reason) = try candidateBasename(for: file, theme: theme) else {
      continue
    }

    reserved.remove(file.path)
    let target = disambiguatedTarget(
      directory: file.deletingLastPathComponent(),
      basename: newBasename,
      ext: file.pathExtension,
      reserved: &reserved
    )

    if target.path == file.path {
      reserved.insert(file.path)
      continue
    }

    planned.append(PlannedRename(source: file, target: target, reason: reason))
  }

  let targets = Dictionary(grouping: planned, by: \.target.path)
  for (_, group) in targets where group.count > 1 {
    if let collision = group.first?.target {
      throw RenameError.renameConflict(collision)
    }
  }

  return planned
}

func applyRenames(_ planned: [PlannedRename]) throws {
  let fileManager = FileManager.default
  var temporaryMoves: [(temp: URL, final: URL)] = []

  for action in planned {
    let tempName = ".codex-rename-\(UUID().uuidString)-\(action.source.lastPathComponent)"
    let tempURL = action.source.deletingLastPathComponent().appendingPathComponent(tempName)
    try fileManager.moveItem(at: action.source, to: tempURL)
    temporaryMoves.append((temp: tempURL, final: action.target))
  }

  for move in temporaryMoves {
    try fileManager.moveItem(at: move.temp, to: move.final)
  }
}

func relativePath(_ url: URL) -> String {
  let currentDirectory = URL(fileURLWithPath: FileManager.default.currentDirectoryPath, isDirectory: true)
  let currentPath = currentDirectory.standardizedFileURL.path
  let fullPath = url.standardizedFileURL.path

  if fullPath.hasPrefix(currentPath + "/") {
    return String(fullPath.dropFirst(currentPath.count + 1))
  }

  return fullPath
}

func inspect(filePath: String, root: URL) {
  _ = root
  let fileURL = URL(fileURLWithPath: filePath, relativeTo: URL(fileURLWithPath: FileManager.default.currentDirectoryPath))
    .standardizedFileURL
  let theme = fileURL.deletingLastPathComponent().lastPathComponent
  let basename = fileURL.deletingPathExtension().lastPathComponent
  let existing = cleanedExistingTokens(from: basename, theme: theme)

  print("File: \(relativePath(fileURL))")
  print("Theme: \(theme)")
  print("Existing tokens: \(existing)")
  print("Looks opaque: \(looksOpaque(basename))")
  print("Has source noise: \(hasSourceNoise(basename))")
  print("Has trailing ordinal noise: \(hasTrailingOrdinalNoise(basename))")

  do {
    let classified = try classifyImage(at: fileURL)
    print("Classifier tokens: \(classified)")
  } catch {
    print("Classifier error: \(error)")
  }

  do {
    if let (candidate, reason) = try candidateBasename(for: fileURL, theme: theme) {
      print("Proposed rename: \(candidate).\(fileURL.pathExtension) [\(reason)]")
    } else {
      print("Proposed rename: <none>")
    }
  } catch {
    print("Rename planning error: \(error)")
  }
}

do {
  let options = try parseArgs()
  if let inspectPath = options.inspectPath {
    inspect(filePath: inspectPath, root: options.root)
    exit(0)
  }
  let planned = try planRenames(root: options.root, themes: options.themes)

  if planned.isEmpty {
    print("No rename candidates found.")
    exit(0)
  }

  for action in planned {
    print("[\(action.reason)] \(relativePath(action.source)) -> \(relativePath(action.target))")
  }

  print("")
  print("Planned renames: \(planned.count)")

  if options.apply {
    try applyRenames(planned)
    print("Applied renames.")
  } else {
    print("Dry run only. Re-run with --apply to rename files.")
  }
} catch let error as RenameError {
  fputs("error: \(error)\n", stderr)
  exit(1)
} catch {
  fputs("error: \(error.localizedDescription)\n", stderr)
  exit(1)
}
