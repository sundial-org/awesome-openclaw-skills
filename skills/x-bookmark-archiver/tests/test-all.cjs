#!/usr/bin/env node
/**
 * Test runner - runs all tests
 */

const { execSync } = require('child_process');
const path = require('path');

const tests = [
  { name: 'Categorize Unit Tests', file: 'lib/categorize.test.cjs' },
  { name: 'State Unit Tests', file: 'lib/state.test.cjs' },
  { name: 'Integration Tests', file: 'integration.test.cjs' }
];

console.log('═══════════════════════════════════════════');
console.log('   X-Bookmark-Archiver Test Suite');
console.log('═══════════════════════════════════════════\n');

let failed = 0;

for (const test of tests) {
  console.log(`\n▶ Running: ${test.name}`);
  console.log('─'.repeat(40));
  
  try {
    execSync(`node "${path.join(__dirname, test.file)}"`, {
      stdio: 'inherit',
      cwd: __dirname
    });
  } catch (e) {
    failed++;
  }
}

console.log('\n═══════════════════════════════════════════');
if (failed === 0) {
  console.log('   ✅ All test suites passed!');
} else {
  console.log(`   ❌ ${failed} test suite(s) failed`);
}
console.log('═══════════════════════════════════════════\n');

process.exit(failed > 0 ? 1 : 0);
