# ImageMagick Moltbot Skill

Comprehensive ImageMagick operations for Moltbot — background removal, resizing, format conversion, watermarks, thumbnails, and more.

## Quick Start

```bash
# Install ImageMagick
brew install imagemagick  # macOS
sudo apt install imagemagick  # Linux

# Remove white background from an icon
./scripts/remove-bg.sh icon.png icon-clean.png
```

## Features

- 🖼️ **Background Removal** — Strip white/solid backgrounds with configurable tolerance
- 📐 **Resize** — Scale images to any dimension
- 🔄 **Format Conversion** — PNG ↔ WebP ↔ JPG ↔ GIF
- 💧 **Watermarks** — Overlay logos or text
- 📸 **Thumbnails** — Batch generate previews
- 🎨 **Color Adjustments** — Brightness, contrast, saturation, grayscale

## Documentation

See [SKILL.md](SKILL.md) for full usage examples and patterns.

## License

MIT
