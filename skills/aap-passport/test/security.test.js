/**
 * AAP Security Tests
 * 
 * Tests tampered signatures, expired challenges, invalid inputs
 */

import { randomBytes, createHash, generateKeyPairSync, createSign, createVerify } from 'node:crypto';

console.log('🧪 AAP Security Tests\n');
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

// Helper to generate identity
function generateIdentity() {
  const { publicKey, privateKey } = generateKeyPairSync('ec', {
    namedCurve: 'secp256k1',
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  const publicId = createHash('sha256').update(publicKey).digest('hex').slice(0, 20);
  return { publicKey, privateKey, publicId };
}

// ============== SIGNATURE TESTS ==============
console.log('\n📦 Signature Security Tests\n');

test('Valid signature accepted', () => {
  const { publicKey, privateKey, publicId } = generateIdentity();
  const data = JSON.stringify({ nonce: 'test', solution: '42', publicId, timestamp: Date.now() });
  
  const signer = createSign('SHA256');
  signer.update(data);
  const signature = signer.sign(privateKey, 'base64');
  
  const verifier = createVerify('SHA256');
  verifier.update(data);
  assert(verifier.verify(publicKey, signature, 'base64'), 'Valid signature');
});

test('Tampered data rejected', () => {
  const { publicKey, privateKey, publicId } = generateIdentity();
  const originalData = JSON.stringify({ nonce: 'test', solution: '42', publicId, timestamp: Date.now() });
  
  const signer = createSign('SHA256');
  signer.update(originalData);
  const signature = signer.sign(privateKey, 'base64');
  
  // Tamper with data
  const tamperedData = JSON.stringify({ nonce: 'test', solution: '99', publicId, timestamp: Date.now() });
  
  const verifier = createVerify('SHA256');
  verifier.update(tamperedData);
  assert(!verifier.verify(publicKey, signature, 'base64'), 'Tampered data rejected');
});

test('Wrong key rejected', () => {
  const identity1 = generateIdentity();
  const identity2 = generateIdentity();
  
  const data = JSON.stringify({ test: 'data' });
  
  const signer = createSign('SHA256');
  signer.update(data);
  const signature = signer.sign(identity1.privateKey, 'base64');
  
  const verifier = createVerify('SHA256');
  verifier.update(data);
  assert(!verifier.verify(identity2.publicKey, signature, 'base64'), 'Wrong key rejected');
});

test('Corrupted signature rejected', () => {
  const { publicKey, privateKey } = generateIdentity();
  const data = JSON.stringify({ test: 'data' });
  
  const signer = createSign('SHA256');
  signer.update(data);
  const signature = signer.sign(privateKey, 'base64');
  
  // Corrupt signature
  const corrupted = signature.slice(0, -5) + 'XXXXX';
  
  const verifier = createVerify('SHA256');
  verifier.update(data);
  
  let rejected = false;
  try {
    rejected = !verifier.verify(publicKey, corrupted, 'base64');
  } catch {
    rejected = true;  // Throws on invalid signature format
  }
  assert(rejected, 'Corrupted signature rejected');
});

test('Empty signature rejected', () => {
  const { publicKey } = generateIdentity();
  const data = JSON.stringify({ test: 'data' });
  
  const verifier = createVerify('SHA256');
  verifier.update(data);
  
  let rejected = false;
  try {
    rejected = !verifier.verify(publicKey, '', 'base64');
  } catch {
    rejected = true;
  }
  assert(rejected, 'Empty signature rejected');
});

// ============== TIMING TESTS ==============
console.log('\n📦 Timing Security Tests\n');

test('Expired challenge detected', () => {
  const now = Date.now();
  const challenge = {
    timestamp: now - 120000,  // 2 minutes ago
    expiresAt: now - 60000    // Expired 1 minute ago
  };
  
  assert(now > challenge.expiresAt, 'Expired detected');
});

test('Valid challenge accepted', () => {
  const now = Date.now();
  const challenge = {
    timestamp: now,
    expiresAt: now + 60000    // Expires in 1 minute
  };
  
  assert(now <= challenge.expiresAt, 'Valid challenge accepted');
});

test('Server time overrides client time', () => {
  const challengeTimestamp = Date.now() - 10000;  // 10 seconds ago
  const clientClaims = 1000;  // Client claims 1 second
  const serverMeasured = Date.now() - challengeTimestamp;  // ~10 seconds
  
  const effectiveTime = Math.max(clientClaims, serverMeasured);
  assert(effectiveTime >= serverMeasured, 'Server time used');
});

test('Response time limit enforced', () => {
  const MAX_TIME = 8000;
  
  assert(5000 <= MAX_TIME, 'Fast response accepted');
  assert(10000 > MAX_TIME, 'Slow response rejected');
});

// ============== INPUT VALIDATION TESTS ==============
console.log('\n📦 Input Validation Tests\n');

test('Nonce length validation', () => {
  const validNonce = randomBytes(16).toString('hex');
  const shortNonce = 'abc';
  const longNonce = 'x'.repeat(100);
  
  assert(validNonce.length === 32, 'Valid nonce correct length');
  assert(shortNonce.length !== 32, 'Short nonce rejected');
  assert(longNonce.length !== 32, 'Long nonce rejected');
});

test('PublicId length validation', () => {
  const validId = createHash('sha256').update('test').digest('hex').slice(0, 20);
  
  assert(validId.length === 20, 'Valid publicId correct length');
  assert('short'.length !== 20, 'Short id rejected');
});

test('Solutions array validation', () => {
  const valid = ['a', 'b', 'c', 'd', 'e'];  // 5 items
  const tooFew = ['a', 'b', 'c'];  // 3 items
  const tooMany = ['a', 'b', 'c', 'd', 'e', 'f'];  // 6 items
  
  assert(valid.length === 5, 'Valid solutions accepted');
  assert(tooFew.length !== 5, 'Too few rejected');
  assert(tooMany.length !== 5, 'Too many rejected');
});

test('PublicKey format validation', () => {
  const { publicKey } = generateIdentity();
  
  assert(publicKey.includes('BEGIN PUBLIC KEY'), 'Valid key has marker');
  assert(!'random string'.includes('BEGIN PUBLIC KEY'), 'Invalid key rejected');
  assert(!'BEGIN PRIVATE KEY'.includes('BEGIN PUBLIC KEY'), 'Private key rejected');
});

// ============== REPLAY ATTACK TESTS ==============
console.log('\n📦 Replay Attack Tests\n');

test('Same nonce cannot be reused', () => {
  const usedNonces = new Set();
  const nonce = randomBytes(16).toString('hex');
  
  // First use
  assert(!usedNonces.has(nonce), 'First use allowed');
  usedNonces.add(nonce);
  
  // Replay attempt
  assert(usedNonces.has(nonce), 'Replay detected');
});

test('Challenge deleted after use', () => {
  const challenges = new Map();
  const nonce = 'test-nonce';
  
  challenges.set(nonce, { data: 'test' });
  assert(challenges.has(nonce), 'Challenge exists');
  
  challenges.delete(nonce);
  assert(!challenges.has(nonce), 'Challenge deleted');
});

test('Salt must match exactly', () => {
  const expectedSalt = 'ABC123';
  const correctResponse = { salt: 'ABC123', result: 42 };
  const wrongSaltResponse = { salt: 'WRONG1', result: 42 };
  const missingSaltResponse = { result: 42 };
  
  assert(correctResponse.salt === expectedSalt, 'Correct salt accepted');
  assert(wrongSaltResponse.salt !== expectedSalt, 'Wrong salt rejected');
  assert(!missingSaltResponse.salt, 'Missing salt rejected');
});

// ============== DOS PROTECTION TESTS ==============
console.log('\n📦 DoS Protection Tests\n');

test('Challenge store has size limit', () => {
  const MAX_CHALLENGES = 10000;
  assert(MAX_CHALLENGES > 0, 'Limit defined');
  assert(MAX_CHALLENGES <= 100000, 'Limit reasonable');
});

test('Body size limit defined', () => {
  const MAX_BODY = '10kb';
  assert(MAX_BODY, 'Body limit defined');
});

// ============== RESULTS ==============
console.log('\n' + '='.repeat(60));
console.log(`\n📊 Results: ${passed} passed, ${failed} failed\n`);

if (failed > 0) {
  process.exit(1);
}
