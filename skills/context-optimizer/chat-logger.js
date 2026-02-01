// Simple chat logger for context optimizer
// This demonstrates how to log optimization events to chat

class ContextOptimizerLogger {
  constructor(options = {}) {
    this.logToChat = options.logToChat !== false;
    this.logLevel = options.chatLogLevel || 'brief';
    this.logFormat = options.chatLogFormat || '📊 {action}: {details}';
    
    // Default log handler
    this.onLog = options.onLog || this.defaultLogHandler;
  }
  
  defaultLogHandler(level, message, data = {}) {
    if (this.logToChat && this.logLevel !== 'none') {
      const formatted = this.formatLogMessage(data.action, data.details);
      console.log(formatted);
      
      // In a real implementation, this would send to chat:
      // sendToChat(formatted);
    }
  }
  
  formatLogMessage(action, details) {
    return this.logFormat
      .replace('{action}', action)
      .replace('{details}', details);
  }
  
  // Log events
  logCompaction(before, after, strategy) {
    const reduction = Math.round((1 - after / before) * 100);
    const details = `Compacted ${before} messages → ${after} (${reduction}% reduction) using ${strategy}`;
    
    this.onLog('info', 'Context compaction completed', {
      action: 'Context optimized',
      details,
      before,
      after,
      reduction,
      strategy
    });
  }
  
  logArchiveSearch(query, results, avgSimilarity) {
    const similarity = Math.round(avgSimilarity * 100);
    const details = `Found ${results} relevant snippets (${similarity}% similarity) for "${query.substring(0, 30)}..."`;
    
    this.onLog('info', 'Archive search completed', {
      action: 'Archive search',
      details,
      query,
      results,
      similarity: avgSimilarity
    });
  }
  
  logDynamicContext(filtered, total, avgRelevance) {
    const relevance = Math.round(avgRelevance * 100);
    const details = `Filtered ${filtered} low-relevance messages (avg relevance: ${relevance}%)`;
    
    this.onLog('info', 'Dynamic context filtering', {
      action: 'Dynamic context',
      details,
      filtered,
      total,
      avgRelevance
    });
  }
  
  logHealthCheck(health, tokens, limit) {
    const usage = Math.round((tokens / limit) * 100);
    const details = `Health: ${health}, Usage: ${usage}% (${tokens}/${limit} tokens)`;
    
    this.onLog('info', 'Context health check', {
      action: 'Context health',
      details,
      health,
      tokens,
      limit,
      usage
    });
  }
}

// Example usage
function runDemo() {
  const logger = new ContextOptimizerLogger({
    logToChat: true,
    chatLogLevel: 'brief',
    chatLogFormat: '🧠 {action}: {details}'
  });
  
  console.log('=== Context Optimizer Chat Log Demo ===\n');
  
  // Simulate optimization events
  logger.logCompaction(15, 8, 'semantic');
  logger.logArchiveSearch('previous conversation about memory', 3, 0.42);
  logger.logDynamicContext(12, 25, 0.28);
  logger.logHealthCheck('good', 45200, 64000);
  
  console.log('\n=== End Demo ===');
}

// Run demo if script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runDemo();
}

export default ContextOptimizerLogger;