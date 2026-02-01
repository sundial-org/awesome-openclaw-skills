/**
 * AAP Prover v2.5
 * 
 * Generates proofs for AAP verification.
 * Supports batch challenges with salt injection.
 */

import { createSign, createHash, randomBytes } from 'node:crypto';
import { getPrivateKey, getPublicIdentity } from './identity.js';

/**
 * Generate proof for a batch of challenges
 * 
 * @param {Object} challengeBatch - Batch challenge from server
 * @param {Function|null} llmCallback - Async LLM callback for solving
 * @returns {Promise<Object>} Proof object ready for submission
 */
export async function generateBatchProof(challengeBatch, llmCallback) {
  const startTime = Date.now();
  const { nonce, challenges } = challengeBatch;
  
  // Solve all challenges
  let solutions;
  
  if (llmCallback) {
    // Use LLM to solve
    const prompt = createBatchPrompt(challenges);
    const llmResponse = await llmCallback(prompt);
    solutions = parseBatchResponse(llmResponse, challenges.length);
  } else {
    // Fallback: return placeholder (will fail verification)
    console.warn('[AAP] No LLM callback provided. Using placeholders.');
    solutions = challenges.map((c, i) => {
      const saltMatch = c.challenge_string.match(/\[REQ-([A-Z0-9]+)\]/);
      const salt = saltMatch ? saltMatch[1] : 'UNKNOWN';
      return JSON.stringify({ salt, error: 'No LLM available' });
    });
  }
  
  // Sign proof
  const identity = getPublicIdentity();
  const privateKey = getPrivateKey();
  const timestamp = Date.now();
  
  const proofData = JSON.stringify({
    nonce,
    solution: JSON.stringify(solutions),
    publicId: identity.publicId,
    timestamp
  });
  
  const signer = createSign('SHA256');
  signer.update(proofData);
  const signature = signer.sign(privateKey, 'base64');
  
  const responseTimeMs = Date.now() - startTime;
  
  return {
    solutions,
    signature,
    publicKey: identity.publicKey,
    publicId: identity.publicId,
    nonce,
    timestamp,
    responseTimeMs
  };
}

/**
 * Generate proof for a single challenge (legacy support)
 * 
 * @param {Object} challenge - Single challenge
 * @param {Function|string|null} solutionOrCallback - Solution or LLM callback
 * @returns {Promise<Object>} Proof object
 */
export async function generateProof(challenge, solutionOrCallback) {
  const startTime = Date.now();
  const { challenge_string, nonce, type } = challenge;
  
  // Get solution
  let solution;
  if (typeof solutionOrCallback === 'string') {
    solution = solutionOrCallback;
  } else if (typeof solutionOrCallback === 'function') {
    solution = await solutionOrCallback(challenge_string, nonce, type);
  } else {
    solution = `{"error": "No solution provided"}`;
  }
  
  // Sign
  const identity = getPublicIdentity();
  const privateKey = getPrivateKey();
  const timestamp = Date.now();
  
  const proofData = JSON.stringify({
    nonce,
    solution,
    publicId: identity.publicId,
    timestamp
  });
  
  const signer = createSign('SHA256');
  signer.update(proofData);
  const signature = signer.sign(privateKey, 'base64');
  
  return {
    solution,
    signature,
    publicKey: identity.publicKey,
    publicId: identity.publicId,
    nonce,
    timestamp,
    responseTimeMs: Date.now() - startTime
  };
}

/**
 * Create prompt for batch solving
 * @param {Array} challenges - Array of challenges
 * @returns {string} Combined prompt
 */
function createBatchPrompt(challenges) {
  let prompt = `You are solving AAP (Agent Attestation Protocol) verification challenges.
Solve ALL challenges below. Each response MUST include the exact salt from [REQ-XXXXXX].

CHALLENGES:
`;

  challenges.forEach((c, i) => {
    prompt += `\n[${i}] ${c.challenge_string}\n`;
  });

  prompt += `
IMPORTANT:
- Include the salt in every response
- Follow the exact response format specified
- Return a JSON array with ${challenges.length} solutions

Respond ONLY with a valid JSON array:
[
  {"salt": "...", ...},
  {"salt": "...", ...},
  ...
]`;

  return prompt;
}

/**
 * Parse LLM response into solutions array
 * @param {string} response - LLM response
 * @param {number} expectedCount - Expected number of solutions
 * @returns {Array} Parsed solutions
 */
function parseBatchResponse(response, expectedCount) {
  try {
    // Try to find JSON array in response
    const match = response.match(/\[[\s\S]*\]/);
    if (match) {
      const arr = JSON.parse(match[0]);
      if (Array.isArray(arr)) {
        return arr.map(item => 
          typeof item === 'string' ? item : JSON.stringify(item)
        );
      }
    }
    
    // Try to find individual JSON objects
    const objects = [];
    const regex = /\{[^{}]*"salt"[^{}]*\}/g;
    let m;
    while ((m = regex.exec(response)) !== null) {
      objects.push(m[0]);
    }
    
    if (objects.length >= expectedCount) {
      return objects.slice(0, expectedCount);
    }
    
    // Fallback: return raw response split
    console.warn('[AAP] Could not parse LLM response, using fallback');
    return Array(expectedCount).fill('{"error": "parse failed"}');
    
  } catch (error) {
    console.error('[AAP] Failed to parse LLM response:', error);
    return Array(expectedCount).fill('{"error": "parse failed"}');
  }
}

/**
 * Create a test challenge
 * @param {string} [prompt] - Custom prompt
 * @returns {Object} Challenge object
 */
export function createChallenge(prompt) {
  const nonce = randomBytes(16).toString('hex');
  const salt = nonce.slice(0, 6).toUpperCase();
  
  return {
    challenge_string: prompt || `[REQ-${salt}] Test challenge. Respond with: {"salt": "${salt}", "test": true}`,
    nonce,
    type: 'test',
    timestamp: Date.now()
  };
}

export default { generateProof, generateBatchProof, createChallenge };
