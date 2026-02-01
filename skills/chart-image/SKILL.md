---
name: chart-image
version: 1.0.0
description: Generate publication-quality chart images from data. Supports line, bar, area, and point charts. Use when visualizing data, creating graphs, plotting time series, or generating chart images for reports/alerts. Designed for Fly.io/VPS deployments - no native compilation, no Puppeteer, no browser required. Pure Node.js with prebuilt binaries.
provides:
  - capability: chart-generation
    methods: [lineChart, barChart, areaChart]
---

# Chart Image Generator

Generate PNG chart images from data using Vega-Lite. Perfect for headless server environments.

## Why This Skill?

**Built for Fly.io / VPS / Docker deployments:**
- ✅ **No native compilation** - Uses Sharp with prebuilt binaries (unlike `canvas` which requires build tools)
- ✅ **No Puppeteer/browser** - Pure Node.js, no Chrome download, no headless browser overhead
- ✅ **Lightweight** - ~15MB total dependencies vs 400MB+ for Puppeteer-based solutions
- ✅ **Fast cold starts** - No browser spinup delay, generates charts in <500ms
- ✅ **Works offline** - No external API calls (unlike QuickChart.io)

**Alternatives and why they don't work well on Fly:**
- `canvas` npm - Requires native compilation, fails on minimal Docker images
- Puppeteer + Chart.js - 400MB+ Chrome download, slow cold starts, memory heavy
- QuickChart API - External dependency, rate limits, privacy concerns
- Plotly - Needs Puppeteer for static image export

## Setup (one-time)

```bash
cd /data/clawd/skills/chart-image/scripts && npm install
```

## Quick Usage

```bash
node /data/clawd/skills/chart-image/scripts/chart.mjs \
  --type line \
  --data '[{"x":"10:00","y":25},{"x":"10:30","y":27},{"x":"11:00","y":31}]' \
  --title "Price Over Time" \
  --output chart.png
```

## Alert-Style Chart (recommended for monitors)

```bash
# Full data with zoomed Y-axis
node /data/clawd/skills/chart-image/scripts/chart.mjs \
  --type line \
  --data '[...]' \
  --title "Elon Posts 34 Tweets This Week" \
  --show-change \
  --focus-change \
  --show-values \
  --dark \
  --output alert.png

# Focus on recent action (last 4 points)
node /data/clawd/skills/chart-image/scripts/chart.mjs \
  --type line \
  --data '[hourly data...]' \
  --title "Elon Tweet Odds (24h)" \
  --show-change \
  --focus-change \
  --focus-recent 4 \
  --show-values \
  --dark \
  --output alert-recent.png
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--type` | Chart type: `line`, `bar`, `area`, `point` | line |
| `--data` | JSON array of data points | - |
| `--spec` | Path to full Vega-Lite spec file | - |
| `--output` | Output PNG path | chart.png |
| `--title` | Chart title | - |
| `--width` | Width in pixels | 600 |
| `--height` | Height in pixels | 300 |
| `--x-field` | Field name for X axis | x |
| `--y-field` | Field name for Y axis | y |
| `--x-title` | X axis label | field name |
| `--y-title` | Y axis label | field name |
| `--color` | Line/bar color | #e63946 |
| `--y-domain` | Y scale as "min,max" | auto |
| `--show-change` | Show +/-% change annotation | false |
| `--focus-change` | Zoom Y-axis to 2x data range | false |
| `--focus-recent N` | Show only last N data points | all |
| `--show-values` | Label min/max peak points | false |
| `--dark` | Dark mode theme | false |
| `--svg` | Output SVG instead of PNG | false |
| `--sparkline` | Tiny inline chart (80x20, no axes) | false |
| `--stacked` | Stacked bar chart (requires --color-field) | false |
| `--color-field` | Field name for stack categories | - |
| `--series-field` | Field for multi-series line charts | - |

## Multi-Series Line Charts

Compare multiple trends on one chart:

```bash
node chart.mjs \
  --type line \
  --series-field "market" \
  --data '[{"x":"Jan","y":10,"market":"A"},{"x":"Jan","y":15,"market":"B"},{"x":"Feb","y":12,"market":"A"},{"x":"Feb","y":18,"market":"B"}]' \
  --title "Comparison" \
  --output multi.png
```

Each unique value in `--series-field` becomes a separate colored line with legend.

## Stacked Bar Charts

Visualize breakdowns by category:

```bash
node chart.mjs \
  --type bar \
  --stacked \
  --color-field "category" \
  --data '[{"x":"Mon","y":10,"category":"Work"},{"x":"Mon","y":5,"category":"Personal"}]' \
  --title "Hours by Category" \
  --output stacked.png
```

Data needs three fields: x (groups), y (values), and the color-field (stack categories).

## Sparklines (inline mini-charts)

Tiny charts for embedding in text summaries:

```bash
node chart.mjs \
  --sparkline \
  --data '[{"x":"1","y":10},{"x":"2","y":15},{"x":"3","y":12}]' \
  --output spark.png
```

Sparklines are 80x20 by default (override with `--width` / `--height`), transparent background, no axes.

## Theme Selection

Use `--dark` for dark mode. Recommended to auto-select based on time:
- **Night (20:00-07:00 local)**: `--dark`
- **Day (07:00-20:00 local)**: no flag (light mode)

## Piping Data

```bash
echo '[{"x":"A","y":1},{"x":"B","y":2}]' | node chart.mjs --output out.png
```

## Custom Vega-Lite Spec

For advanced charts, pass a full Vega-Lite spec:

```bash
node chart.mjs --spec my-spec.json --output custom.png
```
