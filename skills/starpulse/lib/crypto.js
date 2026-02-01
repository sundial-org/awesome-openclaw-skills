import nacl from 'tweetnacl';
import { createHash } from 'crypto';

/**
 * Hash an event to get its ID
 */
export function hashEvent(event) {
  const serialized = JSON.stringify([
    0,
    event.pubkey,
    event.created_at,
    event.kind,
    event.tags || [],
    event.content || ''
  ]);
  
  return createHash('sha256').update(serialized).digest('hex');
}

/**
 * Generate a new keypair
 */
export function generateKeypair() {
  const keypair = nacl.sign.keyPair();
  return {
    publicKey: bytesToHex(keypair.publicKey),
    secretKey: bytesToHex(keypair.secretKey)
  };
}

/**
 * Sign an event
 */
export function signEvent(event, secretKeyHex) {
  const id = hashEvent(event);
  const secretKey = hexToBytes(secretKeyHex);
  const message = new TextEncoder().encode(id);
  const sig = nacl.sign.detached(message, secretKey);
  
  return {
    ...event,
    id,
    sig: bytesToHex(sig)
  };
}

function hexToBytes(hex) {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
  }
  return bytes;
}

function bytesToHex(bytes) {
  return Array.from(bytes)
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}
