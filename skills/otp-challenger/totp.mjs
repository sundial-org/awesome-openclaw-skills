#!/usr/bin/env node

/**
 * TOTP CLI - Standalone Time-based One-Time Password tool
 * 
 * Commands:
 *   totp generate [account] [issuer]  - Generate a new TOTP secret
 *   totp validate <secret> <code>     - Validate a TOTP code
 *   totp uri <secret> <account> [issuer] - Generate otpauth:// URI
 * 
 * Examples:
 *   totp generate user@example.com MyApp
 *   totp validate JBSWY3DPEHPK3PXP 123456
 *   totp uri JBSWY3DPEHPK3PXP user@example.com MyApp
 */

import { TOTP, Secret } from 'otpauth';
import { createHash, randomBytes } from 'crypto';

const [,, command, ...args] = process.argv;

function printUsage() {
  console.log(`
TOTP CLI - Time-based One-Time Password tool

Usage:
  totp generate [account] [issuer]     Generate a new TOTP secret
  totp validate <secret> <code>        Validate a TOTP code
  totp uri <secret> <account> [issuer] Generate otpauth:// URI
  totp current <secret>                Get current valid code

Examples:
  totp generate user@example.com MyApp
  totp validate JBSWY3DPEHPK3PXP 123456
  totp uri JBSWY3DPEHPK3PXP user@example.com MyApp
  totp current JBSWY3DPEHPK3PXP
`);
}

function generateSecret(account = 'user', issuer = 'TOTP') {
  // Generate random secret (otpauth library handles this)
  const secret = new Secret({ size: 20 });
  
  const totp = new TOTP({
    issuer,
    label: account,
    algorithm: 'SHA1',
    digits: 6,
    period: 30,
    secret
  });

  console.log(JSON.stringify({
    secret: secret.base32,
    account,
    issuer,
    uri: totp.toString()
  }, null, 2));
}

function validateCode(secretBase32, code) {
  try {
    const secret = Secret.fromBase32(secretBase32);
    const totp = new TOTP({
      algorithm: 'SHA1',
      digits: 6,
      period: 30,
      secret
    });

    // Validate with 1 period window (±30s tolerance)
    const delta = totp.validate({ token: code, window: 1 });
    
    if (delta !== null) {
      console.log('VALID');
      process.exit(0);
    } else {
      console.log('INVALID');
      process.exit(1);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(2);
  }
}

function generateUri(secretBase32, account, issuer = 'TOTP') {
  try {
    const secret = Secret.fromBase32(secretBase32);
    const totp = new TOTP({
      issuer,
      label: account,
      algorithm: 'SHA1',
      digits: 6,
      period: 30,
      secret
    });

    console.log(totp.toString());
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(2);
  }
}

function getCurrentCode(secretBase32) {
  try {
    const secret = Secret.fromBase32(secretBase32);
    const totp = new TOTP({
      algorithm: 'SHA1',
      digits: 6,
      period: 30,
      secret
    });

    const code = totp.generate();
    console.log(code);
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(2);
  }
}

// Main command router
switch (command) {
  case 'generate':
    generateSecret(args[0], args[1]);
    break;
  
  case 'validate':
    if (args.length < 2) {
      console.error('Error: validate requires <secret> <code>');
      process.exit(2);
    }
    validateCode(args[0], args[1]);
    break;
  
  case 'uri':
    if (args.length < 2) {
      console.error('Error: uri requires <secret> <account> [issuer]');
      process.exit(2);
    }
    generateUri(args[0], args[1], args[2]);
    break;
  
  case 'current':
    if (args.length < 1) {
      console.error('Error: current requires <secret>');
      process.exit(2);
    }
    getCurrentCode(args[0]);
    break;
  
  case 'help':
  case '--help':
  case '-h':
  case undefined:
    printUsage();
    break;
  
  default:
    console.error(`Unknown command: ${command}`);
    printUsage();
    process.exit(2);
}
