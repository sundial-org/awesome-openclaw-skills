# Architecture Overview

## What is keep?

**keep** is a semantic memory system providing persistent associative storage with vector similarity search. It's designed as an agent skill for OpenClaw and other agentic environments, enabling agents to remember information across sessions over time.

Think of it as: **ChromaDB + embeddings + summarization + tagging** wrapped in a simple API.

Published by Hugh Pyle, "inguz ᛜ outcomes", under the MIT license.
Contributions are welcome; code is conversation, "right speech" is encouraged.

---

## Core Concept

Every stored item has:
- **ID**: URI or custom identifier
- **Summary**: Human-readable text (stored, searchable)
- **Embedding**: Vector representation (for semantic search)
- **Tags**: Key-value metadata (for filtering)
- **Timestamps**: Created/updated (auto-managed)

The original document content is **not stored** — only the summary and embedding.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  API Layer (api.py)                                          │
│  - Keeper class                                   │
│  - High-level operations: update(), remember(), find()       │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────────┐
        │          │          │              │
        ▼          ▼          ▼              ▼
   ┌────────┐ ┌─────────┐ ┌──────────┐ ┌─────────┐
   │Document│ │Embedding│ │Summary   │ │Vector   │
   │Provider│ │Provider │ │Provider  │ │Store    │
   └────────┘ └─────────┘ └──────────┘ └─────────┘
       │          │            │             │
       │          │            │             │
   fetch()    embed()     summarize()   upsert()/
   from URI   text→vec   text→summary   query()
```

### Components

**[api.py](keep/api.py)** — Main facade
- `Keeper` class
- Coordinates providers and store
- Implements query operations with recency decay

**[store.py](keep/store.py)** — Persistence layer
- `ChromaStore` wraps ChromaDB
- Handles vector storage, similarity search, metadata queries
- Automatic timestamp management

**[providers/](keep/providers/)** — Pluggable services
- **Document**: Fetch content from URIs (file://, https://)
- **Embedding**: Generate vectors (sentence-transformers, OpenAI, MLX)
- **Summarization**: Generate summaries (truncate, LLM-based)
- **Registry**: Factory for lazy-loading providers

**[config.py](keep/config.py)** — Configuration
- Detects available providers (platform, API keys)
- Persists choices in `keep.toml`
- Auto-creates on first use

**[types.py](keep/types.py)** — Data model
- `Item`: Immutable result type
- System tag protection (prefix: `_`)

---

## Data Flow

### Indexing: update(uri) or remember(content)

```
URI or content
    │
    ▼
┌─────────────────┐
│ Fetch/Use input │ ← DocumentProvider (for URIs only)
└────────┬────────┘
         │ content (text)
         │
    ┌────┴────┬─────────────┐
    │         │             │
    ▼         ▼             ▼
  embed()  summarize()   tags (from args)
    │         │             │
    └────┬────┴─────────────┘
         │
         ▼
    ┌─────────────────┐
    │ ChromaStore     │
    │ upsert()        │
    │ - embedding     │
    │ - summary       │
    │ - tags          │
    │ - timestamps    │
    └─────────────────┘
```

### Retrieval: find(query)

```
query text
    │
    ▼
  embed()  ← EmbeddingProvider
    │
    │ query vector
    ▼
┌───────────────────┐
│ ChromaStore       │
│ query_embedding() │ ← L2 distance search
└─────────┬─────────┘
          │
          ▼ results with distance scores
    ┌──────────────┐
    │ Apply decay  │ ← Recency weighting (ACT-R style)
    │ score × 0.5^(days/half_life)
    └──────┬───────┘
           │
           ▼
    list[Item] (sorted by effective score)
```

---

## Key Design Decisions

**1. Schema as Data**
- System configuration stored as documents in the store
- Enables agents to query and update behavior
- (Not yet implemented: routing, guidance documents)

**2. Lazy Provider Loading**
- Providers registered at first use, not import time
- Avoids crashes when optional dependencies missing
- Better error messages about what's needed

**3. Separation of Concerns**
- Store is provider-agnostic (only knows about vectors/metadata)
- Providers are store-agnostic (only know about text→vectors)
- Easy to swap implementations

**4. No Original Content Storage**
- Reduces storage size
- Forces meaningful summarization
- URIs can be re-fetched if needed

**5. Immutable Items**
- `Item` is frozen dataclass
- Updates via `update()` return new Item
- Prevents accidental mutation bugs

**6. System Tag Protection**
- Tags prefixed with `_` are system-managed
- Source tags filtered before storage
- Prevents user override of timestamps, etc.

---

## Storage Layout

```
store_path/
├── keep.toml           # Provider configuration
├── chroma/                 # ChromaDB persistence
│   └── [collection]/       # One collection = one namespace
│       ├── embeddings
│       ├── metadata
│       └── documents
└── embedding_cache.db      # SQLite cache for embeddings
```

---

## Provider Types

### Embedding Providers
Generate vector representations for semantic search.

- **sentence-transformers**: Local, CPU/GPU, no API key (default)
- **MLX**: Apple Silicon optimized, local, no API key
- **OpenAI**: API-based, requires key, high quality

Dimension determined by model. Must be consistent across indexing and queries.

### Summarization Providers
Generate human-readable summaries from content.

- **truncate**: Simple text truncation (default)
- **first_paragraph**: Extract first meaningful chunk
- **passthrough**: Store content as-is (with length limit)
- **MLX**: LLM-based, local, no API key
- **OpenAI**: LLM-based, API, high quality

### Document Providers
Fetch content from URIs.

- **composite**: Handles file://, https:// (default)
- Extensible for s3://, gs://, etc.

---

## Extension Points

**New Provider**
1. Implement Protocol from [providers/base.py](keep/providers/base.py)
2. Register with `get_registry().register_X("name", YourClass)`
3. Reference by name in config

**New Store Backend**
- Current: ChromaDB
- Future: Could extract Protocol from `ChromaStore`
- Candidates: PostgreSQL+pgvector, SQLite+faiss

**New Query Types**
- Add methods to `Keeper`
- Delegate to `ChromaStore` or implement in API layer

---

## Performance Characteristics

**Indexing**
- Embedding: ~50-200ms per item (local models)
- Summarization: ~100ms-2s per item (depends on provider)
- Storage: ~10ms per item

**Querying**
- Semantic search: ~10-50ms for 10k items
- Tag queries: ~1-10ms
- Full-text search: ~10-100ms

**Caching**
- Embedding cache avoids re-computing for repeated queries
- Persists across sessions in SQLite

**Scaling**
- ChromaDB handles ~100k items comfortably
- Larger datasets may benefit from PostgreSQL backend
- Embedding dimension affects memory (384d vs 1536d)

---

## Failure Modes

**Missing Dependencies**
- Registry provides clear error about which provider failed
- Lists available alternatives
- Lazy loading prevents import-time crashes

**URI Fetch Failures**
- `update()` raises `IOError` for unreachable URIs
- Original error preserved in exception chain

**Invalid Config**
- Config auto-created with detected defaults
- Validation on load with clear error messages

**Store Corruption**
- ChromaDB is resilient (SQLite-backed)
- Embedding cache can be deleted and rebuilt
- No critical data loss if store is backed up

---

## Testing Strategy

**Unit Tests**: [tests/test_core.py](tests/test_core.py)
- Data types (Item, filtering)
- Context dataclasses
- No external dependencies

**Integration Tests**: [tests/test_integration.py](tests/test_integration.py)
- End-to-end: remember → find
- Multiple collections
- Recency decay
- Embedding cache

**Provider Tests**: (TODO)
- Each provider independently
- Graceful degradation when unavailable

---

## Future Work

### Planned (in [later/](later/))
- **Relationships**: Link items with typed edges
- **Advanced Tagging**: LLM-based tag generation
- **Hierarchical Context**: Topic summaries, working context

### Under Consideration
- Multi-store facade (private/shared routing)
- Batch operations for performance
- Incremental indexing (track changes)
- Export/import for backup
- Web UI for exploration
