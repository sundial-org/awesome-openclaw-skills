/**
 * AAP HTTP Client v2.5
 * 
 * Handles communication with AAP verification servers.
 * Supports batch challenges (5 challenges, 8 seconds).
 */

import { generateBatchProof } from './prover.js';
import { getPublicIdentity } from './identity.js';

/**
 * Perform full AAP verification against a server
 * 
 * @param {string} serverUrl - Base URL of the verification server
 * @param {Function} [llmCallback] - Async LLM callback for intelligent responses
 * @returns {Promise<Object>} Verification result
 */
export async function verify(serverUrl, llmCallback) {
  const baseUrl = serverUrl.replace(/\/$/, '');
  
  console.log(`[AAP] Starting verification with ${baseUrl}...`);
  
  // Step 1: Request batch challenge
  console.log('[AAP] Step 1: Requesting batch challenge...');
  const challengeRes = await fetch(`${baseUrl}/challenge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (!challengeRes.ok) {
    const error = await challengeRes.text();
    throw new Error(`Challenge request failed: ${error}`);
  }
  
  const challengeBatch = await challengeRes.json();
  console.log(`[AAP] Received ${challengeBatch.challenges?.length || 1} challenges`);
  
  // Step 2: Generate proof (solve + sign)
  console.log('[AAP] Step 2: Generating proof...');
  const proof = await generateBatchProof(challengeBatch, llmCallback);
  console.log(`[AAP] Proof generated in ${proof.responseTimeMs}ms`);
  
  // Step 3: Submit for verification
  console.log('[AAP] Step 3: Submitting proof...');
  const verifyRes = await fetch(`${baseUrl}/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(proof)
  });
  
  const result = await verifyRes.json();
  
  if (result.verified) {
    console.log('[AAP] ✅ Verification successful!');
  } else {
    console.log(`[AAP] ❌ Verification failed: ${result.error}`);
  }
  
  return {
    ...result,
    challenge: challengeBatch,
    proof: {
      solutions: proof.solutions,
      responseTimeMs: proof.responseTimeMs,
      publicId: proof.publicId
    }
  };
}

/**
 * Check if a verification server is healthy
 * 
 * @param {string} serverUrl - Base URL of the verification server
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth(serverUrl) {
  const baseUrl = serverUrl.replace(/\/$/, '');
  
  try {
    const res = await fetch(`${baseUrl}/health`);
    if (!res.ok) {
      return { healthy: false, error: `HTTP ${res.status}` };
    }
    
    const data = await res.json();
    return {
      healthy: true,
      ...data
    };
  } catch (error) {
    return { healthy: false, error: error.message };
  }
}

/**
 * Get challenge from server (without solving)
 * 
 * @param {string} serverUrl - Base URL
 * @returns {Promise<Object>} Challenge batch
 */
export async function getChallenge(serverUrl) {
  const baseUrl = serverUrl.replace(/\/$/, '');
  
  const res = await fetch(`${baseUrl}/challenge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (!res.ok) {
    throw new Error(`Challenge request failed: ${res.status}`);
  }
  
  return res.json();
}

/**
 * Submit proof to server
 * 
 * @param {string} serverUrl - Base URL
 * @param {Object} proof - Generated proof
 * @returns {Promise<Object>} Verification result
 */
export async function submitProof(serverUrl, proof) {
  const baseUrl = serverUrl.replace(/\/$/, '');
  
  const res = await fetch(`${baseUrl}/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(proof)
  });
  
  return res.json();
}

export default { verify, checkHealth, getChallenge, submitProof };
