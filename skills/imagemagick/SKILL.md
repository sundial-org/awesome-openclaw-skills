# ImageMagick Moltbot Skill

Comprehensive ImageMagick operations for image manipulation in Moltbot.

## Installation

**macOS:**
```bash
brew install imagemagick
```

**Linux:**
```bash
sudo apt install imagemagick  # Debian/Ubuntu
sudo dnf install ImageMagick  # Fedora
```

**Verify:**
```bash
convert --version
```

## Available Operations

### 1. Remove Background (white/solid color → transparent)
```bash
./scripts/remove-bg.sh input.png output.png [tolerance] [color]
```

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| input.png | — | — | Source image |
| output.png | — | — | Output transparent PNG |
| tolerance | 20 | 0-255 | Color matching fuzz factor |
| color | #FFFFFF | hex | Color to remove |

**Examples:**
```bash
./scripts/remove-bg.sh icon.png icon-clean.png              # default white
./scripts/remove-bg.sh icon.png icon-clean.png 30           # loose tolerance
./scripts/remove-bg.sh icon.png icon-clean.png 10 "#000000" # remove black
```

### 2. Resize Image
```bash
convert input.png -resize 256x256 output.png
```

### 3. Convert Format
```bash
convert input.png output.webp          # PNG → WebP
convert input.jpg output.png           # JPG → PNG
convert input.png -quality 80 output.jpg  # Compress
```

### 4. Rounded Corners (iOS style)
```bash
convert input.png -alpha set -virtual pixel transparent \
    -distort viewport 512x512+0+0 \
    -channel A -blur 0x10 -threshold 50% \
    output-rounded.png
```

### 5. Add Watermark
```bash
convert base.png watermark.png -gravity southeast -composite output.png
```

### 6. Batch Thumbnail Generation
```bash
for f in *.png; do convert "$f" -resize 128x128 "thumbs/$f"; done
```

### 7. Color Adjustments
```bash
convert input.png -brightness-contrast 10x0 output.png      # brighter
convert input.png -grayscale output.png                     # grayscale
convert input.png -modulate 100,150,100 output.png          # more saturation
```

## Common Patterns

### Flat Icon → Transparent Background
```bash
./scripts/remove-bg.sh icon.png icon-clean.png 15
```

### Generate App Icon Set (iOS)
```bash
for size in 1024 512 256 128 64 32 16; do
    convert icon.png -resize ${size}x${size} icon-${size}.png
done
```

### Optimize for Web
```bash
convert large.png -quality 85 -resize 2000x2000\> optimized.webp
```

## Tips

- **Higher tolerance (20-50):** Better for anti-aliased edges, may remove some foreground
- **Lower tolerance (5-15):** Preserves detail, may leave color fringes
- **For flat icons:** 10-20 usually works best
- Use `-quality` for JPEG/WebP compression (0-100)
- Use `-strip` to remove metadata for smaller files
