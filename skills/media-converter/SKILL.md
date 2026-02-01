# Media Converter Skill

## Description
Detects media file types via magic bytes and fixes file extensions to ensure compatibility with Gemini (which rejects `application/octet-stream`). Handles basic conversion logic (placeholder for future ffmpeg support).

## Usage
```bash
# Detect MIME type and return JSON
node skills/media-converter/index.js detect --file <path>

# Fix extension based on detected MIME (renames file if needed)
node skills/media-converter/index.js fix --file <path>
```

## Examples
```bash
# Check a file masked as .bin
node skills/media-converter/index.js detect --file /tmp/unknown.bin
# Output: {"mime": "image/gif", "ext": "gif"}

# Rename a file to match its content
node skills/media-converter/index.js fix --file /tmp/unknown.bin
# Output: {"original": "/tmp/unknown.bin", "fixed": "/tmp/unknown.gif", "mime": "image/gif"}
```
