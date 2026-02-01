/**
 * Simple integration example for Clawdbot
 * 
 * This shows how to use the context pruner with archive support in a Clawdbot skill.
 */

import { createContextPruner } from '../lib/index.js';

// Simple wrapper for Clawdbot integration
class SimpleContextManager {
  constructor(options = {}) {
    this.pruner = createContextPruner({
      contextLimit: 64000,
      autoCompact: true,
      dynamicContext: true,
      strategies: ['semantic', 'temporal', 'extractive', 'adaptive'],
      queryAwareCompaction: true,
      preserveRecent: 15,
      preserveSystem: true,
      preserveHighPriority: 8,
      compactThreshold: 0.75,      // Start compacting at 75% usage
      aggressiveCompactThreshold: 0.9, // Aggressive compaction at 90%
      minRelevanceScore: 0.3,
      relevanceDecay: 0.95,
      enableArchive: true,
      archivePath: './context-archive',
      archiveMaxSize: 50 * 1024 * 1024, // 50MB for demo
      ...options
    });
    
    this.conversation = [];
    this.initialized = false;
  }
  
  async initialize() {
    if (!this.initialized) {
      await this.pruner.initialize();
      this.initialized = true;
      console.log('[Context] Initialized with archive support');
    }
  }
  
  // Add a message to the conversation
  async addMessage(role, content, priority = 5) {
    await this.initialize();
    
    const message = {
      role,
      content,
      priority,
      timestamp: Date.now(),
    };
    
    this.conversation.push(message);
    
    // Auto-compact if needed
    const status = this.pruner.getStatus();
    if (status.health !== 'HEALTHY') {
      console.log(`[Context] Health: ${status.health} - auto-compacting...`);
      await this.autoCompact();
    }
    
    return message;
  }
  
  // Get the current conversation (pruned if needed)
  async getConversation() {
    await this.initialize();
    
    // Process messages with pruning and archive storage
    this.conversation = await this.pruner.processMessages(this.conversation);
    
    return [...this.conversation];
  }
  
  // Auto-compact based on current health status
  async autoCompact() {
    const status = this.pruner.getStatus();
    let strategy;
    
    switch (status.health) {
      case 'AGGRESSIVE_COMPACT':
        strategy = 'aggressive';
        break;
      case 'COMPACT':
        strategy = 'balanced';
        break;
      default:
        return; // No compaction needed
    }
    
    console.log(`[Context] Auto-compacting with ${strategy} strategy`);
    this.conversation = await this.pruner.autoCompact(this.conversation, null, strategy);
  }
  
  // Force compact to specific token count
  async compactTo(targetTokens) {
    await this.initialize();
    
    this.conversation = await this.pruner.adaptiveCompact(this.conversation, targetTokens, 'balanced');
    
    return this.conversation;
  }
  
  // Search archive for relevant information
  async searchArchive(query, options = {}) {
    await this.initialize();
    
    const result = await this.pruner.retrieveFromArchive(query, {
      maxContextTokens: 1000,
      minRelevance: 0.4,
      ...options,
    });
    
    return result;
  }
  
  // Get current status
  getStatus() {
    return this.pruner.getStatus();
  }
  
  // Clear conversation
  clear() {
    this.conversation = [];
    this.pruner.resetStats();
    console.log('[Context] Conversation cleared');
  }
  
  // Get statistics
  getStats() {
    const stats = this.pruner.getStats();
    const status = this.pruner.getStatus();
    
    return {
      ...stats,
      archive: status.archive,
      relevanceStats: status.relevanceStats,
    };
  }
}

// Example usage
async function demonstrate() {
  console.log('=== Context Manager with Auto-Compaction Demo ===\n');
  
  const manager = new SimpleContextManager({
    contextLimit: 2000, // Small for demo
    compactThreshold: 0.6,
    aggressiveCompactThreshold: 0.8,
  });
  
  await manager.initialize();
  
  // Simulate a conversation
  console.log('1. Starting conversation...');
  
  await manager.addMessage('system', 'You are a helpful assistant.', 9);
  await manager.addMessage('user', 'Hello! I need help with programming.', 6);
  await manager.addMessage('assistant', 'Hi there! I can help with programming. What language are you using?', 5);
  await manager.addMessage('user', 'I\'m using TypeScript. I need to create a function that sorts an array.', 7);
  await manager.addMessage('assistant', 'Here\'s a TypeScript function that sorts an array:\n\n```typescript\nfunction sortArray<T>(arr: T[]): T[] {\n  return [...arr].sort();\n}\n```', 6);
  
  let status = manager.getStatus();
  console.log(`Initial: ${status.messages} messages, ${status.tokens.used}/${status.tokens.limit} tokens`);
  console.log(`Health: ${status.health}`);
  console.log(`Archive enabled: ${status.archive.enabled}\n`);
  
  // Add many messages to exceed context
  console.log('2. Adding many messages to trigger auto-compaction...');
  
  for (let i = 0; i < 30; i++) {
    await manager.addMessage(
      i % 2 === 0 ? 'user' : 'assistant',
      `Discussion ${i}: This is a detailed conversation about programming concepts ` +
      `including data structures, algorithms, and best practices. We're discussing ` +
      `how to implement efficient sorting algorithms in TypeScript.`,
      i % 5 === 0 ? 8 : 5
    );
    
    // Check status every 5 messages
    if (i % 5 === 0 && i > 0) {
      status = manager.getStatus();
      console.log(`After ${i} messages: ${status.tokens.used} tokens, Health: ${status.health}`);
      
      if (status.archive.enabled) {
        console.log(`  Archive: ${status.archive.stats.totalEntries} entries`);
      }
      
      if (status.relevanceStats) {
        console.log(`  Relevance: avg ${status.relevanceStats.avg.toFixed(2)}, ` +
                   `${status.relevanceStats.lowRelevance} low-relevance messages`);
      }
    }
  }
  
  // Final status
  status = manager.getStatus();
  const stats = manager.getStats();
  
  console.log('\n3. Final Results:');
  console.log(`Conversation length: ${status.messages} messages`);
  console.log(`Token usage: ${status.tokens.used}/${status.tokens.limit} (${status.tokens.percentage}%)`);
  console.log(`Health: ${status.health}`);
  console.log(`\nStatistics:`);
  console.log(`  Messages compacted: ${stats.totalCompacted}`);
  console.log(`  Tokens saved: ${stats.totalTokensSaved}`);
  console.log(`  Archive stores: ${stats.archiveStores}`);
  console.log(`  Compaction operations: ${stats.compactions}`);
  console.log(`  Dynamic adjustments: ${stats.dynamicAdjustments}`);
  console.log(`  Relevance updates: ${stats.relevanceUpdates}`);
  
  if (status.archive.enabled) {
    console.log(`\nArchive Statistics:`);
    console.log(`  Total entries: ${status.archive.stats.totalEntries}`);
    console.log(`  Archive size: ${Math.round(status.archive.stats.totalSize / 1024)}KB / ${Math.round(status.archive.stats.maxSize / 1024 / 1024)}MB`);
    console.log(`  Usage: ${Math.round(status.archive.stats.usagePercentage)}%`);
    console.log(`  Searches: ${status.archive.stats.searches} (Hits: ${status.archive.stats.hits}, Misses: ${status.archive.stats.misses})`);
  }
  
  // Demonstrate archive retrieval
  console.log('\n4. Demonstrating archive retrieval...');
  
  const archiveResult = await manager.searchArchive('TypeScript sorting function');
  
  if (archiveResult.found) {
    console.log(`Found ${archiveResult.sources.length} relevant sources in archive:`);
    archiveResult.sources.forEach((source, i) => {
      console.log(`  Source ${i + 1}: Score ${source.score.toFixed(2)}, ${source.snippetsCount} snippets`);
    });
    
    console.log(`\nRetrieved ${archiveResult.totalTokens} tokens from archive:`);
    archiveResult.snippets.forEach((snippet, i) => {
      const shortSnippet = snippet.length > 80 ? snippet.substring(0, 77) + '...' : snippet;
      console.log(`  [${i + 1}] ${shortSnippet}`);
    });
  } else {
    console.log('No relevant information found in archive.');
  }
  
  // Show current conversation summary
  const conversation = await manager.getConversation();
  console.log(`\n5. Current conversation (${conversation.length} messages):`);
  conversation.forEach((msg, i) => {
    const shortContent = msg.content.length > 60 
      ? msg.content.substring(0, 57) + '...' 
      : msg.content;
    const compressedFlag = msg.compressed ? ' [C]' : '';
    console.log(`  [${i}] ${msg.role.toUpperCase()}${compressedFlag} (prio: ${msg.priority || 5}): ${shortContent}`);
  });
  
  // Clear and reset
  manager.clear();
  
  console.log('\nDemo completed!');
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  demonstrate().catch(console.error);
}

export { SimpleContextManager };