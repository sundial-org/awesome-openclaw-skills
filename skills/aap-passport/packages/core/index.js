/**
 * @aap/core
 * 
 * Core utilities for Agent Attestation Protocol.
 * Provides cryptographic primitives and identity management.
 */

export * from './crypto.js';
export * from './identity.js';

// Re-export defaults
import crypto from './crypto.js';
import identity from './identity.js';

export { crypto, identity };

// Protocol constants (v2.5.0)
export const PROTOCOL_VERSION = '2.5.0';
export const DEFAULT_CHALLENGE_EXPIRY_MS = 60000;
export const DEFAULT_MAX_RESPONSE_TIME_MS = 8000;
export const NONCE_BYTES = 16;
export const BATCH_SIZE = 5;

// Challenge types (v2.5)
export const CHALLENGE_TYPES = [
  'nlp_math', 'nlp_logic', 'nlp_extract', 'nlp_count',
  'nlp_transform', 'nlp_multistep', 'nlp_pattern', 'nlp_analysis'
];

export default {
  ...crypto,
  ...identity,
  PROTOCOL_VERSION,
  DEFAULT_CHALLENGE_EXPIRY_MS,
  DEFAULT_MAX_RESPONSE_TIME_MS,
  NONCE_BYTES,
  CHALLENGE_TYPES
};
