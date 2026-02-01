#!/usr/bin/env node
/**
 * Generate Apple Music Developer Token (JWT)
 * 
 * Usage: node generate-token.js <key-path> <key-id> <team-id> [expiry-days]
 * 
 * The token is signed with ES256 and valid for up to 6 months (180 days).
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

function base64UrlEncode(data) {
  return Buffer.from(data)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

function generateToken(keyPath, keyId, teamId, expiryDays = 180) {
  // Read the private key
  let privateKey;
  try {
    privateKey = fs.readFileSync(keyPath, 'utf8');
  } catch (err) {
    console.error(`Error: Could not read private key file: ${keyPath}`);
    console.error(err.message);
    process.exit(1);
  }

  // Validate expiry (max 6 months = ~180 days)
  if (expiryDays > 180) {
    console.error('Warning: Apple limits tokens to 6 months. Setting to 180 days.');
    expiryDays = 180;
  }

  const now = Math.floor(Date.now() / 1000);
  const expiry = now + (expiryDays * 24 * 60 * 60);

  // JWT Header
  const header = {
    alg: 'ES256',
    kid: keyId
  };

  // JWT Payload
  const payload = {
    iss: teamId,
    iat: now,
    exp: expiry
  };

  // Encode header and payload
  const headerEncoded = base64UrlEncode(JSON.stringify(header));
  const payloadEncoded = base64UrlEncode(JSON.stringify(payload));
  const signingInput = `${headerEncoded}.${payloadEncoded}`;

  // Sign with ES256
  let signature;
  try {
    const sign = crypto.createSign('SHA256');
    sign.update(signingInput);
    sign.end();
    
    // Get the DER signature
    const derSignature = sign.sign(privateKey);
    
    // Convert DER to raw r||s format for JWT
    // DER format: 0x30 [total-length] 0x02 [r-length] [r] 0x02 [s-length] [s]
    const rStart = 4;
    const rLength = derSignature[3];
    let r = derSignature.slice(rStart, rStart + rLength);
    
    const sStart = rStart + rLength + 2;
    const sLength = derSignature[rStart + rLength + 1];
    let s = derSignature.slice(sStart, sStart + sLength);
    
    // Remove leading zeros and pad to 32 bytes
    if (r.length > 32) r = r.slice(r.length - 32);
    if (s.length > 32) s = s.slice(s.length - 32);
    
    const rPadded = Buffer.concat([Buffer.alloc(32 - r.length), r]);
    const sPadded = Buffer.concat([Buffer.alloc(32 - s.length), s]);
    
    signature = base64UrlEncode(Buffer.concat([rPadded, sPadded]));
  } catch (err) {
    console.error('Error: Failed to sign token.');
    console.error('Make sure the .p8 file is a valid Apple private key.');
    console.error(err.message);
    process.exit(1);
  }

  const token = `${signingInput}.${signature}`;
  
  // Output just the token (for capture by shell script)
  console.log(token);
}

// Parse arguments
const args = process.argv.slice(2);

if (args.length < 3) {
  console.error('Usage: node generate-token.js <key-path> <key-id> <team-id> [expiry-days]');
  console.error('');
  console.error('Arguments:');
  console.error('  key-path    Path to your .p8 private key file');
  console.error('  key-id      The Key ID from Apple Developer portal');
  console.error('  team-id     Your Apple Developer Team ID');
  console.error('  expiry-days Days until expiration (default: 180, max: 180)');
  process.exit(1);
}

const [keyPath, keyId, teamId, expiryDays] = args;
generateToken(keyPath, keyId, teamId, parseInt(expiryDays) || 180);
