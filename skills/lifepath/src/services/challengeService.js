// Challenge Service - Weekly/daily challenges

class ChallengeService {
  constructor(db) {
    this.db = db;
  }

  // Get active challenges
  async getActiveChallenges() {
    const query = `
      SELECT * FROM challenges 
      WHERE active = TRUE 
      AND (end_date IS NULL OR end_date >= CURRENT_DATE)
      ORDER BY difficulty ASC
    `;
    
    const result = await this.db.query(query);
    return result.rows;
  }

  // Join a challenge
  async joinChallenge(userId, challengeId, lifeId) {
    // Check if already joined
    const checkQuery = `
      SELECT * FROM user_challenges 
      WHERE user_id = $1 AND challenge_id = $2 AND life_id = $3
    `;
    const checkResult = await this.db.query(checkQuery, [userId, challengeId, lifeId]);
    
    if (checkResult.rows.length > 0) {
      return { alreadyJoined: true, progress: checkResult.rows[0] };
    }
    
    const query = `
      INSERT INTO user_challenges (user_id, challenge_id, life_id, progress)
      VALUES ($1, $2, $3, '{}')
      RETURNING *
    `;
    
    const result = await this.db.query(query, [userId, challengeId, lifeId]);
    
    // Increment participant count
    await this.db.query(
      'UPDATE challenges SET participants = participants + 1 WHERE id = $1',
      [challengeId]
    );
    
    return { joined: true, progress: result.rows[0] };
  }

  // Check challenge progress
  async checkProgress(userId, lifeId, lifeStats) {
    const query = `
      SELECT uc.*, c.*
      FROM user_challenges uc
      JOIN challenges c ON uc.challenge_id = c.id
      WHERE uc.user_id = $1 AND uc.life_id = $2 AND uc.completed = FALSE
    `;
    
    const result = await this.db.query(query, [userId, lifeId]);
    const progressUpdates = [];
    
    for (const entry of result.rows) {
      const completed = this.evaluateChallenge(entry, lifeStats);
      
      if (completed && !entry.completed) {
        await this.completeChallenge(entry.id, entry.reward_type, entry.reward_amount);
        progressUpdates.push({
          challengeName: entry.name,
          completed: true,
          reward: `${entry.reward_amount} ${entry.reward_type}`
        });
      } else {
        progressUpdates.push({
          challengeName: entry.name,
          completed: false,
          progress: this.calculateProgress(entry, lifeStats)
        });
      }
    }
    
    return progressUpdates;
  }

  evaluateChallenge(challenge, lifeStats) {
    const criteria = challenge.goal_criteria;
    
    switch (challenge.type) {
      case 'survival':
        return lifeStats.age >= criteria.min_age && 
               lifeStats.alive &&
               (!criteria.required_era || lifeStats.era === criteria.required_era);
      
      case 'achievement':
        if (criteria.min_wealth && lifeStats.wealth < criteria.min_wealth) return false;
        if (criteria.min_intelligence && lifeStats.intelligence < criteria.min_intelligence) return false;
        if (criteria.before_age && lifeStats.age > criteria.before_age) return false;
        if (criteria.max_starting_wealth && lifeStats.startingWealth > criteria.max_starting_wealth) return false;
        return true;
      
      case 'longevity':
        return lifeStats.age >= criteria.min_age;
      
      case 'dynasty':
        return lifeStats.dynastyGenerations >= criteria.min_generations &&
               lifeStats.dynastyWealth >= criteria.min_total_wealth;
      
      default:
        return false;
    }
  }

  calculateProgress(challenge, lifeStats) {
    const criteria = challenge.goal_criteria;
    let progress = 0;
    let total = 1;
    
    if (criteria.min_age) {
      progress = Math.min(lifeStats.age / criteria.min_age, 1);
      total = criteria.min_age;
    }
    
    if (criteria.min_wealth) {
      progress = Math.min(lifeStats.wealth / criteria.min_wealth, 1);
      total = criteria.min_wealth;
    }
    
    return { percentage: Math.round(progress * 100), current: Math.min(lifeStats.age, total), total };
  }

  async completeChallenge(userChallengeId, rewardType, rewardAmount) {
    const query = `
      UPDATE user_challenges 
      SET completed = TRUE, completed_at = NOW()
      WHERE id = $1
      RETURNING *
    `;
    
    await this.db.query(query, [userChallengeId]);
    
    // Grant reward
    if (rewardType === 'premium_days') {
      // Logic to extend premium status would go here
      console.log(`Granted ${rewardAmount} premium days`);
    }
    
    return { rewardGranted: true, type: rewardType, amount: rewardAmount };
  }

  // Get user's challenge progress
  async getUserChallenges(userId) {
    const query = `
      SELECT uc.*, c.name, c.description, c.reward_type, c.reward_amount
      FROM user_challenges uc
      JOIN challenges c ON uc.challenge_id = c.id
      WHERE uc.user_id = $1
      ORDER BY uc.created_at DESC
    `;
    
    const result = await this.db.query(query, [userId]);
    return result.rows;
  }

  // Create new challenge (admin)
  async createChallenge(challengeData) {
    const query = `
      INSERT INTO challenges 
      (name, description, type, difficulty, goal_criteria, reward_type, reward_amount, start_date, end_date)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
      RETURNING *
    `;
    
    const result = await this.db.query(query, [
      challengeData.name,
      challengeData.description,
      challengeData.type,
      challengeData.difficulty,
      JSON.stringify(challengeData.goal_criteria),
      challengeData.reward_type,
      challengeData.reward_amount,
      challengeData.start_date,
      challengeData.end_date
    ]);
    
    return result.rows[0];
  }

  // Get challenge leaderboard
  async getChallengeLeaderboard(challengeId) {
    const query = `
      SELECT uc.*, u.telegram_username, u.moltbook_username,
        l.birth_country, l.current_age, l.wealth
      FROM user_challenges uc
      JOIN users u ON uc.user_id = u.id
      JOIN lives l ON uc.life_id = l.id
      WHERE uc.challenge_id = $1 AND uc.completed = TRUE
      ORDER BY uc.completed_at ASC
      LIMIT 20
    `;
    
    const result = await this.db.query(query, [challengeId]);
    return result.rows;
  }
}

module.exports = { ChallengeService };
