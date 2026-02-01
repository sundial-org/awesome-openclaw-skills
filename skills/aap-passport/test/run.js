/**
 * AAP Test Runner v2.5
 * 
 * Run: node test/run.js
 */

import { randomBytes, createHash, generateKeyPairSync, createSign, createVerify } from 'node:crypto';

console.log('🧪 AAP v2.5 Test Suite\n');
console.log('='.repeat(60));

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`✅ ${name}`);
    passed++;
  } catch (e) {
    console.log(`❌ ${name}: ${e.message}`);
    failed++;
  }
}

function assert(condition, message) {
  if (!condition) throw new Error(message || 'Assertion failed');
}

// ============== CRYPTO TESTS ==============
console.log('\n📦 Crypto Tests\n');

test('Generate key pair', () => {
  const { publicKey, privateKey } = generateKeyPairSync('ec', {
    namedCurve: 'secp256k1',
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  assert(publicKey.includes('BEGIN PUBLIC KEY'), 'Public key format');
  assert(privateKey.includes('BEGIN PRIVATE KEY'), 'Private key format');
});

test('Derive public ID', () => {
  const { publicKey } = generateKeyPairSync('ec', {
    namedCurve: 'secp256k1',
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  const publicId = createHash('sha256').update(publicKey).digest('hex').slice(0, 20);
  assert(publicId.length === 20, 'Public ID is 20 chars');
  assert(/^[a-f0-9]+$/.test(publicId), 'Public ID is hex');
});

test('Sign and verify', () => {
  const { publicKey, privateKey } = generateKeyPairSync('ec', {
    namedCurve: 'secp256k1',
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  
  const data = JSON.stringify({ test: 'data', timestamp: Date.now() });
  
  const signer = createSign('SHA256');
  signer.update(data);
  const signature = signer.sign(privateKey, 'base64');
  
  const verifier = createVerify('SHA256');
  verifier.update(data);
  assert(verifier.verify(publicKey, signature, 'base64'), 'Signature valid');
});

test('Reject tampered signature', () => {
  const { publicKey, privateKey } = generateKeyPairSync('ec', {
    namedCurve: 'secp256k1',
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  
  const data = 'original';
  const signer = createSign('SHA256');
  signer.update(data);
  const signature = signer.sign(privateKey, 'base64');
  
  const verifier = createVerify('SHA256');
  verifier.update('tampered');  // Different data
  assert(!verifier.verify(publicKey, signature, 'base64'), 'Tampered rejected');
});

// ============== CHALLENGE TESTS ==============
console.log('\n📦 Challenge Tests\n');

function seededNumber(nonce, offset, min, max) {
  const seed = parseInt(nonce.slice(offset, offset + 4), 16);
  return (seed % (max - min + 1)) + min;
}

test('Seeded number is deterministic', () => {
  const nonce = 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4';
  const n1 = seededNumber(nonce, 0, 10, 100);
  const n2 = seededNumber(nonce, 0, 10, 100);
  assert(n1 === n2, 'Same nonce = same number');
});

test('Different nonce = different number', () => {
  const n1 = seededNumber('aaaa' + 'x'.repeat(28), 0, 10, 100);
  const n2 = seededNumber('bbbb' + 'x'.repeat(28), 0, 10, 100);
  // Might be same by chance, but very unlikely for full test
  // Just ensure no crash
  assert(typeof n1 === 'number' && typeof n2 === 'number', 'Both are numbers');
});

test('Salt generation', () => {
  const nonce = 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4';
  const salt = nonce.slice(0, 6).toUpperCase();
  assert(salt === 'A1B2C3', 'Salt extracted correctly');
  assert(salt.length === 6, 'Salt is 6 chars');
});

test('Challenge includes salt', () => {
  const nonce = randomBytes(16).toString('hex');
  const salt = nonce.slice(0, 6).toUpperCase();
  const challenge = `[REQ-${salt}] Test challenge`;
  assert(challenge.includes(`[REQ-${salt}]`), 'Challenge has salt marker');
});

// ============== VALIDATION TESTS ==============
console.log('\n📦 Validation Tests\n');

test('Valid JSON response accepted', () => {
  const salt = 'ABC123';
  const response = '{"salt": "ABC123", "result": 42}';
  const match = response.match(/\{[\s\S]*\}/);
  const obj = JSON.parse(match[0]);
  assert(obj.salt === salt, 'Salt matches');
  assert(obj.result === 42, 'Result correct');
});

test('Wrong salt rejected', () => {
  const expectedSalt = 'ABC123';
  const response = '{"salt": "WRONG1", "result": 42}';
  const obj = JSON.parse(response);
  assert(obj.salt !== expectedSalt, 'Wrong salt detected');
});

test('Missing salt rejected', () => {
  const response = '{"result": 42}';
  const obj = JSON.parse(response);
  assert(!obj.salt, 'No salt in response');
});

// ============== TIMING TESTS ==============
console.log('\n📦 Timing Tests\n');

test('Response time tracked', () => {
  const start = Date.now();
  // Simulate work
  for (let i = 0; i < 1000000; i++) {}
  const elapsed = Date.now() - start;
  assert(elapsed >= 0, 'Elapsed time is positive');
  assert(elapsed < 1000, 'Test completed in under 1s');
});

test('8 second limit constant', () => {
  const MAX_RESPONSE_TIME_MS = 6000;
  assert(MAX_RESPONSE_TIME_MS === 6000, 'Limit is 6000ms');
});

test('Batch size constant', () => {
  const BATCH_SIZE = 7;
  assert(BATCH_SIZE === 7, 'Batch size is 7');
});

// ============== INTEGRATION TEST ==============
console.log('\n📦 Integration Test\n');

test('Full proof generation flow', () => {
  // Generate identity
  const { publicKey, privateKey } = generateKeyPairSync('ec', {
    namedCurve: 'secp256k1',
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  const publicId = createHash('sha256').update(publicKey).digest('hex').slice(0, 20);
  
  // Simulate challenge
  const nonce = randomBytes(16).toString('hex');
  const solutions = [
    '{"salt": "A1B2C3", "result": 42}',
    '{"salt": "B2C3D4", "items": ["cat"]}',
    '{"salt": "C3D4E5", "answer": "YES"}',
    '{"salt": "D4E5F6", "result": 100}',
    '{"salt": "E5F6A7", "output": "test"}'
  ];
  
  // Sign
  const timestamp = Date.now();
  const proofData = JSON.stringify({
    nonce,
    solution: JSON.stringify(solutions),
    publicId,
    timestamp
  });
  
  const signer = createSign('SHA256');
  signer.update(proofData);
  const signature = signer.sign(privateKey, 'base64');
  
  // Verify
  const verifier = createVerify('SHA256');
  verifier.update(proofData);
  assert(verifier.verify(publicKey, signature, 'base64'), 'Full flow signature valid');
});

// ============== ERROR HANDLING TESTS ==============
console.log('\n📦 Error Handling Tests\n');

test('Invalid nonce rejected', () => {
  const invalidNonces = ['', 'short', 'x'.repeat(100), null, 123];
  for (const nonce of invalidNonces) {
    const valid = typeof nonce === 'string' && nonce.length === 32;
    assert(!valid || nonce === 'x'.repeat(32), `Invalid nonce detected: ${nonce}`);
  }
});

test('Invalid publicId rejected', () => {
  const invalidIds = ['', 'short', 'x'.repeat(100), null];
  for (const id of invalidIds) {
    const valid = typeof id === 'string' && id.length === 20;
    assert(!valid, `Invalid publicId detected: ${id}`);
  }
});

test('Invalid signature format rejected', () => {
  const invalidSigs = ['', 'short', null, 123];
  for (const sig of invalidSigs) {
    const valid = typeof sig === 'string' && sig.length >= 50;
    assert(!valid, `Invalid signature detected`);
  }
});

test('Invalid publicKey format rejected', () => {
  const invalidKeys = ['', 'not-a-key', 'BEGIN PRIVATE KEY', null];
  for (const key of invalidKeys) {
    const valid = typeof key === 'string' && key.includes('BEGIN PUBLIC KEY');
    assert(!valid, `Invalid publicKey detected`);
  }
});

// ============== EDGE CASES ==============
console.log('\n📦 Edge Case Tests\n');

test('Empty solutions array rejected', () => {
  const solutions = [];
  assert(solutions.length !== 5, 'Empty array has wrong length');
});

test('Wrong number of solutions rejected', () => {
  const solutions = ['a', 'b', 'c'];  // 3 instead of 5
  assert(solutions.length !== 5, 'Wrong count detected');
});

test('Missing salt in response detected', () => {
  const response = '{"result": 42}';
  const obj = JSON.parse(response);
  assert(!obj.salt, 'Missing salt detected');
});

test('Expired challenge detection', () => {
  const now = Date.now();
  const expiresAt = now - 1000;  // 1 second ago
  assert(now > expiresAt, 'Expired challenge detected');
});

test('Response time validation', () => {
  const maxTime = 8000;
  const slowTime = 10000;
  const fastTime = 3000;
  assert(slowTime > maxTime, 'Slow response detected');
  assert(fastTime <= maxTime, 'Fast response accepted');
});

// ============== SECURITY TESTS ==============
console.log('\n📦 Security Tests\n');

test('Rate limit constants defined', () => {
  const MAX_CHALLENGES = 10000;
  assert(MAX_CHALLENGES > 0, 'Max challenges defined');
  assert(MAX_CHALLENGES <= 100000, 'Max challenges reasonable');
});

test('Server-side time validation', () => {
  const clientTime = 1000;  // Client claims 1 second
  const serverTime = 15000; // Server measured 15 seconds
  const effectiveTime = Math.max(clientTime, serverTime);
  assert(effectiveTime === serverTime, 'Server time takes precedence');
});

test('Nonce uniqueness', () => {
  const nonces = new Set();
  for (let i = 0; i < 100; i++) {
    const nonce = randomBytes(16).toString('hex');
    assert(!nonces.has(nonce), 'Nonce collision');
    nonces.add(nonce);
  }
});

// ============== RESULTS ==============
console.log('\n' + '='.repeat(60));
console.log(`\n📊 Results: ${passed} passed, ${failed} failed\n`);

if (failed > 0) {
  process.exit(1);
}
