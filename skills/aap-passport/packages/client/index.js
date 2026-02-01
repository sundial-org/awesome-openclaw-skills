/**
 * @aap/client v3.2.0
 * 
 * WebSocket client with mandatory signature.
 * Proves cryptographic identity via secp256k1.
 */

import WebSocket from 'ws';
import { generateKeyPairSync, createSign, createHash, randomBytes } from 'crypto';

export const PROTOCOL_VERSION = '3.2.0';

/**
 * Generate secp256k1 key pair for agent identity
 */
export function generateIdentity() {
  const { publicKey, privateKey } = generateKeyPairSync('ec', {
    namedCurve: 'secp256k1',
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  
  const publicId = createHash('sha256').update(publicKey).digest('hex').slice(0, 16);
  
  return { publicKey, privateKey, publicId };
}

/**
 * Sign data with private key
 */
export function sign(data, privateKey) {
  const signer = createSign('SHA256');
  signer.update(data);
  return signer.sign(privateKey, 'base64');
}

/**
 * AAP WebSocket Client
 */
export class AAPClient {
  constructor(options = {}) {
    this.serverUrl = options.serverUrl || 'ws://localhost:3000/aap';
    this.identity = options.identity || generateIdentity();
    this.solver = options.solver || null;
  }

  get publicKey() { return this.identity.publicKey; }
  get publicId() { return this.identity.publicId; }

  /**
   * Connect and verify with signature
   * @param {Function} [solver] - async (challenges) => answers[]
   * @returns {Promise<Object>} Verification result
   */
  async verify(solver) {
    const solve = solver || this.solver;
    const { publicKey, privateKey, publicId } = this.identity;
    
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(this.serverUrl);
      let result = null;
      let nonce = null;

      ws.on('open', () => {});

      ws.on('message', async (data) => {
        try {
          const msg = JSON.parse(data.toString());

          switch (msg.type) {
            case 'handshake':
              // Send ready with public key
              ws.send(JSON.stringify({
                type: 'ready',
                publicKey
              }));
              break;

            case 'challenges':
              nonce = msg.nonce;
              
              if (!solve) {
                // No solver - will fail
                const timestamp = Date.now();
                const answers = [];
                const proofData = JSON.stringify({ nonce, answers, publicId, timestamp });
                const signature = sign(proofData, privateKey);
                ws.send(JSON.stringify({ type: 'answers', answers, signature, timestamp }));
                break;
              }

              try {
                const answers = await solve(msg.challenges);
                const timestamp = Date.now();
                
                // Sign the proof
                const proofData = JSON.stringify({ nonce, answers, publicId, timestamp });
                const signature = sign(proofData, privateKey);
                
                ws.send(JSON.stringify({ type: 'answers', answers, signature, timestamp }));
              } catch (e) {
                const timestamp = Date.now();
                const answers = [];
                const proofData = JSON.stringify({ nonce, answers, publicId, timestamp });
                const signature = sign(proofData, privateKey);
                ws.send(JSON.stringify({ type: 'answers', answers, signature, timestamp }));
              }
              break;

            case 'result':
              result = msg;
              break;

            case 'error':
              reject(new Error(msg.message || 'Unknown error'));
              ws.close();
              break;
          }
        } catch (e) {
          reject(e);
          ws.close();
        }
      });

      ws.on('close', () => {
        if (result) resolve(result);
        else reject(new Error('Connection closed without result'));
      });

      ws.on('error', reject);
    });
  }
}

/**
 * Create a solver function from an LLM callback
 * @param {Function} llm - async (prompt) => responseString
 * @returns {Function} Solver function
 */
export function createSolver(llm) {
  return async (challenges) => {
    const prompt = `Solve ALL these challenges. Return a JSON array of answers in order.

${challenges.map((c, i) => `[${i}] ${c.challenge}`).join('\n\n')}

Respond with ONLY a JSON array like: [{...}, {...}, ...]`;

    const response = await llm(prompt);
    const match = response.match(/\[[\s\S]*\]/);
    if (!match) throw new Error('No JSON array found');
    return JSON.parse(match[0]);
  };
}

/**
 * Quick verify helper
 */
export async function verify(serverUrl, solver, identity) {
  const client = new AAPClient({ serverUrl, solver, identity });
  return client.verify();
}

export function createClient(options) {
  return new AAPClient(options);
}

export default { AAPClient, createClient, createSolver, verify, generateIdentity, sign, PROTOCOL_VERSION };
