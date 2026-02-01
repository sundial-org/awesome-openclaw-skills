// Dynasty Service - Multi-generational lives

class DynastyService {
  constructor(db, storyGen) {
    this.db = db;
    this.storyGen = storyGen;
  }

  // Create a new dynasty from a founding life
  async createDynasty(foundingLifeId, userId, dynastyName) {
    const query = `
      INSERT INTO dynasties (name, founder_user_id, founder_life_id, total_generations)
      VALUES ($1, $2, $3, 1)
      RETURNING *
    `;
    
    const result = await this.db.query(query, [dynastyName, userId, foundingLifeId]);
    const dynasty = result.rows[0];
    
    // Update the founding life
    await this.db.query(
      'UPDATE lives SET dynasty_id = $1, generation = 1 WHERE id = $2',
      [dynasty.id, foundingLifeId]
    );
    
    // Update user stats
    await this.db.query(
      'UPDATE users SET total_dynasties = total_dynasties + 1 WHERE id = $1',
      [userId]
    );
    
    return dynasty;
  }

  // Continue as child after death
  async continueAsChild(parentLifeId, userId, gender) {
    const parent = await this.getLife(parentLifeId);
    
    if (!parent || parent.alive) {
      throw new Error('Parent life not found or still alive');
    }
    
    // Calculate birth year (20 years after parent's birth + parent's age at death)
    const childBirthYear = parent.birth_year + parent.current_age + 20;
    
    // Inherit traits
    const inheritedTraits = this.calculateInheritance(parent);
    
    // Create child life
    const query = `
      INSERT INTO lives (
        user_id, mode, birth_country, birth_year, gender, 
        seed, dynasty_id, generation, parent_life_id, 
        health, happiness, wealth, intelligence, game_mode
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
      RETURNING *
    `;
    
    const seed = require('crypto').randomBytes(32).toString('hex');
    const generation = (parent.generation || 1) + 1;
    
    const result = await this.db.query(query, [
      userId,
      parent.mode,
      parent.birth_country, // Usually same country
      childBirthYear,
      gender,
      seed,
      parent.dynasty_id,
      generation,
      parentLifeId,
      inheritedTraits.health,
      inheritedTraits.happiness,
      inheritedTraits.wealth,
      inheritedTraits.intelligence,
      parent.game_mode
    ]);
    
    const childLife = result.rows[0];
    
    // Update dynasty
    await this.updateDynastyStats(parent.dynasty_id);
    
    // Generate birth narrative mentioning parent
    const birthNarrative = await this.generateChildBirthNarrative(parent, childLife);
    
    return {
      ...childLife,
      birthNarrative,
      inheritedFrom: {
        parentName: parent.name || 'Parent',
        parentAgeAtDeath: parent.current_age,
        wealth: inheritedTraits.wealth,
        traits: inheritedTraits
      }
    };
  }

  calculateInheritance(parent) {
    // Heritability rates
    const heritability = {
      intelligence: 0.3,
      health: 0.2,
      wealth: 0.8 // Wealth is highly inheritable
    };
    
    return {
      intelligence: Math.round(
        (parent.intelligence * heritability.intelligence) + 
        (Math.random() * 70)
      ),
      health: Math.round(
        (parent.health * heritability.health) + 
        (Math.random() * 80)
      ),
      wealth: Math.round(parent.wealth * heritability.wealth),
      happiness: 50 + Math.floor(Math.random() * 20) // Start neutral
    };
  }

  async generateChildBirthNarrative(parent, child) {
    const prompt = `
      Write a birth narrative for a child born in ${child.birth_country} in ${child.birth_year}.
      
      CONTEXT:
      - Parent died at age ${parent.current_age} in ${parent.birth_year + parent.current_age}
      - Parent's final wealth: ${parent.wealth}/100
      - Parent's reputation: ${parent.happiness > 50 ? 'beloved' : 'controversial'}
      - This is generation ${child.generation} of the dynasty
      
      Include:
      - How the parent's legacy affects the child's birth
      - Family circumstances (wealth, status)
      - Hopes for the new generation
      
      Tone: Hopeful but realistic, acknowledging the parent's death
    `;
    
    return await this.storyGen.generateSimpleText(prompt);
  }

  async updateDynastyStats(dynastyId) {
    const query = `
      UPDATE dynasties 
      SET total_generations = (
        SELECT MAX(generation) FROM lives WHERE dynasty_id = $1
      ),
      total_wealth = (
        SELECT COALESCE(SUM(wealth), 0) FROM lives WHERE dynasty_id = $1
      )
      WHERE id = $1
    `;
    
    await this.db.query(query, [dynastyId]);
  }

  // Get dynasty details with all generations
  async getDynasty(dynastyId) {
    const dynastyQuery = 'SELECT * FROM dynasties WHERE id = $1';
    const dynastyResult = await this.db.query(dynastyQuery, [dynastyId]);
    
    if (dynastyResult.rows.length === 0) {
      return null;
    }
    
    const dynasty = dynastyResult.rows[0];
    
    // Get all lives in dynasty
    const livesQuery = `
      SELECT * FROM lives 
      WHERE dynasty_id = $1 
      ORDER BY generation ASC, birth_year ASC
    `;
    const livesResult = await this.db.query(livesQuery, [dynastyId]);
    
    return {
      ...dynasty,
      lives: livesResult.rows,
      totalLives: livesResult.rows.length,
      averageLifespan: this.calculateAverageLifespan(livesResult.rows),
      totalWealth: livesResult.rows.reduce((sum, l) => sum + (l.wealth || 0), 0)
    };
  }

  calculateAverageLifespan(lives) {
    const completed = lives.filter(l => !l.alive);
    if (completed.length === 0) return 0;
    return completed.reduce((sum, l) => sum + l.current_age, 0) / completed.length;
  }

  // Get dynasty leaderboard
  async getDynastyLeaderboard(limit = 10) {
    const query = `
      SELECT d.*, 
        (SELECT COUNT(*) FROM lives WHERE dynasty_id = d.id) as life_count,
        (SELECT AVG(current_age) FROM lives WHERE dynasty_id = d.id AND alive = FALSE) as avg_lifespan
      FROM dynasties d
      ORDER BY d.total_wealth DESC, life_count DESC
      LIMIT $1
    `;
    
    const result = await this.db.query(query, [limit]);
    return result.rows;
  }

  async getLife(lifeId) {
    const query = 'SELECT * FROM lives WHERE id = $1';
    const result = await this.db.query(query, [lifeId]);
    return result.rows[0];
  }
}

module.exports = { DynastyService };
