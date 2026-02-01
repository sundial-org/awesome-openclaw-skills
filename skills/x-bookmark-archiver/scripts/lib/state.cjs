/**
 * State management for bookmark processing
 * Tracks pending and processed bookmarks
 */

const fs = require('fs');
const path = require('path');

const STATE_DIR = process.env.X_BOOKMARK_STATE_DIR || (require('os').homedir() + '/.clawd/.state');
const PENDING = path.join(STATE_DIR, 'x-bookmark-pending.json');
const PROCESSED = path.join(STATE_DIR, 'x-bookmark-processed.json');

/**
 * Ensure state directory exists
 */
function ensureStateDir() {
  if (!fs.existsSync(STATE_DIR)) {
    fs.mkdirSync(STATE_DIR, { recursive: true });
  }
}

/**
 * Load pending bookmarks
 * @returns {Array} - Array of pending bookmark objects
 */
function loadPending() {
  ensureStateDir();
  if (!fs.existsSync(PENDING)) return [];
  try {
    const data = fs.readFileSync(PENDING, 'utf8');
    return JSON.parse(data);
  } catch (e) {
    console.error('Error loading pending:', e.message);
    return [];
  }
}

/**
 * Save pending bookmarks
 * @param {Array} data - Array of bookmark objects
 */
function savePending(data) {
  ensureStateDir();
  fs.writeFileSync(PENDING, JSON.stringify(data, null, 2));
}

/**
 * Load processed bookmark IDs
 * @returns {Set} - Set of processed bookmark IDs
 */
function loadProcessed() {
  ensureStateDir();
  if (!fs.existsSync(PROCESSED)) return new Set();
  try {
    const data = fs.readFileSync(PROCESSED, 'utf8');
    const arr = JSON.parse(data);
    return new Set(arr);
  } catch (e) {
    console.error('Error loading processed:', e.message);
    return new Set();
  }
}

/**
 * Save processed bookmark IDs
 * @param {Set} set - Set of processed IDs
 */
function saveProcessed(set) {
  ensureStateDir();
  fs.writeFileSync(PROCESSED, JSON.stringify([...set], null, 2));
}

/**
 * Add IDs to processed list
 * @param {string[]} ids - Array of bookmark IDs to add
 */
function markProcessed(ids) {
  const processed = loadProcessed();
  ids.forEach(id => processed.add(id));
  saveProcessed(processed);
}

/**
 * Clear pending list
 */
function clearPending() {
  savePending([]);
}

module.exports = {
  loadPending,
  savePending,
  loadProcessed,
  saveProcessed,
  markProcessed,
  clearPending,
  PENDING,
  PROCESSED
};
