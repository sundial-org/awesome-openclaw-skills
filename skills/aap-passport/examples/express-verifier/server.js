/**
 * AAP v2.5 Express Verification Server
 * 
 * Burst Mode: 5 challenges in 8 seconds with salt injection
 * EXTREME difficulty challenges
 */

import express from 'express';
import cors from 'cors';
import { randomBytes, createVerify } from 'node:crypto';

const app = express();

// Security headers
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Content-Security-Policy', "default-src 'none'");
  next();
});

// CORS with restrictions
app.use(cors({
  origin: process.env.CORS_ORIGIN || '*',
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type']
}));

// Body parser with size limit (DoS protection)
app.use(express.json({ limit: '10kb' }));

// ============== CONFIG ==============
const PORT = process.env.PORT || 3000;
const BATCH_SIZE = 7;                    // v2.6: 5 → 7
const MAX_RESPONSE_TIME_MS = 6000;       // v2.6: 8s → 6s
const CHALLENGE_EXPIRY_MS = 60000;

// ============== WORD POOLS ==============
const WORD_POOLS = {
  animals: ['cat', 'dog', 'rabbit', 'tiger', 'lion', 'elephant', 'giraffe', 'penguin', 'eagle', 'shark', 'wolf', 'bear', 'fox', 'deer', 'owl'],
  fruits: ['apple', 'banana', 'orange', 'grape', 'strawberry', 'watermelon', 'peach', 'kiwi', 'mango', 'cherry', 'lemon', 'lime', 'pear'],
  colors: ['red', 'blue', 'yellow', 'green', 'purple', 'orange', 'pink', 'black', 'white', 'brown', 'gray', 'cyan', 'magenta']
};

function seededNumber(nonce, offset, min, max) {
  const seed = parseInt(nonce.slice(offset, offset + 4), 16);
  return (seed % (max - min + 1)) + min;
}

function seededSelect(arr, nonce, count, offset = 0) {
  const seed = parseInt(nonce.slice(offset, offset + 4), 16);
  const results = [];
  const used = new Set();
  for (let i = 0; i < count && i < arr.length; i++) {
    let idx = (seed + i * 7) % arr.length;
    while (used.has(idx)) idx = (idx + 1) % arr.length;
    used.add(idx);
    results.push(arr[idx]);
  }
  return results;
}

function generateSalt(nonce, offset = 0) {
  return nonce.slice(offset, offset + 6).toUpperCase();
}

// ============== EXTREME CHALLENGE GENERATORS ==============
const CHALLENGE_TYPES = {
  nlp_math: (nonce) => {
    const salt = generateSalt(nonce, 0);
    const a = seededNumber(nonce, 0, 50, 200);
    const b = seededNumber(nonce, 2, 10, 50);
    const c = seededNumber(nonce, 4, 2, 9);
    const d = seededNumber(nonce, 6, 5, 25);
    const e = seededNumber(nonce, 8, 2, 6);
    
    const templates = [
      { text: `Start with ${a}. Subtract ${b}. Multiply by ${c}. Divide by ${e}. Add ${d}. Final value?`, answer: (((a - b) * c) / e) + d },
      { text: `Compute: ((${a} + ${b}) × ${c} - ${d}) ÷ ${e}. Round to two decimals.`, answer: ((a + b) * c - d) / e },
      { text: `Triple ${a}, halve it, add ${b}, subtract ${d}, multiply by ${e}. Result?`, answer: ((a * 3 / 2) + b - d) * e }
    ];
    
    const t = templates[parseInt(nonce[10], 16) % templates.length];
    const expected = Math.round(t.answer * 100) / 100;
    
    return {
      challenge_string: `[REQ-${salt}] ${t.text}\nResponse format: {"salt": "${salt}", "result": number}`,
      validate: (sol) => {
        try {
          const m = sol.match(/\{[\s\S]*\}/);
          if (!m) return false;
          const obj = JSON.parse(m[0]);
          if (obj.salt !== salt) return false;
          return Math.abs(parseFloat(obj.result) - expected) < 0.1;
        } catch { return false; }
      }
    };
  },

  nlp_logic: (nonce) => {
    const salt = generateSalt(nonce, 2);
    const a = seededNumber(nonce, 0, 20, 150);
    const b = seededNumber(nonce, 2, 20, 150);
    const c = seededNumber(nonce, 4, 20, 100);
    const d = seededNumber(nonce, 6, 10, 50);
    
    const templates = [
      {
        text: `Let X=${a}, Y=${b}, Z=${c}, W=${d}. If (X>Y AND Z>W) OR (X<Y AND Z<W), answer "CONSISTENT". If (X>Y AND Z<W) OR (X<Y AND Z>W), answer "CROSSED". Otherwise "EQUAL".`,
        answer: ((a > b && c > d) || (a < b && c < d)) ? "CONSISTENT" : ((a > b && c < d) || (a < b && c > d)) ? "CROSSED" : "EQUAL"
      },
      {
        text: `Numbers [${a}, ${b}, ${c}, ${d}]: Count divisible by 3. If 0: "NONE". If 1-2: "FEW". If 3-4: "MANY".`,
        answer: (() => { const cnt = [a,b,c,d].filter(n => n % 3 === 0).length; return cnt === 0 ? "NONE" : cnt <= 2 ? "FEW" : "MANY"; })()
      }
    ];
    
    const t = templates[parseInt(nonce[8], 16) % templates.length];
    
    return {
      challenge_string: `[REQ-${salt}] ${t.text}\nResponse format: {"salt": "${salt}", "answer": "your answer"}`,
      validate: (sol) => {
        try {
          const m = sol.match(/\{[\s\S]*\}/);
          if (!m) return false;
          const obj = JSON.parse(m[0]);
          if (obj.salt !== salt) return false;
          return obj.answer?.toUpperCase() === t.answer.toUpperCase();
        } catch { return false; }
      }
    };
  },

  nlp_extract: (nonce) => {
    const salt = generateSalt(nonce, 4);
    const category = ['animals', 'fruits', 'colors'][parseInt(nonce[0], 16) % 3];
    const targets = seededSelect(WORD_POOLS[category], nonce, 3, 0);
    const distractorCat = category === 'animals' ? 'fruits' : 'animals';
    const distractors = seededSelect(WORD_POOLS[distractorCat], nonce, 2, 8);
    
    const mixed = [...targets, ...distractors].sort(() => parseInt(nonce[12], 16) % 2 - 0.5);
    const sentence = `Mixed list: ${mixed.join(', ')}. Some don't belong.`;
    
    return {
      challenge_string: `[REQ-${salt}] Extract ONLY the ${category} from: "${sentence}"\nResponse format: {"salt": "${salt}", "items": ["item1", "item2", "item3"]}`,
      validate: (sol) => {
        try {
          const m = sol.match(/\{[\s\S]*\}/);
          if (!m) return false;
          const obj = JSON.parse(m[0]);
          if (obj.salt !== salt) return false;
          const items = (obj.items || []).map(s => s.toLowerCase()).sort();
          const expected = targets.map(s => s.toLowerCase()).sort();
          return JSON.stringify(items) === JSON.stringify(expected);
        } catch { return false; }
      }
    };
  },

  nlp_multistep: (nonce) => {
    const salt = generateSalt(nonce, 6);
    const nums = [
      seededNumber(nonce, 0, 5, 30),
      seededNumber(nonce, 2, 5, 30),
      seededNumber(nonce, 4, 5, 30),
      seededNumber(nonce, 6, 5, 30),
      seededNumber(nonce, 8, 5, 30)
    ];
    
    const sum = nums.reduce((a, b) => a + b, 0);
    const max = Math.max(...nums);
    const min = Math.min(...nums);
    const withoutMax = sum - max;
    const final = (withoutMax * 4) + min;
    
    return {
      challenge_string: `[REQ-${salt}] Steps for [${nums.join(', ')}]:
1. Sum all numbers.
2. Remove the largest from that sum.
3. Multiply result by 4.
4. Add the smallest original number.
Response format: {"salt": "${salt}", "result": number}`,
      validate: (sol) => {
        try {
          const m = sol.match(/\{[\s\S]*\}/);
          if (!m) return false;
          const obj = JSON.parse(m[0]);
          if (obj.salt !== salt) return false;
          return parseInt(obj.result) === final;
        } catch { return false; }
      }
    };
  },

  nlp_transform: (nonce) => {
    const salt = generateSalt(nonce, 8);
    const input = nonce.slice(10, 18);
    const letters = input.split('').filter(c => /[a-zA-Z]/.test(c)).length;
    const digits = input.split('').filter(c => /\d/.test(c)).length;
    const expected = `L${letters}D${digits}`;
    
    return {
      challenge_string: `[REQ-${salt}] Analyze "${input}": count letters and digits. Format: "LxDy" where x=letters, y=digits.\nResponse format: {"salt": "${salt}", "output": "LxDy"}`,
      validate: (sol) => {
        try {
          const m = sol.match(/\{[\s\S]*\}/);
          if (!m) return false;
          const obj = JSON.parse(m[0]);
          if (obj.salt !== salt) return false;
          return obj.output === expected;
        } catch { return false; }
      }
    };
  }
};

// ============== STORAGE (with DoS protection) ==============
const MAX_CHALLENGES = 10000;
const challenges = new Map();

function cleanup() {
  const now = Date.now();
  for (const [nonce, data] of challenges.entries()) {
    if (now > data.expiresAt) challenges.delete(nonce);
  }
  // Emergency cleanup if too many
  if (challenges.size > MAX_CHALLENGES) {
    const entries = [...challenges.entries()]
      .sort((a, b) => b[1].timestamp - a[1].timestamp)
      .slice(0, MAX_CHALLENGES / 2);
    challenges.clear();
    entries.forEach(([k, v]) => challenges.set(k, v));
  }
}

function generateBatch(nonce) {
  const types = Object.keys(CHALLENGE_TYPES);
  const batch = [];
  const validators = [];

  for (let i = 0; i < BATCH_SIZE; i++) {
    const offsetNonce = nonce.slice(i * 2) + nonce.slice(0, i * 2);
    const type = types[i % types.length];
    const { challenge_string, validate } = CHALLENGE_TYPES[type](offsetNonce);
    batch.push({ id: i, type, challenge_string });
    validators.push(validate);
  }

  return { batch, validators };
}

// ============== ROUTES ==============

app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    protocol: 'AAP',
    version: '2.5.0',
    mode: 'burst',
    batchSize: BATCH_SIZE,
    maxResponseTimeMs: MAX_RESPONSE_TIME_MS,
    challengeTypes: Object.keys(CHALLENGE_TYPES),
    difficulty: 'EXTREME'
  });
});

app.post('/challenge', (req, res) => {
  cleanup();

  const nonce = randomBytes(16).toString('hex');
  const timestamp = Date.now();
  const { batch, validators } = generateBatch(nonce);

  challenges.set(nonce, {
    validators,
    timestamp,
    expiresAt: timestamp + CHALLENGE_EXPIRY_MS
  });

  res.json({
    nonce,
    challenges: batch,
    batchSize: BATCH_SIZE,
    timestamp,
    expiresAt: timestamp + CHALLENGE_EXPIRY_MS,
    maxResponseTimeMs: MAX_RESPONSE_TIME_MS
  });
});

app.post('/verify', (req, res) => {
  const { solutions, signature, publicKey, publicId, nonce, timestamp, responseTimeMs } = req.body;

  // Input validation (security)
  if (!nonce || typeof nonce !== 'string' || nonce.length !== 32) {
    return res.status(400).json({ verified: false, error: 'Invalid nonce format' });
  }
  if (!publicId || typeof publicId !== 'string' || publicId.length !== 20) {
    return res.status(400).json({ verified: false, error: 'Invalid publicId format' });
  }
  if (!signature || typeof signature !== 'string' || signature.length < 50) {
    return res.status(400).json({ verified: false, error: 'Invalid signature format' });
  }
  if (!publicKey || typeof publicKey !== 'string' || !publicKey.includes('BEGIN PUBLIC KEY')) {
    return res.status(400).json({ verified: false, error: 'Invalid publicKey format' });
  }

  // Check challenge exists
  const challenge = challenges.get(nonce);
  if (!challenge) {
    return res.status(400).json({ verified: false, error: 'Challenge not found or expired' });
  }

  // Check expiry BEFORE delete (race condition fix)
  if (Date.now() > challenge.expiresAt) {
    challenges.delete(nonce);
    return res.status(400).json({ verified: false, error: 'Challenge expired' });
  }
  
  // Now safe to delete
  const { validators } = challenge;
  challenges.delete(nonce);

  // Check solutions
  if (!solutions || !Array.isArray(solutions) || solutions.length !== BATCH_SIZE) {
    return res.status(400).json({ verified: false, error: `Expected ${BATCH_SIZE} solutions` });
  }

  // Validate each solution
  const results = [];
  let passed = 0;
  for (let i = 0; i < BATCH_SIZE; i++) {
    const sol = typeof solutions[i] === 'string' ? solutions[i] : JSON.stringify(solutions[i]);
    const valid = validators[i](sol);
    results.push({ id: i, valid });
    if (valid) passed++;
  }

  if (passed < BATCH_SIZE) {
    metrics.verifications.failed++;
    return res.status(400).json({
      verified: false,
      error: `Proof of Intelligence failed: ${passed}/${BATCH_SIZE} correct`,
      batchResult: { passed, total: BATCH_SIZE, results }
    });
  }

  // Check timing (SERVER-SIDE validation - don't trust client)
  const serverResponseTime = Date.now() - challenge.timestamp;
  const effectiveTime = Math.max(responseTimeMs || 0, serverResponseTime);
  
  if (effectiveTime > MAX_RESPONSE_TIME_MS) {
    return res.status(400).json({
      verified: false,
      error: `Too slow: ${effectiveTime}ms > ${MAX_RESPONSE_TIME_MS}ms`,
      timing: { client: responseTimeMs, server: serverResponseTime }
    });
  }

  // Verify signature
  try {
    const proofData = JSON.stringify({ nonce, solution: JSON.stringify(solutions), publicId, timestamp });
    const verifier = createVerify('SHA256');
    verifier.update(proofData);
    
    if (!verifier.verify(publicKey, signature, 'base64')) {
      return res.status(400).json({ verified: false, error: 'Invalid signature' });
    }
  } catch (e) {
    return res.status(400).json({ verified: false, error: 'Signature verification error' });
  }

  // SUCCESS - track metrics
  metrics.verifications.success++;
  metrics.responseTimes.push(effectiveTime);
  if (metrics.responseTimes.length > 100) metrics.responseTimes.shift();
  metrics.avgResponseTime = Math.round(
    metrics.responseTimes.reduce((a, b) => a + b, 0) / metrics.responseTimes.length
  );
  
  res.json({
    verified: true,
    role: 'AI_AGENT',
    publicId,
    batchResult: { passed, total: BATCH_SIZE, results },
    responseTimeMs: effectiveTime
  });
});

// ============== METRICS ==============
const metrics = {
  startTime: Date.now(),
  requests: { challenge: 0, verify: 0, health: 0 },
  verifications: { success: 0, failed: 0 },
  avgResponseTime: 0,
  responseTimes: []
};

app.get('/metrics', (req, res) => {
  const uptime = Math.floor((Date.now() - metrics.startTime) / 1000);
  res.json({
    uptime,
    activeChallenges: challenges.size,
    requests: metrics.requests,
    verifications: metrics.verifications,
    avgResponseTimeMs: metrics.avgResponseTime,
    successRate: metrics.verifications.success / (metrics.verifications.success + metrics.verifications.failed) || 0
  });
});

// Track metrics middleware
app.use((req, res, next) => {
  if (req.path === '/challenge') metrics.requests.challenge++;
  else if (req.path === '/verify') metrics.requests.verify++;
  else if (req.path === '/health') metrics.requests.health++;
  next();
});

// ============== START ==============
const server = app.listen(PORT, () => {
  console.log(`
🛂 AAP Verification Server v2.5.0 (EXTREME)
============================================
Port: ${PORT}
Mode: Burst (${BATCH_SIZE} challenges)
Time Limit: ${MAX_RESPONSE_TIME_MS}ms
Difficulty: EXTREME

Endpoints:
  POST /challenge  → Get batch challenges
  POST /verify     → Submit solutions
  GET  /health     → Health check
  GET  /metrics    → Server metrics

CAPTCHAs block bots. AAP blocks humans. 🤖
`);
});

// ============== GRACEFUL SHUTDOWN ==============
let isShuttingDown = false;

function gracefulShutdown(signal) {
  if (isShuttingDown) return;
  isShuttingDown = true;
  
  console.log(`\n[AAP] ${signal} received, shutting down gracefully...`);
  
  server.close(() => {
    console.log('[AAP] HTTP server closed');
    console.log(`[AAP] Final stats: ${metrics.verifications.success} successful verifications`);
    process.exit(0);
  });
  
  // Force exit after 10 seconds
  setTimeout(() => {
    console.error('[AAP] Forced shutdown after timeout');
    process.exit(1);
  }, 10000);
}

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));
