# Language Models Commands

Commands for interacting with language models (LLMs) in Foundry, including Anthropic Claude models and OpenAI embeddings.

## Model RID Format
`ri.language-models.main.model.{uuid}`

## Anthropic Claude Commands

### Simple Message (Single-Turn)

Send a single message to an Anthropic Claude model for simple Q&A.

```bash
pltr language-models anthropic messages MODEL_RID --message "MESSAGE" [OPTIONS]

# Options:
#   --message, -m TEXT      User message text (required)
#   --max-tokens INTEGER    Maximum tokens to generate [default: 1024]
#   --system, -s TEXT       System prompt to guide model behavior
#   --temperature, -t FLOAT Sampling temperature (0.0-1.0)
#   --stop TEXT             Stop sequences (can be specified multiple times)
#   --top-k INTEGER         Sample from top K tokens
#   --top-p FLOAT           Nucleus sampling threshold (0.0-1.0)
#   --preview               Enable preview mode
#   --format, -f TEXT       Output format (table, json, csv)
#   --output, -o TEXT       Output file path
#   --profile, -p TEXT      Profile name

# Examples
pltr language-models anthropic messages ri.language-models.main.model.abc123 \
    --message "Explain quantum computing"

pltr language-models anthropic messages ri.language-models.main.model.abc123 \
    --message "Write a haiku" \
    --system "You are a poetic assistant" \
    --temperature 0.8 \
    --max-tokens 100

pltr language-models anthropic messages ri.language-models.main.model.abc123 \
    --message "List three items" \
    --stop "." --stop "\n\n"

pltr language-models anthropic messages ri.language-models.main.model.abc123 \
    --message "Summarize AI trends" \
    --output response.json
```

### Advanced Messages (Multi-Turn)

Send complex requests with multi-turn conversations, tool calling, or extended thinking.

```bash
pltr language-models anthropic messages-advanced MODEL_RID --request REQUEST_JSON [OPTIONS]

# Options:
#   --request, -r TEXT      Request JSON (inline or @file.json) - required
#   --preview               Enable preview mode
#   --format, -f TEXT       Output format (table, json, csv)
#   --output, -o TEXT       Output file path
#   --profile, -p TEXT      Profile name

# Request JSON structure:
# {
#   "messages": [...],      # Required: List of message objects
#   "maxTokens": 1024,      # Required: Maximum tokens to generate
#   "system": [...],        # Optional: System prompt blocks
#   "temperature": 0.7,     # Optional: Sampling temperature
#   "thinking": {...},      # Optional: Extended thinking config
#   "tools": [...],         # Optional: Tool definitions
#   "toolChoice": {...},    # Optional: Tool selection strategy
#   "stopSequences": [...], # Optional: Stop sequences
#   "topK": 40,             # Optional: Top K sampling
#   "topP": 0.95            # Optional: Nucleus sampling
# }
```

#### Multi-Turn Conversation Example

```bash
# Create conversation.json:
# {
#   "messages": [
#     {"role": "user", "content": [{"type": "text", "text": "Hi, I need help with Python"}]},
#     {"role": "assistant", "content": [{"type": "text", "text": "I'd be happy to help! What do you need?"}]},
#     {"role": "user", "content": [{"type": "text", "text": "How do I read a CSV file?"}]}
#   ],
#   "maxTokens": 500
# }

pltr language-models anthropic messages-advanced ri.language-models.main.model.abc123 \
    --request @conversation.json
```

#### Extended Thinking Example

```bash
pltr language-models anthropic messages-advanced ri.language-models.main.model.abc123 \
    --request '{"messages": [{"role": "user", "content": [{"type": "text", "text": "Solve this complex problem"}]}], "maxTokens": 2000, "thinking": {"type": "enabled", "budget": 10000}}'
```

#### Inline with System Prompt

```bash
pltr language-models anthropic messages-advanced ri.language-models.main.model.abc123 \
    --request '{"messages": [{"role": "user", "content": [{"type": "text", "text": "Hi"}]}], "maxTokens": 100, "system": [{"type": "text", "text": "Be concise"}]}'
```

## OpenAI Commands

### Generate Embeddings

Generate embedding vectors for text using OpenAI models.

```bash
pltr language-models openai embeddings MODEL_RID --input INPUT [OPTIONS]

# Options:
#   --input, -i TEXT        Input text(s) - single string, JSON array, or @file.json (required)
#   --dimensions, -d INT    Custom embedding dimensions (not all models support this)
#   --encoding, -e TEXT     Output encoding format: 'float' or 'base64'
#   --preview               Enable preview mode
#   --format, -f TEXT       Output format (table, json, csv)
#   --output, -o TEXT       Output file path
#   --profile, -p TEXT      Profile name

# Examples

# Single text
pltr language-models openai embeddings ri.language-models.main.model.xyz789 \
    --input "Machine learning is fascinating"

# Multiple texts (inline JSON array)
pltr language-models openai embeddings ri.language-models.main.model.xyz789 \
    --input '["Document 1", "Document 2", "Document 3"]'

# Multiple texts from file (texts.json: ["Text 1", "Text 2", "Text 3"])
pltr language-models openai embeddings ri.language-models.main.model.xyz789 \
    --input @texts.json

# Custom dimensions and encoding
pltr language-models openai embeddings ri.language-models.main.model.xyz789 \
    --input "Sample text" \
    --dimensions 1024 \
    --encoding base64

# Save embeddings to file
pltr language-models openai embeddings ri.language-models.main.model.xyz789 \
    --input '["Text 1", "Text 2"]' \
    --output embeddings.json
```

## Response Format

### Anthropic Response

Responses include token usage information:

```json
{
  "content": [
    {"type": "text", "text": "The response text..."}
  ],
  "usage": {
    "inputTokens": 25,
    "outputTokens": 150,
    "totalTokens": 175
  },
  "stopReason": "end_turn",
  "model": "claude-3-sonnet"
}
```

Token usage is displayed prominently:
```
Token usage - Input: 25, Output: 150, Total: 175
```

### OpenAI Embeddings Response

```json
{
  "data": [
    {
      "embedding": [0.0123, -0.0456, ...],
      "index": 0
    }
  ],
  "usage": {
    "promptTokens": 8,
    "totalTokens": 8
  },
  "model": "text-embedding-3-small"
}
```

## JSON Input Methods

Both inline JSON and file references are supported:

```bash
# Inline JSON
--request '{"messages": [...], "maxTokens": 100}'

# File reference (prefix with @)
--request @request.json
--input @texts.json
```

## Common Patterns

### Interactive Chat Session

```bash
# Save each response and build conversation history
pltr language-models anthropic messages ri.language-models.main.model.abc123 \
    --message "Hello!" \
    --output turn1.json

# Then use messages-advanced for follow-up with full history
```

### Batch Embeddings for Semantic Search

```bash
# Generate embeddings for document corpus
pltr language-models openai embeddings ri.language-models.main.model.xyz789 \
    --input @documents.json \
    --output corpus-embeddings.json

# Later: generate embedding for query and compare
pltr language-models openai embeddings ri.language-models.main.model.xyz789 \
    --input "search query" \
    --output query-embedding.json
```
