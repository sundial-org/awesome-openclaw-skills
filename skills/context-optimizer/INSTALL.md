# Installation Guide

## Installation

The context-pruner skill requires dependencies for full functionality including semantic pruning and archive features:

```bash
# Install dependencies
cd context-pruner
npm install

# Or install globally
npm install -g .
```

**Required Dependencies:**
- `tiktoken` for accurate token counting
- `@xenova/transformers` for semantic embeddings and archive indexing

## Integration with Clawdbot

### Method 1: As a Standalone Skill

1. Copy the skill to your Clawdbot skills directory:
   ```bash
   cp -r context-pruner /Users/atharvadeshmukh/clawd/skills/
   ```

2. The skill will appear in your available skills list

### Method 2: Direct Code Integration

Add this to your Clawdbot agent or skill:

```javascript
import { createContextPruner } from './skills/context-pruner/lib/index.js';

class MyAgent {
  constructor() {
    this.pruner = createContextPruner({
      contextLimit: 64000,
      autoCompact: true, // Enable auto-compaction
      dynamicContext: true, // Enable dynamic context
      strategies: ['semantic', 'temporal', 'extractive', 'adaptive'],
      queryAwareCompaction: true, // Compact based on query relevance
      enableArchive: true, // Enable hierarchical memory
      archivePath: './context-archive',
    });
    
    await this.pruner.initialize();
  }
  
  async processConversation(messages, currentQuery = null) {
    // Process messages with auto-compaction and dynamic context
    const processed = await this.pruner.processMessages(messages, currentQuery);
    
    // Get context status
    const status = this.pruner.getStatus();
    console.log(`Context health: ${status.health}, Tokens: ${status.tokens.used}/${status.tokens.limit}`);
    console.log(`Relevance scores: ${status.relevanceScores} messages scored`);
    
    return processed;
  }
  
  async searchArchive(query) {
    // When something isn't in current context, search archive
    const result = await this.pruner.retrieveFromArchive(query, {
      maxContextTokens: 1000,
      minRelevance: 0.4,
    });
    
    if (result.found) {
      console.log(`Found ${result.sources.length} relevant sources in archive`);
      return result.snippets.join('\n\n');
    }
    
    return null;
  }
}
```

### Method 3: Configuration-based (if supported by your Clawdbot version)

Add to your Clawdbot config file:

```yaml
skills:
  context-pruner:
    enabled: true
    config:
      contextLimit: 64000
      autoPrune: true
      strategies: ['semantic', 'temporal', 'extractive']
      preserveRecent: 15
      preserveSystem: true
      enableArchive: true
      archivePath: './context-archive'
      archiveMaxSize: 100000000  # 100MB
```

## Testing

Run the basic test to verify installation:

```bash
cd context-pruner
node lib/index.test.js
```

Or run the integration example:

```bash
cd context-pruner
node examples/simple-integration.js
```

## Auto-Compaction & Dynamic Context

The new system focuses on intelligent compaction rather than simple pruning:

- **Auto-Compaction**: Automatically compacts content when context usage exceeds thresholds
- **Dynamic Context**: Adjusts context based on relevance to current query
- **Semantic Merging**: Merges similar messages instead of removing them
- **Query-Aware**: Compaction decisions consider current conversation topic

### Auto-Compaction Example

```javascript
// Initialize pruner with auto-compaction
const pruner = createContextPruner({
  autoCompact: true,
  compactThreshold: 0.75, // Start compacting at 75% usage
  dynamicContext: true,
  queryAwareCompaction: true,
  enableArchive: true,
  archivePath: './my-context-archive',
});

await pruner.initialize();

// Process messages with current query for relevance scoring
const processed = await pruner.processMessages(conversation, currentUserQuery);

// Check compaction status
const status = pruner.getStatus();
console.log(`Compacted ${status.stats.totalCompacted} messages`);
console.log(`Saved ${status.stats.totalTokensSaved} tokens`);
console.log(`Relevance distribution:`, status.relevanceStats);

// Later, search archive for compacted content
const archiveResult = await pruner.retrieveFromArchive('query about previous discussion', {
  maxContextTokens: 800,
  minRelevance: 0.5,
});

if (archiveResult.found) {
  // Add relevant archive snippets to context
  const enhancedContext = [
    ...processed,
    { role: 'system', content: `[Relevant from Archive]: ${archiveResult.snippets.join('\n\n')}` }
  ];
}
```

## Troubleshooting

### "Cannot find module" errors
- Install dependencies with `npm install`
- Check Node.js version (requires Node 18+)

### Pruning too aggressively
- Increase `preserveRecent` value
- Adjust threshold values (`warningThreshold`, `pruneThreshold`)
- Use `conservative` strategy

### Archive not working
- Ensure `enableArchive: true` is set
- Check write permissions for `archivePath`
- Archive requires embedding model initialization

### Performance issues with embeddings
- First run downloads embedding model (~80MB)
- Subsequent runs use cached model
- Disable `archiveIndexing: false` if embeddings are too slow

### Archive size growing too large
- Archive auto-cleans when exceeding `archiveMaxSize`
- Lower priority entries removed first
- Adjust `archiveMaxSize` based on your storage

## Monitoring

Check archive statistics:

```javascript
const status = pruner.getStatus();
console.log('Archive stats:', status.archive.stats);
```

Archive statistics include:
- Total entries stored
- Archive size vs max size
- Search hit/miss rates
- Storage efficiency

## Updating

To update the skill:

```bash
cd /Users/atharvadeshmukh/clawd/skills/context-pruner
git pull  # if cloned from git
npm install  # update dependencies
# Or copy the updated files manually
```

## Uninstalling

Remove the skill folder and archive data:

```bash
rm -rf /Users/atharvadeshmukh/clawd/skills/context-pruner
rm -rf ./context-archive  # or your custom archive path
```