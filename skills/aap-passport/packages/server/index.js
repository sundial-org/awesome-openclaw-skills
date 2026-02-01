/**
 * @aap/server v3.0.0
 * 
 * WebSocket-only Agent Attestation Protocol.
 * Sequential challenges - no preview, no mercy.
 */

// Core WebSocket server
export { createAAPWebSocket } from './websocket.js';

// Challenge generation (internal use)
export { 
  generate, 
  generateBatch, 
  validateBatch, 
  getTypes,
  BATCH_SIZE,
  CHALLENGE_TYPES
} from './challenges.js';

// Optional utilities
export { createWhitelist, createKeyRotation } from './whitelist.js';
export { createStore, createMemoryStore, createFileStore, createRedisStore } from './persistence.js';
export * as logger from './logger.js';

// Constants
export const PROTOCOL_VERSION = '3.2.0';
export const TOTAL_TIME_MS = 6000;
export const CHALLENGE_COUNT = 7;
export const CONNECTION_TIMEOUT_MS = 60000;

import { createAAPWebSocket } from './websocket.js';

export default {
  createAAPWebSocket,
  PROTOCOL_VERSION,
  TOTAL_TIME_MS,
  CHALLENGE_COUNT
};
