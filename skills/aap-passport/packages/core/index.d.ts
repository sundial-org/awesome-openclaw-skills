/**
 * AAP Core - TypeScript Definitions v2.5.0
 */

// ============== Constants ==============

export const PROTOCOL_VERSION: '2.5.0';
export const CHALLENGE_EXPIRY_MS: 60000;
export const MAX_RESPONSE_TIME_MS: 8000;
export const BATCH_SIZE: 5;
export const NONCE_BYTES: 16;
export const NONCE_LENGTH: 32;
export const SALT_LENGTH: 6;
export const PUBLIC_ID_LENGTH: 20;
export const SIGNATURE_MIN_LENGTH: 50;
export const MAX_CHALLENGES_STORED: 10000;

export const CHALLENGE_TYPES: [
  'nlp_math', 'nlp_logic', 'nlp_extract', 'nlp_count',
  'nlp_transform', 'nlp_multistep', 'nlp_pattern', 'nlp_analysis'
];

// ============== Crypto ==============

export interface KeyPair {
  publicKey: string;
  privateKey: string;
}

export function generateKeyPair(): KeyPair;
export function derivePublicId(publicKey: string): string;
export function sign(data: string, privateKey: string): string;
export function verify(data: string, signature: string, publicKey: string): boolean;
export function generateNonce(bytes?: number): string;
export function safeCompare(a: string, b: string): boolean;

export interface ProofDataParams {
  nonce: string;
  solution: string;
  publicId: string;
  timestamp: number;
}

export function createProofData(params: ProofDataParams): string;

// ============== Identity ==============

export interface IdentityOptions {
  storagePath?: string;
}

export interface PublicIdentity {
  publicKey: string;
  publicId: string;
  createdAt: string;
  protocol: 'AAP';
  version: '2.5.0';
}

export class Identity {
  constructor(options?: IdentityOptions);
  init(): PublicIdentity;
  getPublic(): PublicIdentity;
  sign(data: string): string;
  exists(): boolean;
  delete(): void;
  static verify(data: string, signature: string, publicKey: string): boolean;
}

export function getDefaultIdentity(options?: IdentityOptions): Identity;

export default {
  generateKeyPair: typeof generateKeyPair;
  derivePublicId: typeof derivePublicId;
  sign: typeof sign;
  verify: typeof verify;
  generateNonce: typeof generateNonce;
  createProofData: typeof createProofData;
  Identity: typeof Identity;
  PROTOCOL_VERSION: typeof PROTOCOL_VERSION;
  CHALLENGE_EXPIRY_MS: typeof CHALLENGE_EXPIRY_MS;
  MAX_RESPONSE_TIME_MS: typeof MAX_RESPONSE_TIME_MS;
  BATCH_SIZE: typeof BATCH_SIZE;
  CHALLENGE_TYPES: typeof CHALLENGE_TYPES;
};
