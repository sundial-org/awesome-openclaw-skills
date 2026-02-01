---
name: style-transfer
description: Professional artistic style transfer via OpenAI Images API. Transform images into specific art styles, eras, and visual aesthetics. Use when user needs to convert an existing image into different artistic styles, apply famous art movements, or transform visual content with specific stylistic parameters (e.g., "make this photo look like an oil painting", "apply cyberpunk aesthetic", "transform into vintage photography").
---

# Style Transfer Pro

Apply artistic style transfer to images using OpenAI Images API with curated style prompts.

## Setup

- Needs env: `OPENAI_API_KEY`
- Needs source image URL (public URL or base64 data URI)

## Quick Start

Transform an image to oil painting style:

```bash
python3 ~/Projects/agent-scripts/skills/style-transfer/scripts/transfer.py \
  --source "https://example.com/photo.jpg" \
  --style "oil painting on linen, impressionist brushwork, rich texture, van gogh style"
```

Transform to multiple styles at once:

```bash
python3 ~/Projects/agent-scripts/skills/style-transfer/scripts/transfer.py \
  --source "https://example.com/photo.jpg" \
  --style "oil painting" \
  --style "watercolor illustration" \
  --style "cyberpunk neon" \
  --style "vintage sepia photograph"
```

## Style Library

Use these pre-defined style names (or provide custom prompts):

### Art Movements
- `impressionist-oil` - Impressionist oil painting with visible brushwork
- `watercolor-dream` - Soft watercolor with ink linework
- `digital-art` - Modern digital art with crisp details
- `comic-book` - Bold comic book illustration style
- `anime-studio` - Anime/ manga studio style
- `pixel-art` - Retro pixel art aesthetic
- `vector-flat` - Clean flat vector illustration
- `surreal-abstract` - Surrealist abstract art

### Photographic Styles
- `vintage-sepia` - Sepia vintage photography
- `polaroid` - Instant polaroid look with faded tones
- `film-noir` - Black and white film noir aesthetic
- `candid-snapshot` - Authentic snapshot look
- `studio-portrait` - Professional studio photography
- `vogue-editorial` - Fashion editorial style
- `golden-hour` - Golden hour warm lighting
- `neon-noir` - Cyberpunk neon noir

### Period Styles
- `renaissance-portrait` - Classical Renaissance oil painting
- `baroque-drama` - Dramatic Baroque chiaroscuro
- `art-deco-elegance` - Art Deco geometric elegance
- `mid-century-modern` - Mid-century modern illustration
- `victorian-etching` - Victorian etching aesthetic
- `steampunk-gear` - Steampunk mechanical style
- `dystopian-grunge` - Dystopian grunge aesthetic
- `psychedelic-60s` - 1960s psychedelic art

## Custom Style Prompts

For fine-grained control, provide full style prompts:

```bash
python3 ~/Projects/agent-scripts/skills/style-transfer/scripts/transfer.py \
  --source "https://example.com/photo.jpg" \
  --prompt "watercolor painting, soft brushstrokes, pastel color palette, hand-painted illustration style, minimal detail, elegant and dreamy"
```

Style prompt structure:
1. Medium: "oil painting", "watercolor", "digital art", "photography"
2. Technique: "impressionist", "glazing", "crosshatching", "flat design"
3. Lighting: "softbox", "golden hour", "dramatic chiaroscuro", "diffuse"
4. Color: "pastel", "muted", "vibrant", "muted earth tones"
5. Quality: "ultra-detailed", "minimalist", "sketch", "finished artwork"

## Parameters

- `--source` - Source image URL (required)
- `--style` - Pre-defined style name (repeatable)
- `--prompt` - Full custom style prompt (overrides --style)
- `--out-dir` - Output directory (default: ~/Projects/tmp/style-transfer-*)
- `--size` - Image size: 1024x1024, 1792x1024, 1024x1792 (default: 1024x1024)
- `--quality` - high/standard (default: high)
- `--model` - OpenAI image model (default: gpt-image-1.5)
- `--api-key` - OpenAI API key (or use OPENAI_API_KEY env)

## Output

- `*.png` - Transformed images
- `prompts.json` - Style prompts used
- `index.html` - Thumbnail gallery comparing styles
