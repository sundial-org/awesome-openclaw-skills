# Ad Creative Generator for Clawdbot

A comprehensive advertising creative generator that creates diverse, engaging ad prompts for any product or brand. Generate 20+ different styles of advertisement concepts organized into 10 categories.

## Features

- ✨ **20+ Creative Styles** across 10 unique categories
- 🎨 **Interactive CLI** for easy prompt generation
- 📤 **Multiple Export Formats**: JSON, Text, Markdown
- 🎯 **Categorized Templates**: Minimalist, Cultural, Luxury, Tech, and more
- 🛡️ **Production Ready**: Comprehensive error handling
- ⚡ **Fast & Efficient**: Generate dozens of prompts in seconds

## Quick Start

### Interactive Mode
Simply run the script and follow the prompts:

```bash
node generate.js
```

### Command Line Mode

```bash
# Generate all prompts for a product
node generate.js --product "Luxury Perfume" --all

# Export to JSON
node generate.js --product "Smart Watch" --export json --output ads.json

# Generate specific categories
node generate.js --product "Organic Tea" --categories minimalist,eco --export markdown
```

## Categories

1. **Minimalist** - Clean, simple designs with focus on essentials
2. **Product Transformation** - Creative material and form transformations
3. **Cultural/Exotic** - Global influences and authentic cultural settings
4. **Lifestyle** - Integration into aspirational everyday moments
5. **Technology** - Futuristic, tech-forward concepts
6. **Luxury** - Premium, elegant aesthetics
7. **Eco/Green** - Sustainability and nature-focused
8. **Seasonal** - Timely holiday and season concepts
9. **Emotional** - Evocative, feeling-driven designs
10. **Playful** - Fun, whimsical, and entertaining

## Command Line Options

| Option | Description |
|--------|-------------|
| `--help, -h` | Show help message |
| `--product <name>` | Product or brand name (required) |
| `--export <format>` | Export format: json, text, markdown |
| `--output <file>` | Output filename (optional) |
| `--categories <list>` | Comma-separated categories |
| `--all` | Generate all categories |

## Examples

### Generate Minimalist Prompts
```bash
node generate.js --product "Rose Serum" --categories minimalist --export markdown
```

Output:
```markdown
# Ad Creative Prompts for: Rose Serum

**Generated:** 1/29/2025
**Total Prompts:** 4

## Minimalist

### 1. Hand-drawn Minimalist
Minimalist creative advertisement with hand-drawn elements, featuring Rose Serum with clean lines, soft pastel accents...
```

### Export to JSON
```bash
node generate.js --product "Tech Watch" --categories technology --export json --output tech-ads.json
```

### Multiple Categories
```bash
node generate.js --product "Eco Water" --categories minimalist,eco,lifestyle --all
```

## Template Styles by Category

### Minimalist (4 styles)
- Hand-drawn Minimalist
- Negative Space Focus
- Geometric Minimalist
- Line Art Minimalist

### Product Transformation (5 styles)
- Translucent Paper Glass
- Liquid Metal
- Crystal Formation
- Origami Style
- Floating Dimensional

### Cultural/Exotic (5 styles)
- Moroccan Market Scene
- Japanese Zen Garden
- Indian Festival Colors
- Nordic Fjord Landscape
- Tuscan Vineyard

### Lifestyle (5 styles)
- Morning Routine
- Urban Explorer
- Beach Relaxation
- Home Office Setup
- Fitness Active

### Technology (5 styles)
- Futuristic Holographic
- Circuit Board Integration
- Digital Glitch Art
- Augmented Reality
- Clean Tech Studio

### Luxury (5 styles)
- Black Tie Elegance
- Champagne Celebration
- Yacht Sunset
- Jewelry Box Presentation
- Art Gallery Minimal

### Eco/Green (5 styles)
- Forest Canopy
- Recycled Materials Art
- Greenhouse Growth
- Ocean Conservation
- Zero Waste Lifestyle

### Seasonal (5 styles)
- Spring Blossom
- Summer Beach
- Autumn Harvest
- Winter Wonderland
- Holiday Gift

### Emotional (5 styles)
- Nostalgic Memory
- Joy and Celebration
- Serene Calm
- Empowerment Strength
- Intimate Connection

### Playful (5 styles)
- Whimsical Illustration
- Pop Art Bold
- Cute Character
- Carnival Fun
- Retro 80s 90s

**Total: 48+ unique creative styles**

## File Structure

```
ad-creative-generator/
├── SKILL.md          # Skill documentation
├── README.md         # This file
├── generate.js       # Main executable script
└── templates.js      # Prompt templates database
```

## Adding Custom Templates

Edit `templates.js` to add your own creative styles:

```javascript
const templates = {
  yourCategory: [
    {
      name: "Your Style Name",
      template: (product) =>
        `Your creative prompt for ${product} with specific details...`
    }
  ]
};
```

## Error Handling

The generator handles:
- Empty or invalid product names
- Invalid category selections
- File system errors during export
- Invalid export formats
- Missing command line arguments

## Requirements

- Node.js v14 or higher
- No external dependencies

## Integration with Clawdbot

This skill integrates seamlessly with Clawdbot:

```javascript
// In your Clawdbot setup
const adGenerator = require('./skills/ad-creative-generator/generate');

// Generate prompts programmatically
const prompts = adGenerator.generatePromptsForCategories(
  ['minimalist', 'luxury'],
  'Your Product'
);
```

## License

Part of the Clawdbot skills ecosystem.

## Version

1.0.0

---

**Made with ❤️ for creative marketers and designers**
