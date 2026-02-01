const fastify = require('fastify')({ logger: true });
const path = require('path');
require('dotenv').config();

const { LifeService } = require('./src/services/lifeService');
const { TelegramBot } = require('./src/services/telegramBot');

// Register plugins
fastify.register(require('@fastify/cors'), {
  origin: true,
  credentials: true
});

// Initialize life service
const lifeService = new LifeService(fastify.pg);

// Health check
fastify.get('/health', async () => {
  return { 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    features: ['private_mode', 'story_generation', 'telegram_bot']
  };
});

// API Routes
fastify.register(require('./src/routes/life'), { 
  prefix: '/api/life',
  lifeService 
});

fastify.register(require('./src/routes/payment'), { 
  prefix: '/api/payment' 
});

fastify.register(require('./src/routes/moltbook'), { 
  prefix: '/api/moltbook',
  lifeService 
});

// Start server
const start = async () => {
  try {
    // Check for required env vars
    const required = ['GEMINI_API_KEY', 'DATABASE_URL'];
    const missing = required.filter(key => !process.env[key]);
    
    if (missing.length > 0) {
      console.error('❌ Missing required environment variables:', missing.join(', '));
      console.error('Copy .env.example to .env and fill in the values');
      process.exit(1);
    }
    
    // Start HTTP server
    await fastify.listen({ 
      port: process.env.PORT || 3000, 
      host: '0.0.0.0' 
    });
    
    fastify.log.info(`🚀 LifePath API server listening on port ${process.env.PORT || 3000}`);
    
    // Start Telegram bot if token provided
    if (process.env.TELEGRAM_BOT_TOKEN) {
      const bot = new TelegramBot(fastify.pg);
      bot.launch();
      fastify.log.info('🤖 Telegram bot started');
    } else {
      fastify.log.warn('⚠️  TELEGRAM_BOT_TOKEN not set - bot will not start');
    }
    
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Shutting down gracefully...');
  await fastify.close();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n🛑 Shutting down gracefully...');
  await fastify.close();
  process.exit(0);
});

start();
