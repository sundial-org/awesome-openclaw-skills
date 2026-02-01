// Image Service - Banana.dev integration for life portraits

const axios = require('axios');
const fs = require('fs');
const path = require('path');

class ImageService {
  constructor(db) {
    this.db = db;
    this.bananaApiKey = process.env.BANANA_API_KEY;
    this.modelKey = process.env.BANANA_MODEL_KEY || 'dreambooth-model';
    this.imageStoragePath = process.env.IMAGE_STORAGE_PATH || './images';
    
    // Ensure storage directory exists
    if (!fs.existsSync(this.imageStoragePath)) {
      fs.mkdirSync(this.imageStoragePath, { recursive: true });
    }
  }

  // Generate image for life event
  async generateLifeImage(lifeId, age, imageType, lifeData) {
    const prompt = this.buildPrompt(imageType, lifeData, age);
    
    try {
      // Call Banana.dev API
      const result = await this.callBananaAPI(prompt);
      
      // Save image locally
      const imagePath = await this.saveImage(result.image, lifeId, age, imageType);
      
      // Store reference in database
      await this.storeImageReference(lifeId, age, imageType, imagePath, prompt);
      
      return {
        success: true,
        imageUrl: imagePath,
        prompt: prompt,
        age: age,
        type: imageType
      };
      
    } catch (error) {
      console.error('Image generation failed:', error);
      return {
        success: false,
        error: error.message,
        fallback: true
      };
    }
  }

  buildPrompt(imageType, lifeData, age) {
    const currentYear = lifeData.birth_year + age;
    const era = this.getEra(currentYear);
    
    const basePrompts = {
      birth: `Newborn baby, ${lifeData.birth_country}, ${lifeData.birth_year}, 
              ${era.style}, soft natural lighting, emotional moment, 
              ${lifeData.gender === 'female' ? 'baby girl' : lifeData.gender === 'male' ? 'baby boy' : 'infant'},
              hospital or home setting, tender atmosphere`,
      
      childhood: `Child aged ${age}, playing in ${lifeData.birth_country}, 
                  ${currentYear}, ${era.style}, joyful, outdoor or indoor setting,
                  period-appropriate clothing, candid moment`,
      
      young_adult: `Young adult aged ${age}, ${lifeData.birth_country}, 
                    ${currentYear}, ${era.style}, confident pose,
                    professional or casual attire, environmental portrait,
                    ${lifeData.wealth > 70 ? 'wealthy appearance' : 'working class setting'}`,
      
      adult: `Adult aged ${age}, ${lifeData.birth_country}, 
              ${currentYear}, ${era.style}, mature, experienced,
              ${lifeData.happiness > 70 ? 'warm smile' : 'contemplative expression'},
              authentic period detail`,
      
      elder: `Elderly person aged ${age}, ${lifeData.birth_country}, 
              ${currentYear}, ${era.style}, wise, weathered face,
              grey hair, peaceful expression, lifetime of experience`,
      
      death: `Elderly person on deathbed, peaceful, ${lifeData.birth_country}, 
              ${currentYear}, ${era.style}, final moments, family around,
              bittersweet, life reflection, dignified ending`,
      
      milestone: `Portrait of person aged ${age}, ${lifeData.birth_country}, 
                  ${currentYear}, ${era.style}, significant life moment,
                  ${this.getMilestoneContext(lifeData, age)}`,
      
      default: `Portrait of ${age}-year-old person, ${lifeData.birth_country}, 
                ${currentYear}, ${era.style}, photorealistic, cinematic lighting`
    };
    
    return basePrompts[imageType] || basePrompts.default;
  }

  getEra(year) {
    if (year < 1920) {
      return {
        name: 'early 20th century',
        style: 'vintage sepia, early photography, soft focus'
      };
    } else if (year < 1960) {
      return {
        name: 'mid 20th century',
        style: '1950s color film, Kodachrome, vibrant colors'
      };
    } else if (year < 1990) {
      return {
        name: 'late 20th century',
        style: '1980s aesthetic, analog film, grainy texture'
      };
    } else {
      return {
        name: 'modern era',
        style: 'modern digital photography, sharp focus, natural lighting'
      };
    }
  }

  getMilestoneContext(lifeData, age) {
    // Determine milestone type based on age
    if (age >= 18 && age <= 25) {
      return 'graduation or career start, hopeful, ambitious';
    } else if (age >= 25 && age <= 35) {
      return 'marriage or family, domestic happiness';
    } else if (age >= 40 && age <= 50) {
      return 'career peak, professional success, confident';
    } else if (age >= 60) {
      return 'retirement, legacy, family gathered';
    }
    return 'significant life achievement';
  }

  async callBananaAPI(prompt) {
    // If no API key, return mock response for development
    if (!this.bananaApiKey) {
      console.log('No Banana API key - returning mock image');
      return {
        image: 'mock-image-data',
        mock: true
      };
    }
    
    const response = await axios.post(
      `https://api.banana.dev/v1/models/${this.modelKey}/runs`,
      {
        prompt: prompt,
        width: 512,
        height: 512,
        num_inference_steps: 25,
        guidance_scale: 7.5
      },
      {
        headers: {
          'Authorization': `Bearer ${this.bananaApiKey}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    return response.data;
  }

  async saveImage(imageData, lifeId, age, imageType) {
    const filename = `${lifeId}_${age}_${imageType}.png`;
    const filepath = path.join(this.imageStoragePath, filename);
    
    // In production, this would decode base64 and save
    // For now, store reference
    if (imageData === 'mock-image-data') {
      // Create a placeholder
      fs.writeFileSync(filepath, 'mock-image-placeholder');
    } else {
      // Decode and save real image
      const buffer = Buffer.from(imageData, 'base64');
      fs.writeFileSync(filepath, buffer);
    }
    
    return filepath;
  }

  async storeImageReference(lifeId, age, imageType, imageUrl, prompt) {
    const query = `
      INSERT INTO life_images (life_id, age, image_type, image_url, prompt, model_used)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING *
    `;
    
    await this.db.query(query, [
      lifeId, age, imageType, imageUrl, prompt, 'banana-dev'
    ]);
  }

  // Get images for a life
  async getLifeImages(lifeId) {
    const query = `
      SELECT * FROM life_images 
      WHERE life_id = $1 
      ORDER BY age ASC
    `;
    
    const result = await this.db.query(query, [lifeId]);
    return result.rows;
  }

  // Generate key milestone images for a life
  async generateMilestoneImages(lifeId, lifeData) {
    const milestones = [
      { age: 0, type: 'birth' },
      { age: Math.floor(lifeData.current_age * 0.3), type: 'young_adult' },
      { age: Math.floor(lifeData.current_age * 0.6), type: 'adult' },
      { age: lifeData.current_age - 1, type: 'elder' }
    ].filter(m => m.age >= 0 && m.age < lifeData.current_age);
    
    const images = [];
    
    for (const milestone of milestones) {
      const image = await this.generateLifeImage(lifeId, milestone.age, milestone.type, lifeData);
      if (image.success) {
        images.push(image);
      }
    }
    
    return images;
  }

  // Get image generation cost estimate
  getCostEstimate(imageCount) {
    // Banana.dev pricing (approximate)
    const costPerImage = 0.02; // $0.02 per image
    return {
      estimatedCost: imageCount * costPerImage,
      currency: 'USD',
      perImage: costPerImage
    };
  }
}

module.exports = { ImageService };
