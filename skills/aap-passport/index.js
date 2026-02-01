/**
 * AAP Passport - Agent Attestation Protocol Skill v2.5
 * 
 * The Reverse Turing Test.
 * CAPTCHAs block bots. AAP blocks humans.
 * 
 * Features:
 * - Automatic identity generation (secp256k1 key pair)
 * - Batch challenge support (5 challenges, 8 seconds)
 * - Salt injection for anti-caching
 * - Full verification flow with HTTP client
 */

import * as identity from './lib/identity.js';
import * as prover from './lib/prover.js';
import * as client from './lib/client.js';

/**
 * Skill startup hook
 * Called automatically when the skill is loaded by Clawdbot
 */
export async function onStartup(context) {
  console.log('[AAP] Initializing Agent Attestation Protocol...');
  
  // Auto-generate identity if not exists
  identity.checkAndCreate();
  
  console.log('[AAP] Ready for verification challenges!');
}

/**
 * Tool: Get public identity information
 * Returns the agent's public key and ID (safe to share)
 */
export async function aap_get_identity() {
  const publicIdentity = identity.getPublicIdentity();
  
  if (!publicIdentity) {
    return {
      error: 'Identity not initialized. Please restart the bot.'
    };
  }
  
  return publicIdentity;
}

/**
 * Tool: Sign a message with the agent's private key
 * @param {Object} params
 * @param {string} params.message - Message to sign
 */
export async function aap_sign_message({ message }) {
  if (!message) {
    return { error: 'Message is required' };
  }
  
  const signature = identity.sign(message);
  const publicIdentity = identity.getPublicIdentity();
  
  return {
    message,
    signature,
    publicId: publicIdentity.publicId,
    timestamp: Date.now()
  };
}

/**
 * Tool: Generate a complete AAP proof for a server challenge
 * Supports both single and batch challenges
 * 
 * @param {Object} params
 * @param {string} [params.challenge_string] - Single challenge prompt
 * @param {string} params.nonce - Server-provided nonce
 * @param {string} [params.type] - Challenge type
 * @param {string|Array} [params.solution] - Pre-generated solution(s)
 * @param {Array} [params.challenges] - Batch challenges array
 */
export async function aap_generate_proof({ challenge_string, nonce, type, solution, challenges }) {
  if (!nonce) {
    return { error: 'nonce is required' };
  }
  
  // Batch mode
  if (challenges && Array.isArray(challenges)) {
    const llmCallback = solution 
      ? async () => (Array.isArray(solution) ? solution.join('\n') : solution)
      : null;
    
    const proof = await prover.generateBatchProof({ nonce, challenges }, llmCallback);
    return proof;
  }
  
  // Single mode (legacy)
  if (!challenge_string) {
    return { error: 'challenge_string or challenges array required' };
  }
  
  const challenge = { challenge_string, nonce, type };
  const llmCallback = solution ? async () => solution : null;
  const proof = await prover.generateProof(challenge, llmCallback);
  
  return proof;
}

/**
 * Tool: Perform full verification against a server
 * This handles the complete flow: get challenge -> generate proof -> verify
 * 
 * @param {Object} params
 * @param {string} params.server_url - URL of the verification server
 * @param {string} [params.solution] - Optional pre-generated solution from LLM
 */
export async function aap_verify({ server_url, solution }) {
  if (!server_url) {
    return { error: 'server_url is required' };
  }
  
  try {
    // If solution is provided, create a callback that returns it
    const llmCallback = solution 
      ? async (challenge, nonce, type) => solution
      : null;
    
    const result = await client.verify(server_url, llmCallback);
    return result;
  } catch (error) {
    return { 
      error: `Verification failed: ${error.message}`,
      verified: false
    };
  }
}

/**
 * Tool: Check if a verification server is healthy
 * @param {Object} params
 * @param {string} params.server_url - URL of the verification server
 */
export async function aap_check_server({ server_url }) {
  if (!server_url) {
    return { error: 'server_url is required' };
  }
  
  try {
    const health = await client.checkHealth(server_url);
    return health;
  } catch (error) {
    return { healthy: false, error: error.message };
  }
}

/**
 * Tool: Verify another agent's signature
 * @param {Object} params
 * @param {string} params.data - Original data
 * @param {string} params.signature - Signature to verify
 * @param {string} params.publicKey - Signer's public key
 */
export async function aap_verify_signature({ data, signature, publicKey }) {
  if (!data || !signature || !publicKey) {
    return { error: 'data, signature, and publicKey are required' };
  }
  
  const isValid = identity.verify(data, signature, publicKey);
  
  return {
    valid: isValid,
    data,
    verifiedAt: Date.now()
  };
}

/**
 * Tool: Create a test challenge (for development/testing)
 * @param {Object} params
 * @param {string} [params.prompt] - Custom challenge prompt
 */
export async function aap_create_challenge({ prompt } = {}) {
  const challenge = prover.createChallenge(prompt);
  return challenge;
}

// Export tools for Clawdbot registration
export const tools = {
  aap_get_identity: {
    description: 'Get this agent\'s public identity (public key and ID)',
    parameters: {}
  },
  aap_sign_message: {
    description: 'Sign a message with this agent\'s private key',
    parameters: {
      message: { type: 'string', description: 'Message to sign', required: true }
    }
  },
  aap_generate_proof: {
    description: 'Generate a complete AAP proof for server verification',
    parameters: {
      challenge_string: { type: 'string', description: 'Challenge prompt from server', required: true },
      nonce: { type: 'string', description: 'Server-provided nonce', required: true },
      type: { type: 'string', description: 'Challenge type (poem, math, wordplay, reverse, description)' },
      solution: { type: 'string', description: 'Pre-generated solution from LLM (optional)' }
    }
  },
  aap_verify: {
    description: 'Perform full AAP verification against a server (get challenge -> prove -> verify)',
    parameters: {
      server_url: { type: 'string', description: 'URL of the verification server', required: true },
      solution: { type: 'string', description: 'Optional pre-generated solution from LLM' }
    }
  },
  aap_check_server: {
    description: 'Check if an AAP verification server is healthy and running',
    parameters: {
      server_url: { type: 'string', description: 'URL of the verification server', required: true }
    }
  },
  aap_verify_signature: {
    description: 'Verify another agent\'s signature',
    parameters: {
      data: { type: 'string', description: 'Original signed data', required: true },
      signature: { type: 'string', description: 'Signature to verify', required: true },
      publicKey: { type: 'string', description: 'Public key of the signer', required: true }
    }
  },
  aap_create_challenge: {
    description: 'Create a test challenge for development',
    parameters: {
      prompt: { type: 'string', description: 'Custom challenge prompt' }
    }
  }
};

export default {
  onStartup,
  aap_get_identity,
  aap_sign_message,
  aap_generate_proof,
  aap_verify,
  aap_check_server,
  aap_verify_signature,
  aap_create_challenge,
  tools
};
