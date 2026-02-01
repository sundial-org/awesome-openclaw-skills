// Life API Routes

async function lifeRoutes(fastify, options) {
  const { lifeService } = options;

  // Start a new life
  fastify.post('/start', async (request, reply) => {
    try {
      const { userId, mode, country, year, gender } = request.body;
      
      const life = await lifeService.createLife(userId, mode, country, year, gender);
      
      return {
        success: true,
        life: {
          id: life.id,
          country: life.birth_country,
          year: life.birth_year,
          seed: life.seed
        }
      };
    } catch (error) {
      reply.code(400);
      return { success: false, error: error.message };
    }
  });

  // Get life details
  fastify.get('/:lifeId', async (request, reply) => {
    try {
      const { lifeId } = request.params;
      const life = await lifeService.getLife(lifeId);
      
      if (!life) {
        reply.code(404);
        return { success: false, error: 'Life not found' };
      }
      
      const history = await lifeService.getLifeHistory(lifeId);
      
      return {
        success: true,
        life: {
          ...life,
          history
        }
      };
    } catch (error) {
      reply.code(500);
      return { success: false, error: error.message };
    }
  });

  // Advance life by one year
  fastify.post('/:lifeId/advance', async (request, reply) => {
    try {
      const { lifeId } = request.params;
      const life = await lifeService.getLife(lifeId);
      
      if (!life || !life.alive) {
        reply.code(400);
        return { success: false, error: 'Life not found or already ended' };
      }
      
      // This would integrate with the story generator
      // For now, return placeholder
      return {
        success: true,
        message: 'Year advanced',
        currentAge: life.current_age + 1
      };
    } catch (error) {
      reply.code(500);
      return { success: false, error: error.message };
    }
  });

  // Get available countries
  fastify.get('/countries', async (request, reply) => {
    const countries = lifeService.getAvailableCountries();
    return {
      success: true,
      countries,
      count: countries.length
    };
  });

  // Get user's active life
  fastify.get('/user/:userId/active', async (request, reply) => {
    try {
      const { userId } = request.params;
      const life = await lifeService.getActiveLifeForUser(userId);
      
      if (!life) {
        return { success: true, life: null };
      }
      
      return { success: true, life };
    } catch (error) {
      reply.code(500);
      return { success: false, error: error.message };
    }
  });

  // Get life statistics
  fastify.get('/stats/global', async (request, reply) => {
    try {
      const query = `
        SELECT 
          COUNT(*) as total_lives,
          COUNT(CASE WHEN alive = TRUE THEN 1 END) as active_lives,
          COUNT(CASE WHEN alive = FALSE THEN 1 END) as completed_lives,
          AVG(CASE WHEN alive = FALSE THEN current_age END) as avg_lifespan
        FROM lives
      `;
      
      const result = await lifeService.db.query(query);
      
      return {
        success: true,
        stats: result.rows[0]
      };
    } catch (error) {
      reply.code(500);
      return { success: false, error: error.message };
    }
  });
}

module.exports = lifeRoutes;
