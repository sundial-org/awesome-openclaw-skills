/**
 * @aap/core - Identity Management
 * 
 * Manages agent identity (key generation, storage, signing).
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, dirname } from 'node:path';
import { generateKeyPair, derivePublicId, sign as cryptoSign, verify as cryptoVerify } from './crypto.js';

/**
 * Identity manager class
 */
export class Identity {
  constructor(options = {}) {
    this.storagePath = options.storagePath || join(homedir(), '.aap', 'identity.json');
    this.identity = null;
  }

  /**
   * Initialize identity (load existing or generate new)
   * @returns {Object} Public identity info
   */
  init() {
    if (this.identity) {
      return this.getPublic();
    }

    // Ensure directory exists
    const dir = dirname(this.storagePath);
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }

    // Load existing identity
    if (existsSync(this.storagePath)) {
      try {
        const data = readFileSync(this.storagePath, 'utf8');
        this.identity = JSON.parse(data);
        return this.getPublic();
      } catch (error) {
        console.error('[AAP] Failed to load identity:', error.message);
      }
    }

    // Generate new identity
    const { publicKey, privateKey } = generateKeyPair();
    const publicId = derivePublicId(publicKey);

    this.identity = {
      publicKey,
      privateKey,
      publicId,
      createdAt: new Date().toISOString(),
      protocol: 'AAP',
      version: '1.0.0'
    };

    // Save to file with secure permissions
    writeFileSync(this.storagePath, JSON.stringify(this.identity, null, 2), {
      mode: 0o600
    });

    return this.getPublic();
  }

  /**
   * Get public identity (safe to share)
   * @returns {Object} Public identity without private key
   */
  getPublic() {
    if (!this.identity) {
      this.init();
    }

    return {
      publicKey: this.identity.publicKey,
      publicId: this.identity.publicId,
      createdAt: this.identity.createdAt,
      protocol: this.identity.protocol,
      version: this.identity.version
    };
  }

  /**
   * Sign data with the identity's private key
   * @param {string} data - Data to sign
   * @returns {string} Base64-encoded signature
   */
  sign(data) {
    if (!this.identity) {
      this.init();
    }
    return cryptoSign(data, this.identity.privateKey);
  }

  /**
   * Verify a signature (static method for verifying others)
   * @param {string} data - Original data
   * @param {string} signature - Signature to verify
   * @param {string} publicKey - Public key of signer
   * @returns {boolean} True if valid
   */
  static verify(data, signature, publicKey) {
    return cryptoVerify(data, signature, publicKey);
  }

  /**
   * Check if identity exists
   * @returns {boolean}
   */
  exists() {
    return existsSync(this.storagePath);
  }

  /**
   * Delete identity (for testing)
   */
  delete() {
    if (existsSync(this.storagePath)) {
      const { unlinkSync } = require('node:fs');
      unlinkSync(this.storagePath);
    }
    this.identity = null;
  }
}

// Default instance
let defaultIdentity = null;

/**
 * Get or create the default identity instance
 * @param {Object} [options] - Options for new instance
 * @returns {Identity}
 */
export function getDefaultIdentity(options) {
  if (!defaultIdentity) {
    defaultIdentity = new Identity(options);
  }
  return defaultIdentity;
}

export default { Identity, getDefaultIdentity };
