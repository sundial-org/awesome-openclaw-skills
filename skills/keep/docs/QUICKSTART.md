# Quick Start

## Installation

```bash
# Recommended: Install with local models (sentence-transformers)
# Includes sentence-transformers + MLX on Apple Silicon
pip install 'keep[local]'

# Minimal: Core only (you'll need to configure providers manually)
pip install keep

# API-based: Use OpenAI for embeddings (requires OPENAI_API_KEY)
pip install 'keep[openai]'

# Development: Include test tools
pip install 'keep[dev]'
```

**What gets installed:**

| Extra | Dependencies | Use case |
|-------|--------------|----------|
| `[local]` | sentence-transformers, MLX (Apple Silicon only) | Best default - works offline |
| `[openai]` | openai SDK | API-based, requires key, high quality |
| `[dev]` | pytest, pytest-cov | For running tests |
| (none) | chromadb, typer, tomli-w | Minimal - configure providers yourself |

## Basic Usage

```python
from keep import Keeper

# Initialize (creates .keep/ at git repo root by default)
kp = Keeper()

# Index a document from URI
item = kp.update("file:///path/to/document.md")

# Remember inline content
item = kp.remember("Important insight about authentication patterns")

# Semantic search
results = kp.find("how does authentication work?", limit=5)
for r in results:
    print(f"[{r.score:.2f}] {r.id}: {r.summary}")

# Get specific item
item = kp.get("file:///path/to/document.md")

# Tag-based lookup
docs = kp.query_tag("project", "myapp")

# Check if item exists
if kp.exists("file:///path/to/document.md"):
    print("Already indexed")
```

## CLI Usage

```bash
# Initialize store
keep init

# Index a document
keep update file:///path/to/doc.md -t project=myapp

# Remember inline content
keep remember "Meeting notes from today" -t type=meeting

# Search
keep find "authentication" --limit 5

# Get by ID
keep get file:///path/to/doc.md

# Tag lookup
keep tag project myapp

# List collections
keep collections

# Output as JSON
keep find "auth" --json
```

## Lazy Summarization

When using local models (MLX) for summarization, indexing can be slow. Use `--lazy` for fast indexing:

```bash
# Fast indexing: uses truncated placeholder, summarizes in background
keep update file:///path/to/doc.md --lazy

# Background processor starts automatically
# Check pending count:
keep process-pending --json
# {"processed": 0, "remaining": 1}

# Or process manually:
keep process-pending --all
```

**How it works:**
- `--lazy` stores immediately with a truncated placeholder summary
- A background processor spawns automatically (singleton, exits when done)
- Full summaries are generated asynchronously
- Search works immediately (embeddings are computed synchronously)

**When to use `--lazy`:**
- Local MLX summarization (slow but private)
- Batch indexing many documents
- When you don't need the summary immediately

**When NOT to use `--lazy`:**
- API-based summarization (OpenAI, Anthropic) — already fast
- When you need the summary for immediate display

## Configuration

First run auto-detects best providers and creates `.keep/keep.toml`:

```toml
[store]
version = 1
created = "2026-01-30T12:00:00Z"

[embedding]
name = "sentence-transformers"
model = "all-MiniLM-L6-v2"

[summarization]
name = "truncate"
max_length = 500

[document]
name = "composite"
```

Edit to customize providers or models.

## Working with Collections

Collections partition the store into separate namespaces:

```python
# Specify collection
kp = Keeper(collection="work")

# Or pass at operation time
kp.remember("Note", collection="personal")
results = kp.find("query", collection="work")
```

## Recency Decay

Items decay in relevance over time (ACT-R model):

```python
# Configure half-life (default: 30 days)
kp = Keeper(decay_half_life_days=7.0)

# Disable decay
kp = Keeper(decay_half_life_days=0)
```

After one half-life, an item's effective score is multiplied by 0.5.

## Error Handling

```python
try:
    item = kp.update("https://unreachable.com/doc")
except IOError as e:
    print(f"Failed to fetch: {e}")

try:
    kp = Keeper(collection="Invalid-Name!")
except ValueError as e:
    print(f"Invalid collection name: {e}")
```

## Environment Variables

```bash
# Store location
export KEEP_STORE_PATH=/path/to/store

# OpenAI API key (if using openai provider)
export OPENAI_API_KEY=sk-...
# or
export KEEP_OPENAI_API_KEY=sk-...
```

## Common Patterns

### Indexing Files from a Directory

```python
from pathlib import Path

for file in Path("docs").rglob("*.md"):
    uri = file.as_uri()
    if not kp.exists(uri):
        kp.update(uri, source_tags={"type": "documentation"})
```

### Tagging Strategy

```python
# Source tags (provided at index time)
kp.update(uri, source_tags={
    "project": "myapp",
    "module": "auth",
    "language": "python"
})

# System tags (auto-managed, prefixed with _)
item.tags["_created"]      # ISO timestamp
item.tags["_updated"]      # ISO timestamp
item.tags["_content_type"] # MIME type
item.tags["_source"]       # "uri" or "inline"
```

### Search Refinement

```python
# Broad semantic search
results = kp.find("database connection")

# Narrow by tags
results = kp.query_tag("module", "database")

# Full-text search in summaries
results = kp.query_fulltext("PostgreSQL")
```

## Provider Options

### Embedding Providers

**sentence-transformers** (default)
- Local, no API key
- CPU or GPU
- Model: all-MiniLM-L6-v2 (384 dims)

**MLX** (Apple Silicon)
- Local, Metal-accelerated
- Requires: `pip install mlx sentence-transformers`
- Configure in toml: `name = "mlx"`

**OpenAI**
- API-based, requires key
- High quality, fast
- Model: text-embedding-3-small (1536 dims)

### Summarization Providers

**truncate** (default fallback)
- Fast, zero dependencies
- Simple text truncation

**MLX** (Apple Silicon default)
- LLM-based, local, private
- Requires: `pip install mlx-lm`
- Model: Llama-3.2-3B-Instruct-4bit
- **Recommended: use `--lazy` flag** (slow but runs in background)

**OpenAI**
- LLM-based, API
- Requires key
- Model: gpt-4o-mini
- Fast, no need for `--lazy`

**Anthropic** (via OpenClaw integration)
- LLM-based, API
- Requires ANTHROPIC_API_KEY
- Model: claude-3-5-haiku or configured model
- Fast, no need for `--lazy`

## Troubleshooting

**Import fails with missing dependency**
- Providers are lazy-loaded now
- Only fails when you try to create Keeper
- Error message shows available providers and what's missing

**Model download hangs**
- First use downloads models (sentence-transformers, MLX)
- Can take minutes depending on connection
- Models cached in `~/.cache/huggingface/` or `~/.cache/mlx/`

**ChromaDB errors**
- Delete `.keep/chroma/` to reset
- Embedding cache can be deleted: `.keep/embedding_cache.db`

**Slow queries**
- Check embedding dimension (lower is faster)
- Reduce collection size or increase decay rate
- Consider batch operations

## Bootstrap Your Memory

After `keep init`, seed your memory with foundational material. These documents teach how to use memory well.

Use `--lazy` for fast indexing (recommended with local MLX models):

```bash
# The practice frameworks
keep update "file://$PWD/patterns/conversations.md" -t type=pattern -t topic=process --lazy
keep update "file://$PWD/patterns/domains.md" -t type=pattern -t topic=organization --lazy

# Seed wisdom (from tests/data/)
keep update "file://$PWD/tests/data/mn61.html" -t type=teaching -t topic=reflection --lazy
keep update "file://$PWD/tests/data/true_person_no_rank.md" -t type=teaching -t topic=commentary --lazy
keep update "file://$PWD/tests/data/impermanence_verse.txt" -t type=teaching -t topic=impermanence --lazy

# Summaries generate in background - check progress:
keep process-pending --json
```

**What these teach:**
- **conversations.md** — How to recognize where you are in work (action, possibility, clarification)
- **domains.md** — How to organize knowledge by domain
- **mn61.html** — The triple-check practice: reflect before, during, and after action
- **true_person_no_rank.md** — How perspectives layer organically, not cumulatively
- **impermanence_verse.txt** — Brief reminders. "Wake up!"

Now try:
```bash
keep find "how to reflect on actions"
keep find "what kind of conversation is this"
```

See [SKILL.md](../SKILL.md) for the full practice framework.

## Next Steps

- See [SKILL.md](../SKILL.md) for agent-focused patterns and the reflective practice
- See [AGENT-GUIDE.md](AGENT-GUIDE.md) for detailed working session patterns
- See [ARCHITECTURE.md](ARCHITECTURE.md) for internals
- See [REFERENCE.md](REFERENCE.md) for complete API
