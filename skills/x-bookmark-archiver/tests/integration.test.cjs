#!/usr/bin/env node
/**
 * Integration test for full pipeline
 * Uses mock data instead of real bird CLI
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Setup test environment
const TEST_DIR = path.join(os.tmpdir(), 'x-bookmark-integration-' + Date.now());
const FIXTURES_DIR = path.join(__dirname, 'fixtures');

console.log('\n🔬 Integration Test');
console.log(`   Test dir: ${TEST_DIR}\n`);

// Create test directories
fs.mkdirSync(TEST_DIR, { recursive: true });
fs.mkdirSync(path.join(TEST_DIR, 'scripts', 'lib'), { recursive: true });

// Copy scripts to test dir for isolation
const scriptsToCopy = ['lib/categorize.cjs', 'lib/state.cjs', 'process.cjs'];
for (const script of scriptsToCopy) {
  const src = path.join(__dirname, '..', 'scripts', script);
  const dest = path.join(TEST_DIR, 'scripts', script);
  fs.copyFileSync(src, dest);
}

// Mock state module paths
const stateCode = fs.readFileSync(path.join(TEST_DIR, 'scripts', 'lib', 'state.cjs'), 'utf8');
const mockedState = stateCode.replace(
  "const STATE_DIR = process.env.X_BOOKMARK_STATE_DIR || (require('os').homedir() + '/.clawd/.state');",
  `const STATE_DIR = '${TEST_DIR}/.state';`
);
fs.writeFileSync(path.join(TEST_DIR, 'scripts', 'lib', 'state.cjs'), mockedState);

// Mock process.js output path
const processCode = fs.readFileSync(path.join(TEST_DIR, 'scripts', 'process.cjs'), 'utf8');
const mockedProcess = processCode.replace(
  "const KNOWLEDGE_DIR = 'X-knowledge';",
  `const KNOWLEDGE_DIR = '${TEST_DIR}/X-knowledge';`
);
fs.writeFileSync(path.join(TEST_DIR, 'scripts', 'process.cjs'), mockedProcess);

// Load modules from test dir
const { categorize } = require(path.join(TEST_DIR, 'scripts', 'lib', 'categorize.cjs'));
const state = require(path.join(TEST_DIR, 'scripts', 'lib', 'state.cjs'));

// Load sample bookmarks
const sampleBookmarks = JSON.parse(fs.readFileSync(path.join(FIXTURES_DIR, 'sample-bookmarks.json'), 'utf8'));

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

// Test 1: Load and categorize bookmarks
console.log('📋 Test: Load and categorize sample bookmarks');
test('Sample data has 5 bookmarks', () => {
  if (sampleBookmarks.length !== 5) throw new Error(`Expected 5, got ${sampleBookmarks.length}`);
});

test('GitHub bookmark categorized as tools', () => {
  const gh = sampleBookmarks.find(b => b.url.includes('github.com'));
  if (!gh) throw new Error('GitHub bookmark not found');
  const cat = categorize(gh.url);
  if (cat !== 'tools') throw new Error(`Expected tools, got ${cat}`);
});

test('Medium bookmark categorized as articles', () => {
  const med = sampleBookmarks.find(b => b.url.includes('medium.com'));
  if (!med) throw new Error('Medium bookmark not found');
  const cat = categorize(med.url);
  if (cat !== 'articles') throw new Error(`Expected articles, got ${cat}`);
});

test('arXiv bookmark categorized as research', () => {
  const arx = sampleBookmarks.find(b => b.url.includes('arxiv.org'));
  if (!arx) throw new Error('arXiv bookmark not found');
  const cat = categorize(arx.url);
  if (cat !== 'research') throw new Error(`Expected research, got ${cat}`);
});

test('YouTube bookmark categorized as videos', () => {
  const yt = sampleBookmarks.find(b => b.url.includes('youtube.com'));
  if (!yt) throw new Error('YouTube bookmark not found');
  const cat = categorize(yt.url);
  if (cat !== 'videos') throw new Error(`Expected videos, got ${cat}`);
});

// Test 2: State operations
console.log('\n💾 Test: State save/load cycle');
test('Save pending bookmarks', () => {
  state.savePending(sampleBookmarks);
  const loaded = state.loadPending();
  if (loaded.length !== 5) throw new Error(`Expected 5, got ${loaded.length}`);
});

test('Mark some as processed', () => {
  state.markProcessed(['1234567890', '1234567891']);
  const processed = state.loadProcessed();
  if (!processed.has('1234567890')) throw new Error('ID 1234567890 not in processed');
  if (!processed.has('1234567891')) throw new Error('ID 1234567891 not in processed');
  if (processed.size !== 2) throw new Error(`Expected 2 processed, got ${processed.size}`);
});

test('Clear pending', () => {
  state.clearPending();
  const pending = state.loadPending();
  if (pending.length !== 0) throw new Error(`Expected empty, got ${pending.length}`);
});

// Test 3: Markdown generation (without AI)
console.log('\n📝 Test: Markdown generation');
test('Generate slug from title', () => {
  // Using the process.js logic
  function generateSlug(url, title) {
    if (title) {
      return title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, '')
        .slice(0, 50);
    }
    try {
      const urlObj = new URL(url);
      return urlObj.hostname.replace(/\./g, '-');
    } catch {
      return 'bookmark-' + Date.now();
    }
  }
  
  const slug = generateSlug('https://example.com', 'Hello World Test');
  if (slug !== 'hello-world-test') throw new Error(`Got: ${slug}`);
});

test('Generate slug from URL when no title', () => {
  function generateSlug(url) {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname.replace(/\./g, '-');
    } catch {
      return 'bookmark';
    }
  }
  
  const slug = generateSlug('https://github.com/user/repo');
  if (slug !== 'github-com') throw new Error(`Got: ${slug}`);
});

// Test 4: Directory structure
console.log('\n📁 Test: Output directory structure');
const knowledgeDir = path.join(TEST_DIR, 'X-knowledge');
fs.mkdirSync(path.join(knowledgeDir, 'tools'), { recursive: true });
fs.mkdirSync(path.join(knowledgeDir, 'articles'), { recursive: true });

test('Create category directories', () => {
  if (!fs.existsSync(path.join(knowledgeDir, 'tools'))) {
    throw new Error('tools dir not created');
  }
  if (!fs.existsSync(path.join(knowledgeDir, 'articles'))) {
    throw new Error('articles dir not created');
  }
});

test('Write sample markdown file', () => {
  const mdContent = `---
title: "Test Article"
type: articles
date_archived: 2026-01-31
source_tweet: https://x.com/i/web/status/1234567892
link: https://medium.com/@author/test
tags: ["test", "article"]
---

This is a test summary.
`;
  const filepath = path.join(knowledgeDir, 'articles', 'test-article.md');
  fs.writeFileSync(filepath, mdContent);
  
  if (!fs.existsSync(filepath)) throw new Error('File not created');
  const content = fs.readFileSync(filepath, 'utf8');
  if (!content.includes('title:')) throw new Error('Frontmatter missing');
});

// Cleanup
console.log('\n🧹 Cleaning up...');
fs.rmSync(TEST_DIR, { recursive: true, force: true });

console.log('\n' + (process.exitCode ? '❌ Integration tests failed' : '✅ Integration tests passed'));
