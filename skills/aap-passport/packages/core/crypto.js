/**
 * @aap/core - Cryptographic utilities
 * 
 * Core cryptographic functions for Agent Attestation Protocol.
 * Uses secp256k1 (same as Bitcoin/Ethereum) for compatibility.
 */

import { 
  generateKeyPairSync, 
  createSign, 
  createVerify, 
  createHash,
  randomBytes,
  timingSafeEqual
} from 'node:crypto';

/**
 * Generate a new secp256k1 key pair
 * @returns {Object} { publicKey, privateKey } in PEM format
 */
export function generateKeyPair() {
  const { publicKey, privateKey } = generateKeyPairSync('ec', {
    namedCurve: 'secp256k1',
    publicKeyEncoding: {
      type: 'spki',
      format: 'pem'
    },
    privateKeyEncoding: {
      type: 'pkcs8',
      format: 'pem'
    }
  });
  
  return { publicKey, privateKey };
}

/**
 * Derive a short public ID from a public key
 * @param {string} publicKey - PEM-encoded public key
 * @returns {string} 20-character hex identifier
 */
export function derivePublicId(publicKey) {
  const hash = createHash('sha256').update(publicKey).digest('hex');
  return hash.slice(0, 20);
}

/**
 * Sign data with a private key
 * @param {string} data - Data to sign
 * @param {string} privateKey - PEM-encoded private key
 * @returns {string} Base64-encoded signature
 */
export function sign(data, privateKey) {
  const signer = createSign('SHA256');
  signer.update(data);
  signer.end();
  return signer.sign(privateKey, 'base64');
}

/**
 * Verify a signature
 * @param {string} data - Original data
 * @param {string} signature - Base64-encoded signature
 * @param {string} publicKey - PEM-encoded public key
 * @returns {boolean} True if valid
 */
export function verify(data, signature, publicKey) {
  try {
    const verifier = createVerify('SHA256');
    verifier.update(data);
    verifier.end();
    return verifier.verify(publicKey, signature, 'base64');
  } catch (error) {
    return false;
  }
}

/**
 * Generate a cryptographically secure nonce
 * @param {number} [bytes=16] - Number of random bytes
 * @returns {string} Hex-encoded nonce
 */
export function generateNonce(bytes = 16) {
  return randomBytes(bytes).toString('hex');
}

/**
 * Timing-safe comparison of two strings
 * Prevents timing attacks on token comparison
 * @param {string} a - First string
 * @param {string} b - Second string
 * @returns {boolean} True if equal
 */
export function safeCompare(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string') {
    return false;
  }
  
  const bufA = Buffer.from(a);
  const bufB = Buffer.from(b);
  
  if (bufA.length !== bufB.length) {
    return false;
  }
  
  return timingSafeEqual(bufA, bufB);
}

/**
 * Create the canonical proof data object for signing/verification
 * @param {Object} params
 * @param {string} params.nonce - Challenge nonce
 * @param {string} params.solution - Agent's solution
 * @param {string} params.publicId - Agent's public ID
 * @param {number} params.timestamp - Unix timestamp in ms
 * @returns {string} JSON string for signing
 */
export function createProofData({ nonce, solution, publicId, timestamp }) {
  return JSON.stringify({ nonce, solution, publicId, timestamp });
}

export default {
  generateKeyPair,
  derivePublicId,
  sign,
  verify,
  generateNonce,
  safeCompare,
  createProofData
};
