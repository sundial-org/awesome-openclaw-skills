const fetch = require('node-fetch');

const MINTGARDEN_API = 'https://api.mintgarden.io';

/**
 * Verify a Chia wallet signature using MintGarden API
 * @param {string} address - Chia wallet address
 * @param {string} message - Original message that was signed
 * @param {string} signature - Signature from wallet
 * @param {string} publicKey - Public key from wallet
 * @returns {Promise<object>} - Verification result
 */
async function verifySignature(address, message, signature, publicKey) {
  try {
    const response = await fetch(`${MINTGARDEN_API}/address/verify_signature`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        address,
        message,
        signature,
        pubkey: publicKey
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`MintGarden API error: ${response.status} - ${errorText}`);
    }

    const result = await response.json();
    
    return {
      verified: result.verified === true,
      address,
      message,
      timestamp: Date.now(),
      ...result
    };
  } catch (error) {
    console.error('❌ Signature verification failed:', error);
    return {
      verified: false,
      error: error.message,
      address,
      message
    };
  }
}

/**
 * Check if an address is valid Chia format
 * @param {string} address - Address to validate
 * @returns {boolean} - True if valid format
 */
function isValidChiaAddress(address) {
  // Chia addresses start with 'xch' and are 62 characters long
  const chiaAddressRegex = /^xch1[a-z0-9]{59}$/;
  return chiaAddressRegex.test(address);
}

module.exports = {
  verifySignature,
  isValidChiaAddress
};
