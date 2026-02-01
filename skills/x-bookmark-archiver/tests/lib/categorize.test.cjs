/**
 * Tests for categorize.js
 */

const { categorize, getCategories, CATEGORIES } = require('../../scripts/lib/categorize.cjs');

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
  if (actual !== expected) {
    throw new Error(`${msg || 'Assertion failed'}: expected "${expected}", got "${actual}"`);
  }
}

// Test: Tools categorization
console.log('\n📁 Tools Category Tests');
test('GitHub repo URL', () => {
  assertEqual(categorize('https://github.com/user/repo'), 'tools');
});
test('GitHub raw URL', () => {
  assertEqual(categorize('https://raw.githubusercontent.com/...'), 'tools');
});
test('HuggingFace', () => {
  assertEqual(categorize('https://huggingface.co/spaces/demo'), 'tools');
});
test('Vercel deployment', () => {
  assertEqual(categorize('https://myapp.vercel.app'), 'tools');
});

// Test: Articles categorization
console.log('\n📄 Articles Category Tests');
test('Medium article', () => {
  assertEqual(categorize('https://medium.com/@user/article'), 'articles');
});
test('Substack newsletter', () => {
  assertEqual(categorize('https://newsletter.substack.com/p/post'), 'articles');
});
test('Dev.to post', () => {
  assertEqual(categorize('https://dev.to/user/post-title'), 'articles');
});
test('X article', () => {
  assertEqual(categorize('https://x.com/i/article/12345'), 'articles');
});
test('Blog subdomain', () => {
  assertEqual(categorize('https://blog.example.com/post'), 'articles');
});

// Test: Videos categorization
console.log('\n🎬 Videos Category Tests');
test('YouTube video', () => {
  assertEqual(categorize('https://youtube.com/watch?v=123'), 'videos');
});
test('YouTube short URL', () => {
  assertEqual(categorize('https://youtu.be/abc123'), 'videos');
});
test('Vimeo', () => {
  assertEqual(categorize('https://vimeo.com/123456'), 'videos');
});

// Test: Research categorization
console.log('\n🔬 Research Category Tests');
test('arXiv paper', () => {
  assertEqual(categorize('https://arxiv.org/abs/1234.5678'), 'research');
});
test('Papers With Code', () => {
  assertEqual(categorize('https://paperswithcode.com/paper/abc'), 'research');
});

// Test: News categorization
console.log('\n📰 News Category Tests');
test('TechCrunch', () => {
  assertEqual(categorize('https://techcrunch.com/2024/01/01/article'), 'news');
});
test('Hacker News', () => {
  assertEqual(categorize('https://news.ycombinator.com/item?id=123'), 'news');
});

// Test: Fallback
console.log('\n📌 Fallback Tests');
test('Unknown domain falls back to bookmarks', () => {
  assertEqual(categorize('https://random-unknown-site.com/page'), 'bookmarks');
});
test('Empty string falls back', () => {
  assertEqual(categorize(''), 'bookmarks');
});

// Test: Case insensitivity
console.log('\n🔤 Case Insensitivity Tests');
test('Uppercase GitHub', () => {
  assertEqual(categorize('https://GITHUB.COM/user/repo'), 'tools');
});
test('Mixed case YouTube', () => {
  assertEqual(categorize('https://YouTube.Com/watch'), 'videos');
});

// Test: getCategories
console.log('\n📋 Category List Test');
test('getCategories returns all categories', () => {
  const cats = getCategories();
  if (!cats.includes('tools')) throw new Error('Missing tools');
  if (!cats.includes('articles')) throw new Error('Missing articles');
  if (!cats.includes('bookmarks')) throw new Error('Missing bookmarks');
});

console.log('\n' + (process.exitCode ? '❌ Some tests failed' : '✅ All tests passed'));
