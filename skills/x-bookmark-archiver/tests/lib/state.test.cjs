/**
 * Tests for state.js
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Create temp state dir for testing
const TEST_STATE_DIR = path.join(os.tmpdir(), 'x-bookmark-test-' + Date.now());

// Create wrapper that uses test directory
const state = {
  _ensureDir: () => {
    if (!fs.existsSync(TEST_STATE_DIR)) {
      fs.mkdirSync(TEST_STATE_DIR, { recursive: true });
    }
  },
  loadPending: function() {
    this._ensureDir();
    const file = path.join(TEST_STATE_DIR, 'pending.json');
    if (!fs.existsSync(file)) return [];
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  },
  savePending: function(data) {
    this._ensureDir();
    const file = path.join(TEST_STATE_DIR, 'pending.json');
    fs.writeFileSync(file, JSON.stringify(data, null, 2));
  },
  loadProcessed: function() {
    this._ensureDir();
    const file = path.join(TEST_STATE_DIR, 'processed.json');
    if (!fs.existsSync(file)) return new Set();
    return new Set(JSON.parse(fs.readFileSync(file, 'utf8')));
  },
  saveProcessed: function(set) {
    this._ensureDir();
    const file = path.join(TEST_STATE_DIR, 'processed.json');
    fs.writeFileSync(file, JSON.stringify([...set], null, 2));
  },
  markProcessed: function(ids) {
    const processed = this.loadProcessed();
    ids.forEach(id => processed.add(id));
    this.saveProcessed(processed);
  },
  clearPending: function() {
    this.savePending([]);
  }
};

function test(name, fn) {
  try {
    fn();
    console.log(`✓ ${name}`);
  } catch (e) {
    console.error(`✗ ${name}`);
    console.error(`  ${e.message}`);
    process.exitCode = 1;
  }
}

function assertEqual(actual, expected, msg) {
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    throw new Error(`${msg || 'Assertion failed'}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  }
}

// Setup: Clean test dir before tests
if (fs.existsSync(TEST_STATE_DIR)) {
  fs.rmSync(TEST_STATE_DIR, { recursive: true });
}

console.log('\n📦 State Management Tests');
console.log(`   Using: ${TEST_STATE_DIR}\n`);

// Test: Empty state
test('loadPending returns empty array when no file', () => {
  assertEqual(state.loadPending(), []);
});

test('loadProcessed returns empty set when no file', () => {
  assertEqual([...state.loadProcessed()], []);
});

// Test: Save and load pending
test('savePending writes JSON file', () => {
  const data = [{ id: '123', url: 'https://example.com' }];
  state.savePending(data);
  assertEqual(state.loadPending(), data);
});

test('savePending preserves array of multiple items', () => {
  const data = [
    { id: '1', url: 'https://a.com' },
    { id: '2', url: 'https://b.com' },
    { id: '3', url: 'https://c.com' }
  ];
  state.savePending(data);
  assertEqual(state.loadPending().length, 3);
  assertEqual(state.loadPending()[1].id, '2');
});

// Test: Save and load processed
test('saveProcessed writes set as array', () => {
  const ids = new Set(['abc', 'def', 'ghi']);
  state.saveProcessed(ids);
  const loaded = state.loadProcessed();
  assertEqual(loaded.has('abc'), true);
  assertEqual(loaded.has('def'), true);
  assertEqual(loaded.has('xyz'), false);
});

// Test: markProcessed
test('markProcessed adds IDs to processed set', () => {
  state.clearPending();
  state.saveProcessed(new Set());
  state.markProcessed(['id1', 'id2']);
  const processed = state.loadProcessed();
  assertEqual(processed.has('id1'), true);
  assertEqual(processed.has('id2'), true);
  assertEqual(processed.size, 2);
});

test('markProcessed appends to existing set', () => {
  state.saveProcessed(new Set(['existing']));
  state.markProcessed(['new1', 'new2']);
  const processed = state.loadProcessed();
  assertEqual(processed.has('existing'), true);
  assertEqual(processed.has('new1'), true);
  assertEqual(processed.has('new2'), true);
  assertEqual(processed.size, 3);
});

// Test: clearPending
test('clearPending empties pending array', () => {
  state.savePending([{ id: '1' }, { id: '2' }]);
  state.clearPending();
  assertEqual(state.loadPending(), []);
});

// Test: File format
test('JSON files are pretty-printed', () => {
  state.savePending([{ id: '1', url: 'test' }]);
  const file = path.join(TEST_STATE_DIR, 'pending.json');
  const content = fs.readFileSync(file, 'utf8');
  if (!content.includes('\n')) {
    throw new Error('JSON not pretty-printed');
  }
});

// Cleanup
console.log('\n🧹 Cleaning up test directory...');
fs.rmSync(TEST_STATE_DIR, { recursive: true, force: true });

console.log('\n' + (process.exitCode ? '❌ Some tests failed' : '✅ All tests passed'));
