/**
 * AAP Challenge Persistence
 * 
 * Optional: Persist challenges to survive server restarts
 * Supports: Memory (default), File, Redis
 */

import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';

/**
 * Create in-memory store (default, no persistence)
 */
export function createMemoryStore() {
  const challenges = new Map();

  return {
    type: 'memory',
    
    async get(nonce) {
      return challenges.get(nonce) || null;
    },

    async set(nonce, data) {
      challenges.set(nonce, data);
    },

    async delete(nonce) {
      challenges.delete(nonce);
    },

    async has(nonce) {
      return challenges.has(nonce);
    },

    async size() {
      return challenges.size;
    },

    async keys() {
      return [...challenges.keys()];
    },

    async clear() {
      challenges.clear();
    },

    async cleanup(now = Date.now()) {
      for (const [nonce, data] of challenges.entries()) {
        if (now > data.expiresAt) {
          challenges.delete(nonce);
        }
      }
    }
  };
}

/**
 * Create file-based store (survives restarts)
 * @param {string} filePath - Path to store file
 */
export function createFileStore(filePath = '.aap/challenges.json') {
  const fullPath = join(process.cwd(), filePath);
  let challenges = new Map();

  // Load existing data
  try {
    if (existsSync(fullPath)) {
      const data = JSON.parse(readFileSync(fullPath, 'utf8'));
      challenges = new Map(Object.entries(data));
      console.log(`[AAP] Loaded ${challenges.size} challenges from ${fullPath}`);
    }
  } catch (error) {
    console.warn('[AAP] Could not load challenges:', error.message);
  }

  // Save to file
  const save = () => {
    try {
      const dir = dirname(fullPath);
      if (!existsSync(dir)) {
        mkdirSync(dir, { recursive: true });
      }
      
      const data = Object.fromEntries(challenges);
      // Remove validator functions (not serializable)
      for (const key of Object.keys(data)) {
        delete data[key].validators;
      }
      
      writeFileSync(fullPath, JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('[AAP] Could not save challenges:', error.message);
    }
  };

  // Auto-save periodically
  const saveInterval = setInterval(save, 30000);

  return {
    type: 'file',
    
    async get(nonce) {
      return challenges.get(nonce) || null;
    },

    async set(nonce, data) {
      challenges.set(nonce, data);
      save();
    },

    async delete(nonce) {
      challenges.delete(nonce);
      save();
    },

    async has(nonce) {
      return challenges.has(nonce);
    },

    async size() {
      return challenges.size;
    },

    async keys() {
      return [...challenges.keys()];
    },

    async clear() {
      challenges.clear();
      save();
    },

    async cleanup(now = Date.now()) {
      let cleaned = 0;
      for (const [nonce, data] of challenges.entries()) {
        if (now > data.expiresAt) {
          challenges.delete(nonce);
          cleaned++;
        }
      }
      if (cleaned > 0) save();
      return cleaned;
    },

    close() {
      clearInterval(saveInterval);
      save();
    }
  };
}

/**
 * Create Redis-based store (for distributed deployments)
 * @param {Object} redisClient - Redis client instance (ioredis or redis)
 * @param {string} [prefix='aap:challenge:'] - Key prefix
 */
export function createRedisStore(redisClient, prefix = 'aap:challenge:') {
  return {
    type: 'redis',
    
    async get(nonce) {
      const data = await redisClient.get(prefix + nonce);
      return data ? JSON.parse(data) : null;
    },

    async set(nonce, data, ttlMs = 60000) {
      // Store without validators (not serializable)
      const { validators, ...storable } = data;
      await redisClient.set(
        prefix + nonce,
        JSON.stringify(storable),
        'PX',
        ttlMs
      );
    },

    async delete(nonce) {
      await redisClient.del(prefix + nonce);
    },

    async has(nonce) {
      return (await redisClient.exists(prefix + nonce)) === 1;
    },

    async size() {
      const keys = await redisClient.keys(prefix + '*');
      return keys.length;
    },

    async keys() {
      const keys = await redisClient.keys(prefix + '*');
      return keys.map(k => k.slice(prefix.length));
    },

    async clear() {
      const keys = await redisClient.keys(prefix + '*');
      if (keys.length > 0) {
        await redisClient.del(...keys);
      }
    },

    async cleanup() {
      // Redis handles TTL automatically
      return 0;
    }
  };
}

/**
 * Auto-detect and create appropriate store
 * @param {Object} options
 * @param {'memory'|'file'|'redis'} [options.type='memory']
 * @param {string} [options.filePath]
 * @param {Object} [options.redisClient]
 */
export function createStore(options = {}) {
  const { type = 'memory', filePath, redisClient } = options;

  switch (type) {
    case 'file':
      return createFileStore(filePath);
    case 'redis':
      if (!redisClient) {
        throw new Error('Redis client required for redis store');
      }
      return createRedisStore(redisClient);
    default:
      return createMemoryStore();
  }
}

export default {
  createMemoryStore,
  createFileStore,
  createRedisStore,
  createStore
};
