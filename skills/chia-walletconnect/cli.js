#!/usr/bin/env node

const { generateChallenge, createSimpleChallenge } = require('./lib/challenge');
const { verifySignature, isValidChiaAddress } = require('./lib/verify');

/**
 * CLI for Chia Wallet Verification
 */

const args = process.argv.slice(2);
const command = args[0];

async function main() {
  switch (command) {
    case 'challenge':
      handleChallenge(args.slice(1));
      break;
    
    case 'verify':
      await handleVerify(args.slice(1));
      break;
    
    case 'validate':
      handleValidate(args.slice(1));
      break;
    
    case 'server':
      handleServer();
      break;
    
    case 'help':
    case '--help':
    case '-h':
    default:
      showHelp();
      break;
  }
}

/**
 * Generate a challenge message
 */
function handleChallenge(args) {
  const address = args[0];
  const userId = args[1] || 'cli_user';
  
  if (!address) {
    console.error('❌ Error: Address required');
    console.log('\nUsage: chia-wallet challenge <address> [userId]');
    process.exit(1);
  }
  
  if (!isValidChiaAddress(address)) {
    console.error('❌ Error: Invalid Chia address format');
    console.log('Expected format: xch1...');
    process.exit(1);
  }
  
  const challenge = generateChallenge(address, userId);
  
  console.log('📝 Challenge Generated\n');
  console.log('Message to sign:');
  console.log('─'.repeat(50));
  console.log(challenge.message);
  console.log('─'.repeat(50));
  console.log('\nChallenge Data:');
  console.log(JSON.stringify(challenge, null, 2));
}

/**
 * Verify a signature
 */
async function handleVerify(args) {
  const address = args[0];
  const message = args[1];
  const signature = args[2];
  const publicKey = args[3];
  
  if (!address || !message || !signature) {
    console.error('❌ Error: Missing required arguments');
    console.log('\nUsage: chia-wallet verify <address> <message> <signature> [publicKey]');
    process.exit(1);
  }
  
  console.log('🔐 Verifying signature...\n');
  console.log(`Address:   ${address}`);
  console.log(`Message:   ${message.substring(0, 50)}...`);
  console.log(`Signature: ${signature.substring(0, 50)}...`);
  if (publicKey) {
    console.log(`PubKey:    ${publicKey.substring(0, 50)}...`);
  }
  console.log();
  
  const result = await verifySignature(address, message, signature, publicKey);
  
  if (result.verified) {
    console.log('✅ Signature verified successfully!\n');
    console.log('Verification Details:');
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log('❌ Signature verification failed!\n');
    console.log('Error:', result.error);
  }
}

/**
 * Validate address format
 */
function handleValidate(args) {
  const address = args[0];
  
  if (!address) {
    console.error('❌ Error: Address required');
    console.log('\nUsage: chia-wallet validate <address>');
    process.exit(1);
  }
  
  const isValid = isValidChiaAddress(address);
  
  if (isValid) {
    console.log(`✅ Valid Chia address: ${address}`);
  } else {
    console.log(`❌ Invalid Chia address: ${address}`);
    console.log('\nExpected format: xch1 followed by 59 lowercase alphanumeric characters');
  }
}

/**
 * Start the web server
 */
function handleServer() {
  console.log('🚀 Starting Chia WalletConnect server...\n');
  require('./server/index.js');
}

/**
 * Show help
 */
function showHelp() {
  console.log(`
🌱 Chia Wallet Verification CLI

USAGE:
  chia-wallet <command> [options]

COMMANDS:
  challenge <address> [userId]         Generate a challenge message
  verify <addr> <msg> <sig> [pubkey]   Verify a signature
  validate <address>                   Validate Chia address format
  server                               Start the web server
  help                                 Show this help message

EXAMPLES:
  # Generate challenge
  chia-wallet challenge xch1abc... user123

  # Verify signature
  chia-wallet verify xch1abc... "message" "signature" "pubkey"

  # Validate address
  chia-wallet validate xch1abc...

  # Start server
  chia-wallet server

TELEGRAM INTEGRATION:
  1. Deploy the web app to a public URL (Vercel, Netlify, etc.)
  2. Register the URL with BotFather as a Web App
  3. Send inline keyboard button to launch the app
  4. Handle web_app_data callback in your bot

For more info, see README.md
  `);
}

// Run CLI
main().catch(error => {
  console.error('❌ Fatal error:', error.message);
  process.exit(1);
});
