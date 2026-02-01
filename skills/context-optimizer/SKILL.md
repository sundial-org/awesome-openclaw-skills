---
name: context-optimizer
description: Advanced context management with auto-compaction and dynamic context optimization for DeepSeek's 64k context window. Features intelligent compaction (merging, summarizing, extracting), query-aware relevance scoring, and hierarchical memory system with context archive. Logs optimization events to chat.
homepage: https://github.com/clawdbot/clawdbot
metadata:
  clawdbot:
    emoji: "🧠"
    requires:
      bins: []
      npm: ["tiktoken", "@xenova/transformers"]
    install:
      - id: npm
        kind: npm
        label: Install Context Pruner dependencies
        command: "cd ~/.clawdbot/skills/context-pruner && npm install"
---

# Context Pruner

Advanced context management optimized for DeepSeek's 64k context window. Provides intelligent pruning, compression, and token optimization to prevent context overflow while preserving important information.

## Key Features

- **DeepSeek-optimized**: Specifically tuned for 64k context window
- **Adaptive pruning**: Multiple strategies based on context usage
- **Semantic deduplication**: Removes redundant information
- **Priority-aware**: Preserves high-value messages
- **Token-efficient**: Minimizes token overhead
- **Real-time monitoring**: Continuous context health tracking

## Quick Start

### Auto-compaction with dynamic context:
```javascript
import { createContextPruner } from './lib/index.js';

const pruner = createContextPruner({
  contextLimit: 64000, // DeepSeek's limit
  autoCompact: true,    // Enable automatic compaction
  dynamicContext: true, // Enable dynamic relevance-based context
  strategies: ['semantic', 'temporal', 'extractive', 'adaptive'],
  queryAwareCompaction: true, // Compact based on current query relevance
});

await pruner.initialize();

// Process messages with auto-compaction and dynamic context
const processed = await pruner.processMessages(messages, currentQuery);

// Get context health status
const status = pruner.getStatus();
console.log(`Context health: ${status.health}, Relevance scores: ${status.relevanceScores}`);

// Manual compaction when needed
const compacted = await pruner.autoCompact(messages, currentQuery);
```

### Archive Retrieval (Hierarchical Memory):
```javascript
// When something isn't in current context, search archive
const archiveResult = await pruner.retrieveFromArchive('query about previous conversation', {
  maxContextTokens: 1000,
  minRelevance: 0.4,
});

if (archiveResult.found) {
  // Add relevant snippets to current context
  const archiveContext = archiveResult.snippets.join('\n\n');
  // Use archiveContext in your prompt
  console.log(`Found ${archiveResult.sources.length} relevant sources`);
  console.log(`Retrieved ${archiveResult.totalTokens} tokens from archive`);
}
```

## Auto-Compaction Strategies

1. **Semantic Compaction**: Merges similar messages instead of removing them
2. **Temporal Compaction**: Summarizes older conversations by time windows  
3. **Extractive Compaction**: Extracts key information from verbose messages
4. **Adaptive Compaction**: Chooses best strategy based on message characteristics
5. **Dynamic Context**: Filters messages based on relevance to current query

## Dynamic Context Management

- **Query-aware Relevance**: Scores messages based on similarity to current query
- **Relevance Decay**: Relevance scores decay over time for older conversations
- **Adaptive Filtering**: Automatically filters low-relevance messages
- **Priority Integration**: Combines message priority with semantic relevance

## Hierarchical Memory System

The context archive provides a RAM vs Storage approach:

- **Current Context (RAM)**: Limited (64k tokens), fast access, auto-compacted
- **Archive (Storage)**: Larger (100MB), slower but searchable
- **Smart Retrieval**: When information isn't in current context, efficiently search archive
- **Selective Loading**: Extract only relevant snippets, not entire documents
- **Automatic Storage**: Compacted content automatically stored in archive

## Configuration

```javascript
{
  contextLimit: 64000, // DeepSeek's context window
  autoCompact: true, // Enable automatic compaction
  compactThreshold: 0.75, // Start compacting at 75% usage
  aggressiveCompactThreshold: 0.9, // Aggressive compaction at 90%
  
  dynamicContext: true, // Enable dynamic context management
  relevanceDecay: 0.95, // Relevance decays 5% per time step
  minRelevanceScore: 0.3, // Minimum relevance to keep
  queryAwareCompaction: true, // Compact based on current query relevance
  
  strategies: ['semantic', 'temporal', 'extractive', 'adaptive'],
  preserveRecent: 10, // Always keep last N messages
  preserveSystem: true, // Always keep system messages
  minSimilarity: 0.85, // Semantic similarity threshold
  
  // Archive settings
  enableArchive: true, // Enable hierarchical memory system
  archivePath: './context-archive',
  archiveSearchLimit: 10,
  archiveMaxSize: 100 * 1024 * 1024, // 100MB
  archiveIndexing: true,
  
  // Chat logging
  logToChat: true, // Log optimization events to chat
  chatLogLevel: 'brief', // 'brief', 'detailed', or 'none'
  chatLogFormat: '📊 {action}: {details}', // Format for chat messages
  
  // Performance
  batchSize: 5, // Messages to process in batch
  maxCompactionRatio: 0.5, // Maximum 50% compaction in one pass
}
```

## Chat Logging

The context optimizer can log events directly to chat:

```javascript
// Example chat log messages:
// 📊 Context optimized: Compacted 15 messages → 8 (47% reduction)
// 📊 Archive search: Found 3 relevant snippets (42% similarity)
// 📊 Dynamic context: Filtered 12 low-relevance messages

// Configure logging:
const pruner = createContextPruner({
  logToChat: true,
  chatLogLevel: 'brief', // Options: 'brief', 'detailed', 'none'
  chatLogFormat: '📊 {action}: {details}',
  
  // Custom log handler (optional)
  onLog: (level, message, data) => {
    if (level === 'info' && data.action === 'compaction') {
      // Send to chat
      console.log(`🧠 Context optimized: ${message}`);
    }
  }
});
```

## Integration with Clawdbot

Add to your Clawdbot config:

```yaml
skills:
  context-pruner:
    enabled: true
    config:
      contextLimit: 64000
      autoPrune: true
```

The pruner will automatically monitor context usage and apply appropriate pruning strategies to stay within DeepSeek's 64k limit.