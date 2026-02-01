const crypto = require('crypto');

/**
 * Generate a challenge message for wallet signature verification
 * @param {string} address - Chia wallet address
 * @param {string} userId - Telegram user ID or identifier
 * @returns {object} - Challenge data with message, nonce, and timestamp
 */
function generateChallenge(address, userId = 'unknown') {
  const timestamp = Date.now();
  const nonce = crypto.randomBytes(16).toString('hex');
  
  const message = `Verify ownership of Chia wallet:\n${address}\n\nTimestamp: ${timestamp}\nNonce: ${nonce}\nUser: ${userId}`;
  
  return {
    message,
    nonce,
    timestamp,
    address,
    userId
  };
}

/**
 * Validate that a challenge is recent (within 5 minutes)
 * @param {number} timestamp - Challenge timestamp
 * @returns {boolean} - True if valid
 */
function validateChallengeTimestamp(timestamp) {
  const now = Date.now();
  const fiveMinutes = 5 * 60 * 1000;
  
  return (now - timestamp) < fiveMinutes;
}

/**
 * Create a simple challenge for testing
 * @param {string} address - Chia wallet address
 * @returns {string} - Simple challenge message
 */
function createSimpleChallenge(address) {
  const timestamp = new Date().toISOString();
  return `Sign this message to verify ownership of ${address} at ${timestamp}`;
}

module.exports = {
  generateChallenge,
  validateChallengeTimestamp,
  createSimpleChallenge
};
