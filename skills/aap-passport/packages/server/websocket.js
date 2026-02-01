/**
 * AAP WebSocket Server v3.2
 * 
 * Batch challenge + mandatory signature verification.
 * No signature = no entry.
 */

import { WebSocketServer } from 'ws';
import { randomBytes, createHash, createVerify } from 'node:crypto';

// ============== CONSTANTS ==============
export const PROTOCOL_VERSION = '3.2.0';
export const CHALLENGE_COUNT = 7;
export const TOTAL_TIME_MS = 6000;
export const CONNECTION_TIMEOUT_MS = 60000;

// ============== CHALLENGE GENERATORS ==============
const GENERATORS = {
  math: (salt, seed) => {
    const a = 10 + (seed % 90);
    const b = 10 + ((seed * 7) % 90);
    const ops = ['+', '-', '*'];
    const op = ops[seed % 3];
    const answer = op === '+' ? a + b : op === '-' ? a - b : a * b;
    return {
      q: `[REQ-${salt}] What is ${a} ${op} ${b}?\nFormat: {"salt":"${salt}","result":number}`,
      v: (r) => r?.salt === salt && r?.result === answer
    };
  },
  
  logic: (salt, seed) => {
    const x = 10 + (seed % 50);
    const y = 10 + ((seed * 3) % 50);
    const answer = x > y ? 'GREATER' : x < y ? 'LESS' : 'EQUAL';
    return {
      q: `[REQ-${salt}] X=${x}, Y=${y}. Answer "GREATER" if X>Y, "LESS" if X<Y, "EQUAL" if X=Y.\nFormat: {"salt":"${salt}","answer":"..."}`,
      v: (r) => r?.salt === salt && r?.answer === answer
    };
  },
  
  count: (salt, seed) => {
    const all = ['cat','dog','apple','bird','car','fish','tree','book','lion','grape'];
    const animals = ['cat','dog','bird','fish','lion'];
    const n = 4 + (seed % 5);
    const items = [];
    for (let i = 0; i < n; i++) {
      items.push(all[(seed + i * 3) % all.length]);
    }
    const count = items.filter(i => animals.includes(i)).length;
    return {
      q: `[REQ-${salt}] Count animals: ${items.join(', ')}\nFormat: {"salt":"${salt}","count":number}`,
      v: (r) => r?.salt === salt && r?.count === count
    };
  },
  
  pattern: (salt, seed) => {
    const start = 2 + (seed % 10);
    const step = 2 + (seed % 6);
    const seq = [start, start+step, start+step*2, start+step*3];
    const next = [start+step*4, start+step*5];
    return {
      q: `[REQ-${salt}] Next 2 numbers: [${seq.join(', ')}, ?, ?]\nFormat: {"salt":"${salt}","next":[n1,n2]}`,
      v: (r) => r?.salt === salt && Array.isArray(r?.next) && r.next[0] === next[0] && r.next[1] === next[1]
    };
  },
  
  reverse: (salt, seed) => {
    const words = ['hello','world','agent','robot','claw','alpha','delta'];
    const word = words[seed % words.length];
    const rev = word.split('').reverse().join('');
    return {
      q: `[REQ-${salt}] Reverse the string: "${word}"\nFormat: {"salt":"${salt}","result":"..."}`,
      v: (r) => r?.salt === salt && r?.result === rev
    };
  },
  
  extract: (salt, seed) => {
    const colors = ['red','blue','green','yellow','purple','orange'];
    const color = colors[seed % colors.length];
    const nouns = ['car','robot','bird','house'];
    const noun = nouns[seed % nouns.length];
    return {
      q: `[REQ-${salt}] Extract the color: "The ${color} ${noun} moved quickly"\nFormat: {"salt":"${salt}","color":"..."}`,
      v: (r) => r?.salt === salt && r?.color === color
    };
  },
  
  longest: (salt, seed) => {
    const sets = [
      ['cat', 'elephant', 'dog', 'ant'],
      ['bee', 'hippopotamus', 'fox', 'rat'],
      ['owl', 'crocodile', 'bat', 'fly']
    ];
    const words = sets[seed % sets.length];
    const longest = words.reduce((a, b) => a.length >= b.length ? a : b);
    return {
      q: `[REQ-${salt}] Find longest word: ${words.join(', ')}\nFormat: {"salt":"${salt}","answer":"..."}`,
      v: (r) => r?.salt === salt && r?.answer === longest
    };
  }
};

const TYPES = Object.keys(GENERATORS);

function generateChallenge(nonce, index) {
  const type = TYPES[index % TYPES.length];
  const salt = createHash('sha256').update(nonce + index).digest('hex').slice(0, 6).toUpperCase();
  const seed = parseInt(nonce.slice(index * 2, index * 2 + 8), 16) || (index * 17);
  const { q, v } = GENERATORS[type](salt, seed);
  return { id: index, type, challenge: q, validate: v };
}

/**
 * Verify secp256k1 signature
 */
function verifySignature(data, signature, publicKey) {
  try {
    const verifier = createVerify('SHA256');
    verifier.update(data);
    return verifier.verify(publicKey, signature, 'base64');
  } catch {
    return false;
  }
}

/**
 * Derive public ID from public key
 */
function derivePublicId(publicKey) {
  return createHash('sha256').update(publicKey).digest('hex').slice(0, 16);
}

// ============== WEBSOCKET SERVER ==============

/**
 * Create AAP WebSocket verification server
 */
export function createAAPWebSocket(options = {}) {
  const {
    port,
    server,
    path = '/aap',
    challengeCount = CHALLENGE_COUNT,
    totalTimeMs = TOTAL_TIME_MS,
    connectionTimeoutMs = CONNECTION_TIMEOUT_MS,
    requireSignature = true,  // v3.2: signature required by default
    onVerified,
    onFailed
  } = options;

  const wssOptions = server ? { server, path } : { port };
  const wss = new WebSocketServer(wssOptions);
  const verifiedTokens = new Map();

  wss.on('connection', (ws) => {
    const sessionId = randomBytes(16).toString('hex');
    const nonce = randomBytes(16).toString('hex');
    let challenges = [];
    let validators = [];
    let challengesSentAt = null;
    let publicKey = null;
    let publicId = null;
    let answered = false;

    // Generate challenges
    for (let i = 0; i < challengeCount; i++) {
      const ch = generateChallenge(nonce, i);
      challenges.push({ id: ch.id, type: ch.type, challenge: ch.challenge });
      validators.push(ch.validate);
    }

    // Connection timeout
    const connTimer = setTimeout(() => {
      send(ws, { type: 'error', code: 'TIMEOUT', message: 'Connection timeout' });
      ws.close();
    }, connectionTimeoutMs);

    // Send handshake
    send(ws, {
      type: 'handshake',
      sessionId,
      protocol: 'AAP',
      version: PROTOCOL_VERSION,
      mode: 'batch',
      challengeCount,
      totalTimeMs,
      requireSignature,
      message: 'Send {"type":"ready","publicKey":"..."} to receive challenges.'
    });

    ws.on('message', (data) => {
      let msg;
      try {
        msg = JSON.parse(data.toString());
      } catch {
        send(ws, { type: 'error', code: 'INVALID_JSON', message: 'Invalid JSON' });
        return;
      }

      if (msg.type === 'ready' && !challengesSentAt) {
        // v3.2: publicKey required
        if (requireSignature && !msg.publicKey) {
          send(ws, { type: 'error', code: 'MISSING_PUBLIC_KEY', message: 'publicKey required for signature verification' });
          return;
        }
        
        publicKey = msg.publicKey || null;
        publicId = publicKey ? derivePublicId(publicKey) : 'anon-' + randomBytes(4).toString('hex');
        challengesSentAt = Date.now();
        
        // Send all challenges at once
        send(ws, {
          type: 'challenges',
          nonce,
          challenges,
          totalTimeMs,
          expiresAt: challengesSentAt + totalTimeMs
        });
      }
      else if (msg.type === 'answers' && challengesSentAt && !answered) {
        answered = true;
        clearTimeout(connTimer);
        
        const elapsed = Date.now() - challengesSentAt;
        const answers = msg.answers || [];
        const signature = msg.signature;
        const timestamp = msg.timestamp;

        // v3.2: Verify signature first
        if (requireSignature) {
          if (!signature) {
            const result = {
              type: 'result',
              verified: false,
              message: 'Missing signature',
              code: 'MISSING_SIGNATURE',
              publicId
            };
            if (onFailed) onFailed(result);
            send(ws, result);
            setTimeout(() => ws.close(), 300);
            return;
          }
          
          // Create proof data for verification
          const proofData = JSON.stringify({ nonce, answers, publicId, timestamp });
          
          if (!verifySignature(proofData, signature, publicKey)) {
            const result = {
              type: 'result',
              verified: false,
              message: 'Invalid signature',
              code: 'INVALID_SIGNATURE',
              publicId
            };
            if (onFailed) onFailed(result);
            send(ws, result);
            setTimeout(() => ws.close(), 300);
            return;
          }
        }
        
        // Too slow?
        if (elapsed > totalTimeMs) {
          const result = {
            type: 'result',
            verified: false,
            message: `Too slow: ${elapsed}ms > ${totalTimeMs}ms`,
            code: 'TOO_SLOW',
            publicId,
            responseTimeMs: elapsed
          };
          if (onFailed) onFailed(result);
          send(ws, result);
          setTimeout(() => ws.close(), 300);
          return;
        }
        
        // Validate all answers
        let passed = 0;
        const results = [];
        for (let i = 0; i < challengeCount; i++) {
          const valid = validators[i](answers[i]);
          if (valid) passed++;
          results.push({ id: i, valid });
        }
        
        const success = passed === challengeCount;
        const result = {
          type: 'result',
          verified: success,
          message: success ? 'All challenges passed' : `Failed: ${passed}/${challengeCount}`,
          publicId,
          passed,
          total: challengeCount,
          results,
          responseTimeMs: elapsed
        };
        
        if (success) {
          result.role = 'AI_AGENT';
          result.sessionToken = randomBytes(32).toString('hex');
          
          verifiedTokens.set(result.sessionToken, {
            publicId,
            publicKey,
            nonce,
            verifiedAt: Date.now(),
            expiresAt: Date.now() + 3600000,
            responseTimeMs: elapsed
          });
          
          if (onVerified) onVerified(result);
        } else {
          if (onFailed) onFailed(result);
        }
        
        send(ws, result);
        setTimeout(() => ws.close(), 300);
      }
    });

    ws.on('close', () => clearTimeout(connTimer));
    ws.on('error', () => clearTimeout(connTimer));
  });

  return {
    wss,
    verifiedTokens,
    close: () => wss.close(),
    isVerified: (token) => {
      const session = verifiedTokens.get(token);
      return session && Date.now() < session.expiresAt;
    },
    getSession: (token) => verifiedTokens.get(token)
  };
}

function send(ws, data) {
  if (ws.readyState === 1) ws.send(JSON.stringify(data));
}

export default { createAAPWebSocket, PROTOCOL_VERSION, CHALLENGE_COUNT, TOTAL_TIME_MS };
