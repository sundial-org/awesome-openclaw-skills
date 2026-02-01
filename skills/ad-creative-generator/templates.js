/**
 * Ad Creative Generator - Prompt Templates
 *
 * Organized by category with 20+ unique creative styles
 * Each template includes placeholders for dynamic product/brand insertion
 */

const templates = {
  minimalist: [
    {
      name: "Hand-drawn Minimalist",
      template: (product) =>
        `Minimalist creative advertisement with hand-drawn elements, featuring ${product} with clean lines, soft pastel accents, negative space emphasizing the product, botanical sketches of ingredients, elegant typography, white background`
    },
    {
      name: "Negative Space Focus",
      template: (product) =>
        `Minimalist advertisement for ${product} with generous negative space, product centered with breathing room, monochromatic color scheme, sleek sans-serif typography, subtle gradient background, premium minimalist aesthetic`
    },
    {
      name: "Geometric Minimalist",
      template: (product) =>
        `${product} minimalist ad with geometric shapes, clean lines, bold circles and squares framing the product, limited color palette (2-3 colors max), modern abstract composition, Scandinavian design influence`
    },
    {
      name: "Line Art Minimalist",
      template: (product) =>
        `Single continuous line drawing advertisement for ${product}, elegant flowing lines creating product silhouette, minimal color accents on white background, artistic and sophisticated, modern art gallery aesthetic`
    }
  ],

  productTransformation: [
    {
      name: "Translucent Paper Glass",
      template: (product) =>
        `${product} transformed into translucent paper glass material, soft light filtering through, visible layers and internal structure, delicate paper-like texture with glass transparency, ethereal lighting, pastel color gradient background`
    },
    {
      name: "Liquid Metal",
      template: (product) =>
        `${product} in liquid metal form, flowing mercury-like surface, reflective and metallic with motion blur, chrome aesthetic, dramatic studio lighting, dark background with light reflections, futuristic luxury feel`
    },
    {
      name: "Crystal Formation",
      template: (product) =>
        `${product} emerging from crystal formation, geometric crystal structures growing around product, refractive light through crystal facets, prismatic color effects, mystical and premium aesthetic, dark dramatic background`
    },
    {
      name: " Origami Style",
      template: (product) =>
        `${product} reimagined as origami art, folded paper aesthetic, sharp creases and geometric folds, paper texture visible, subtle shadows, clean white or soft colored background, artistic and craft-inspired`
    },
    {
      name: "Floating Dimensional",
      template: (product) =>
        `${product} floating in zero gravity, exploded view with components suspended, 3D dimensional effect, layered depth, dramatic lighting from multiple angles, dark background, premium product photography style`
    }
  ],

  culturalExotic: [
    {
      name: "Moroccan Market Scene",
      template: (product) =>
        `${product} in exotic Moroccan market scene, vibrant souk stalls, golden hour lighting, intricate mosaic patterns as background, cultural textiles and rugs, authenticity, warm color palette (terracotta, gold, turquoise), cinematic composition`
    },
    {
      name: "Japanese Zen Garden",
      template: (product) =>
        `${product} placed in Japanese zen garden, serene minimal landscape, cherry blossoms in background, stone elements and moss, soft natural lighting, harmonious composition, muted natural color palette, tranquility and balance`
    },
    {
      name: "Indian Festival Colors",
      template: (product) =>
        `${product} during Holi festival celebration, vibrant colored powder explosions, dynamic motion and energy, rich saturated colors (pink, yellow, blue), joyful atmosphere, cultural authenticity, festive and celebratory mood`
    },
    {
      name: "Nordic Fjord Landscape",
      template: (product) =>
        `${product} in Nordic fjord landscape, dramatic mountains and water, Aurora Borealis in sky, crisp cool tones, pristine natural setting, adventure and exploration, premium outdoor aesthetic`
    },
    {
      name: "Tuscan Vineyard",
      template: (product) =>
        `${product} in Tuscan vineyard setting, rolling hills with grapevines, golden hour Italian light, rustic stone walls, warm Mediterranean colors, authentic old-world charm, lifestyle and sophistication`
    }
  ],

  lifestyle: [
    {
      name: "Morning Routine",
      template: (product) =>
        `${product} integrated into modern morning routine, sunlit bedroom with streaming sunlight, cozy bedding and coffee, lifestyle photography aesthetic, natural and authentic, soft warm tones, aspirational yet relatable`
    },
    {
      name: "Urban Explorer",
      template: (product) =>
        `${product} with urban explorer lifestyle, city street scene, modern architecture, person holding product naturally, candid lifestyle shot, dynamic composition, contemporary and energetic`
    },
    {
      name: "Beach Relaxation",
      template: (product) =>
        `${product} on beach relaxation scene, white sand and turquoise water, tropical vibe, product shaded by palm leaf, lifestyle product photography, vacation and leisure, bright and airy aesthetic`
    },
    {
      name: "Home Office Setup",
      template: (product) =>
        `${product} in stylish home office setup, modern desk setup with plants and laptop, productivity and focus, clean and organized space, natural lighting, contemporary work-from-home aesthetic`
    },
    {
      name: "Fitness Active",
      template: (product) =>
        `${product} with fitness and active lifestyle, gym or outdoor workout scene, dynamic movement, athletic aesthetic, motivational energy, vibrant and energetic composition`
    }
  ],

  technology: [
    {
      name: "Futuristic Holographic",
      template: (product) =>
        `${product} with holographic display elements, floating UI and data visualizations, futuristic tech aesthetic, neon blue and purple lighting, dark background, innovation and cutting-edge technology`
    },
    {
      name: "Circuit Board Integration",
      template: (product) =>
        `${product} integrated into circuit board design, microchip patterns and traces, glowing LED elements, tech-focused composition, metallic and electronic aesthetic, innovation theme`
    },
    {
      name: "Digital Glitch Art",
      template: (product) =>
        `${product} with digital glitch art effects, pixelated distortions, RGB color splits, cyberpunk aesthetic, tech-forward design, edgy and contemporary, digital art style`
    },
    {
      name: "Augmented Reality",
      template: (product) =>
        `${product} with AR overlay elements, floating interface graphics, augmented reality visualization, mixed reality aesthetic, innovative tech presentation, blue and white color scheme`
    },
    {
      name: "Clean Tech Studio",
      template: (product) =>
        `${product} in clean tech studio setup, seamless white background, product floating with subtle shadow, premium tech photography, crisp and professional, Apple-style aesthetic`
    }
  ],

  luxury: [
    {
      name: "Black Tie Elegance",
      template: (product) =>
        `${product} with black tie luxury aesthetic, black and gold color scheme, silk and velvet textures, dramatic spotlight on product, premium and sophisticated, exclusive and refined`
    },
    {
      name: "Champagne Celebration",
      template: (product) =>
        `${product} in champagne celebration scene, bubbles and effervescence, golden lighting, festive luxury atmosphere, celebration and success, premium lifestyle photography`
    },
    {
      name: "Yacht Sunset",
      template: (product) =>
        `${product} on luxury yacht at sunset, ocean horizon, golden and platinum tones, affluent lifestyle, exotic travel, premium leisure aesthetic`
    },
    {
      name: "Jewelry Box Presentation",
      template: (product) =>
        `${product} presented like fine jewelry, velvet lined box, spotlight illumination, rich colors (burgundy, navy, emerald), luxury packaging aesthetic, premium gift presentation`
    },
    {
      name: "Art Gallery Minimal",
      template: (product) =>
        `${product} in art gallery setting, museum-quality lighting, white gallery walls, minimalist luxury presentation, sophisticated and refined, collector's item aesthetic`
    }
  ],

  ecoGreen: [
    {
      name: "Forest Canopy",
      template: (product) =>
        `${product} in lush forest canopy setting, dappled sunlight through leaves, surrounded by vibrant greenery, natural and organic, eco-conscious messaging, sustainable lifestyle aesthetic`
    },
    {
      name: "Recycled Materials Art",
      template: (product) =>
        `${product} made from artistic recycled materials, upcycled aesthetic, creative reuse theme, sustainability focus, environmentally conscious message, earth tones`
    },
    {
      name: "Greenhouse Growth",
      template: (product) =>
        `${product} in greenhouse environment, thriving plants, glass structure, natural light and growth, organic and sustainable, eco-friendly brand message`
    },
    {
      name: "Ocean Conservation",
      template: (product) =>
        `${product} with ocean conservation theme, clean ocean water, marine life elements, blue and green tones, environmental awareness, protecting nature aesthetic`
    },
    {
      name: "Zero Waste Lifestyle",
      template: (product) =>
        `${product} in zero waste lifestyle context, reusable and sustainable materials, natural fiber textures, eco-conscious living, earth-friendly color palette`
    }
  ],

  seasonal: [
    {
      name: "Spring Blossom",
      template: (product) =>
        `${product} surrounded by spring blossoms, cherry and apple flowers, fresh growth, pastel pink and green colors, renewal and freshness, seasonal beauty`
    },
    {
      name: "Summer Beach",
      template: (product) =>
        `${product} in summer beach scene, bright sunshine, sand and sea, vibrant colors, vacation and leisure, seasonal energy and joy`
    },
    {
      name: "Autumn Harvest",
      template: (product) =>
        `${product} in autumn harvest setting, falling leaves, warm amber and orange tones, cozy atmosphere, seasonal bounty and comfort`
    },
    {
      name: "Winter Wonderland",
      template: (product) =>
        `${product} in winter wonderland scene, snow and ice, cool blue and white tones, holiday magic and celebration, seasonal beauty`
    },
    {
      name: "Holiday Gift",
      template: (product) =>
        `${product} as holiday gift presentation, festive wrapping, twinkling lights, celebration and joy, seasonal gifting aesthetic, warm and inviting`
    }
  ],

  emotional: [
    {
      name: "Nostalgic Memory",
      template: (product) =>
        `${product} in nostalgic memory scene, vintage film aesthetic, warm sepia tones, sentimental and emotional connection, classic and timeless feeling`
    },
    {
      name: "Joy and Celebration",
      template: (product) =>
        `${product} in moment of pure joy, confetti and celebration, bright happy colors, emotional connection, authentic happiness and excitement`
    },
    {
      name: "Serene Calm",
      template: (product) =>
        `${product} in serene and peaceful setting, soft diffused lighting, tranquil atmosphere, calm and composed, emotional wellness and balance`
    },
    {
      name: "Empowerment Strength",
      template: (product) =>
        `${product} symbolizing empowerment, strong confident pose, bold composition, motivational energy, personal strength and achievement`
    },
    {
      name: "Intimate Connection",
      template: (product) =>
        `${product} in intimate moment, close-up composition, emotional warmth, personal connection, authentic and genuine feeling`
    }
  ],

  playful: [
    {
      name: "Whimsical Illustration",
      template: (product) =>
        `${product} in whimsical illustrated style, playful characters and elements, bright cheerful colors, fun and creative, imaginative fantasy world`
    },
    {
      name: "Pop Art Bold",
      template: (product) =>
        `${product} in pop art style, bold primary colors, comic book aesthetic, halftone dots, dynamic and energetic, Warhol-inspired design`
    },
    {
      name: "Cute Character",
      template: (product) =>
        `${product} with cute mascot character, kawaii aesthetic, soft rounded shapes, adorable and appealing, playful fun brand personality`
    },
    {
      name: "Carnival Fun",
      template: (product) =>
        `${product} at carnival or fairground, colorful lights and rides, festive atmosphere, playful energy, celebration and entertainment`
    },
    {
      name: "Retro 80s 90s",
      template: (product) =>
        `${product} in retro 80s/90s aesthetic, neon colors, synthwave vibes, nostalgic fun, vintage retro futurism, bold and energetic`
    }
  ]
};

// Get all categories
function getAllCategories() {
  return Object.keys(templates);
}

// Get templates by category
function getTemplatesByCategory(category) {
  return templates[category] || [];
}

// Get all templates
function getAllTemplates() {
  return templates;
}

// Get template by category and index
function getTemplate(category, index) {
  if (templates[category] && templates[category][index]) {
    return templates[category][index];
  }
  return null;
}

// Generate prompt for specific category and style
function generatePrompt(category, styleIndex, product) {
  const categoryTemplates = templates[category];
  if (!categoryTemplates || !categoryTemplates[styleIndex]) {
    throw new Error(`Invalid category or style index: ${category}, ${styleIndex}`);
  }

  const style = categoryTemplates[styleIndex];
  return {
    category: category,
    style: style.name,
    prompt: style.template(product)
  };
}

// Generate all prompts for a product
function generateAllPrompts(product) {
  const results = [];

  for (const [category, styles] of Object.entries(templates)) {
    styles.forEach((style, index) => {
      results.push({
        category: category,
        style: style.name,
        prompt: style.template(product)
      });
    });
  }

  return results;
}

// Generate prompts for specific categories
function generatePromptsForCategories(categories, product) {
  const results = [];

  categories.forEach(category => {
    const categoryTemplates = templates[category];
    if (categoryTemplates) {
      categoryTemplates.forEach((style) => {
        results.push({
          category: category,
          style: style.name,
          prompt: style.template(product)
        });
      });
    }
  });

  return results;
}

// Get count of total templates
function getTotalTemplateCount() {
  let count = 0;
  for (const category in templates) {
    count += templates[category].length;
  }
  return count;
}

module.exports = {
  templates,
  getAllCategories,
  getTemplatesByCategory,
  getAllTemplates,
  getTemplate,
  generatePrompt,
  generateAllPrompts,
  generatePromptsForCategories,
  getTotalTemplateCount
};
