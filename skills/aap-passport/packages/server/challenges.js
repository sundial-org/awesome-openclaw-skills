/**
 * @aap/server - Challenge Generator v2.6
 * 
 * "Burst Mode with Entropy Injection"
 * - 7 challenges in 6 seconds (humans cannot pass)
 * - Salt injection prevents caching attacks
 * - Natural language instructions (requires LLM)
 * 
 * v2.6 Changes:
 * - BATCH_SIZE: 5 → 7 (more problems = harder for humans)
 * - MAX_RESPONSE_TIME_MS: 8000 → 6000 (tighter window)
 * - Random chance reduced: (1/3)^7 = 0.05%
 * 
 * v2.5 Changes:
 * - BATCH_SIZE: 3 → 5
 * - MAX_RESPONSE_TIME_MS: 12000 → 8000
 * - Salt injection in challenges (must be echoed back)
 */

import { createHash } from 'node:crypto';

/**
 * Word pools for dynamic challenge generation
 */
const WORD_POOLS = {
  animals: ['cat', 'dog', 'rabbit', 'tiger', 'lion', 'elephant', 'giraffe', 'penguin', 'eagle', 'shark', 'wolf', 'bear', 'fox', 'deer', 'owl'],
  fruits: ['apple', 'banana', 'orange', 'grape', 'strawberry', 'watermelon', 'peach', 'kiwi', 'mango', 'cherry', 'lemon', 'lime', 'pear', 'plum'],
  colors: ['red', 'blue', 'yellow', 'green', 'purple', 'orange', 'pink', 'black', 'white', 'brown', 'gray', 'cyan', 'magenta'],
  countries: ['Korea', 'Japan', 'USA', 'UK', 'France', 'Germany', 'Australia', 'Canada', 'Brazil', 'India', 'Italy', 'Spain', 'Mexico'],
  verbs: ['runs', 'eats', 'sleeps', 'plays', 'works', 'studies', 'travels', 'cooks', 'reads', 'writes', 'sings', 'dances'],
  adjectives: ['big', 'small', 'fast', 'slow', 'beautiful', 'cute', 'delicious', 'interesting', 'bright', 'dark']
};

/**
 * Select random items from array using nonce as seed
 */
function seededSelect(arr, nonce, count, offset = 0) {
  const seed = parseInt(nonce.slice(offset, offset + 4), 16);
  const results = [];
  const used = new Set();
  
  for (let i = 0; i < count && i < arr.length; i++) {
    let idx = (seed + i * 7) % arr.length;
    while (used.has(idx)) {
      idx = (idx + 1) % arr.length;
    }
    used.add(idx);
    results.push(arr[idx]);
  }
  return results;
}

/**
 * Generate a random number from nonce
 */
function seededNumber(nonce, offset, min, max) {
  const seed = parseInt(nonce.slice(offset, offset + 4), 16);
  return (seed % (max - min + 1)) + min;
}

/**
 * Generate salt from nonce (for entropy injection)
 * @param {string} nonce - Base nonce
 * @param {number} offset - Offset for variation
 * @returns {string} 6-character salt
 */
function generateSalt(nonce, offset = 0) {
  return nonce.slice(offset, offset + 6).toUpperCase();
}

/**
 * Challenge type definitions
 */
export const CHALLENGE_TYPES = {
  /**
   * Extract entities from natural language sentence (HARD - more distractors)
   */
  nlp_extract: {
    generate: (nonce) => {
      const salt = generateSalt(nonce, 0);
      const category = ['animals', 'fruits', 'colors'][parseInt(nonce[0], 16) % 3];
      const pool = WORD_POOLS[category];
      const targets = seededSelect(pool, nonce, 3, 0);  // 3 targets now
      const distractorPool = category === 'animals' ? 'fruits' : category === 'fruits' ? 'colors' : 'animals';
      const distractors = seededSelect(WORD_POOLS[distractorPool], nonce, 2, 8);
      const verb = seededSelect(WORD_POOLS.verbs, nonce, 1, 4)[0];
      const adj = seededSelect(WORD_POOLS.adjectives, nonce, 1, 6)[0];
      
      // Complex sentence with distractors mixed in
      const templates = [
        `The ${adj} ${targets[0]}, a ${distractors[0]}, the ${targets[1]}, and ${targets[2]} all ${verb} near the ${distractors[1]}.`,
        `I saw ${targets[0]} and ${distractors[0]} yesterday, but today only ${targets[1]}, ${targets[2]}, and a ${distractors[1]} appeared.`,
        `Between the ${distractors[0]} and ${distractors[1]}, there were ${targets[0]}, ${targets[1]}, and ${targets[2]} ${verb}ing.`
      ];
      const sentence = templates[parseInt(nonce[12], 16) % templates.length];
      
      return {
        challenge_string: `[REQ-${salt}] Extract ONLY the ${category} from this sentence (ignore other categories).
Sentence: "${sentence}"
Response format: {"salt": "${salt}", "items": ["item1", "item2", "item3"]}`,
        expected: { salt, items: targets.map(s => s.toLowerCase()).sort() },
        validate: (solution) => {
          try {
            const match = solution.match(/\{[\s\S]*\}/);
            if (!match) return false;
            const obj = JSON.parse(match[0]);
            
            // Check salt
            if (obj.salt !== salt) return false;
            
            const items = (obj.items || obj.animals || obj.fruits || obj.colors || []).map(s => s.toLowerCase()).sort();
            const expected = targets.map(s => s.toLowerCase()).sort();
            return JSON.stringify(items) === JSON.stringify(expected);
          } catch { return false; }
        }
      };
    }
  },

  /**
   * Math problem expressed in natural language (EXTREME)
   */
  nlp_math: {
    generate: (nonce) => {
      const salt = generateSalt(nonce, 2);
      const a = seededNumber(nonce, 0, 50, 200);
      const b = seededNumber(nonce, 2, 10, 50);
      const c = seededNumber(nonce, 4, 2, 9);
      const d = seededNumber(nonce, 6, 5, 25);
      const e = seededNumber(nonce, 8, 2, 6);
      
      const templates = [
        {
          text: `Start with ${a}. Subtract ${b}. Multiply that by ${c}. Divide the result by ${e}. Finally, add ${d}. What's the final value?`,
          answer: (((a - b) * c) / e) + d
        },
        {
          text: `Compute: ((${a} + ${b}) × ${c} - ${d}) ÷ ${e}. Give the result rounded to two decimal places.`,
          answer: ((a + b) * c - d) / e
        },
        {
          text: `Take the sum of ${a} and ${b}. Square root of that sum, rounded down. Then multiply by ${c} and subtract ${d}.`,
          answer: Math.floor(Math.sqrt(a + b)) * c - d
        },
        {
          text: `${a} divided by ${c}, plus ${b} divided by ${e}, minus ${d}. Round to nearest integer.`,
          answer: Math.round(a / c + b / e - d)
        },
        {
          text: `Triple ${a}, halve that result, add ${b}, then take away ${d}. Multiply everything by ${e}. Final answer?`,
          answer: ((a * 3 / 2) + b - d) * e
        },
        {
          text: `What is ${a} mod ${c} (remainder), plus ${b} mod ${e}, times ${d}?`,
          answer: ((a % c) + (b % e)) * d
        }
      ];
      
      const template = templates[parseInt(nonce[10], 16) % templates.length];
      const expected = Math.round(template.answer * 100) / 100;
      
      return {
        challenge_string: `[REQ-${salt}] ${template.text}
Response format: {"salt": "${salt}", "result": number}`,
        expected: { salt, result: expected },
        validate: (solution) => {
          try {
            const match = solution.match(/\{[\s\S]*\}/);
            if (!match) return false;
            const obj = JSON.parse(match[0]);
            
            if (obj.salt !== salt) return false;
            
            const result = parseFloat(obj.result);
            return Math.abs(result - expected) < 0.01;
          } catch { return false; }
        }
      };
    }
  },

  /**
   * String transformation described in natural language (EXTREME - multi-step transforms)
   */
  nlp_transform: {
    generate: (nonce) => {
      const salt = generateSalt(nonce, 4);
      const input = nonce.slice(6, 16);  // Longer input: 10 chars
      const transformType = parseInt(nonce[16], 16) % 6;
      
      let instruction, expected;
      
      switch (transformType) {
        case 0:
          // Reverse → uppercase → take first 5
          expected = input.split('').reverse().join('').toUpperCase().slice(0, 5);
          instruction = `Take "${input}": reverse it, convert to uppercase, then return only the first 5 characters.`;
          break;
        case 1:
          // Extract digits → sum → return as string with prefix
          const digitSum = input.split('').filter(c => /\d/.test(c)).reduce((a, b) => a + parseInt(b), 0);
          expected = `SUM:${digitSum}`;
          instruction = `From "${input}": extract all digits, sum them, and format as "SUM:X" where X is the total.`;
          break;
        case 2:
          // Letters only → sort → reverse → join with dots
          expected = input.split('').filter(c => /[a-zA-Z]/.test(c)).sort().reverse().join('.');
          instruction = `From "${input}": extract letters only, sort alphabetically, reverse that order, join with dots.`;
          break;
        case 3:
          // Alternate case: odd positions uppercase, even lowercase
          expected = input.split('').map((c, i) => i % 2 === 0 ? c.toLowerCase() : c.toUpperCase()).join('');
          instruction = `Transform "${input}": characters at even positions (0,2,4...) lowercase, odd positions (1,3,5...) uppercase.`;
          break;
        case 4:
          // Count each char type
          const letters = input.split('').filter(c => /[a-zA-Z]/.test(c)).length;
          const digits = input.split('').filter(c => /\d/.test(c)).length;
          expected = `L${letters}D${digits}`;
          instruction = `Analyze "${input}": count letters and digits. Format answer as "LxDy" where x=letter count, y=digit count.`;
          break;
        case 5:
          // Replace vowels with *, consonants with #, keep digits
          expected = input.split('').map(c => {
            if (/[aeiouAEIOU]/.test(c)) return '*';
            if (/[a-zA-Z]/.test(c)) return '#';
            return c;
          }).join('');
          instruction = `Transform "${input}": replace vowels with "*", consonants with "#", keep digits unchanged.`;
          break;
      }
      
      return {
        challenge_string: `[REQ-${salt}] ${instruction}
Response format: {"salt": "${salt}", "output": "result"}`,
        expected: { salt, output: expected },
        validate: (solution) => {
          try {
            const match = solution.match(/\{[\s\S]*\}/);
            if (!match) return false;
            const obj = JSON.parse(match[0]);
            
            if (obj.salt !== salt) return false;
            
            const output = String(obj.output);
            return output === String(expected) || output.toLowerCase() === String(expected).toLowerCase();
          } catch { return false; }
        }
      };
    }
  },

  /**
   * Conditional logic (EXTREME - multi-layer nested conditions)
   */
  nlp_logic: {
    generate: (nonce) => {
      const salt = generateSalt(nonce, 6);
      const a = seededNumber(nonce, 0, 20, 150);
      const b = seededNumber(nonce, 2, 20, 150);
      const c = seededNumber(nonce, 4, 20, 100);
      const d = seededNumber(nonce, 6, 10, 50);
      const threshold = seededNumber(nonce, 8, 40, 100);
      
      const templates = [
        {
          text: `Let X=${a}, Y=${b}, Z=${c}, W=${d}. If (X > Y AND Z > W) OR (X < Y AND Z < W), answer "CONSISTENT". If (X > Y AND Z < W) OR (X < Y AND Z > W), answer "CROSSED". Otherwise, answer "EQUAL".`,
          answer: ((a > b && c > d) || (a < b && c < d)) ? "CONSISTENT" : ((a > b && c < d) || (a < b && c > d)) ? "CROSSED" : "EQUAL"
        },
        {
          text: `Given four numbers [${a}, ${b}, ${c}, ${d}]: Count how many are divisible by 3. If count is 0, say "NONE". If 1-2, say "FEW". If 3-4, say "MANY".`,
          answer: (() => {
            const count = [a, b, c, d].filter(n => n % 3 === 0).length;
            return count === 0 ? "NONE" : count <= 2 ? "FEW" : "MANY";
          })()
        },
        {
          text: `Evaluate: Is (${a} + ${b}) greater than (${c} + ${d})? AND is (${a} × ${d}) less than (${b} × ${c})? If BOTH true: "ALPHA". If NEITHER true: "GAMMA". Otherwise: "BETA".`,
          answer: (() => {
            const cond1 = (a + b) > (c + d);
            const cond2 = (a * d) < (b * c);
            return (cond1 && cond2) ? "ALPHA" : (!cond1 && !cond2) ? "GAMMA" : "BETA";
          })()
        },
        {
          text: `Numbers: ${a}, ${b}, ${c}, ${d}. First, find the median (average of middle two when sorted). If median > ${threshold}, output "HIGH". If median < ${threshold / 2}, output "LOW". Otherwise, output "MID".`,
          answer: (() => {
            const sorted = [a, b, c, d].sort((x, y) => x - y);
            const median = (sorted[1] + sorted[2]) / 2;
            return median > threshold ? "HIGH" : median < (threshold / 2) ? "LOW" : "MID";
          })()
        },
        {
          text: `Check these conditions for [${a}, ${b}, ${c}, ${d}]: (1) Sum > ${threshold * 3}? (2) Product of smallest two < ${threshold * 10}? (3) Largest is even? Count TRUE conditions. Answer with the count (0-3).`,
          answer: (() => {
            const sorted = [a, b, c, d].sort((x, y) => x - y);
            let count = 0;
            if (a + b + c + d > threshold * 3) count++;
            if (sorted[0] * sorted[1] < threshold * 10) count++;
            if (sorted[3] % 2 === 0) count++;
            return String(count);
          })()
        },
        {
          text: `If ${a} AND ${b} are both prime, answer "TWIN". If exactly one is prime, answer "SOLO". If neither is prime, answer "NONE". (Hint: primes are only divisible by 1 and themselves)`,
          answer: (() => {
            const isPrime = n => {
              if (n < 2) return false;
              for (let i = 2; i <= Math.sqrt(n); i++) if (n % i === 0) return false;
              return true;
            };
            const ap = isPrime(a), bp = isPrime(b);
            return (ap && bp) ? "TWIN" : (ap || bp) ? "SOLO" : "NONE";
          })()
        }
      ];
      
      const template = templates[parseInt(nonce[10], 16) % templates.length];
      
      return {
        challenge_string: `[REQ-${salt}] ${template.text}
Response format: {"salt": "${salt}", "answer": "your answer"}`,
        expected: { salt, answer: template.answer },
        validate: (solution) => {
          try {
            const match = solution.match(/\{[\s\S]*\}/);
            if (!match) return false;
            const obj = JSON.parse(match[0]);
            
            if (obj.salt !== salt) return false;
            
            return obj.answer?.toUpperCase() === template.answer.toUpperCase();
          } catch { return false; }
        }
      };
    }
  },

  /**
   * Counting task (EXTREME - multiple categories, complex sentences)
   */
  nlp_count: {
    generate: (nonce) => {
      const salt = generateSalt(nonce, 8);
      const targetCategory = ['animals', 'fruits', 'colors'][parseInt(nonce[0], 16) % 3];
      const pool = WORD_POOLS[targetCategory];
      const targetCount = seededNumber(nonce, 0, 3, 6);
      
      // Add distractors from OTHER categories
      const distractor1Cat = targetCategory === 'animals' ? 'fruits' : 'animals';
      const distractor2Cat = targetCategory === 'colors' ? 'fruits' : 'colors';
      const distractorCount1 = seededNumber(nonce, 2, 2, 4);
      const distractorCount2 = seededNumber(nonce, 4, 2, 3);
      
      const targets = seededSelect(pool, nonce, targetCount, 0);
      const distractors1 = seededSelect(WORD_POOLS[distractor1Cat], nonce, distractorCount1, 6);
      const distractors2 = seededSelect(WORD_POOLS[distractor2Cat], nonce, distractorCount2, 10);
      const countryDistractors = seededSelect(WORD_POOLS.countries, nonce, 2, 14);
      
      // Mix everything together
      const allItems = [...targets, ...distractors1, ...distractors2, ...countryDistractors];
      // Shuffle using nonce
      for (let i = allItems.length - 1; i > 0; i--) {
        const j = parseInt(nonce.slice(i % 28, (i % 28) + 2), 16) % (i + 1);
        [allItems[i], allItems[j]] = [allItems[j], allItems[i]];
      }
      
      const templates = [
        `At the market, I noticed: ${allItems.join(', ')}. Quite a mix!`,
        `The list contains: ${allItems.join(', ')}. Some things don't belong.`,
        `Inventory check: ${allItems.join(', ')}. Sort by category mentally.`,
        `Mixed bag: ${allItems.join(', ')}. Focus on what matters.`
      ];
      const sentence = templates[parseInt(nonce[20], 16) % templates.length];
      
      return {
        challenge_string: `[REQ-${salt}] Count ONLY the ${targetCategory} in this text. Ignore all other categories (other nouns are distractors).
Text: "${sentence}"
Response format: {"salt": "${salt}", "count": number}`,
        expected: { salt, count: targetCount },
        validate: (solution) => {
          try {
            const match = solution.match(/\{[\s\S]*\}/);
            if (!match) return false;
            const obj = JSON.parse(match[0]);
            
            if (obj.salt !== salt) return false;
            
            return parseInt(obj.count) === targetCount;
          } catch { return false; }
        }
      };
    }
  },

  /**
   * Multi-step instruction following (EXTREME - 5-6 steps)
   */
  nlp_multistep: {
    generate: (nonce) => {
      const salt = generateSalt(nonce, 10);
      const numbers = [
        seededNumber(nonce, 0, 5, 30),
        seededNumber(nonce, 2, 5, 30),
        seededNumber(nonce, 4, 5, 30),
        seededNumber(nonce, 6, 5, 30),
        seededNumber(nonce, 8, 5, 30),
        seededNumber(nonce, 10, 5, 30)
      ];
      
      const templateType = parseInt(nonce[12], 16) % 4;
      let instructions, final;
      
      if (templateType === 0) {
        // Complex: filter → transform → aggregate → adjust
        const evens = numbers.filter(n => n % 2 === 0);
        const odds = numbers.filter(n => n % 2 !== 0);
        const evensProduct = evens.length > 0 ? evens.reduce((a, b) => a * b, 1) : 0;
        const oddsSum = odds.reduce((a, b) => a + b, 0);
        const diff = Math.abs(evensProduct - oddsSum);
        final = diff % 100;  // Keep manageable
        instructions = `1. From [${numbers.join(', ')}], separate even and odd numbers.
2. Calculate the PRODUCT of all even numbers (or 0 if none).
3. Calculate the SUM of all odd numbers.
4. Find the absolute difference between these two results.
5. Take that difference modulo 100 (remainder when divided by 100).`;
      } else if (templateType === 1) {
        // Sort → pair operations → combine
        const sorted = [...numbers].sort((a, b) => a - b);
        const pair1 = sorted[0] * sorted[5];  // smallest × largest
        const pair2 = sorted[1] + sorted[4];  // 2nd smallest + 2nd largest
        const pair3 = sorted[2] - sorted[3];  // middle pair difference (might be negative)
        final = pair1 + pair2 + Math.abs(pair3);
        instructions = `1. Sort [${numbers.join(', ')}] from smallest to largest.
2. Multiply the smallest by the largest.
3. Add the second-smallest to the second-largest.
4. Find absolute difference between the two middle numbers.
5. Sum all three results from steps 2, 3, and 4.`;
      } else if (templateType === 2) {
        // Chunked processing
        const chunk1 = numbers.slice(0, 3);
        const chunk2 = numbers.slice(3, 6);
        const avg1 = chunk1.reduce((a, b) => a + b, 0) / 3;
        const avg2 = chunk2.reduce((a, b) => a + b, 0) / 3;
        const max1 = Math.max(...chunk1);
        const max2 = Math.max(...chunk2);
        final = Math.round((avg1 + avg2) * (max1 > max2 ? 2 : 1));
        instructions = `1. Split [${numbers.join(', ')}] into two groups: first 3 and last 3.
2. Calculate average of first group: [${chunk1.join(', ')}].
3. Calculate average of second group: [${chunk2.join(', ')}].
4. Add both averages together.
5. If max of first group > max of second group, double the sum. Otherwise keep as is.
6. Round to nearest integer.`;
      } else {
        // Recursive-style
        let val = numbers[0];
        for (let i = 1; i < numbers.length; i++) {
          if (i % 2 === 1) val += numbers[i];
          else val -= numbers[i];
        }
        val = Math.abs(val);
        final = val * (numbers.length);
        instructions = `1. Start with the first number from [${numbers.join(', ')}].
2. Add the 2nd number.
3. Subtract the 3rd number.
4. Add the 4th number.
5. Subtract the 5th number.
6. Add the 6th number.
7. Take absolute value of result.
8. Multiply by 6 (the count of numbers).`;
      }
      
      return {
        challenge_string: `[REQ-${salt}] Execute these steps IN ORDER:
${instructions}
Response format: {"salt": "${salt}", "result": final_value}`,
        expected: { salt, result: final },
        validate: (solution) => {
          try {
            const match = solution.match(/\{[\s\S]*\}/);
            if (!match) return false;
            const obj = JSON.parse(match[0]);
            
            if (obj.salt !== salt) return false;
            
            return parseInt(obj.result) === final;
          } catch { return false; }
        }
      };
    }
  },

  /**
   * Pattern recognition and completion
   */
  nlp_pattern: {
    generate: (nonce) => {
      const salt = generateSalt(nonce, 12);
      const start = seededNumber(nonce, 0, 1, 10);
      const step = seededNumber(nonce, 2, 2, 5);
      const patternType = parseInt(nonce[4], 16) % 3;
      
      let sequence, next2, instruction;
      
      switch (patternType) {
        case 0: // Arithmetic
          sequence = [start, start + step, start + step * 2, start + step * 3];
          next2 = [start + step * 4, start + step * 5];
          instruction = `Find the pattern and provide the next 2 numbers: [${sequence.join(', ')}, ?, ?]`;
          break;
        case 1: // Geometric (doubling)
          sequence = [start, start * 2, start * 4, start * 8];
          next2 = [start * 16, start * 32];
          instruction = `Find the pattern and provide the next 2 numbers: [${sequence.join(', ')}, ?, ?]`;
          break;
        case 2: // Fibonacci-like
          sequence = [start, step, start + step, step + (start + step)];
          next2 = [sequence[2] + sequence[3], sequence[3] + (sequence[2] + sequence[3])];
          instruction = `Find the pattern and provide the next 2 numbers: [${sequence.join(', ')}, ?, ?]`;
          break;
      }
      
      return {
        challenge_string: `[REQ-${salt}] ${instruction}
Response format: {"salt": "${salt}", "next": [number1, number2]}`,
        expected: { salt, next: next2 },
        validate: (solution) => {
          try {
            const match = solution.match(/\{[\s\S]*\}/);
            if (!match) return false;
            const obj = JSON.parse(match[0]);
            
            if (obj.salt !== salt) return false;
            
            const next = obj.next;
            return Array.isArray(next) && 
                   parseInt(next[0]) === next2[0] && 
                   parseInt(next[1]) === next2[1];
          } catch { return false; }
        }
      };
    }
  },

  /**
   * Text analysis - find specific properties
   */
  nlp_analysis: {
    generate: (nonce) => {
      const salt = generateSalt(nonce, 14);
      const words = seededSelect([...WORD_POOLS.animals, ...WORD_POOLS.fruits], nonce, 5, 0);
      const analysisType = parseInt(nonce[8], 16) % 3;
      
      let instruction, expected;
      const wordList = words.join(', ');
      
      switch (analysisType) {
        case 0: // Longest word
          expected = words.reduce((a, b) => a.length >= b.length ? a : b);
          instruction = `Find the longest word from the following list: ${wordList}`;
          break;
        case 1: // Shortest word
          expected = words.reduce((a, b) => a.length <= b.length ? a : b);
          instruction = `Find the shortest word from the following list: ${wordList}`;
          break;
        case 2: // First alphabetically
          expected = [...words].sort()[0];
          instruction = `Find the word that comes first alphabetically from the following list: ${wordList}`;
          break;
      }
      
      return {
        challenge_string: `[REQ-${salt}] ${instruction}
Response format: {"salt": "${salt}", "answer": "word"}`,
        expected: { salt, answer: expected },
        validate: (solution) => {
          try {
            const match = solution.match(/\{[\s\S]*\}/);
            if (!match) return false;
            const obj = JSON.parse(match[0]);
            
            if (obj.salt !== salt) return false;
            
            return obj.answer?.toLowerCase() === expected.toLowerCase();
          } catch { return false; }
        }
      };
    }
  }
};

// ============== Protocol Constants v2.5 ==============

/**
 * Batch challenge settings (v2.5 - Burst Mode)
 */
export const BATCH_SIZE = 7;               // 7 challenges per batch (v2.6: was 5)
export const MAX_RESPONSE_TIME_MS = 6000;  // 6 seconds total (v2.6: was 8)
export const CHALLENGE_EXPIRY_MS = 60000;  // 60 seconds

/**
 * Get list of available challenge types
 * @returns {string[]}
 */
export function getTypes() {
  return Object.keys(CHALLENGE_TYPES);
}

/**
 * Generate a single random challenge
 * @param {string} nonce - The nonce to incorporate
 * @param {string} [type] - Specific type (random if not specified)
 * @returns {Object} { type, challenge_string, validate, expected }
 */
export function generate(nonce, type) {
  const types = getTypes();
  const selectedType = type && types.includes(type) 
    ? type 
    : types[Math.floor(Math.random() * types.length)];
  
  const generator = CHALLENGE_TYPES[selectedType];
  const result = generator.generate(nonce);
  
  return {
    type: selectedType,
    challenge_string: result.challenge_string,
    validate: result.validate,
    expected: result.expected  // For debugging only
  };
}

/**
 * Generate a batch of challenges (Burst Mode)
 * @param {string} nonce - Base nonce
 * @param {number} [count=BATCH_SIZE] - Number of challenges
 * @returns {Object} { challenges: [...], validators: [...] }
 */
export function generateBatch(nonce, count = BATCH_SIZE) {
  const types = getTypes();
  const usedTypes = new Set();
  const challenges = [];
  const validators = [];
  const expected = [];
  
  for (let i = 0; i < count; i++) {
    // Use different nonce offset for each challenge
    const offsetNonce = nonce.slice(i * 2) + nonce.slice(0, i * 2);
    
    // Select different type for each challenge (ensure variety)
    let selectedType;
    let attempts = 0;
    do {
      const seed = parseInt(offsetNonce.slice(0, 4), 16);
      selectedType = types[(seed + i * 3 + attempts) % types.length];
      attempts++;
    } while (usedTypes.has(selectedType) && usedTypes.size < types.length);
    usedTypes.add(selectedType);
    
    const generator = CHALLENGE_TYPES[selectedType];
    const result = generator.generate(offsetNonce);
    
    challenges.push({
      id: i,
      type: selectedType,
      challenge_string: result.challenge_string
    });
    
    validators.push(result.validate);
    expected.push(result.expected);
  }
  
  return {
    challenges,
    validators,  // Keep on server, don't send to client
    expected     // For debugging
  };
}

/**
 * Validate batch solutions
 * @param {Array} validators - Validator functions from generateBatch
 * @param {Array} solutions - Array of solutions from client
 * @returns {Object} { passed, total, results: [{id, valid}] }
 */
export function validateBatch(validators, solutions) {
  const results = [];
  let passed = 0;
  
  for (let i = 0; i < validators.length; i++) {
    const solution = solutions[i];
    const valid = solution && validators[i](
      typeof solution === 'string' ? solution : JSON.stringify(solution)
    );
    
    results.push({ id: i, valid });
    if (valid) passed++;
  }
  
  return {
    passed,
    total: validators.length,
    allPassed: passed === validators.length,
    results
  };
}

/**
 * Validate a single solution against a challenge
 * @param {string} type - Challenge type
 * @param {string} nonce - Original nonce
 * @param {string} solution - Agent's solution
 * @returns {boolean}
 */
export function validate(type, nonce, solution) {
  const generator = CHALLENGE_TYPES[type];
  if (!generator) {
    return false;
  }
  
  const { validate: validateFn } = generator.generate(nonce);
  return validateFn(solution);
}

export default {
  CHALLENGE_TYPES,
  BATCH_SIZE,
  MAX_RESPONSE_TIME_MS,
  CHALLENGE_EXPIRY_MS,
  getTypes,
  generate,
  generateBatch,
  validateBatch,
  validate
};
