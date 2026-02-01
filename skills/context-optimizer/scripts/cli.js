#!/usr/bin/env node

/**
 * CLI for Context Pruner
 */

import { createContextPruner } from '../lib/index.js';
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command || command === 'help') {
    showHelp();
    return;
  }
  
  const pruner = createContextPruner({
    contextLimit: 64000,
    autoPrune: true,
    strategies: ['semantic', 'temporal', 'extractive'],
  });
  
  await pruner.initialize();
  
  switch (command) {
    case 'test':
      await runTest();
      break;
      
    case 'status':
      showStatus(pruner);
      break;
      
    case 'prune':
      await pruneFile(args[1], args[2], pruner);
      break;
      
    case 'stats':
      showStats(pruner);
      break;
      
    default:
      console.error(`Unknown command: ${command}`);
      showHelp();
      process.exit(1);
  }
  
  pruner.destroy();
}

function showHelp() {
  console.log(`
Context Pruner CLI - Advanced context management for DeepSeek

Usage:
  node cli.js <command> [options]

Commands:
  test        Run basic tests
  status      Show current pruner status
  prune <input> <output>  Prune a JSON file with messages
  stats       Show pruning statistics
  help        Show this help message

Examples:
  node cli.js test
  node cli.js status
  node cli.js prune messages.json pruned.json
  `);
}

async function runTest() {
  console.log('Running Context Pruner tests...\n');
  
  // Import and run the test
  const testModule = await import('../lib/index.test.js');
  await testModule.testContextPruner();
}

function showStatus(pruner) {
  const status = pruner.getStatus();
  console.log('Context Pruner Status:');
  console.log('=====================\n');
  
  console.log(`Health: ${status.health}`);
  console.log(`Tokens: ${status.tokens.used}/${status.tokens.limit} (${status.tokens.percentage}%)`);
  console.log(`Remaining: ${status.tokens.remaining} tokens`);
  console.log(`Messages in history: ${status.messages}`);
  
  console.log('\nConfiguration:');
  console.log(`  Strategies: ${status.config.strategies.join(', ')}`);
  console.log(`  Auto-prune: ${status.config.autoPrune ? 'Enabled' : 'Disabled'}`);
  console.log(`  Thresholds: Warning=${status.config.thresholds.warning*100}%, ` +
              `Prune=${status.config.thresholds.prune*100}%, ` +
              `Emergency=${status.config.thresholds.emergency*100}%`);
  
  console.log('\nStatistics:');
  console.log(`  Total pruned: ${status.stats.totalPruned} messages`);
  console.log(`  Total compressed: ${status.stats.totalCompressed} messages`);
  console.log(`  Total tokens saved: ${status.stats.totalTokensSaved}`);
  console.log(`  Prune operations: ${status.stats.prunes}`);
  console.log(`  Compression operations: ${status.stats.compressions}`);
}

async function pruneFile(inputPath, outputPath, pruner) {
  if (!inputPath || !outputPath) {
    console.error('Error: Both input and output paths are required');
    console.log('Usage: node cli.js prune <input.json> <output.json>');
    process.exit(1);
  }
  
  try {
    // Read input file
    const inputData = JSON.parse(readFileSync(inputPath, 'utf8'));
    
    if (!Array.isArray(inputData.messages) && !Array.isArray(inputData)) {
      console.error('Error: Input file must contain a "messages" array or be an array of messages');
      process.exit(1);
    }
    
    const messages = Array.isArray(inputData.messages) ? inputData.messages : inputData;
    
    console.log(`Processing ${messages.length} messages...`);
    console.log(`Initial tokens: ${pruner.countTokensForMessages(messages)}`);
    
    // Process messages
    const processed = await pruner.processMessages(messages);
    
    console.log(`After pruning: ${processed.length} messages`);
    console.log(`Final tokens: ${pruner.countTokensForMessages(processed)}`);
    
    // Save output
    const outputData = Array.isArray(inputData.messages) 
      ? { ...inputData, messages: processed }
      : processed;
    
    writeFileSync(outputPath, JSON.stringify(outputData, null, 2));
    
    console.log(`\nSaved pruned messages to: ${outputPath}`);
    showStatus(pruner);
    
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

function showStats(pruner) {
  const stats = pruner.getStats();
  console.log('Context Pruner Statistics:');
  console.log('==========================\n');
  
  console.log(`Total messages pruned: ${stats.totalPruned}`);
  console.log(`Total messages compressed: ${stats.totalCompressed}`);
  console.log(`Total tokens saved: ${stats.totalTokensSaved}`);
  console.log(`Prune operations: ${stats.prunes}`);
  console.log(`Compression operations: ${stats.compressions}`);
  
  if (stats.prunes > 0) {
    const avgPrunedPerOp = stats.totalPruned / stats.prunes;
    const avgTokensSavedPerOp = stats.totalTokensSaved / stats.prunes;
    console.log(`\nAverages per prune operation:`);
    console.log(`  Messages pruned: ${avgPrunedPerOp.toFixed(1)}`);
    console.log(`  Tokens saved: ${avgTokensSavedPerOp.toFixed(0)}`);
  }
}

// Run CLI
main().catch(console.error);