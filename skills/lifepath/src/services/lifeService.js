// Life Service - Core business logic for life simulation

class LifeService {
  constructor(db) {
    this.db = db;
  }

  async createUser(telegramId, telegramUsername) {
    const query = `
      INSERT INTO users (telegram_id, telegram_username, tier, daily_lives_remaining)
      VALUES ($1, $2, 'free', 3)
      ON CONFLICT (telegram_id) DO UPDATE SET
        telegram_username = EXCLUDED.telegram_username
      RETURNING *
    `;
    const result = await this.db.query(query, [telegramId, telegramUsername]);
    return result.rows[0];
  }

  async getUserByTelegramId(telegramId) {
    const query = 'SELECT * FROM users WHERE telegram_id = $1';
    const result = await this.db.query(query, [telegramId]);
    return result.rows[0];
  }

  async canStartLife(userId) {
    const user = await this.getUserById(userId);
    
    // Check if premium
    if (user.tier === 'premium' && user.premium_until > new Date()) {
      return { allowed: true, remaining: Infinity };
    }
    
    // Check daily reset
    const today = new Date().toDateString();
    const lastReset = new Date(user.last_life_reset).toDateString();
    
    if (today !== lastReset) {
      // Reset daily lives
      await this.db.query(
        'UPDATE users SET daily_lives_remaining = 3, last_life_reset = CURRENT_DATE WHERE id = $1',
        [userId]
      );
      return { allowed: true, remaining: 3 };
    }
    
    return { 
      allowed: user.daily_lives_remaining > 0, 
      remaining: user.daily_lives_remaining 
    };
  }

  async getUserById(userId) {
    const query = 'SELECT * FROM users WHERE id = $1';
    const result = await this.db.query(query, [userId]);
    return result.rows[0];
  }

  async createLife(userId, mode, country, year, gender) {
    // Check if user can start a life
    const canStart = await this.canStartLife(userId);
    if (!canStart.allowed) {
      throw new Error('Daily life limit reached. Upgrade to premium or wait until tomorrow.');
    }

    // Generate unique seed
    const seed = require('crypto').randomBytes(32).toString('hex');

    const query = `
      INSERT INTO lives (user_id, mode, birth_country, birth_year, gender, seed, current_age, alive)
      VALUES ($1, $2, $3, $4, $5, $6, 0, TRUE)
      RETURNING *
    `;
    
    const result = await this.db.query(query, [
      userId, mode, country, year, gender, seed
    ]);
    
    const life = result.rows[0];
    
    // Decrement daily lives for free users
    if (canStart.remaining !== Infinity) {
      await this.db.query(
        'UPDATE users SET daily_lives_remaining = daily_lives_remaining - 1 WHERE id = $1',
        [userId]
      );
    }
    
    return life;
  }

  async getLife(lifeId) {
    const query = `
      SELECT l.*, u.telegram_username, u.tier 
      FROM lives l 
      JOIN users u ON l.user_id = u.id 
      WHERE l.id = $1
    `;
    const result = await this.db.query(query, [lifeId]);
    return result.rows[0];
  }

  async getActiveLifeForUser(userId) {
    const query = `
      SELECT * FROM lives 
      WHERE user_id = $1 AND alive = TRUE 
      ORDER BY created_at DESC 
      LIMIT 1
    `;
    const result = await this.db.query(query, [userId]);
    return result.rows[0];
  }

  async addLifeEvent(lifeId, year, age, eventType, title, description, consequences = {}, playerChoice = null) {
    const query = `
      INSERT INTO life_events (life_id, year, age, event_type, title, description, consequences, player_choice)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      RETURNING *
    `;
    
    const result = await this.db.query(query, [
      lifeId, year, age, eventType, title, description, 
      JSON.stringify(consequences), 
      playerChoice ? JSON.stringify(playerChoice) : null
    ]);
    
    // Update life history
    await this.updateLifeHistory(lifeId, result.rows[0]);
    
    return result.rows[0];
  }

  async updateLifeHistory(lifeId, event) {
    const query = `
      UPDATE lives 
      SET history = history || $2::jsonb,
          current_age = $3
      WHERE id = $1
    `;
    await this.db.query(query, [lifeId, JSON.stringify([event]), event.age]);
  }

  async updateAttributes(lifeId, changes) {
    const query = `
      UPDATE lives 
      SET health = GREATEST(0, LEAST(100, health + $2)),
          happiness = GREATEST(0, LEAST(100, happiness + $3)),
          wealth = GREATEST(0, LEAST(100, wealth + $4)),
          intelligence = GREATEST(0, LEAST(100, intelligence + $5))
      WHERE id = $1
      RETURNING health, happiness, wealth, intelligence
    `;
    
    const result = await this.db.query(query, [
      lifeId,
      changes.health || 0,
      changes.happiness || 0,
      changes.wealth || 0,
      changes.intelligence || 0
    ]);
    
    return result.rows[0];
  }

  async completeLife(lifeId, finalAge, cause) {
    const query = `
      UPDATE lives 
      SET alive = FALSE, 
          completed_at = NOW(),
          current_age = $2
      WHERE id = $1
      RETURNING *
    `;
    const result = await this.db.query(query, [lifeId, finalAge]);
    return result.rows[0];
  }

  async getLifeHistory(lifeId) {
    const query = `
      SELECT * FROM life_events 
      WHERE life_id = $1 
      ORDER BY year ASC, created_at ASC
    `;
    const result = await this.db.query(query, [lifeId]);
    return result.rows;
  }

  async addImage(lifeId, imageUrl, age) {
    const query = `
      UPDATE lives 
      SET images = images || $2::jsonb
      WHERE id = $1
    `;
    await this.db.query(query, [lifeId, JSON.stringify([{ url: imageUrl, age }])]);
  }

  async markSharedToMoltbook(lifeId, postId) {
    const query = `
      UPDATE lives 
      SET shared_to_moltbook = TRUE, moltbook_post_id = $2
      WHERE id = $1
    `;
    await this.db.query(query, [lifeId, postId]);
  }

  // Random death calculation based on age and attributes
  shouldDie(age, health) {
    // Base death chance increases with age
    let deathChance = 0;
    
    if (age < 10) deathChance = 0.02;      // Child mortality
    else if (age < 30) deathChance = 0.01; // Young adult
    else if (age < 50) deathChance = 0.03; // Middle age
    else if (age < 70) deathChance = 0.08; // Senior
    else if (age < 90) deathChance = 0.20; // Elderly
    else deathChance = 0.40;               // Very old
    
    // Health modifier
    const healthModifier = (50 - health) / 100; // -0.5 to +0.5
    deathChance += healthModifier;
    
    // Cap at reasonable bounds
    deathChance = Math.max(0.001, Math.min(0.5, deathChance));
    
    return Math.random() < deathChance;
  }

  getDeathCause(age, health) {
    const causes = {
      young: ['illness', 'accident', 'tragedy'],
      middle: ['illness', 'accident', 'violence'],
      old: ['natural causes', 'illness', 'peaceful death'],
      veryOld: ['natural causes', 'peaceful death']
    };
    
    let category = 'middle';
    if (age < 30) category = 'young';
    else if (age > 70) category = 'old';
    else if (age > 90) category = 'veryOld';
    
    const options = causes[category];
    return options[Math.floor(Math.random() * options.length)];
  }

  // Get country list (from LifePath data)
  getAvailableCountries() {
    return [
      'United States', 'India', 'China', 'Russia', 'Japan',
      'Germany', 'United Kingdom', 'France', 'Egypt', 'Nigeria',
      'Brazil', 'Mexico', 'Argentina', 'Greece', 'Iran',
      'Italy', 'Mongolia', 'Spain', 'Turkey', 'Australia',
      'Canada', 'South Korea', 'Vietnam', 'Poland', 'Ukraine'
    ];
  }

  getPremiumCountries() {
    // All 195 countries would be here
    return this.getAvailableCountries(); // Simplified for MVP
  }

  // ENHANCED METHODS FOR V2.0

  // Create life with game mode
  async createLifeEnhanced(userId, mode, country, year, gender, gameMode = 'normal', sharedWorld = false, challengeId = null) {
    // Check if user can start a life
    const canStart = await this.canStartLife(userId);
    if (!canStart.allowed) {
      throw new Error('Daily life limit reached. Upgrade to premium or wait until tomorrow.');
    }

    // Generate unique seed
    const seed = require('crypto').randomBytes(32).toString('hex');

    const query = `
      INSERT INTO lives (user_id, mode, birth_country, birth_year, gender, seed, current_age, alive, game_mode, shared_world, challenge_id)
      VALUES ($1, $2, $3, $4, $5, $6, 0, TRUE, $7, $8, $9)
      RETURNING *
    `;
    
    const result = await this.db.query(query, [
      userId, mode, country, year, gender, seed, gameMode, sharedWorld, challengeId
    ]);
    
    const life = result.rows[0];
    
    // Decrement daily lives for free users
    if (canStart.remaining !== Infinity) {
      await this.db.query(
        'UPDATE users SET daily_lives_remaining = daily_lives_remaining - 1 WHERE id = $1',
        [userId]
      );
    }
    
    // Join challenge if specified
    if (challengeId && this.challengeService) {
      await this.challengeService.joinChallenge(userId, challengeId, life.id);
    }
    
    return life;
  }

  // Continue to next year with all enhancements
  async advanceYearEnhanced(lifeId, userId, choice = null) {
    const life = await this.getLife(lifeId);
    
    if (!life || !life.alive) {
      throw new Error('Life not found or already ended');
    }
    
    const nextAge = life.current_age + 1;
    const currentYear = life.birth_year + nextAge;
    
    // Check for death
    if (this.shouldDie(nextAge, life.health)) {
      return await this.handleDeath(life, nextAge);
    }
    
    // Check for intersections (shared world)
    let intersection = null;
    if (life.shared_world && this.intersectionService) {
      intersection = await this.intersectionService.checkAndCreateIntersection(lifeId, nextAge);
    }
    
    // Generate year narrative with game mode adjustments
    const history = await this.getLifeHistory(lifeId);
    const gameMode = life.game_mode || 'normal';
    
    // Adjust generation based on game mode
    let yearChapter = await this.storyGen.generateYearChapter(life, currentYear, nextAge, history);
    
    if (gameMode === 'darkLore') {
      yearChapter = await this.makeDarkLore(yearChapter);
    } else if (gameMode === 'comedy') {
      yearChapter = await this.makeComedy(yearChapter);
    } else if (gameMode === 'tragedy') {
      yearChapter = await this.makeTragedy(yearChapter);
    }
    
    // Update attributes
    if (yearChapter.attributeChanges) {
      await this.updateAttributes(lifeId, yearChapter.attributeChanges);
    }
    
    // Save event
    await this.addLifeEvent(
      lifeId,
      currentYear,
      nextAge,
      intersection ? 'intersection' : 'year_passed',
      intersection ? `Met ${intersection.withAgent}` : `Age ${nextAge}`,
      intersection ? intersection.description : yearChapter.text
    );
    
    // Check challenge progress
    if (this.challengeService) {
      await this.challengeService.checkProgress(userId, lifeId, {
        age: nextAge,
        health: life.health,
        wealth: life.wealth,
        intelligence: life.intelligence,
        alive: true
      });
    }
    
    // Generate milestone image (if premium)
    if (nextAge % 10 === 0 && this.imageService) {
      const imageType = nextAge < 20 ? 'young_adult' : nextAge < 60 ? 'adult' : 'elder';
      await this.imageService.generateLifeImage(lifeId, nextAge, imageType, life);
    }
    
    return {
      year: currentYear,
      age: nextAge,
      text: yearChapter.text,
      intersection: intersection,
      choices: yearChapter.choices
    };
  }

  async handleDeath(life, finalAge) {
    const cause = this.getDeathCause(finalAge, life.health);
    
    // Generate death narrative
    const deathNarrative = await this.storyGen.generateDeathChapter(life, finalAge, cause);
    
    await this.addLifeEvent(
      life.id,
      life.birth_year + finalAge,
      finalAge,
      'death',
      `Death at age ${finalAge}`,
      deathNarrative.text,
      { cause }
    );
    
    await this.completeLife(life.id, finalAge, cause);
    
    // Generate final image
    if (this.imageService) {
      await this.imageService.generateLifeImage(life.id, finalAge, 'death', life);
    }
    
    // Check challenge completion on death
    if (this.challengeService) {
      await this.challengeService.checkProgress(life.user_id, life.id, {
        age: finalAge,
        health: life.health,
        wealth: life.wealth,
        intelligence: life.intelligence,
        alive: false
      });
    }
    
    return {
      died: true,
      age: finalAge,
      cause: cause,
      text: deathNarrative.text
    };
  }

  // Game mode modifiers
  async makeDarkLore(chapter) {
    // Add dark elements to the narrative
    return {
      ...chapter,
      text: chapter.text + '\n\n[Dark undercurrent: Something sinister lurks beneath the surface...]'
    };
  }

  async makeComedy(chapter) {
    // Add absurd elements
    return {
      ...chapter,
      text: chapter.text + '\n\n[Comedic twist: The absurdity of it all...]'
    };
  }

  async makeTragedy(chapter) {
    // Emphasize sadness
    return {
      ...chapter,
      text: chapter.text + '\n\n[Tragic undertone: The inevitable sorrow of existence...]'
    };
  }

  // Continue as child (dynasty mode)
  async continueAsChild(parentLifeId, userId, gender) {
    if (!this.dynastyService) {
      throw new Error('Dynasty service not available');
    }
    
    return await this.dynastyService.continueAsChild(parentLifeId, userId, gender);
  }

  // Get enhanced life summary
  async getLifeSummary(lifeId) {
    const life = await this.getLife(lifeId);
    const history = await this.getLifeHistory(lifeId);
    
    const summary = {
      ...life,
      history,
      intersections: [],
      images: [],
      dynasty: null,
      challengeProgress: []
    };
    
    // Get intersections
    if (this.intersectionService) {
      summary.intersections = await this.intersectionService.getIntersections(lifeId);
    }
    
    // Get images
    if (this.imageService) {
      summary.images = await this.imageService.getLifeImages(lifeId);
    }
    
    // Get dynasty info
    if (life.dynasty_id && this.dynastyService) {
      summary.dynasty = await this.dynastyService.getDynasty(life.dynasty_id);
    }
    
    // Get challenge progress
    if (this.challengeService) {
      summary.challengeProgress = await this.challengeService.getUserChallenges(life.user_id);
    }
    
    return summary;
  }
}

module.exports = { LifeService };
