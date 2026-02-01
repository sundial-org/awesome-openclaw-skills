# keep

**Associative memory for reflection and skillful action.**

---

## What is this?

A practice tool for agents who want to develop judgment.

An agent who rushes to act without checking memory will repeat mistakes, miss context, and fail to grow. An agent who reflects — before, during, after — becomes skillful. This library provides the mirror: persistent semantic memory that lets you ask "what do I already know?" before acting, and "what did I learn?" after.

For the full practice guide, see **[SKILL.md](SKILL.md)**.

Technically: semantic search using embeddings, backed by ChromaDB, with tag-based organization and recency decay. Available as CLI and Python API.

```python
from keep import Keeper

kp = Keeper()

# Before acting: what do I already know?
results = kp.find("how should we handle auth?")

# After learning: capture it for future you
kp.remember("User prefers OAuth2 with PKCE for authentication")
```

**The practice:**
- Pause before acting — check what you already know
- Notice breakdowns — when assumptions surface, that's valuable
- Reflect after — capture learnings so future you can find them

**The technology:**
- Semantic search (by meaning, not keywords)
- Persistent across sessions (ChromaDB)
- Tag-based organization and filtering
- Recency decay (recent items rank higher)
- Provider abstraction (local models or APIs)
- CLI and Python API

---

## Quick Start

### Requirements

- **Python:** 3.11, 3.12, or 3.13 (3.14+ not yet supported due to dependency constraints)
- **Installation time:** 3-5 minutes (ChromaDB dependency resolution + embedding model downloads)

### Installation

```bash
# Recommended: Install with local models
pip install 'keep[local]'

# Faster alternative (recommended):
uv pip install 'keep[local]'  # ~60 seconds vs ~300 seconds

# Or install as a CLI tool:
uv tool install 'keep[local]'
# Then add ~/.local/bin to your PATH if not already:
# export PATH="$HOME/.local/bin:$PATH"

# OpenClaw integration (uses configured models):
pip install 'keep[openclaw]'

# Or minimal install (configure providers manually)
pip install keep
```

**After installation:**

```bash
keep init
# ⚠️  Remember to add .keep/ to .gitignore
```

```python
from keep import Keeper

kp = Keeper()

# Index a file
kp.update("file:///path/to/document.md", source_tags={"project": "myapp"})

# Remember inline content
kp.remember("Important: rate limit is 100 req/min", source_tags={"topic": "api"})

# Semantic search
results = kp.find("what's the rate limit?", limit=5)
for r in results:
    print(f"[{r.score:.2f}] {r.summary}")

# Tag lookup
api_docs = kp.query_tag("topic", "api")
```

See [docs/QUICKSTART.md](docs/QUICKSTART.md) for more examples.

---

## OpenClaw Integration

If you have [OpenClaw](https://openclaw.dev) configured, keep automatically uses your configured models:

```bash
# Install with OpenClaw support
pip install 'keep[openclaw]'

# Set your Anthropic API key (if using Claude models)
export ANTHROPIC_API_KEY=sk-ant-...

# Initialize (auto-detects ~/.openclaw/openclaw.json)
keep init
# ✓ Detected providers:
#   Embedding: sentence-transformers (local)
#   Summarization: anthropic (claude-sonnet-4)
```

**Benefits:**
- 🔄 Unified model configuration (DRY principle)
- 🧠 Best of both: local embeddings + smart summarization
- 🔒 Privacy-preserving (embeddings stay local)
- 💰 Cost-effective (~$0.0001/document)

See [docs/OPENCLAW-INTEGRATION.md](docs/OPENCLAW-INTEGRATION.md) for details.

---

## Documentation

- **[SKILL.md](SKILL.md)** — The practice guide (start here for how to use memory skillfully)
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** — Installation, setup, configuration
- **[docs/AGENT-GUIDE.md](docs/AGENT-GUIDE.md)** — Detailed agent patterns, Python API
- **[docs/REFERENCE.md](docs/REFERENCE.md)** — Complete API reference
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — How it works under the hood
- **[docs/OPENCLAW-INTEGRATION.md](docs/OPENCLAW-INTEGRATION.md)** — OpenClaw integration guide
- **[patterns/](patterns/)** — Domain and conversation patterns

---

## Philosophy

### Practice

Memory isn't storage — it's a mirror for reflection.

The triple check: before acting (what do I know?), during (notice breakdowns), after (capture learning). Breakdowns are valuable — they reveal assumptions. Index them, don't hide them.

An agent without memory reacts to each moment as if it were new. An agent with memory reflects, learns, and grows. See **[SKILL.md](SKILL.md)** for the full practice guide.

### Technical Design

**Schema as Data** — Configuration stored as queryable documents, not hardcoded.

**Semantic by Default** — Search by meaning via vector similarity, not keywords.

**Lazy Loading** — Dependencies loaded only when needed; missing providers give helpful errors.

**Provider Agnostic** — Pluggable backends for embeddings, summarization, and storage.

**No Original Content** — Only summaries and embeddings stored. URIs can be re-fetched if needed.

---

## Status

**Current**: v0.1.0 — Early draft

**Working:**
- ✅ Core indexing (`update`, `remember`)
- ✅ Semantic search (`find`, `find_similar`)
- ✅ Tag queries and full-text search
- ✅ Embedding cache for performance
- ✅ Recency decay (ACT-R style)
- ✅ CLI interface
- ✅ Provider abstraction with lazy loading

**Planned** (see [later/](later/)):
- ⏳ Context management (working context, top-of-mind retrieval)
- ⏳ Private/shared routing
- ⏳ Relationship graphs between items
- ⏳ LLM-based tagging

---

## Requirements

- Python 3.11+
- ChromaDB (vector store)
- One embedding provider:
  - sentence-transformers (local, default)
  - MLX (Apple Silicon, local)
  - OpenAI (API, requires key)

---

## License

MIT

---

## Contributing

This is an early draft. Issues and PRs welcome, especially for:
- Additional provider implementations
- Performance improvements
- Documentation clarity
- OpenClaw integration patterns

---

## Related Projects

- [ChromaDB](https://github.com/chroma-core/chroma) — Vector database backend
- [sentence-transformers](https://github.com/UKPLab/sentence-transformers) — Embedding models
- [MLX](https://github.com/ml-explore/mlx) — Apple Silicon ML framework
- [OpenClaw](https://openclaw.dev) — Agent framework (integration target)
