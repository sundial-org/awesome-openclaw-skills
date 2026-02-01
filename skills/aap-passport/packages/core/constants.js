/**
 * AAP Constants
 * 
 * Centralized constants to avoid magic numbers
 */

// Protocol
export const PROTOCOL_VERSION = '2.6.0';
export const PROTOCOL_NAME = 'AAP';

// Timing
export const CHALLENGE_EXPIRY_MS = 60000;      // 60 seconds
export const MAX_RESPONSE_TIME_MS = 6000;      // 6 seconds (v2.6: 8s → 6s)
export const FETCH_TIMEOUT_MS = 30000;         // 30 seconds

// Batch
export const BATCH_SIZE = 7;                   // v2.6: 5 → 7 challenges
export const MIN_PASS_COUNT = 7;               // All must pass by default

// Crypto
export const NONCE_BYTES = 16;
export const NONCE_LENGTH = 32;                // Hex string length
export const SALT_LENGTH = 6;
export const PUBLIC_ID_LENGTH = 20;
export const SIGNATURE_MIN_LENGTH = 50;

// Seeded random helpers
export const SEED_OFFSET_MULTIPLIER = 7;       // Used in seededSelect
export const SEED_HEX_SLICE = 4;               // nonce.slice(offset, offset + 4)

// Security
export const MAX_CHALLENGES_STORED = 10000;    // DoS protection
export const MAX_BODY_SIZE = '10kb';
export const RATE_LIMIT_WINDOW_MS = 60000;
export const RATE_LIMIT_MAX_REQUESTS = 10;
export const RATE_LIMIT_MAX_FAILURES = 5;

// Challenge types
export const CHALLENGE_TYPES = [
  'nlp_math',
  'nlp_logic', 
  'nlp_extract',
  'nlp_count',
  'nlp_transform',
  'nlp_multistep',
  'nlp_pattern',
  'nlp_analysis'
];

// Key format markers
export const PUBLIC_KEY_MARKER = 'BEGIN PUBLIC KEY';
export const PRIVATE_KEY_MARKER = 'BEGIN PRIVATE KEY';

// Default paths
export const DEFAULT_IDENTITY_PATH = '.aap/identity.json';

export default {
  PROTOCOL_VERSION,
  PROTOCOL_NAME,
  CHALLENGE_EXPIRY_MS,
  MAX_RESPONSE_TIME_MS,
  FETCH_TIMEOUT_MS,
  BATCH_SIZE,
  MIN_PASS_COUNT,
  NONCE_BYTES,
  NONCE_LENGTH,
  SALT_LENGTH,
  PUBLIC_ID_LENGTH,
  SIGNATURE_MIN_LENGTH,
  SEED_OFFSET_MULTIPLIER,
  SEED_HEX_SLICE,
  MAX_CHALLENGES_STORED,
  MAX_BODY_SIZE,
  RATE_LIMIT_WINDOW_MS,
  RATE_LIMIT_MAX_REQUESTS,
  RATE_LIMIT_MAX_FAILURES,
  CHALLENGE_TYPES,
  PUBLIC_KEY_MARKER,
  PRIVATE_KEY_MARKER,
  DEFAULT_IDENTITY_PATH
};
