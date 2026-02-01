---
name: sfsymbol-generator
description: Generate an Xcode SF Symbol asset catalog .symbolset from an SVG. Use when you need to add a custom SF Symbol (build-time) by creating the symbolset folder, Contents.json, and SVG file.
---

# SF Symbol Generator

## Usage

You can override the default asset catalog location with `SFSYMBOL_ASSETS_DIR`.

### Raw symbolset (no template injection)

```bash
./scripts/generate.sh <symbol-name> <svg-path> [assets-dir]
```

- `symbol-name`: Full symbol name (e.g., `custom.logo`, `brand.icon.fill`).
- `svg-path`: Path to the source SVG file.
- `assets-dir` (optional): Path to `Assets.xcassets/Symbols` (defaults to `Assets.xcassets/Symbols` or `SFSYMBOL_ASSETS_DIR`).

### Template-based symbolset (recommended)

```bash
./scripts/generate-from-template.js <symbol-name> <svg-path> [template-svg] [assets-dir]
```

- `template-svg` (optional): SF Symbols template SVG to inject into (defaults to the first `.symbolset` SVG found in `Assets.xcassets/Symbols`, otherwise uses the bundled skill template).

## Example

```bash
./scripts/generate-from-template.js pi.logo /Users/admin/Desktop/pi-logo.svg
```

## Requirements

- SVG must include a `viewBox`.
- Use **path-based** shapes (paths are required; rects are supported and converted, but other shapes should be converted to paths).
- Prefer **filled** shapes (no strokes) to avoid thin artifacts.

## Workflow

1. Validates the SVG path and viewBox.
2. Computes path bounds and centers within the SF Symbols template margins.
3. Injects the paths into the SF Symbols template (Ultralight/Regular/Black).
4. Creates `<symbol-name>.symbolset` inside the asset catalog Symbols folder.
5. Writes a matching `Contents.json`.
