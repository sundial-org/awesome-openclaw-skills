/**
 * AAP v2.0 - Real LLM Batch Test
 * 
 * Tests batch challenges with actual LLM API
 */

import { randomBytes, createHash, generateKeyPairSync, createSign } from 'node:crypto';

// ============== CONFIG ==============
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
const MODEL = 'anthropic/claude-sonnet-4';

if (!OPENROUTER_API_KEY) {
  console.error('❌ Set OPENROUTER_API_KEY environment variable');
  process.exit(1);
}

// ============== WORD POOLS ==============
const WORD_POOLS = {
  animals: ['cat', 'dog', 'rabbit', 'tiger', 'lion', 'elephant', 'giraffe', 'penguin', 'eagle', 'shark'],
  fruits: ['apple', 'banana', 'orange', 'grape', 'strawberry', 'watermelon', 'peach', 'kiwi', 'mango', 'cherry'],
  colors: ['red', 'blue', 'yellow', 'green', 'purple', 'orange', 'pink', 'black', 'white', 'brown'],
  countries: ['Korea', 'Japan', 'USA', 'UK', 'France', 'Germany', 'Australia', 'Canada', 'Brazil', 'India'],
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
          const m = sol.match(/\{[\s\S]*\}/);
          if (!m) return false;
          const obj = JSON.parse(m[0]);
          return Math.abs(obj.result - expected) < 0.01;
        } catch { return false; }
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
          const m = sol.match(/\{[\s\S]*\}/);
          if (!m) return false;
          const obj = JSON.parse(m[0]);
          const items = (obj.items || []).map(s => s.toLowerCase()).sort();
          return JSON.stringify(items) === JSON.stringify(targets.map(s => s.toLowerCase()).sort());
        } catch { return false; }
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
          const m = sol.match(/\{[\s\S]*\}/);
          if (!m) return false;
          const obj = JSON.parse(m[0]);
          return obj.answer?.toUpperCase() === expected;
        } catch { return false; }
      },
      expected
    };
  }
};

// ============== LLM CALL ==============
async function callLLM(prompt) {
  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: MODEL,
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 500
    })
  });

  if (!response.ok) {
    throw new Error(`LLM API error: ${response.status}`);
  }

  const data = await response.json();
  return data.choices[0].message.content;
}

// ============== MAIN TEST ==============
async function runTest() {
  console.log('🧪 AAP v2.0 - Real LLM Batch Test\n');
  console.log(`Model: ${MODEL}`);
  console.log('='.repeat(60));

  // Generate identity
  const { publicKey, privateKey } = generateKeyPairSync('ec', {
    namedCurve: 'secp256k1',
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  const publicId = createHash('sha256').update(publicKey).digest('hex').slice(0, 20);
  console.log(`\nAgent ID: ${publicId}`);

  // Generate nonce and challenges
  const nonce = randomBytes(16).toString('hex');
  console.log(`Nonce: ${nonce}\n`);

  const types = ['nlp_math', 'nlp_extract', 'nlp_logic'];
  const challenges = [];
  const validators = [];
  const expectedAnswers = [];

  console.log('📋 Generating Batch Challenges...\n');

  for (let i = 0; i < 3; i++) {
    const offsetNonce = nonce.slice(i * 2) + nonce.slice(0, i * 2);
    const type = types[i];
    const { challenge_string, validate, expected } = CHALLENGES[type](offsetNonce);
    
    challenges.push({ id: i, type, challenge_string });
    validators.push(validate);
    expectedAnswers.push(expected);

    console.log(`[${i}] ${type}:`);
    console.log(`    ${challenge_string.split('\n')[0]}`);
    console.log(`    Expected: ${JSON.stringify(expected)}\n`);
  }

  // Create batch prompt for LLM
  let batchPrompt = `Solve all of the following challenges. Respond with a JSON array containing exactly 3 solutions in order.\n\n`;
  challenges.forEach((c, i) => {
    batchPrompt += `Challenge ${i + 1} (${c.type}):\n${c.challenge_string}\n\n`;
  });
  batchPrompt += `\nRespond with ONLY a JSON array like: [{"result": ...}, {"items": [...]}, {"answer": "..."}]\nNo other text, just the JSON array.`;

  console.log('='.repeat(60));
  console.log('🤖 Calling LLM...\n');

  const startTime = Date.now();
  
  try {
    const llmResponse = await callLLM(batchPrompt);
    const responseTimeMs = Date.now() - startTime;
    
    console.log(`LLM Response (${responseTimeMs}ms):`);
    console.log(llmResponse);
    console.log('\n' + '='.repeat(60));

    // Parse solutions
    const arrayMatch = llmResponse.match(/\[[\s\S]*\]/);
    if (!arrayMatch) {
      console.log('❌ Failed to extract JSON array from response');
      return;
    }

    const solutions = JSON.parse(arrayMatch[0]);
    console.log('\n✅ Parsed Solutions:');
    solutions.forEach((s, i) => {
      console.log(`  [${i}] ${JSON.stringify(s)}`);
    });

    // Validate each solution
    console.log('\n📊 Validation Results:\n');
    let passed = 0;

    for (let i = 0; i < 3; i++) {
      const solution = JSON.stringify(solutions[i]);
      const valid = validators[i](solution);
      
      console.log(`  [${i}] ${challenges[i].type}:`);
      console.log(`      Expected: ${JSON.stringify(expectedAnswers[i])}`);
      console.log(`      Got: ${JSON.stringify(solutions[i])}`);
      console.log(`      ${valid ? '✅ PASS' : '❌ FAIL'}`);
      
      if (valid) passed++;
    }

    console.log('\n' + '='.repeat(60));
    console.log(`\n📈 Results:`);
    console.log(`   Passed: ${passed}/3`);
    console.log(`   Response Time: ${responseTimeMs}ms`);
    console.log(`   Time Limit: 12000ms`);
    console.log(`   ${responseTimeMs < 12000 ? '✅ Within time limit' : '❌ Exceeded time limit'}`);

    // Final verdict
    const verified = passed === 3 && responseTimeMs < 12000;
    console.log(`\n🎯 VERIFICATION: ${verified ? '✅ PASSED' : '❌ FAILED'}`);

    if (verified) {
      console.log('\n🎉 This agent is verified as AI_AGENT!');
    }

  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

runTest();
