# Associative Memory — Agent Reference Card

**Purpose:** Persistent memory for documents with semantic search.

**Default store:** `.keep/` at git repo root (auto-created)

**Key principle:** The schema is data. System documents control behavior and can be queried/updated.

## Python API
```python
from keep import Keeper, Item
kp = Keeper()  # uses default store

# Core indexing
kp.update(uri, source_tags={})          # Index document from URI → Item
kp.remember(content, id=None, ...)      # Index inline content → Item

# Search
kp.find(query, limit=10)                # Semantic search → list[Item]
kp.find_similar(uri, limit=10)          # Similar items → list[Item]
kp.query_tag(key, value=None)           # Tag lookup → list[Item]
kp.query_fulltext(query)                # Text search → list[Item]

# Item access
kp.get(id)                              # Fetch by ID → Item | None
kp.exists(id)                           # Check existence → bool
kp.list_collections()                   # All collections → list[str]

# Context & top-of-mind (for agent handoff)
kp.set_context(summary, ...)            # Set working context
kp.get_context()                        # Get working context → WorkingContext
kp.top_of_mind(hint=None, limit=5)      # Relevance + recency → list[Item]
kp.recent(limit=10, since=None)         # Just recent items → list[Item]
kp.list_topics()                        # Active topics → list[str]
kp.get_topic_summary(topic)             # Topic overview → TopicSummary

# System documents (schema as data)
kp.get_routing()                        # Get routing config → RoutingContext
kp.get_system_document(name)            # Get _system:{name} → Item | None
kp.list_system_documents()              # All system docs → list[Item]
```

## Item Fields
`id`, `summary`, `tags` (dict), `score` (searches only)

Timestamps accessed via properties: `item.created`, `item.updated` (read from tags)

## System Tags (auto-managed)
`_created`, `_updated`, `_updated_date`, `_content_type`, `_source`
`_session`, `_topic`, `_level`, `_summarizes`, `_system`, `_visibility`, `_for`

**System tags cannot be set by source_tags or generated tags** — they are managed by the system.

```python
kp.query_tag("_updated_date", "2026-01-30")  # Temporal query
kp.query_tag("_source", "inline")            # Find remembered content
kp.query_tag("_system", "true")              # All system documents
```

**Note:** Relevance/focus scores are computed at query time, not stored.
This preserves agility between broad exploration and focused work.

## System Documents
The schema is data. Behavior is controlled by documents in the store:

| Document | Purpose |
|----------|---------|
| `_system:routing` | Private/shared routing patterns |
| `_system:context` | Current working context |
| `_system:guidance` | Local behavioral guidance |
| `_system:guidance:{topic}` | Topic-specific guidance |

```python
# Query and update system documents like any item
guidance = kp.get_system_document("guidance:code_review")

# Create/update guidance through remember()
kp.remember(
    content="For code review: check security, tests, docs",
    id="_system:guidance:code_review",
    source_tags={"_system": "true"}
)
```

## Agent Session Pattern
```python
# New session starts
ctx = kp.get_context()                 # What were we doing?
items = kp.top_of_mind()               # What's relevant now?

# ... work happens ...

# End of session
kp.set_context(
    summary="Finished auth flow. Next: tests.",
    active_items=["file:///src/auth.py"],
    topics=["authentication"]
)
```

## CLI
```bash
keep <cmd> [args]
# Commands: find, similar, search, tag, update, get, exists, collections, init
```

## When to Use
- `update()` — when referencing any file/URL worth remembering
- `remember()` — capture conversation insights, decisions, notes
- `find()` — before searching filesystem; may already be indexed
- `top_of_mind()` — at session start for context
- `set_context()` — at session end for handoff

## Private vs Shared Routing
Items tagged for private visibility route to a **physically separate** store.

**Default private patterns:**
- `{"_visibility": "draft"}`
- `{"_visibility": "private"}`
- `{"_for": "self"}`

Private items cannot be seen from the shared store — physical separation, not convention.

Routing rules live in `_system:routing` document (shared store). Update it to customize.

## Domain Patterns
See [patterns/domains.md](../patterns/domains.md) for organization templates.
See [patterns/conversations.md](../patterns/conversations.md) for process knowledge.
