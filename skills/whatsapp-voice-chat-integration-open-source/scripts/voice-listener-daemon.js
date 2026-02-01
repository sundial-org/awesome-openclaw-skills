#!/usr/bin/env node
/**
 * Voice Listener Daemon
 * Watches for incoming voice messages and processes them in real-time
 * 
 * Part of: whatsapp-voice-talk skill
 */

const fs = require('fs');
const path = require('path');
const { processVoiceNote } = require('./voice-processor');

// Configuration
const CONFIG = {
  inboundDir: path.join(process.env.APPDATA || process.env.HOME, '.clawdbot', 'media', 'inbound'),
  processedLog: path.join(__dirname, '.voice-processed.log'),
  checkInterval: 5000, // 5 seconds
  autoSendResponse: true
};

/**
 * Load list of already processed files
 */
function loadProcessedFiles() {
  if (fs.existsSync(CONFIG.processedLog)) {
    return new Set(fs.readFileSync(CONFIG.processedLog, 'utf8').split('\n').filter(x => x));
  }
  return new Set();
}

/**
 * Mark file as processed
 */
function markProcessed(filename) {
  fs.appendFileSync(CONFIG.processedLog, filename + '\n');
}

/**
 * Process a voice file
 */
async function processVoiceFile(filePath) {
  try {
    const filename = path.basename(filePath);
    console.log(`[LISTENER] Found voice: ${filename}`);
    
    // Read file
    const buffer = fs.readFileSync(filePath);
    
    // Process
    const result = await processVoiceNote(buffer);
    
    if (result.status === 'success') {
      console.log(`[LISTENER] ✅ Processed: "${result.transcript}"`);
      console.log(`[LISTENER] Response: "${result.response}"`);
      
      // Emit response event for parent process to handle sending
      console.log(JSON.stringify({
        type: 'voice-response',
        data: result
      }));
      
    } else {
      console.log(`[LISTENER] ❌ Error: ${result.response || result.error}`);
    }
    
    // Mark as processed
    markProcessed(filename);
    
  } catch (e) {
    console.error(`[LISTENER] Error processing file: ${e.message}`);
  }
}

/**
 * Check for new voice files
 */
async function checkForNewVoices() {
  try {
    if (!fs.existsSync(CONFIG.inboundDir)) {
      console.log(`[LISTENER] Waiting for directory: ${CONFIG.inboundDir}`);
      return;
    }
    
    const processed = loadProcessedFiles();
    const files = fs.readdirSync(CONFIG.inboundDir)
      .filter(f => /\.(ogg|m4a|wav|mp3)$/i.test(f));
    
    for (const file of files) {
      if (!processed.has(file)) {
        const filePath = path.join(CONFIG.inboundDir, file);
        await processVoiceFile(filePath);
      }
    }
    
  } catch (e) {
    console.error(`[LISTENER] Scan error: ${e.message}`);
  }
}

/**
 * Start the daemon
 */
function start() {
  console.log('[LISTENER] Starting voice listener daemon...');
  console.log(`[LISTENER] Watching: ${CONFIG.inboundDir}`);
  console.log(`[LISTENER] Checking every ${CONFIG.checkInterval}ms...`);
  
  // Check immediately
  checkForNewVoices();
  
  // Then check periodically
  const interval = setInterval(checkForNewVoices, CONFIG.checkInterval);
  
  // Handle shutdown
  process.on('SIGINT', () => {
    console.log('\n[LISTENER] Shutting down...');
    clearInterval(interval);
    process.exit(0);
  });
  
  return interval;
}

// Start if run directly
if (require.main === module) {
  start();
}

module.exports = { start, checkForNewVoices, processVoiceFile };
