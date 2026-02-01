// Intersection Service - Multiplayer life intersections

class IntersectionService {
  constructor(db, storyGen) {
    this.db = db;
    this.storyGen = storyGen;
  }

  // Enable/disable shared world mode for user
  async toggleSharedWorld(userId, enabled) {
    const query = 'UPDATE users SET shared_world_enabled = $1 WHERE id = $2';
    await this.db.query(query, [enabled, userId]);
    return { enabled };
  }

  // Find potential intersections for a life
  async findPotentialIntersections(lifeId, age) {
    const life = await this.getLife(lifeId);
    
    if (!life || !life.shared_world) {
      return [];
    }

    const currentYear = life.birth_year + age;
    
    const query = `
      SELECT l.*, u.telegram_username, u.moltbook_username
      FROM lives l
      JOIN users u ON l.user_id = u.id
      WHERE l.birth_country = $1
      AND l.birth_year BETWEEN $2 AND $3
      AND l.alive = TRUE
      AND l.current_age >= $4
      AND l.user_id != $5
      AND l.shared_world = TRUE
      AND l.id NOT IN (
        SELECT life_id_2 FROM life_intersections WHERE life_id_1 = $6
        UNION
        SELECT life_id_1 FROM life_intersections WHERE life_id_2 = $6
      )
      ORDER BY RANDOM()
      LIMIT 3
    `;
    
    const result = await this.db.query(query, [
      life.birth_country,
      life.birth_year - 5,
      life.birth_year + 5,
      age - 2, // Close in age
      life.user_id,
      lifeId
    ]);
    
    return result.rows;
  }

  // Check for and create intersection
  async checkAndCreateIntersection(lifeId, age) {
    const candidates = await this.findPotentialIntersections(lifeId, age);
    
    // 30% chance of intersection if candidates exist
    if (candidates.length === 0 || Math.random() > 0.3) {
      return null;
    }
    
    const otherLife = candidates[0];
    
    // Determine intersection type
    const types = [
      'school', 'work', 'neighborhood', 'hospital', 'travel',
      'competition', 'romance', 'friendship', 'conflict'
    ];
    const type = types[Math.floor(Math.random() * types.length)];
    
    // Generate intersection narrative
    const narrative = await this.generateIntersectionNarrative(
      lifeId, otherLife.id, age, type
    );
    
    // Record intersection
    const query = `
      INSERT INTO life_intersections 
      (life_id_1, life_id_2, intersection_age, intersection_type, description)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `;
    
    await this.db.query(query, [
      lifeId, otherLife.id, age, type, narrative
    ]);
    
    return {
      type,
      withAgent: otherLife.moltbook_username || otherLife.telegram_username || 'Anonymous',
      description: narrative,
      theirLifeId: otherLife.id
    };
  }

  async generateIntersectionNarrative(lifeId1, lifeId2, age, type) {
    const life1 = await this.getLife(lifeId1);
    const life2 = await this.getLife(lifeId2);
    
    const prompts = {
      school: `Two students meet at school in ${life1.birth_country}, ${life1.birth_year + age}. One is known for their ${life1.attributes || 'unique personality'}. Describe their first encounter.`,
      work: `Two colleagues start working at the same company in ${life1.birth_country}. Describe their professional relationship and first meeting.`,
      neighborhood: `New neighbors meet in ${life1.birth_country} during ${life1.birth_year + age}. Describe the circumstances of their meeting.`,
      romance: `Two people meet romantically in ${life1.birth_country}, ${life1.birth_year + age}. Describe their attraction and first date.`,
      conflict: `Two rivals clash in ${life1.birth_country}, ${life1.birth_year + age}. Describe the source of their conflict.`
    };
    
    const prompt = prompts[type] || prompts.friendship;
    
    return await this.storyGen.generateSimpleText(prompt);
  }

  // Get all intersections for a life
  async getIntersections(lifeId) {
    const query = `
      SELECT li.*, 
        CASE 
          WHEN li.life_id_1 = $1 THEN l2.id
          ELSE l1.id
        END as other_life_id,
        CASE 
          WHEN li.life_id_1 = $1 THEN u2.moltbook_username
          ELSE u1.moltbook_username
        END as other_agent_name
      FROM life_intersections li
      JOIN lives l1 ON li.life_id_1 = l1.id
      JOIN lives l2 ON li.life_id_2 = l2.id
      JOIN users u1 ON l1.user_id = u1.id
      JOIN users u2 ON l2.user_id = u2.id
      WHERE li.life_id_1 = $1 OR li.life_id_2 = $1
      ORDER BY li.intersection_age ASC
    `;
    
    const result = await this.db.query(query, [lifeId]);
    return result.rows;
  }

  async getLife(lifeId) {
    const query = 'SELECT * FROM lives WHERE id = $1';
    const result = await this.db.query(query, [lifeId]);
    return result.rows[0];
  }
}

module.exports = { IntersectionService };
