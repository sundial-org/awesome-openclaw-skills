---
name: pptx-creator
description: Create professional PowerPoint presentations from outlines, data sources, or AI-generated content. Supports custom templates, style presets, charts/tables from data, and AI-generated images. Use when asked to create slides, pitch decks, reports, or presentations.
homepage: https://python-pptx.readthedocs.io
metadata: {"clawdbot":{"emoji":"📽️","requires":{"bins":["uv"]}}}
---

# PowerPoint Creator

Create professional presentations from outlines, topics, or data sources.

## Quick Start

### From Outline/Markdown
```bash
uv run {baseDir}/scripts/create_pptx.py --outline outline.md --output deck.pptx
```

### From Topic
```bash
uv run {baseDir}/scripts/create_pptx.py --topic "Q4 Sales Review" --slides 8 --output review.pptx
```

### With Style Template
```bash
uv run {baseDir}/scripts/create_pptx.py --outline outline.md --template corporate --output deck.pptx
```

### From JSON Structure
```bash
uv run {baseDir}/scripts/create_pptx.py --json slides.json --output deck.pptx
```

## Outline Format (Markdown)

```markdown
# Presentation Title
subtitle: Annual Review 2026
author: Your Name

## Introduction
- Welcome and agenda
- Key objectives for today
- ![image](generate: modern office building, minimalist style)

## Market Analysis
- chart: bar
- data: sales_by_region.csv
- Market grew 15% YoY
- Strong competitive position

## Financial Summary
- table: quarterly_results
- Strong Q4 performance
- Revenue targets exceeded
```

## JSON Structure

```json
{
  "title": "Quarterly Review",
  "subtitle": "Q4 Performance",
  "author": "Your Name",
  "template": "corporate",
  "slides": [
    {
      "title": "Introduction",
      "layout": "title_and_content",
      "bullets": ["Welcome", "Agenda", "Goals"],
      "notes": "Speaker notes here"
    },
    {
      "title": "Revenue Chart",
      "layout": "chart",
      "chart_type": "bar"
    },
    {
      "title": "Team",
      "layout": "image_and_text",
      "image": "generate: professional team collaboration, corporate style",
      "bullets": ["Leadership", "Sales", "Operations"]
    }
  ]
}
```

## Built-in Style Templates

- `minimal` — Clean white, Helvetica Neue, blue accent (default)
- `corporate` — Professional blue, Arial, business-ready
- `creative` — Bold orange accents, Avenir, modern feel
- `dark` — Dark background, SF Pro, cyan accents
- `executive` — Gold accents, Georgia/Calibri, refined elegance
- `startup` — Purple accents, Poppins/Inter, pitch-deck ready

### Generate All Templates
```bash
uv run {baseDir}/scripts/create_template.py --all
```

### List Templates
```bash
uv run {baseDir}/scripts/create_pptx.py --list-templates
```

## Custom Templates

### Save Existing PPTX as Template
```bash
uv run {baseDir}/scripts/create_pptx.py --save-template "my-brand" --from existing.pptx
```

### Analyze Template Structure
```bash
uv run {baseDir}/scripts/analyze_template.py existing.pptx
uv run {baseDir}/scripts/analyze_template.py existing.pptx --json
```

### Build from Custom Template
```bash
uv run {baseDir}/scripts/use_template.py \
  --template my-brand \
  --slides content.json \
  --keep-slides 2 \
  --output presentation.pptx
```

## Data Sources

### CSV/Excel
```markdown
## Regional Sales
- chart: pie
- data: sales.csv
- columns: region, revenue
```

### Inline Data
```markdown
## Quarterly Comparison
- chart: bar
- data:
  - Q1: 120
  - Q2: 145  
  - Q3: 132
  - Q4: 178
```

## Image Generation

Generate images inline using compatible image generation skills:

```markdown
## Our Vision
- ![hero](generate: futuristic cityscape, clean energy, optimistic)
- Building tomorrow's solutions
```

Or via JSON:
```json
{
  "title": "Innovation",
  "image": {
    "generate": "abstract technology visualization, blue tones",
    "position": "right",
    "size": "half"
  }
}
```

## Layouts

- `title` — Title slide
- `title_and_content` — Title + bullet points (default)
- `two_column` — Side-by-side content
- `image_and_text` — Image with text
- `chart` — Full chart slide
- `table` — Data table
- `section` — Section divider
- `blank` — Empty slide for custom content

## Chart Types

- `bar` / `bar_stacked`
- `column` / `column_stacked`
- `line` / `line_markers`
- `pie` / `doughnut`
- `area` / `area_stacked`
- `scatter`

## Examples

### Pitch Deck
```bash
uv run {baseDir}/scripts/create_pptx.py \
  --topic "Series A pitch for tech startup" \
  --slides 10 \
  --template startup \
  --output pitch-deck.pptx
```

### Executive Report
```bash
uv run {baseDir}/scripts/create_pptx.py \
  --outline report.md \
  --template executive \
  --output board-report.pptx
```

### Marketing Presentation
```bash
uv run {baseDir}/scripts/create_pptx.py \
  --outline campaign.md \
  --template creative \
  --output marketing-deck.pptx
```
