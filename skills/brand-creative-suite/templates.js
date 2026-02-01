// 品牌创意套件 - 提示词模板库
// Source: Nano Banana Pro 908+ 精选案例
// https://github.com/xianyu110/awesome-nanobananapro-prompts

const templates = {
  // 1. 品牌浪漫花束 (案例ID: 11)
  bouquet: {
    id: 'bouquet',
    name: '品牌浪漫花束',
    description: '用品牌元素创造的浪漫花束,玫瑰由品牌视觉纹理制成',
    source_id: 11,
    category: 'brand',
    template: `A romantic square-format bouquet inspired by {BRAND_NAME}. Roses are crafted from visual patterns or textures that reflect the brand's identity. The bouquet is wrapped in luxurious material echoing the brand's signature style (e.g. {BRAND_MATERIAL}), and elegantly tied with one of the brand's iconic products: {BRAND_PRODUCT}, replacing a traditional ribbon. Place it on a surface that matches the brand's aesthetic ({SURFACE}). Cinematic lighting, soft focus, high detail, 8K resolution, professional photography.`,
    parameters: {
      BRAND_NAME: {
        type: 'string',
        required: true,
        description: '品牌名称'
      },
      BRAND_MATERIAL: {
        type: 'string',
        default: 'silk, velvet, leather',
        description: '包装材质'
      },
      BRAND_PRODUCT: {
        type: 'string',
        required: true,
        description: '标志性产品'
      },
      SURFACE: {
        type: 'string',
        default: 'elegant marble table',
        description: '摆放表面'
      },
      BRAND_COLORS: {
        type: 'string',
        description: '品牌主色调'
      }
    },
    output_format: 'square',
    examples: [
      {
        description: '奢华时尚品牌',
        params: {
          BRAND_NAME: 'Gucci',
          BRAND_MATERIAL: 'silk',
          BRAND_PRODUCT: 'perfume bottle',
          SURFACE: 'elegant marble table'
        }
      },
      {
        description: '极简科技品牌',
        params: {
          BRAND_NAME: 'Apple',
          BRAND_MATERIAL: 'leather',
          BRAND_PRODUCT: 'iPhone',
          SURFACE: 'clean white desk'
        }
      }
    ]
  },

  // 2. 品牌星球世界 (案例ID: 16)
  planet: {
    id: 'planet',
    name: '品牌星球世界',
    description: '以品牌为核心构建的异星世界,3025年的奇幻星球',
    source_id: 16,
    category: 'brand',
    template: `Planet {BRAND_NAME}, Year 3025. A distant world shaped entirely by the essence of the brand. The landscapes echo its core identity — {LANDSCAPE_DESCRIPTION}. Native flora and fauna embody its signature ingredients and aesthetics. Rivers flow with iconic flavors. Architecture is inspired by its packaging and visual language, fused with futuristic technology. The atmosphere is {ATMOSPHERE}. Cinematic wide shot, hyper-detailed, sci-fi fantasy concept art, 8K.`,
    parameters: {
      BRAND_NAME: {
        type: 'string',
        required: true,
        description: '品牌名称'
      },
      LANDSCAPE_DESCRIPTION: {
        type: 'string',
        default: 'from surreal terrains to fantastical weather patterns',
        description: '地貌描述'
      },
      ATMOSPHERE: {
        type: 'string',
        default: 'dreamy and ethereal',
        description: '氛围'
      },
      ICONIC_ELEMENTS: {
        type: 'string',
        description: '标志性元素'
      }
    },
    output_format: 'landscape',
    examples: [
      {
        description: '汽水品牌星球',
        params: {
          BRAND_NAME: 'Coca-Cola',
          LANDSCAPE_DESCRIPTION: 'bubbling red lakes and effervescent clouds',
          ATMOSPHERE: 'energetic and refreshing'
        }
      },
      {
        description: '化妆品品牌星球',
        params: {
          BRAND_NAME: 'Chanel',
          LANDSCAPE_DESCRIPTION: 'flowers made of lipstick and makeup packaging mountains',
          ATMOSPHERE: 'elegant and sophisticated'
        }
      }
    ]
  },

  // 3. 品牌水流Logo雕塑 (案例ID: 26)
  water: {
    id: 'water',
    name: '品牌水流Logo雕塑',
    description: '由水流构成的超高清品牌Logo雕塑,极具视觉冲击力',
    source_id: 26,
    category: 'brand',
    template: `An ultra-high resolution 8K cinematic render of the {BRAND_NAME} logo, sculpted entirely from {LIQUID_STYLE}. The liquid forms every curve and edge of the brand's logo with fluid precision, highlighted by vibrant {COLOR_ACCENT} accents inspired by {BRAND_NAME}'s color identity. The background is pitch black, creating sharp contrast and drama. Dynamic {LIGHTING} reveals sharp reflections and refractions within the water. Professional 3D rendering, hyper-realistic, product visualization.`,
    parameters: {
      BRAND_NAME: {
        type: 'string',
        required: true,
        description: '品牌名称'
      },
      LIQUID_STYLE: {
        type: 'string',
        default: 'flowing crystal-clear water',
        description: '水流风格',
        options: ['flowing crystal-clear water', 'frosted liquid glass', 'turbulent fluid', 'smooth silky water']
      },
      COLOR_ACCENT: {
        type: 'string',
        default: 'neon blue and white',
        description: '色彩强调'
      },
      LIGHTING: {
        type: 'string',
        default: 'rim lights',
        description: '光照效果',
        options: ['rim lights', 'dramatic spotlights', 'cinematic lighting', 'studio lighting']
      }
    },
    output_format: 'portrait',
    examples: [
      {
        description: '运动品牌',
        params: {
          BRAND_NAME: 'Nike',
          LIQUID_STYLE: 'turbulent fluid',
          COLOR_ACCENT: 'neon orange and white',
          LIGHTING: 'dramatic spotlights'
        }
      },
      {
        description: '奢侈品牌',
        params: {
          BRAND_NAME: 'Louis Vuitton',
          LIQUID_STYLE: 'smooth silky water',
          COLOR_ACCENT: 'gold and black',
          LIGHTING: 'cinematic lighting'
        }
      }
    ]
  },

  // 4. 品牌树屋场景 (案例ID: 15)
  treehouse: {
    id: 'treehouse',
    name: '品牌树屋场景',
    description: '以品牌为主题打造的奢华树屋度假地',
    source_id: 15,
    category: 'brand',
    template: `A quiet morning in a luxury treehouse retreat created by {BRAND_NAME} — golden light pours through windows framed in the brand's signature colors. A cozy seating area features playful, thematic furniture, and a circular rug inspired by {BRAND_SYMBOL_OR_PRODUCT}. The coffee table bears the embossed logo, while a screen on the wall loops the phrase: "{BRAND_SLOGAN}". A curated display of iconic items from the brand's product line decorates the space. Cinematic photography, warm {TIME_OF_DAY} lighting, cozy atmosphere, 8K, photorealistic.`,
    parameters: {
      BRAND_NAME: {
        type: 'string',
        required: true,
        description: '品牌名称'
      },
      BRAND_SYMBOL_OR_PRODUCT: {
        type: 'string',
        required: true,
        description: '品牌符号或产品'
      },
      BRAND_SLOGAN: {
        type: 'string',
        required: true,
        description: '品牌标语'
      },
      TIME_OF_DAY: {
        type: 'string',
        default: 'morning',
        description: '时间段',
        options: ['morning', 'golden hour', 'dusk', 'evening']
      },
      BRAND_COLORS: {
        type: 'string',
        description: '品牌色调'
      }
    },
    output_format: 'landscape',
    examples: [
      {
        description: '咖啡品牌',
        params: {
          BRAND_NAME: 'Starbucks',
          BRAND_SYMBOL_OR_PRODUCT: 'coffee beans',
          BRAND_SLOGAN: 'Wake Up Perfectly',
          TIME_OF_DAY: 'golden hour',
          BRAND_COLORS: 'green and white'
        }
      },
      {
        description: '户外装备品牌',
        params: {
          BRAND_NAME: 'The North Face',
          BRAND_SYMBOL_OR_PRODUCT: 'mountain peak',
          BRAND_SLOGAN: 'Never Stop Exploring',
          TIME_OF_DAY: 'dusk',
          BRAND_COLORS: 'red and black'
        }
      }
    ]
  },

  // 5. 品牌降落伞包装 (案例ID: 27)
  parachute: {
    id: 'parachute',
    name: '品牌降落伞包装',
    description: '梦幻的品牌产品降落伞包装广告',
    source_id: 27,
    category: 'brand',
    template: `A dreamy brand ad of {BRAND_NAME}, a brand designed bubble-like capsule with {PARACHUTE_COLOR} parachute packaging their classic product: {PRODUCT}, against {SKY} sky with other blurry parachute packaging in the background, {CLOUDS}, a small brand logo on top, a tiny slogan "{SLOGAN}" beneath it, cinematic {WEATHER} lighting, lens flare, depth of field, HDR, 1:1 square format, professional advertising photography.`,
    parameters: {
      BRAND_NAME: {
        type: 'string',
        required: true,
        description: '品牌名称'
      },
      PARACHUTE_COLOR: {
        type: 'string',
        default: 'brand color',
        description: '降落伞颜色'
      },
      PRODUCT: {
        type: 'string',
        required: true,
        description: '经典产品'
      },
      SLOGAN: {
        type: 'string',
        default: '',
        description: '标语'
      },
      SKY: {
        type: 'string',
        default: 'blue',
        description: '天空颜色'
      },
      CLOUDS: {
        type: 'string',
        default: 'white clouds',
        description: '云层描述'
      },
      WEATHER: {
        type: 'string',
        default: 'sunny day',
        description: '天气',
        options: ['sunny day', 'sunset', 'cloudy', 'dramatic']
      }
    },
    output_format: 'square',
    examples: [
      {
        description: '巧克力品牌',
        params: {
          BRAND_NAME: 'Godiva',
          PARACHUTE_COLOR: 'gold',
          PRODUCT: 'chocolate truffles',
          SLOGAN: 'Pure Indulgence',
          SKY: 'golden',
          CLOUDS: 'fluffy white clouds',
          WEATHER: 'sunset'
        }
      },
      {
        description: '科技品牌',
        params: {
          BRAND_NAME: 'Sony',
          PARACHUTE_COLOR: 'navy blue',
          PRODUCT: 'wireless headphones',
          SLOGAN: 'Hear The World',
          SKY: 'blue',
          CLOUDS: 'soft wispy clouds',
          WEATHER: 'sunny day'
        }
      }
    ]
  }
};

// 辅助函数: 模板参数插值
function renderTemplate(templateId, params) {
  const template = templates[templateId];

  if (!template) {
    throw new Error(`Template not found: ${templateId}`);
  }

  let prompt = template.template;

  // 替换所有占位符
  for (const [key, value] of Object.entries(params)) {
    const placeholder = `{${key}}`;
    prompt = prompt.replace(new RegExp(placeholder, 'g'), value);
  }

  return {
    prompt,
    metadata: {
      template_id: template.id,
      template_name: template.name,
      output_format: template.output_format,
      category: template.category
    }
  };
}

// 辅助函数: 生成变体
function generateVariations(baseParams, count = 3) {
  const variations = [];

  for (let i = 0; i < count; i++) {
    const variation = { ...baseParams };

    // 根据模板ID添加随机化逻辑
    if (baseParams.template_id === 'bouquet') {
      const materials = ['silk', 'velvet', 'leather', 'satin', 'linen'];
      const surfaces = ['elegant marble table', 'clean white surface', 'dark wood table', 'glass surface'];
      variation.BRAND_MATERIAL = materials[Math.floor(Math.random() * materials.length)];
      variation.SURFACE = surfaces[Math.floor(Math.random() * surfaces.length)];
    } else if (baseParams.template_id === 'planet') {
      const atmospheres = ['dreamy and ethereal', 'energetic and dynamic', 'mysterious and exotic', 'peaceful and serene'];
      variation.ATMOSPHERE = atmospheres[Math.floor(Math.random() * atmospheres.length)];
    } else if (baseParams.template_id === 'water') {
      const liquidStyles = ['flowing crystal-clear water', 'frosted liquid glass', 'turbulent fluid', 'smooth silky water'];
      variation.LIQUID_STYLE = liquidStyles[Math.floor(Math.random() * liquidStyles.length)];
    } else if (baseParams.template_id === 'treehouse') {
      const times = ['morning', 'golden hour', 'dusk', 'evening'];
      variation.TIME_OF_DAY = times[Math.floor(Math.random() * times.length)];
    } else if (baseParams.template_id === 'parachute') {
      const weathers = ['sunny day', 'sunset', 'cloudy', 'dramatic'];
      variation.WEATHER = weathers[Math.floor(Math.random() * weathers.length)];
    }

    variations.push(variation);
  }

  return variations;
}

// 辅助函数: 验证参数
function validateParams(templateId, params) {
  const template = templates[templateId];

  if (!template) {
    throw new Error(`Template not found: ${templateId}`);
  }

  const errors = [];

  for (const [key, config] of Object.entries(template.parameters)) {
    if (config.required && !params[key]) {
      errors.push(`Missing required parameter: ${key}`);
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

// 导出
module.exports = {
  templates,
  renderTemplate,
  generateVariations,
  validateParams
};
