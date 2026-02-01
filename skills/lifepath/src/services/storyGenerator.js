const { GoogleGenerativeAI } = require('@google/generative-ai');

class StoryGenerator {
  constructor() {
    // Rotate through available API keys
    this.apiKeys = [
      process.env.GEMINI_API_KEY,
      process.env.GEMINI_API_KEY_BACKUP,
      'AIzaSyCaM-ZhzTYy9ZQoqoR0aw5SdldCmPn6wh8',
      'AIzaSyAEwvtsgQ8l10hErJiW5jYrk8NSGFEOchM'
    ].filter(Boolean);
    
    this.currentKeyIndex = 0;
    this.genAI = new GoogleGenerativeAI(this.apiKeys[0]);
  }

  rotateKey() {
    this.currentKeyIndex = (this.currentKeyIndex + 1) % this.apiKeys.length;
    this.genAI = new GoogleGenerativeAI(this.apiKeys[this.currentKeyIndex]);
    console.log(`Rotated to API key ${this.currentKeyIndex + 1}/${this.apiKeys.length}`);
  }

  getModel(modelName = 'gemini-2.0-flash-exp') {
    return this.genAI.getGenerativeModel({ model: modelName });
  }

  async generateBirthChapter(country, year, gender, seed) {
    const model = this.getModel();
    
    const prompt = `
You are narrating the birth and first year of a person's life in a life simulation game.

CONTEXT:
- Born in ${country} in the year ${year}
- Gender: ${gender}
- Historical context: ${this.getHistoricalContext(year)}

Write a vivid, emotionally resonant narrative of:
1. The circumstances of birth (family, location, social class)
2. The first year of life (milestones, family dynamics, environment)
3. End with the child approaching age 1

STYLE: Second person ("You were born..."), sensory details, emotional resonance
LENGTH: 2-3 paragraphs
TONE: Bittersweet, realistic, culturally authentic

Include specific details about ${country} in ${year}.
    `;

    try {
      const result = await model.generateContent(prompt);
      return {
        text: result.response.text(),
        age: 0,
        year: year,
        events: ['birth', 'first_year']
      };
    } catch (error) {
      console.error('Generation error:', error);
      this.rotateKey();
      throw error;
    }
  }

  async generateYearChapter(lifeContext, currentYear, age, previousChoices = []) {
    const model = this.getModel();
    
    // Prepare context from life history
    const historySummary = this.summarizeHistory(previousChoices);
    
    const prompt = `
Continue the life story:

CONTEXT:
- Currently age ${age} in year ${currentYear}
- Born in ${lifeContext.country} in ${lifeContext.birthYear}
- Current attributes: Health ${lifeContext.health}/100, Happiness ${lifeContext.happiness}/100, Wealth ${lifeContext.wealth}/100

LIFE HISTORY:
${historySummary}

Write the events of age ${age}:
1. One major life event (relationship, opportunity, challenge, or tragedy)
2. How the character responds internally
3. The consequences (affect attributes slightly)
4. End with a decision point or natural continuation

STYLE: Second person, vivid sensory details, emotional authenticity
LENGTH: 2-3 paragraphs
DECISION: Include 2-3 choices at the end if appropriate for the story
    `;

    try {
      const result = await model.generateContent(prompt);
      const text = result.response.text();
      
      // Parse choices if present
      const choices = this.extractChoices(text);
      
      return {
        text: text,
        age: age,
        year: currentYear,
        events: ['year_passed'],
        choices: choices,
        attributeChanges: this.calculateAttributeChanges(text)
      };
    } catch (error) {
      console.error('Generation error:', error);
      this.rotateKey();
      throw error;
    }
  }

  async generateDeathChapter(lifeContext, age, cause) {
    const model = this.getModel();
    
    const prompt = `
Write the death scene and life summary for:

- Died at age ${age} in year ${lifeContext.birthYear + age}
- Born in ${lifeContext.country}
- Life summary: ${JSON.stringify(lifeContext.history.slice(-5))}
- Cause: ${cause}

Write:
1. The circumstances of death (peaceful, tragic, sudden, etc.)
2. Final moments and thoughts
3. Legacy summary (what they accomplished, how they're remembered)
4. Final reflection on the life lived

STYLE: Poignant, reflective, emotionally resonant
TONE: Respectful of the life lived, acknowledging both joys and sorrows
LENGTH: 3-4 paragraphs
    `;

    try {
      const result = await model.generateContent(prompt);
      return {
        text: result.response.text(),
        age: age,
        cause: cause,
        final: true
      };
    } catch (error) {
      console.error('Generation error:', error);
      this.rotateKey();
      throw error;
    }
  }

  getHistoricalContext(year) {
    if (year < 1914) return 'Pre-WWI era, industrialization, colonial empires';
    if (year < 1945) return 'World Wars era, great depression, political upheaval';
    if (year < 1991) return 'Cold War era, space race, cultural revolution';
    if (year < 2001) return 'Post-Cold War, internet age, globalization';
    return 'Modern era, digital revolution, climate change';
  }

  summarizeHistory(choices) {
    if (!choices || choices.length === 0) return 'Just beginning life.';
    
    const recent = choices.slice(-3);
    return recent.map((c, i) => {
      const age = c.age || i;
      return `Age ${age}: ${c.description || c.text?.substring(0, 100)}...`;
    }).join('\n');
  }

  extractChoices(text) {
    // Simple choice extraction - look for patterns like "A)" or "1." or "Choice:"
    const choiceRegex = /(?:^|\n)(?:[A-C][).:]\s*|\d+[).:]\s*|Choice\s*\d*[):.]\s*)(.+?)(?=\n(?:[A-C][).:]|\d+[).:]|Choice|$)/gi;
    const matches = text.match(choiceRegex);
    
    if (matches) {
      return matches.map(m => m.trim()).slice(0, 3);
    }
    
    return [];
  }

  calculateAttributeChanges(text) {
    // Simple sentiment analysis for attribute changes
    const changes = {
      health: 0,
      happiness: 0,
      wealth: 0,
      intelligence: 0
    };
    
    const textLower = text.toLowerCase();
    
    // Health indicators
    if (textLower.includes('illness') || textLower.includes('sick') || textLower.includes('injury')) {
      changes.health -= 5;
    }
    if (textLower.includes('healed') || textLower.includes('healthy') || textLower.includes('strong')) {
      changes.health += 3;
    }
    
    // Happiness indicators
    if (textLower.includes('joy') || textLower.includes('happy') || textLower.includes('love')) {
      changes.happiness += 5;
    }
    if (textLower.includes('sad') || textLower.includes('loss') || textLower.includes('grief')) {
      changes.happiness -= 5;
    }
    
    // Wealth indicators
    if (textLower.includes('money') || textLower.includes('rich') || textLower.includes('job')) {
      changes.wealth += Math.floor(Math.random() * 5) - 2;
    }
    
    return changes;
  }

  async generateImagePrompt(age, year, country, event) {
    const model = this.getModel();
    
    const prompt = `
Create a detailed image generation prompt for:
- A person aged ${age} in ${country} during ${year}
- Event: ${event}

FORMAT:
Subject: [description of person]
Setting: [location, time of day, atmosphere]
Style: Cinematic, photorealistic, warm tones
Mood: [emotional tone]
Details: Period clothing, authentic setting, emotional expression

Respond with only the image prompt, no explanation.
    `;

    try {
      const result = await model.generateContent(prompt);
      return result.response.text().trim();
    } catch (error) {
      console.error('Image prompt error:', error);
      return `Portrait of a ${age}-year-old person in ${country}, ${year}, ${event}, cinematic lighting, photorealistic`;
    }
  }
}

module.exports = { StoryGenerator };
