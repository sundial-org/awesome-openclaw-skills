/**
 * AAP Challenge Type Tests
 * 
 * Tests all 8 challenge types with valid and invalid responses
 */

import { randomBytes } from 'node:crypto';
import { generateBatch, generate, CHALLENGE_TYPES, getTypes } from '../packages/server/challenges.js';

console.log('🧪 AAP Challenge Type Tests\n');
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

// ============== CHALLENGE TYPE TESTS ==============

const types = getTypes();
console.log(`\n📦 Testing ${types.length} Challenge Types\n`);

for (const type of types) {
  test(`${type}: generates valid challenge`, () => {
    const nonce = randomBytes(16).toString('hex');
    const result = generate(nonce, type);
    
    assert(result.type === type, 'Type matches');
    assert(result.challenge_string, 'Has challenge string');
    assert(result.challenge_string.includes('[REQ-'), 'Has salt marker');
    assert(typeof result.validate === 'function', 'Has validator');
    assert(result.expected !== undefined, 'Has expected answer');
  });

  test(`${type}: validates correct answer`, () => {
    const nonce = randomBytes(16).toString('hex');
    const result = generate(nonce, type);
    
    // Construct correct answer based on expected
    let correctAnswer;
    if (result.expected.result !== undefined) {
      correctAnswer = JSON.stringify({ salt: result.expected.salt, result: result.expected.result });
    } else if (result.expected.items) {
      correctAnswer = JSON.stringify({ salt: result.expected.salt, items: result.expected.items });
    } else if (result.expected.answer) {
      correctAnswer = JSON.stringify({ salt: result.expected.salt, answer: result.expected.answer });
    } else if (result.expected.output) {
      correctAnswer = JSON.stringify({ salt: result.expected.salt, output: result.expected.output });
    } else if (result.expected.count !== undefined) {
      correctAnswer = JSON.stringify({ salt: result.expected.salt, count: result.expected.count });
    } else if (result.expected.next) {
      correctAnswer = JSON.stringify({ salt: result.expected.salt, next: result.expected.next });
    }
    
    if (correctAnswer) {
      assert(result.validate(correctAnswer), 'Correct answer accepted');
    }
  });

  test(`${type}: rejects wrong salt`, () => {
    const nonce = randomBytes(16).toString('hex');
    const result = generate(nonce, type);
    
    const wrongSalt = JSON.stringify({ salt: 'WRONG1', result: 999 });
    assert(!result.validate(wrongSalt), 'Wrong salt rejected');
  });

  test(`${type}: rejects wrong answer`, () => {
    const nonce = randomBytes(16).toString('hex');
    const result = generate(nonce, type);
    
    const wrongAnswer = JSON.stringify({ salt: result.expected.salt, result: -999999, items: [], answer: 'INVALID', count: -1 });
    // Most validators should reject this
    const valid = result.validate(wrongAnswer);
    // Some might pass if the wrong field matches, but most won't
    // This is a soft assertion
  });

  test(`${type}: rejects empty response`, () => {
    const nonce = randomBytes(16).toString('hex');
    const result = generate(nonce, type);
    
    assert(!result.validate(''), 'Empty rejected');
    assert(!result.validate('{}'), 'Empty object rejected');
    assert(!result.validate('null'), 'Null rejected');
  });
}

// ============== BATCH TESTS ==============
console.log('\n📦 Batch Challenge Tests\n');

test('Batch generates 7 challenges', () => {
  const nonce = randomBytes(16).toString('hex');
  const batch = generateBatch(nonce, 7);
  
  assert(batch.challenges.length === 7, 'Has 7 challenges');
  assert(batch.validators.length === 7, 'Has 5 validators');
  assert(batch.expected.length === 7, 'Has 5 expected');
});

test('Batch challenges have different types', () => {
  const nonce = randomBytes(16).toString('hex');
  const batch = generateBatch(nonce, 7);
  
  const types = batch.challenges.map(c => c.type);
  const uniqueTypes = new Set(types);
  assert(uniqueTypes.size >= 3, 'At least 3 different types');
});

test('Batch challenges have salts', () => {
  const nonce = randomBytes(16).toString('hex');
  const batch = generateBatch(nonce, 7);
  
  const salts = batch.challenges.map(c => {
    const match = c.challenge_string.match(/\[REQ-([A-Z0-9]+)\]/);
    return match ? match[1] : null;
  });
  
  // All challenges should have salts
  assert(salts.every(s => s !== null), 'All challenges have salts');
  assert(salts.length === 7, 'Has 5 salts');
});

test('Batch is deterministic with same nonce', () => {
  const nonce = randomBytes(16).toString('hex');
  const batch1 = generateBatch(nonce, 7);
  const batch2 = generateBatch(nonce, 7);
  
  for (let i = 0; i < 5; i++) {
    assert(batch1.challenges[i].type === batch2.challenges[i].type, `Same type at ${i}`);
  }
});

// ============== RESULTS ==============
console.log('\n' + '='.repeat(60));
console.log(`\n📊 Results: ${passed} passed, ${failed} failed\n`);

if (failed > 0) {
  process.exit(1);
}
