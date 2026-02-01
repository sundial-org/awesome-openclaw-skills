/**
 * AAP v2.0 - LLM Batch Test via Clawdbot Agent
 * 
 * Uses clawdbot agent command to test with actual LLM
 */

import { execSync } from 'node:child_process';
import { randomBytes, createHash, generateKeyPairSync } from 'node:crypto';

// ============== WORD POOLS ==============
const WORD_POOLS = {
  animals: ['cat', 'dog', 'rabbit', 'tiger', 'lion', 'elephant', 'giraffe', 'penguin', 'eagle', 'shark'],
  fruits: ['apple', 'banana', 'orange', 'grape', 'strawberry', 'watermelon', 'peach', 'kiwi', 'mango', 'cherry'],
  verbs: ['runs', 'eats', 'sleeps', 'plays', 'works', 'studies', 'travels', 'cooks']
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

// ============== CHALLENGE GENERATORS ==============
const CHALLENGES = {
  nlp_math: (nonce) => {
    const a = seededNumber(nonce, 0, 10, 50);
    const b = seededNumber(nonce, 2, 5, 20);
    const c = seededNumber(nonce, 4, 2, 5);
    const expected = (a - b) * c;
    return {
      challenge_string: `Subtract ${b} from ${a}, then multiply the result by ${c}.\nResponse format: {"result": number}`,
      validate: (sol) => {
        try {
          const m = sol.match(/\{[\s\S]*?"result"[\s\S]*?\}/);
          if (!m) return { valid: false, reason: 'No JSON found' };
          const obj = JSON.parse(m[0]);
          const valid = Math.abs(obj.result - expected) < 0.01;
          return { valid, got: obj.result, expected };
        } catch (e) { return { valid: false, reason: e.message }; }
      },
      expected
    };
  },

  nlp_extract: (nonce) => {
    const targets = seededSelect(WORD_POOLS.animals, nonce, 2, 0);
    const verb = seededSelect(WORD_POOLS.verbs, nonce, 1, 4)[0];
    const sentence = `The ${targets[0]} and ${targets[1]} ${verb} in the park.`;
    return {
      challenge_string: `Extract only the animals from the following sentence and respond as a JSON array.\nSentence: "${sentence}"\nResponse format: {"items": ["item1", "item2"]}`,
      validate: (sol) => {
        try {
          const m = sol.match(/\{[\s\S]*?"items"[\s\S]*?\}/);
          if (!m) return { valid: false, reason: 'No JSON found' };
          const obj = JSON.parse(m[0]);
          const items = (obj.items || []).map(s => s.toLowerCase()).sort();
          const exp = targets.map(s => s.toLowerCase()).sort();
          const valid = JSON.stringify(items) === JSON.stringify(exp);
          return { valid, got: items, expected: exp };
        } catch (e) { return { valid: false, reason: e.message }; }
      },
      expected: targets
    };
  },

  nlp_logic: (nonce) => {
    const a = seededNumber(nonce, 0, 10, 100);
    const b = seededNumber(nonce, 2, 10, 100);
    const threshold = seededNumber(nonce, 4, 20, 80);
    const expected = Math.max(a, b) > threshold ? "YES" : "NO";
    return {
      challenge_string: `If the larger number between ${a} and ${b} is greater than ${threshold}, answer "YES". Otherwise, answer "NO".\nResponse format: {"answer": "your answer"}`,
      validate: (sol) => {
        try {
          const m = sol.match(/\{[\s\S]*?"answer"[\s\S]*?\}/);
          if (!m) return { valid: false, reason: 'No JSON found' };
          const obj = JSON.parse(m[0]);
          const valid = obj.answer?.toUpperCase() === expected;
          return { valid, got: obj.answer, expected };
        } catch (e) { return { valid: false, reason: e.message }; }
      },
      expected
    };
  }
};

// ============== MAIN ==============
async function main() {
  console.log('🧪 AAP v2.0 - Real LLM Batch Test\n');
  console.log('='.repeat(60));

  const nonce = randomBytes(16).toString('hex');
  console.log(`Nonce: ${nonce}\n`);

  const types = ['nlp_math', 'nlp_extract', 'nlp_logic'];
  const challenges = [];
  const validators = [];

  console.log('📋 Batch Challenges:\n');

  for (let i = 0; i < 3; i++) {
    const offsetNonce = nonce.slice(i * 2) + nonce.slice(0, i * 2);
    const type = types[i];
    const { challenge_string, validate, expected } = CHALLENGES[type](offsetNonce);
    
    challenges.push({ id: i, type, challenge_string });
    validators.push(validate);

    console.log(`[${i}] ${type}:`);
    console.log(`    ${challenge_string.split('\n')[0]}`);
    console.log(`    Expected: ${JSON.stringify(expected)}\n`);
  }

  // Build prompt
  let prompt = `You are being tested. Solve ALL 3 challenges below. 
Return ONLY a JSON array with exactly 3 objects, one for each challenge.
No explanation, no markdown, just the raw JSON array.

`;
  challenges.forEach((c, i) => {
    prompt += `Challenge ${i + 1}:\n${c.challenge_string}\n\n`;
  });
  prompt += `\nRespond with ONLY: [{"result": ...}, {"items": [...]}, {"answer": "..."}]`;

  console.log('='.repeat(60));
  console.log('🤖 Sending to LLM via clawdbot agent...\n');

  const startTime = Date.now();

  try {
    // Use clawdbot agent to call LLM
    const result = execSync(
      `clawdbot agent --message '${prompt.replace(/'/g, "'\\''")}' --json 2>/dev/null`,
      { encoding: 'utf8', timeout: 30000 }
    );
    
    const responseTimeMs = Date.now() - startTime;
    
    // Parse agent response
    const agentResponse = JSON.parse(result);
    const llmResponse = agentResponse.reply || agentResponse.message || result;
    
    console.log(`Response time: ${responseTimeMs}ms`);
    console.log(`\nLLM Response:\n${llmResponse}\n`);
    console.log('='.repeat(60));

    // Extract JSON array
    const arrayMatch = llmResponse.match(/\[[\s\S]*\]/);
    if (!arrayMatch) {
      console.log('❌ Failed to extract JSON array');
      return;
    }

    const solutions = JSON.parse(arrayMatch[0]);
    
    // Validate
    console.log('\n📊 Validation:\n');
    let passed = 0;

    for (let i = 0; i < 3; i++) {
      const result = validators[i](JSON.stringify(solutions[i]));
      console.log(`[${i}] ${challenges[i].type}: ${result.valid ? '✅ PASS' : '❌ FAIL'}`);
      if (!result.valid) {
        console.log(`    Expected: ${JSON.stringify(result.expected)}`);
        console.log(`    Got: ${JSON.stringify(result.got || result.reason)}`);
      }
      if (result.valid) passed++;
    }

    console.log('\n' + '='.repeat(60));
    console.log(`\n📈 Results: ${passed}/3 passed`);
    console.log(`⏱️  Time: ${responseTimeMs}ms / 12000ms limit`);
    console.log(`\n🎯 ${passed === 3 && responseTimeMs < 12000 ? '✅ VERIFIED' : '❌ FAILED'}`);

  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

main();
