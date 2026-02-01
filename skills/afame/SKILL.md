---
name: creative-illustration
description: Generate diverse creative illustrations via OpenAI Images API. Create book illustrations, editorial art, children's book art, concept illustrations, and artistic scenes. Use when user needs creative visual content for stories, articles, presentations, or artistic projects (e.g., "illustrate a fairy tale scene", "create editorial art about technology", "design children's book illustrations", "generate concept art for a story").
---

# Creative Illustration Factory

Generate professional illustrations for books, editorial content, children's stories, and creative projects.

## Setup

- Needs env: `OPENAI_API_KEY`

## Quick Start

Generate a simple illustration:

```bash
python3 ~/Projects/agent-scripts/skills/creative-illustration/scripts/illustrate.py \
  --subject "a cozy cottage in an enchanted forest"
```

Generate with specific style:

```bash
python3 ~/Projects/agent-scripts/skills/creative-illustration/scripts/illustrate.py \
  --subject "a robot learning to paint" \
  --style "watercolor" \
  --mood "whimsical"
```

Generate a story sequence:

```bash
python3 ~/Projects/agent-scripts/skills/creative-illustration/scripts/illustrate.py \
  --subject "Alice discovers a tiny door" \
  --subject "Alice shrinks down" \
  --subject "Alice enters Wonderland" \
  --style "whimsical illustration" \
  --mood "magical"
```

## Illustration Types

### Book Illustrations
- `chapter-opener` - Full-page chapter opening scene
- `character-intro` - Character introduction portrait
- `landscape-scene` - Wide landscape establishing shot
- `action-moment` - Dynamic action or pivotal moment
- `emotional-scene` - Emotional or dramatic scene
- `cover-art` - Book cover illustration style

### Editorial / Magazine Art
- `conceptual-art` - Abstract conceptual illustration
- `info-graphic` - Informational illustration style
- `portrait-editorial` - Editorial portrait
- `spot-illustration` - Small spot illustration
- `full-page-spread` - Magazine full-page spread

### Children's Book Art
- `picture-book` - Classic picture book illustration
- `whimsical` - Playful and imaginative style
- `educational` - Educational book illustration
- `bedtime-story` - Soft, calming bedtime story art
- `adventure-map` - Adventure map or treasure map

### Concept Art
- `environment-concept` - Environmental concept art
- `character-concept` - Character design concept
- `prop-concept` - Object or prop design
- `storyboard` - Storyboard panel style
- `mood-board` - Mood board aesthetic

## Styles

### Traditional Media
- `watercolor` - Watercolor painting with soft edges
- `oil-painting` - Rich oil painting texture
- `charcoal-sketch` - Charcoal drawing style
- `ink-wash` - Ink wash / sumi-e style
- `pastel` - Soft pastel drawing
- `colored-pencil` - Colored pencil illustration
- `gouache` - Gouache opaque watercolor
- `acrylic` - Acrylic painting style
- `lino-cut` - Linocut printmaking style
- `woodcut` - Woodcut print aesthetic

### Digital Styles
- `digital-painting` - Digital painting
- `vector-illustration` - Clean vector art
- `flat-design` - Flat design aesthetic
- `isometric` - Isometric perspective
- `pixel-art` - Retro pixel art
- `concept-art` - Game/film concept art style
- `cel-shaded` - Cel shaded animation style
- `low-poly` - Low poly 3D aesthetic

### Book & Print Styles
- `picture-book` - Classic picture book
- `storybook-illustration` - Vintage storybook art
- `editorial-illustration` - Magazine editorial
- `newspaper-engraving` - Newspaper engraving style
- `poster-art` - Vintage poster design
- `woodblock-print` - Japanese woodblock print
- `screen-print` - Screen print aesthetic

## Mood

- `whimsical` - Playful and imaginative
- `magical` - Magical and enchanting
- `mysterious` - Mysterious and intriguing
- `peaceful` - Calm and serene
- `dramatic` - Dramatic and intense
- `nostalgic` - Warm and nostalgic
- `gloomy` - Dark and atmospheric
- `vibrant` - Bright and energetic
- `romantic` - Soft and romantic
- `quirky` - Quirky and eccentric

## Parameters

- `--subject` - Illustration subject/description (repeatable for batch)
- `--type` - Illustration type (default: illustration)
- `--style` - Artistic style (default: watercolor)
- `--mood` - Mood/atmosphere (default: peaceful)
- `--palette` - Color palette suggestion
- `--composition` - Composition guidance (e.g., "wide shot", "close-up")
- `--count` - Number of variants per subject (default: 1)
- `--out-dir` - Output directory (default: ~/Projects/tmp/creative-illustration-*)
- `--size` - Image size: 1024x1024, 1792x1024, 1024x1792 (default: 1024x1024)
- `--quality` - high/standard (default: high)
- `--model` - OpenAI image model (default: gpt-image-1.5)
- `--api-key` - OpenAI API key (or use OPENAI_API_KEY env)

## Advanced Examples

Children's book page:

```bash
python3 ~/Projects/agent-scripts/skills/creative-illustration/scripts/illustrate.py \
  --subject "a curious rabbit with a pocket watch" \
  --type "picture-book" \
  --style "watercolor" \
  --mood "whimsical" \
  --palette "pastel"
```

Editorial concept art:

```bash
python3 ~/Projects/agent-scripts/skills/creative-illustration/scripts/illustrate.py \
  --subject "AI and humanity working together" \
  --type "conceptual-art" \
  --style "vector-illustration" \
  --mood "optimistic" \
  --composition "symbolic"
```

Story sequence:

```bash
python3 ~/Projects/agent-scripts/skills/creative-illustration/scripts/illustrate.py \
  --subject "Hero finds an ancient map" \
  --subject "Hero deciphers mysterious symbols" \
  --subject "Hero discovers a hidden passage" \
  --subject "Hero enters the forgotten temple" \
  --style "storybook-illustration" \
  --mood "mysterious" \
  --palette "earth tones"
```

Full custom prompt:

```bash
python3 ~/Projects/agent-scripts/skills/creative-illustration/scripts/illustrate.py \
  --prompt "A magical treehouse library nestled among ancient redwoods, spiral staircase winding up the trunk, lanterns hanging from branches, books floating in mid-air, warm golden light streaming through leaves, detailed watercolor illustration style, whimsical and enchanting"
```

## Color Palettes

- `pastel` - Soft pastel colors
- `earth tones` - Natural browns, greens, golds
- `vibrant` - Bright saturated colors
- `muted` - Desaturated, subtle colors
- `monochrome` - Single color variations
- `jewel tones` - Rich ruby, emerald, sapphire
- `autumn` - Orange, red, yellow, brown
- `winter` - Blue, white, silver, purple
- `tropical` - Bright greens, teals, pinks
- `vintage` - Warm sepia, faded tones

## Composition

- `wide shot` - Wide establishing scene
- `close-up` - Intimate close-up
- `panoramic` - Panoramic landscape
- `rule-of-thirds` - Balanced rule of thirds
- `centered` - Centered subject
- `diagonal` - Dynamic diagonal composition
- `triangular` - Triangular composition
- `circular` - Circular / spiral composition
- `symmetrical` - Perfectly symmetrical
- `asymmetrical` - Asymmetrical balance

## Output

- `*.png` - Illustration images
- `prompts.json` - All prompts used
- `index.html` - Illustration gallery

## Project Templates

### Children's Book (4-6 images)

```bash
python3 ~/Projects/agent-scripts/skills/creative-illustration/scripts/illustrate.py \
  --subject "Girl finds a magical seed" \
  --subject "Seed grows into a glowing plant" \
  --subject "Plant reveals a tiny fairy" \
  --subject "Fairy shows girl a secret garden" \
  --subject "Girl shares garden with friends" \
  --type "picture-book" \
  --style "watercolor" \
  --mood "whimsical"
```

### Magazine Editorial (1-2 images)

```bash
python3 ~/Projects/agent-scripts/skills/creative-illustration/scripts/illustrate.py \
  --subject "The future of sustainable cities" \
  --type "conceptual-art" \
  --style "vector-illustration" \
  --mood "optimistic" \
  --count 2
```

### Fantasy Story Chapter Opener (1 image)

```bash
python3 ~/Projects/agent-scripts/skills/creative-illustration/scripts/illustrate.py \
  --subject "The dragon's treasure hoard under ancient runes" \
  --type "chapter-opener" \
  --style "oil-painting" \
  --mood "dramatic" \
  --palette "jewel tones"
```
