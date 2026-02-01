# Context Pruner

Advanced context management optimized for DeepSeek's 64k context window. Provides intelligent pruning, compression, and token optimization to prevent context overflow while preserving important information.

## Features

- **DeepSeek-optimized**: Specifically tuned for 64k context window
- **Multiple pruning strategies**: Semantic, temporal, and extractive compression
- **Adaptive pruning**: Different strategies based on context usage levels
- **Priority-aware**: Preserves high-priority and system messages
- **Real-time monitoring**: Continuous context health tracking
- **Token-efficient**: Minimizes token overhead from pruning operations

## Installation

```bash
# Install dependencies
npm install

# Or install globally for CLI use
npm install -g .
```

## Quick Start

```javascript
import { createContextPruner } from './lib/index.js';

const pruner = createContextPruner({
  contextLimit: 64000, // DeepSeek's limit
  autoPrune: true,
  strategies: ['semantic', 'temporal', 'extractive'],
});

await pruner.initialize();

// Process messages with automatic pruning
const messages = [
  { role: 'user', content: 'Hello!', priority: 5 },
  { role: 'assistant', content: 'Hi there!', priority: 5 },
  // ... more messages
];

const processed = await pruner.processMessages(messages);

// Get status
const status = pruner.getStatus();
console.log(`Health: ${status.health}`);
console.log(`Tokens: ${status.tokens.used}/${status.tokens.limit}`);
```

## CLI Usage

```bash
# Run tests
node scripts/cli.js test

# Show status
node scripts/cli.js status

# Prune a JSON file
node scripts/cli.js prune input.json output.json

# Show statistics
node scripts/cli.js stats
```

## Pruning Strategies

### 1. Semantic Pruning
Removes semantically similar messages using embeddings. Useful for eliminating redundant information.

### 2. Temporal Pruning
Removes older messages first, preserving recent conversation. Configurable preservation of recent messages.

### 3. Extractive Compression
Summarizes groups of messages using extractive summarization. Preserves key information while reducing token count.

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `contextLimit` | 64000 | DeepSeek's context window size |
| `model` | 'deepseek-chat' | Model-specific optimizations |
| `warningThreshold` | 0.7 | Warn at 70% usage |
| `pruneThreshold` | 0.8 | Start pruning at 80% usage |
| `emergencyThreshold` | 0.95 | Aggressive pruning at 95% usage |
| `strategies` | ['semantic', 'temporal', 'extractive'] | Pruning strategies to use |
| `autoPrune` | true | Enable automatic pruning |
| `preserveRecent` | 10 | Always keep last N messages |
| `preserveSystem` | true | Always keep system messages |
| `preserveHighPriority` | 8 | Priority threshold for preservation |
| `minSimilarity` | 0.85 | Semantic deduplication threshold |
| `summarizer` | null | Optional LLM summarizer function |

## Integration with Clawdbot

### As a Skill

1. Copy the `context-pruner` folder to your Clawdbot skills directory
2. Add to your Clawdbot config:

```yaml
skills:
  context-pruner:
    enabled: true
    config:
      contextLimit: 64000
      autoPrune: true
      strategies: ['semantic', 'temporal', 'extractive']
```

### Direct Integration

```javascript
import { ClawdbotContextManager } from './examples/clawdbot-integration.js';

const contextManager = new ClawdbotContextManager();
await contextManager.initialize();

// Add messages
await contextManager.addMessage('user', 'Hello!', 6);

// Get pruned context
const context = await contextManager.getContext();

// Check status
const status = contextManager.getStatus();
```

## Health Status

The pruner monitors context usage and reports health status:

- **HEALTHY**: Below 70% usage
- **WARNING**: 70-80% usage (mild pruning may occur)
- **PRUNE**: 80-95% usage (active pruning)
- **EMERGENCY**: Above 95% usage (aggressive pruning)

## Performance

- **Token counting**: Uses tiktoken for accurate token estimation
- **Embeddings**: Uses Xenova/transformers for local semantic analysis
- **Memory**: Lightweight, with configurable caching
- **Speed**: Optimized for real-time conversation processing

## Testing

```bash
# Run the test suite
npm test

# Or directly
node lib/index.test.js
```

## License

MIT