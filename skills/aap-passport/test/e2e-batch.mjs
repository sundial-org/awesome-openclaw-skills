/**
 * AAP v2.0 - End-to-End Batch Test
 * 
 * Tests complete flow: Challenge → Solve → Sign → Verify
 */

import { randomBytes, createHash, generateKeyPairSync, createSign, createVerify } from 'node:crypto';

console.log('🧪 AAP v2.5 - Burst Mode E2E Test\n');
console.log('='.repeat(60));

// ============== CONFIG ==============
const BATCH_SIZE = 5;  // v2.5 Burst Mode
const MAX_RESPONSE_TIME_MS = 8000;  // v2.5: 8초

// ============== WORD POOLS ==============
const WORD_POOLS = {
  animals: ['cat', 'dog', 'rabbit', 'tiger', 'lion', 'elephant', 'giraffe', 'penguin', 'eagle', 'shark'],
  fruits: ['apple', 'banana', 'orange', 'grape', 'strawberry'],
  colors: ['red', 'blue', 'yellow', 'green', 'purple'],
  verbs: ['runs', 'eats', 'sleeps', 'plays']
};

function seededNumber(nonce, offset, min, max) {
  const seed = parseInt(nonce.slice(offset, offset + 4), 16);
  return (seed % (max - min + 1)) + min;
}

function seededSelect(arr, nonce, count, offset = 0) {
  const seed = parseInt(nonce.slice(offset, offset + 4), 16);
  const results = [];
  for (let i = 0; i < count; i++) {
    results.push(arr[(seed + i * 7) % arr.length]);
  }
  return results;
}

// ============== CHALLENGE GENERATORS (v2.5 with salt) ==============
function generateSalt(nonce, offset = 0) {
  return nonce.slice(offset, offset + 6).toUpperCase();
}

const CHALLENGE_TYPES = {
  nlp_math: (nonce) => {
    const salt = generateSalt(nonce, 0);
    const a = seededNumber(nonce, 0, 10, 50);
    const b = seededNumber(nonce, 2, 5, 20);
    const c = seededNumber(nonce, 4, 2, 5);
    const expected = (a - b) * c;
    return {
      challenge_string: `[REQ-${salt}] Subtract ${b} from ${a}, then multiply the result by ${c}.\nResponse format: {"salt": "${salt}", "result": number}`,
      validate: (sol) => {
        try {
          const m = sol.match(/\{[\s\S]*\}/);
          if (!m) return false;
          const obj = JSON.parse(m[0]);
          if (obj.salt !== salt) return false;
          return Math.abs(obj.result - expected) < 0.01;
        } catch { return false; }
      },
      solve: () => JSON.stringify({ salt, result: expected })
    };
  },

  nlp_extract: (nonce) => {
    const salt = generateSalt(nonce, 2);
    const targets = seededSelect(WORD_POOLS.animals, nonce, 2, 0);
    const verb = seededSelect(WORD_POOLS.verbs, nonce, 1, 4)[0];
    const sentence = `The ${targets[0]} and ${targets[1]} ${verb} in the park.`;
    return {
      challenge_string: `[REQ-${salt}] Extract only the animals from the following sentence.\nSentence: "${sentence}"\nResponse format: {"salt": "${salt}", "items": ["item1", "item2"]}`,
      validate: (sol) => {
        try {
          const m = sol.match(/\{[\s\S]*\}/);
          if (!m) return false;
          const obj = JSON.parse(m[0]);
          if (obj.salt !== salt) return false;
          const items = obj.items.map(s => s.toLowerCase()).sort();
          return JSON.stringify(items) === JSON.stringify(targets.map(s => s.toLowerCase()).sort());
        } catch { return false; }
      },
      solve: () => JSON.stringify({ salt, items: targets })
    };
  },

  nlp_logic: (nonce) => {
    const salt = generateSalt(nonce, 4);
    const a = seededNumber(nonce, 0, 10, 100);
    const b = seededNumber(nonce, 2, 10, 100);
    const threshold = seededNumber(nonce, 4, 20, 80);
    const expected = Math.max(a, b) > threshold ? "YES" : "NO";
    return {
      challenge_string: `[REQ-${salt}] If the larger number between ${a} and ${b} is greater than ${threshold}, answer "YES". Otherwise, answer "NO".\nResponse format: {"salt": "${salt}", "answer": "your answer"}`,
      validate: (sol) => {
        try {
          const m = sol.match(/\{[\s\S]*\}/);
          if (!m) return false;
          const obj = JSON.parse(m[0]);
          if (obj.salt !== salt) return false;
          return obj.answer?.toUpperCase() === expected;
        } catch { return false; }
      },
      solve: () => JSON.stringify({ salt, answer: expected })
    };
  },

  nlp_count: (nonce) => {
    const salt = generateSalt(nonce, 6);
    const count = seededNumber(nonce, 0, 2, 4);
    const animals = seededSelect(WORD_POOLS.animals, nonce, count, 0);
    const countries = seededSelect(WORD_POOLS.colors, nonce, 2, 4);
    const mixed = [...animals, ...countries].sort();
    return {
      challenge_string: `[REQ-${salt}] Count only the animals: ${mixed.join(', ')}\nResponse format: {"salt": "${salt}", "count": number}`,
      validate: (sol) => {
        try {
          const m = sol.match(/\{[\s\S]*\}/);
          if (!m) return false;
          const obj = JSON.parse(m[0]);
          if (obj.salt !== salt) return false;
          return parseInt(obj.count) === count;
        } catch { return false; }
      },
      solve: () => JSON.stringify({ salt, count })
    };
  },

  nlp_transform: (nonce) => {
    const salt = generateSalt(nonce, 8);
    const input = nonce.slice(10, 16);
    const expected = input.split('').reverse().join('').toUpperCase();
    return {
      challenge_string: `[REQ-${salt}] Reverse "${input}" and uppercase it.\nResponse format: {"salt": "${salt}", "output": "result"}`,
      validate: (sol) => {
        try {
          const m = sol.match(/\{[\s\S]*\}/);
          if (!m) return false;
          const obj = JSON.parse(m[0]);
          if (obj.salt !== salt) return false;
          return obj.output === expected;
        } catch { return false; }
      },
      solve: () => JSON.stringify({ salt, output: expected })
    };
  }
};

// ============== SERVER SIMULATION ==============
class MockServer {
  constructor() {
    this.challenges = new Map();
  }

  generateChallenge() {
    const nonce = randomBytes(16).toString('hex');
    const timestamp = Date.now();
    const types = Object.keys(CHALLENGE_TYPES);
    const batch = [];
    const validators = [];
    const solvers = [];

    for (let i = 0; i < BATCH_SIZE; i++) {
      const offsetNonce = nonce.slice(i * 2) + nonce.slice(0, i * 2);
      const type = types[i % types.length];
      const { challenge_string, validate, solve } = CHALLENGE_TYPES[type](offsetNonce);
      
      batch.push({ id: i, type, challenge_string });
      validators.push(validate);
      solvers.push(solve);
    }

    this.challenges.set(nonce, { validators, timestamp, expiresAt: timestamp + 60000 });

    return { nonce, challenges: batch, timestamp, _solvers: solvers };
  }

  verify({ solutions, signature, publicKey, publicId, nonce, timestamp, responseTimeMs }) {
    const challenge = this.challenges.get(nonce);
    if (!challenge) return { verified: false, error: 'Challenge not found' };
    
    this.challenges.delete(nonce);
    
    if (Date.now() > challenge.expiresAt) return { verified: false, error: 'Expired' };
    
    // Validate solutions
    let passed = 0;
    const results = [];
    for (let i = 0; i < BATCH_SIZE; i++) {
      const sol = typeof solutions[i] === 'string' ? solutions[i] : JSON.stringify(solutions[i]);
      const valid = challenge.validators[i](sol);
      results.push({ id: i, valid });
      if (valid) passed++;
    }

    if (passed < BATCH_SIZE) {
      return { verified: false, error: `${passed}/${BATCH_SIZE} correct`, batchResult: { passed, results } };
    }

    // Check timing
    if (responseTimeMs > MAX_RESPONSE_TIME_MS) {
      return { verified: false, error: `Too slow: ${responseTimeMs}ms` };
    }

    // Verify signature
    const proofData = JSON.stringify({ nonce, solution: JSON.stringify(solutions), publicId, timestamp });
    const verifier = createVerify('SHA256');
    verifier.update(proofData);
    
    if (!verifier.verify(publicKey, signature, 'base64')) {
      return { verified: false, error: 'Invalid signature' };
    }

    return { verified: true, role: 'AI_AGENT', publicId, batchResult: { passed, results } };
  }
}

// ============== CLIENT SIMULATION ==============
class MockClient {
  constructor() {
    const { publicKey, privateKey } = generateKeyPairSync('ec', {
      namedCurve: 'secp256k1',
      publicKeyEncoding: { type: 'spki', format: 'pem' },
      privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
    });
    
    this.publicKey = publicKey;
    this.privateKey = privateKey;
    this.publicId = createHash('sha256').update(publicKey).digest('hex').slice(0, 20);
  }

  generateProof(challengeResponse, solvers) {
    const startTime = Date.now();
    const { nonce, challenges } = challengeResponse;
    
    // Solve challenges (simulating LLM)
    const solutions = solvers.map(solve => solve());
    
    const timestamp = Date.now();
    const responseTimeMs = timestamp - startTime;
    
    // Sign
    const proofData = JSON.stringify({ nonce, solution: JSON.stringify(solutions), publicId: this.publicId, timestamp });
    const signer = createSign('SHA256');
    signer.update(proofData);
    const signature = signer.sign(this.privateKey, 'base64');

    return {
      solutions,
      signature,
      publicKey: this.publicKey,
      publicId: this.publicId,
      nonce,
      timestamp,
      responseTimeMs
    };
  }
}

// ============== RUN TEST ==============
const server = new MockServer();
const client = new MockClient();

console.log(`\nAgent Public ID: ${client.publicId}\n`);

// Step 1: Server generates challenge
console.log('📤 Step 1: Server generates batch challenge\n');
const challengeResponse = server.generateChallenge();

console.log(`Nonce: ${challengeResponse.nonce}`);
challengeResponse.challenges.forEach((c, i) => {
  console.log(`\n[${i}] ${c.type}:`);
  console.log(`    ${c.challenge_string.split('\n')[0]}`);
});

// Step 2: Client solves and signs
console.log('\n\n📥 Step 2: Client solves challenges and signs proof\n');
const proof = client.generateProof(challengeResponse, challengeResponse._solvers);

console.log('Solutions:');
proof.solutions.forEach((s, i) => console.log(`  [${i}] ${s}`));
console.log(`\nResponse time: ${proof.responseTimeMs}ms`);
console.log(`Signature: ${proof.signature.slice(0, 40)}...`);

// Step 3: Server verifies
console.log('\n\n✅ Step 3: Server verifies proof\n');
const result = server.verify(proof);

console.log('Verification result:');
console.log(JSON.stringify(result, null, 2));

console.log('\n' + '='.repeat(60));
console.log(`\n🎯 FINAL RESULT: ${result.verified ? '✅ VERIFIED AS AI_AGENT' : '❌ VERIFICATION FAILED'}`);

// Run edge case tests
console.log('\n\n' + '='.repeat(60));
console.log('🧪 Edge Case Tests\n');

// Test 1: Wrong solution
console.log('Test 1: Wrong solution');
const badChallenge = server.generateChallenge();
const badProof = client.generateProof(badChallenge, badChallenge._solvers);
badProof.solutions[0] = '{"result": 99999}';  // Wrong answer
const badResult = server.verify(badProof);
console.log(`  Expected: FAIL | Actual: ${badResult.verified ? 'PASS ❌' : 'FAIL ✅'}`);

// Test 2: Expired challenge
console.log('\nTest 2: Reused nonce');
const expiredResult = server.verify(proof);  // Same nonce, already used
console.log(`  Expected: FAIL | Actual: ${expiredResult.verified ? 'PASS ❌' : 'FAIL ✅'}`);

// Test 3: Invalid signature
console.log('\nTest 3: Tampered signature');
const tamperedChallenge = server.generateChallenge();
const tamperedProof = client.generateProof(tamperedChallenge, tamperedChallenge._solvers);
tamperedProof.signature = 'INVALID_SIGNATURE';
const tamperedResult = server.verify(tamperedProof);
console.log(`  Expected: FAIL | Actual: ${tamperedResult.verified ? 'PASS ❌' : 'FAIL ✅'}`);

console.log('\n' + '='.repeat(60));
console.log('✅ All E2E tests completed!\n');
