---
name: ad-creative-generator
description: Generate diverse, engaging ad prompts for any product or brand across 20+ creative styles and 10 categories. Use when user needs advertisement concepts, marketing prompts, or creative marketing content generation.
---

# Ad Creative Generator

## Overview
A comprehensive advertising creative generator that creates diverse, engaging ad prompts for any product or brand. Generate 20+ different styles of advertisement concepts organized into 10 categories.

## Description
This skill helps marketers, designers, and content creators generate creative advertisement concepts and prompts. It provides:
- 20+ unique creative styles across 10 categories
- Interactive CLI menu for easy selection
- Multiple export formats (JSON, text, markdown)
- Customizable prompts with product/brand input
- Production-ready error handling

## Installation
No additional dependencies required beyond Node.js (v14+).

## Usage

### Basic Usage
```bash
node generate.js
```

### Interactive Mode
Run the script and follow the prompts:
1. Enter your product/brand name
2. Select creative categories (multiple selection supported)
3. Choose specific styles within categories
4. Select export format
5. View or export generated prompts

### Command Line Options
```bash
# Generate prompts for a specific product
node generate.js --product "Luxury Perfume"

# Export directly to JSON
node generate.js --product "Smart Watch" --export json --output ads.json

# Generate specific categories
node generate.js --product "Organic Tea" --categories minimalist,eco

# Generate all categories
node generate.js --product "New App" --all
```

## Categories

### 1. Minimalist
Clean, simple designs with focus on essential elements. Perfect for modern brands.

### 2. Product Transformation
Creative transformations of products into different materials, contexts, or dimensions.

### 3. Cultural/Exotic
Incorporates cultural elements, exotic locations, and diverse aesthetic influences.

### 4. Lifestyle
Shows product integration into aspirational lifestyles and everyday moments.

### 5. Technology
Futuristic, tech-forward concepts with digital elements and innovation themes.

### 6. Luxury
Premium, elegant aesthetics with sophistication and exclusivity.

### 7. Eco/Green
Sustainability-focused, natural, and environmentally conscious designs.

### 8. Seasonal
Timely concepts tied to seasons, holidays, and special occasions.

### 9. Emotional
Evocative designs that connect on an emotional level with audiences.

### 10. Playful
Fun, whimsical, and creative concepts that entertain and engage.

## Output Formats

### JSON
Structured data format perfect for integration with other tools:
```json
{
  "product": "Example Product",
  "generated_at": "2025-01-29T12:00:00Z",
  "prompts": [
    {
      "category": "Minimalist",
      "style": "Hand-drawn Minimalist",
      "prompt": "..."
    }
  ]
}
```

### Text
Plain text format for easy reading and copying.

### Markdown
Formatted markdown with headers and structure for documentation.

## Examples

### Example 1: Minimalist Beauty Product
```
Product: "Rose Glow Serum"
Style: Hand-drawn Minimalist
Output: Minimalist creative advertisement with hand-drawn elements,
featuring Rose Glow Serum with clean lines, soft pastel accents,
negative space emphasizing the product, botanical sketches of rose
ingredients, elegant typography, white background
```

### Example 2: Product Transformation
```
Product: "Crystal Water Bottle"
Style: Translucent Material
Output: Crystal Water Bottle transformed into translucent paper glass
material, soft light filtering through, visible water layers, delicate
paper-like texture, ethereal lighting, pastel color gradient background
```

### Example 3: Cultural Exotic
```
Product: "Spice Blend Collection"
Style: Moroccan Market
Output: Spice Blend Collection beauty product in exotic Moroccan market
scene, vibrant souk stalls, golden hour lighting, intricate mosaic
patterns as background, cultural textiles, authenticity, warm color
palette, cinematic composition
```

## Features
- **20+ Creative Styles**: Diverse prompts across multiple categories
- **Interactive CLI**: User-friendly menu system
- **Batch Generation**: Generate multiple prompts at once
- **Export Options**: JSON, text, and markdown formats
- **Error Handling**: Comprehensive validation and error messages
- **Customizable**: Easy to modify templates and add new styles
- **Production Ready**: Robust code with logging and debugging support

## File Structure
```
ad-creative-generator/
├── SKILL.md           # This file
├── generate.js        # Main script with CLI
├── templates.js       # Prompt templates by category
└── README.md          # Additional usage documentation
```

## Error Handling
The script includes comprehensive error handling for:
- Invalid product names
- File system errors during export
- Invalid command line arguments
- Template rendering errors
- JSON parsing errors

## Contributing
To add new creative styles:
1. Edit `templates.js`
2. Add new category or style object
3. Follow the existing structure
4. Test with `node generate.js`

## License
Part of the Clawdbot skills ecosystem.

## Version
1.0.0
