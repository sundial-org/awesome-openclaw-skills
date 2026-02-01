# OpenClaw Integration

**Status:** Available in v0.1.0+

---

## Overview

keep can automatically integrate with OpenClaw's configured models when both are present. This enables:

- **Unified model configuration** — Configure once in OpenClaw, use everywhere
- **Local-first by default** — Embeddings stay local, summarization can use configured LLM
- **Seamless fallback** — Works standalone without OpenClaw

---

## How It Works

### Detection Priority

**For embeddings**, keep checks in this order:

1. **OpenClaw `memorySearch.provider`** — if set to `openai` or `gemini` and API key available
2. **Auto mode** — if `memorySearch.provider` is `auto`, uses OpenAI if key present, else Gemini
3. **Fallback** — sentence-transformers (local, always works)

**For summarization**, keep checks in this order:

1. **OpenClaw integration** (if `~/.openclaw/openclaw.json` exists and `ANTHROPIC_API_KEY` set)
2. **MLX** (Apple Silicon local models)
3. **OpenAI** (if `OPENAI_API_KEY` set)
4. **Fallback** (truncate)

### What Gets Shared

**From OpenClaw config:**
- **Embedding provider** from `memorySearch.provider` (openai, gemini, or auto)
- **Embedding model** from `memorySearch.model`
- **Model selection for summarization** (e.g., `anthropic/claude-sonnet-4-5`)
- Provider routing (automatically detects Anthropic models)

**Stays local:**
- **Store** remains in `.keep/` (not shared with OpenClaw)
- Falls back to **sentence-transformers** if no API keys available

**API keys** are resolved from:
1. `memorySearch.remote.apiKey` in config
2. Environment variables (`OPENAI_API_KEY`, `GEMINI_API_KEY`, `GOOGLE_API_KEY`)

---

## Setup

### Option 1: Automatic (Recommended)

If you already have OpenClaw configured:

```bash
# 1. Install keep with Anthropic support
pip install 'keep[openclaw]'

# 2. Set your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Initialize (auto-detects OpenClaw config)
keep init
```

**Output:**
```
✓ Store ready: /path/to/workspace/.keep
✓ Collections: ['default']

✓ Detected providers:
  Embedding: sentence-transformers (local)
  Summarization: anthropic (claude-sonnet-4)

To customize, edit .keep/keep.toml
```

### Option 2: Manual Override

Set `OPENCLAW_CONFIG` to use a different config file:

```bash
export OPENCLAW_CONFIG=/custom/path/to/openclaw.json
keep init
```

### Option 3: Disable Integration

Don't set `ANTHROPIC_API_KEY`, or remove `~/.openclaw/openclaw.json`:

```bash
# Will fall back to MLX (Apple Silicon) or sentence-transformers
keep init
```

---

## Configuration Files

### OpenClaw Config Location

Default: `~/.openclaw/openclaw.json`

**Relevant fields:**
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-5"
      }
    }
  }
}
```

### keep Config Location

Created at: `.keep/keep.toml` (workspace root)

**Example (OpenClaw integration active):**
```toml
[store]
version = 1
created = "2026-01-30T12:00:00Z"

[embedding]
name = "sentence-transformers"

[summarization]
name = "anthropic"
model = "claude-sonnet-4-20250514"

[document]
name = "composite"
```

---

## Model Mapping

OpenClaw uses short model names. keep maps them to actual Anthropic API names:

| OpenClaw Model | Anthropic API Model |
|----------------|---------------------|
| `claude-sonnet-4` | `claude-sonnet-4-20250514` |
| `claude-sonnet-4-5` | `claude-sonnet-4-20250514` |
| `claude-sonnet-3-5` | `claude-3-5-sonnet-20241022` |
| `claude-haiku-3-5` | `claude-3-5-haiku-20241022` |

**Unknown models** default to `claude-3-5-haiku-20241022` (fast, cheap).

---

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `ANTHROPIC_API_KEY` | Anthropic API authentication | For Anthropic provider |
| `OPENCLAW_CONFIG` | Override default config location | Optional |
| `KEEP_STORE_PATH` | Override store location | Optional |

---

## Privacy & Local-First

### What Stays Local

✅ **Embeddings** — Always computed locally (sentence-transformers)  
✅ **Vector database** — ChromaDB runs locally  
✅ **Embedding cache** — Cached embeddings never leave your machine  
✅ **Configuration** — Stored in `.keep/` locally

### What Uses API (Optional)

⚠️ **Summarization** — Only if Anthropic provider configured  
⚠️ **Tagging** — Only if using `anthropic` tagging provider (off by default)

**Original documents are never stored** — Only summaries and embeddings.

---

## Use Cases

### Scenario 1: OpenClaw User (Local-First + Smart Summarization)

**Setup:**
```bash
pip install 'keep[openclaw]'
export ANTHROPIC_API_KEY=sk-ant-...
keep init
```

**Result:**
- Embeddings: Local (sentence-transformers)
- Summarization: Anthropic Claude (configured in OpenClaw)
- Cost: ~$0.0001 per document summary
- Privacy: Embeddings local, only summaries sent to API

---

### Scenario 2: Pure Local (No API Calls)

**Setup:**
```bash
pip install 'keep[local]'  # No API dependencies
keep init
```

**Result (Apple Silicon):**
- Embeddings: Local (sentence-transformers)
- Summarization: Local (MLX + Llama 3.2)
- Cost: $0 (all local)
- Privacy: Nothing leaves your machine

**Result (Other platforms):**
- Embeddings: Local (sentence-transformers)
- Summarization: Truncate (first 500 chars)
- Cost: $0
- Privacy: Nothing leaves your machine

---

### Scenario 3: OpenAI User (No OpenClaw)

**Setup:**
```bash
pip install 'keep[openai]'
export OPENAI_API_KEY=sk-...
keep init
```

**Result:**
- Embeddings: Local (sentence-transformers)
- Summarization: OpenAI (gpt-4o-mini)
- Cost: ~$0.0001 per document summary
- Privacy: Embeddings local, only summaries sent to API

---

## Customization

### Override Provider After Init

Edit `.keep/keep.toml`:

```toml
[summarization]
name = "anthropic"
model = "claude-3-5-haiku-20241022"  # Use Haiku instead of Sonnet
max_tokens = 300  # Longer summaries
```

### Use Different Models for Different Collections

Not yet supported. Roadmap feature for v0.2.

---

## Troubleshooting

### "OpenClaw config found but Anthropic provider not used"

**Cause:** `ANTHROPIC_API_KEY` not set

**Fix:**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
rm -rf .keep  # Delete old config
keep init  # Re-initialize
```

---

### "AnthropicSummarization requires 'anthropic' library"

**Cause:** Package not installed

**Fix:**
```bash
pip install 'keep[openclaw]'
```

---

### "Want to use OpenClaw integration but don't have API key"

**Solution:** Use local-first mode. OpenClaw config is ignored if no API key present.

```bash
pip install 'keep[local]'  # MLX on Apple Silicon
keep init
```

---

## Architecture Notes

### Why Embeddings Stay Local

Embeddings are computed frequently (every document indexed, every query). Using an API would:
- 💸 Cost too much (~$0.0001 per call × thousands of calls)
- 🐌 Be too slow (network latency on every query)
- 🔒 Leak query content (privacy issue)

Local embeddings (sentence-transformers) are:
- ✅ Free
- ✅ Fast (~100ms on M1)
- ✅ Private

### Why Summarization Can Use API

Summaries are computed once per document. Using an API:
- 💸 Reasonable cost (~$0.0001 per document)
- ⚡ Acceptable speed (happens during `update`, not `find`)
- 📝 Better quality than truncation
- 🔄 Original content not stored anyway

---

## Future Enhancements

**Planned for v0.2:**
- [ ] OAuth integration (use OpenClaw's OAuth tokens directly)
- [ ] Per-collection provider config
- [ ] Automatic model upgrades when OpenClaw config changes
- [ ] Batch summarization for cost optimization

---

## Example: Full Workflow

```bash
# 1. Install with OpenClaw integration
pip install 'keep[openclaw]'

# 2. Set API key (from Anthropic console)
export ANTHROPIC_API_KEY=sk-ant-api03-...

# 3. Initialize (detects OpenClaw config automatically)
keep init
# ✓ Store ready: /Users/hugh/clawd/.keep
# ✓ Detected providers:
#   Embedding: sentence-transformers (local)
#   Summarization: anthropic (claude-sonnet-4)

# 4. Index a document
keep update "file://./README.md" -t type=docs

# 5. Search semantically
keep find "installation instructions" --limit 3

# 6. Verify costs are reasonable
# Claude Haiku: ~$0.0001 per summary
# 1000 documents = ~$0.10 total
```

---

## Summary

**With OpenClaw integration:**
- 🧠 Best of both worlds: local embeddings + smart summarization
- 🔄 Unified configuration (DRY principle)
- 💰 Cost-effective ($0.0001/document vs $0.001 for OpenAI embeddings)
- 🔒 Privacy-preserving (embeddings + queries stay local)

**Without OpenClaw:**
- 🏠 Pure local-first (MLX on Apple Silicon)
- 💸 Zero cost
- 🔒 Maximum privacy

**Recommendation:** Use OpenClaw integration if you already have it configured. Otherwise, local-first mode is excellent for privacy and zero cost.
