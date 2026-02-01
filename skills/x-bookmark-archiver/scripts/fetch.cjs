#!/usr/bin/env node
/**
 * Fetch bookmarks from X using bird CLI
 * Filters out already-processed bookmarks
 */

const { execSync } = require('child_process');
const { loadProcessed, savePending } = require('./lib/state.cjs');

const FETCH_COUNT = 50;

/**
 * Fetch bookmarks from X using bird CLI
 * @returns {Array} - Array of bookmark objects
 */
function fetchBookmarks() {
  try {
    const output = execSync(`bird bookmarks -n ${FETCH_COUNT} --json`, {
      encoding: 'utf8',
      timeout: 30000
    });
    return JSON.parse(output);
  } catch (e) {
    if (e.stderr?.includes('command not found') || e.message.includes('ENOENT')) {
      console.error('Error: bird CLI not found. Install from https://github.com/smmr-software/bird');
      process.exit(1);
    }
    console.error('Error fetching bookmarks:', e.message);
    return [];
  }
}

/**
 * Main fetch function
 */
function main() {
  console.log('🔍 Fetching bookmarks from X...');
  
  const bookmarks = fetchBookmarks();
  if (bookmarks.length === 0) {
    console.log('No bookmarks found.');
    return;
  }
  
  const processed = loadProcessed();
  
  // Filter out already processed
  const newBookmarks = bookmarks.filter(b => !processed.has(b.id));
  
  if (newBookmarks.length === 0) {
    console.log('✓ No new bookmarks to process');
    return;
  }
  
  // Save to pending
  savePending(newBookmarks);
  
  console.log(`\n✓ Found ${newBookmarks.length} new bookmark${newBookmarks.length === 1 ? '' : 's'}`);
  console.log(`  Total fetched: ${bookmarks.length}`);
  console.log(`  Already processed: ${bookmarks.length - newBookmarks.length}`);
}

if (require.main === module) {
  main();
}

module.exports = { fetchBookmarks };
