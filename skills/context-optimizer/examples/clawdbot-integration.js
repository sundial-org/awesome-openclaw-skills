/**
 * Example: Integrating Context Pruner with Clawdbot
 * 
 * This shows how to use the Context Pruner in a Clawdbot skill or agent.
 */

import { createContextPruner } from '../lib/index.js';

class ClawdbotContextManager {
  constructor() {
    // Create a pruner optimized for DeepSeek
    this.pruner = createContextPruner({
      contextLimit: 64000, // DeepSeek's 64k window
      model: 'deepseek-chat',
      strategies: ['semantic', 'temporal', 'extractive'],
      autoPrune: true,
      warningThreshold: 0.7,
      pruneThreshold: 0.8,
      emergencyThreshold: 0.95,
      preserveRecent: 15,
      preserveSystem: true,
      preserveHighPriority: 8,
    });
    
    this.initialized = false;
    this.messageBuffer = [];
  }
  
  async initialize() {
    if (!this.initialized) {
      await this.pruner.initialize();
      this.initialized = true;
      console.log('Context Pruner initialized for DeepSeek 64k context');
    }
  }
  
  /**
   * Add a message to the conversation and automatically prune if needed
   */
  async addMessage(role, content, priority = 5) {
    await this.initialize();
    
    const message = {
      role,
      content,
      priority,
      timestamp: Date.now(),
    };
    
    this.messageBuffer.push(message);
    
    // Check if we should prune
    const status = this.pruner.getStatus();
    if (status.health !== 'HEALTHY') {
      console.log(`Context health: ${status.health} - pruning...`);
      this.messageBuffer = await this.pruner.processMessages(this.messageBuffer);
    }
    
    return message;
  }
  
  /**
   * Get current conversation context (pruned if needed)
   */
  async getContext() {
    await this.initialize();
    
    // Ensure context is within limits
    const processed = await this.pruner.processMessages(this.messageBuffer);
    
    // Update buffer with processed messages
    this.messageBuffer = processed;
    
    return processed;
  }
  
  /**
   * Force pruning to target token count
   */
  async pruneToTokens(targetTokens) {
    await this.initialize();
    
    this.messageBuffer = await this.pruner.prune(this.messageBuffer, {
      targetTokens,
      strategy: 'balanced',
    });
    
    return this.messageBuffer;
  }
  
  /**
   * Get current status and statistics
   */
  getStatus() {
    const prunerStatus = this.pruner.getStatus();
    const stats = this.pruner.getStats();
    
    return {
      ...prunerStatus,
      bufferSize: this.messageBuffer.length,
      bufferTokens: this.pruner.countTokensForMessages(this.messageBuffer),
      detailedStats: stats,
    };
  }
  
  /**
   * Clear the conversation buffer
   */
  clear() {
    this.messageBuffer = [];
    this.pruner.resetStats();
    console.log('Conversation buffer cleared');
  }
  
  /**
   * Cleanup resources
   */
  destroy() {
    this.pruner.destroy();
    this.initialized = false;
  }
}

// Example usage in a Clawdbot skill
async function exampleUsage() {
  console.log('=== Clawdbot Context Pruner Example ===\n');
  
  const contextManager = new ClawdbotContextManager();
  
  // Simulate a conversation
  console.log('1. Starting conversation...');
  await contextManager.addMessage('system', 'You are Clawdbot, a helpful AI assistant.', 9);
  await contextManager.addMessage('user', 'Hello! Can you help me with some coding?', 6);
  await contextManager.addMessage('assistant', 'Of course! I\'d be happy to help with coding. What language are you using?', 5);
  
  let status = contextManager.getStatus();
  console.log(`Initial status: ${status.bufferSize} messages, ${status.bufferTokens} tokens`);
  console.log(`Health: ${status.health}\n`);
  
  // Simulate a long conversation that would exceed context
  console.log('2. Simulating long conversation...');
  for (let i = 0; i < 100; i++) {
    await contextManager.addMessage(
      i % 2 === 0 ? 'user' : 'assistant',
      `Message ${i}: This is part of a long conversation about programming concepts and best practices. ` +
      `We're discussing various topics to simulate a real conversation that might exceed context limits.`,
      i % 10 === 0 ? 8 : 5 // Every 10th message is high priority
    );
    
    // Check status every 20 messages
    if (i % 20 === 0 && i > 0) {
      status = contextManager.getStatus();
      console.log(`After ${i} messages: ${status.bufferSize} messages, ${status.bufferTokens} tokens`);
      console.log(`Health: ${status.health}, Tokens saved: ${status.detailedStats.totalTokensSaved}`);
    }
  }
  
  // Final status
  status = contextManager.getStatus();
  console.log('\n3. Final status:');
  console.log(`Total messages in buffer: ${status.bufferSize}`);
  console.log(`Total tokens: ${status.bufferTokens}/${status.tokens.limit} (${status.tokens.percentage}%)`);
  console.log(`Health status: ${status.health}`);
  console.log(`\nStatistics:`);
  console.log(`  Messages pruned: ${status.detailedStats.totalPruned}`);
  console.log(`  Messages compressed: ${status.detailedStats.totalCompressed}`);
  console.log(`  Tokens saved: ${status.detailedStats.totalTokensSaved}`);
  console.log(`  Prune operations: ${status.detailedStats.prunes}`);
  console.log(`  Compression operations: ${status.detailedStats.compressions}`);
  
  // Example: Force pruning to specific token count
  console.log('\n4. Force pruning to 30k tokens...');
  await contextManager.pruneToTokens(30000);
  
  status = contextManager.getStatus();
  console.log(`After forced pruning: ${status.bufferSize} messages, ${status.bufferTokens} tokens`);
  
  // Cleanup
  contextManager.destroy();
  console.log('\nExample completed!');
}

// Run example if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  exampleUsage().catch(console.error);
}

export { ClawdbotContextManager };