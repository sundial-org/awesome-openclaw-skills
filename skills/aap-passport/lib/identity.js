/**
 * AAP Identity v2.5
 * 
 * Manages cryptographic identity for AI agents.
 * Uses secp256k1 (same as Bitcoin/Ethereum).
 */

import { generateKeyPairSync, createSign, createVerify, createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, writeFileSync, chmodSync, unlinkSync } from 'node:fs';
import { join } from 'node:path';
import { homedir } from 'node:os';

const DEFAULT_PATH = join(homedir(), '.aap', 'identity.json');

let cachedIdentity = null;

/**
 * Get identity storage path
 * @returns {string}
 */
function getStoragePath() {
  return process.env.AAP_IDENTITY_PATH || DEFAULT_PATH;
}

/**
 * Check if identity exists, create if not
 */
export function checkAndCreate() {
  const path = getStoragePath();
  
  if (existsSync(path)) {
    console.log('[AAP] Identity found at', path);
    loadIdentity();
    return;
  }
  
  console.log('[AAP] Creating new identity...');
  createIdentity();
}

/**
 * Create new identity
 */
function createIdentity() {
  const path = getStoragePath();
  const dir = join(path, '..');
  
  // Ensure directory exists
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
  
  // Generate key pair
  const { publicKey, privateKey } = generateKeyPairSync('ec', {
    namedCurve: 'secp256k1',
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  
  // Derive public ID
  const publicId = createHash('sha256')
    .update(publicKey)
    .digest('hex')
    .slice(0, 20);
  
  const identity = {
    publicKey,
    privateKey,
    publicId,
    createdAt: new Date().toISOString(),
    protocol: 'AAP',
    version: '2.5.0'
  };
  
  // Save with restricted permissions
  writeFileSync(path, JSON.stringify(identity, null, 2));
  
  try {
    chmodSync(path, 0o600);
  } catch (error) {
    console.warn('[AAP] Warning: Could not set file permissions:', error.message);
    console.warn('[AAP] Please manually secure:', path);
  }
  
  cachedIdentity = identity;
  console.log('[AAP] Identity created:', publicId);
}

/**
 * Load existing identity
 */
function loadIdentity() {
  const path = getStoragePath();
  
  try {
    const data = readFileSync(path, 'utf8');
    cachedIdentity = JSON.parse(data);
  } catch (error) {
    console.error('[AAP] Failed to load identity:', error.message);
    cachedIdentity = null;
  }
}

/**
 * Get public identity (safe to share)
 * @returns {Object|null}
 */
export function getPublicIdentity() {
  if (!cachedIdentity) {
    loadIdentity();
  }
  
  if (!cachedIdentity) {
    return null;
  }
  
  return {
    publicKey: cachedIdentity.publicKey,
    publicId: cachedIdentity.publicId,
    createdAt: cachedIdentity.createdAt,
    protocol: cachedIdentity.protocol,
    version: cachedIdentity.version
  };
}

/**
 * Get private key (internal use only)
 * @returns {string|null}
 */
export function getPrivateKey() {
  if (!cachedIdentity) {
    loadIdentity();
  }
  
  return cachedIdentity?.privateKey || null;
}

/**
 * Sign data with private key
 * @param {string} data - Data to sign
 * @returns {string} Base64 signature
 */
export function sign(data) {
  const privateKey = getPrivateKey();
  
  if (!privateKey) {
    throw new Error('Identity not initialized');
  }
  
  const signer = createSign('SHA256');
  signer.update(data);
  return signer.sign(privateKey, 'base64');
}

/**
 * Verify a signature
 * @param {string} data - Original data
 * @param {string} signature - Base64 signature
 * @param {string} publicKey - PEM public key
 * @returns {{valid: boolean, error?: string}}
 */
export function verify(data, signature, publicKey) {
  try {
    const verifier = createVerify('SHA256');
    verifier.update(data);
    const valid = verifier.verify(publicKey, signature, 'base64');
    return { valid, error: valid ? undefined : 'Signature mismatch' };
  } catch (error) {
    const errorType = error.message.includes('key') ? 'Invalid public key format' 
      : error.message.includes('signature') ? 'Invalid signature format'
      : error.message;
    console.error('[AAP] Verification error:', errorType);
    return { valid: false, error: errorType };
  }
}

/**
 * Verify a signature (simple boolean version for compatibility)
 * @param {string} data - Original data
 * @param {string} signature - Base64 signature
 * @param {string} publicKey - PEM public key
 * @returns {boolean}
 */
export function verifySimple(data, signature, publicKey) {
  return verify(data, signature, publicKey).valid;
}

/**
 * Check if identity exists
 * @returns {boolean}
 */
export function exists() {
  return existsSync(getStoragePath());
}

/**
 * Delete identity (use with caution!)
 */
export function deleteIdentity() {
  const path = getStoragePath();
  if (existsSync(path)) {
    unlinkSync(path);
    cachedIdentity = null;
    console.log('[AAP] Identity deleted');
  }
}

export default {
  checkAndCreate,
  getPublicIdentity,
  getPrivateKey,
  sign,
  verify,
  exists,
  deleteIdentity
};
