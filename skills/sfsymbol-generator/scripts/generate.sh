#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $(basename "$0") <symbol-name> <svg-path> [assets-dir]" >&2
  exit 1
fi

symbol_name="$1"
svg_path="$2"
assets_dir="${3:-${SFSYMBOL_ASSETS_DIR:-Assets.xcassets/Symbols}}"

if [[ ! -f "$svg_path" ]]; then
  echo "SVG not found: $svg_path" >&2
  exit 1
fi

symbolset_dir="$assets_dir/${symbol_name}.symbolset"
svg_filename="${symbol_name}.svg"

mkdir -p "$symbolset_dir"
cp "$svg_path" "$symbolset_dir/$svg_filename"

cat > "$symbolset_dir/Contents.json" <<EOF
{
  "info" : {
    "author" : "xcode",
    "version" : 1
  },
  "symbols" : [
    {
      "filename" : "${svg_filename}",
      "idiom" : "universal"
    }
  ]
}
EOF

echo "Created: $symbolset_dir"
