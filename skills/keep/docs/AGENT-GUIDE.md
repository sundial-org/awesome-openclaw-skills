# Associative Memory — Detailed Agent Guide

This guide provides in-depth patterns for using the associative memory store effectively.

For the practice introduction (why and when), see [../SKILL.md](../SKILL.md).
For quick API/CLI reference, see [REFERENCE.md](REFERENCE.md).

---

## Overview

The associative memory provides persistent storage with semantic search.

**Key principle:** The schema is data. Routing rules, domain patterns, process knowledge — all are documents in the store, queryable and updateable. An agent can be asked "research X and update how you handle X" and the changes persist.

## Quick Start (Agent Reference)

```python
from keep import Keeper, Item

# Initialize (defaults to .keep/ at git repo root)
kp = Keeper()

# Index a document from URI (fetches, embeds, summarizes, tags automatically)
item = kp.update("file:///project/readme.md", source_tags={"project": "myapp"})

# Remember inline content (conversations, notes, insights)
kp.remember(
    content="User prefers OAuth2 with PKCE for auth. Discussed tradeoffs.",
    id="conversation:2026-01-30:auth",
    source_tags={"topic": "authentication"}
)

# Semantic search
results: list[Item] = kp.find("authentication flow", limit=5)
for item in results:
    print(f"{item.score:.2f} {item.id}")
    print(f"  {item.summary}")

# Find similar to existing item
similar = kp.find_similar("file:///project/readme.md", limit=3)

# Tag-based lookup (including system tags for temporal queries)
docs = kp.query_tag("project", "myapp")
today = kp.query_tag("_updated_date", "2026-01-30")

# Check if indexed
if kp.exists("file:///project/readme.md"):
    item = kp.get("file:///project/readme.md")
```

**CLI equivalent:**
```bash
# Uses .keep/ at repo root by default
keep update "file:///project/readme.md" -t project=myapp
keep find "authentication flow" --limit 5 --json
keep tag project myapp
```

**Item fields:** `id` (URI or custom), `summary` (str), `tags` (dict), `score` (float, search results only). Timestamps are in tags: `item.created` and `item.updated` are property accessors.

**Prerequisites:** Python 3.11+, `pip install keep[local]` (preferably in a venv)

**Default store location:** `.keep/` at the git repository root (created automatically). Override with `KEEP_STORE_PATH` or explicit path argument. Add `.keep/` to `.gitignore` if the store should not be committed.

**Patterns documentation:**
- [patterns/domains.md](../patterns/domains.md) — domain-specific organization (software dev, research, etc.)
- [patterns/conversations.md](../patterns/conversations.md) — process knowledge: how work proceeds

**When to use:**
- Call `update()` whenever you reference a file or URL worth remembering
- Call `remember()` to capture conversation insights, decisions, or notes
- Call `find()` before filesystem search — the answer may already be indexed
- Call `top_of_mind()` at session start to get current context
- Call `set_context()` when focus changes to help future agents

---

## Working Session Pattern

Use `set_context()` as a scratchpad to track where you are in the work. This isn't enforced structure — it's a convention that helps you (and future agents) maintain perspective.

**Recommended metadata fields:**

| Field | Purpose | Example |
|-------|---------|---------|
| `conversation_type` | What kind of work is this? | `"bug_diagnosis"`, `"feature_request"`, `"research"` |
| `state` | Where are we in the flow? | `"gathering_info"`, `"investigating"`, `"implementing"`, `"awaiting_confirmation"` |
| `commitments` | What have I promised? | `[{"what": "fix the flaky test", "to": "user"}]` |
| `completion_criteria` | What does "done" look like? | `"test passes reliably in CI"` |
| `hypothesis` | Current working theory | `"timing assertion too tight for CI latency"` |
| `blocked_on` | What's preventing progress? | `"need CI logs from user"` |

**Session lifecycle:**

```python
# 1. Starting work — record what we're doing
kp.set_context(
    summary="Diagnosing flaky test in auth module.",
    topics=["auth", "testing"],
    metadata={
        "conversation_type": "bug_diagnosis",
        "state": "gathering_info",
        "commitments": []
    }
)

# 2. Mid-work — update as understanding evolves
kp.set_context(
    summary="Investigating test_token_refresh. Likely timing issue.",
    active_items=["file:///tests/test_oauth_flow.py"],
    topics=["auth", "testing", "timing"],
    metadata={
        "conversation_type": "bug_diagnosis",
        "state": "investigating",
        "hypothesis": "hardcoded 100ms timeout too tight for CI",
        "commitments": []
    }
)

# 3. Committing — I've promised to do something
kp.set_context(
    summary="Implementing mock timer fix for test_token_refresh.",
    active_items=["file:///tests/test_oauth_flow.py"],
    metadata={
        "conversation_type": "bug_fix",
        "state": "implementing",
        "commitments": [{"what": "mock timer fix", "to": "user"}],
        "completion_criteria": "test passes reliably, no timing dependency"
    }
)

# 4. Completing — record the learning
kp.remember(
    content="Flaky timing in CI → mock time instead of real assertions.",
    source_tags={"type": "learning", "domain": "testing"}
)
kp.set_context(
    summary="Completed flaky test fix.",
    metadata={"state": "completed", "commitments": []}
)
```

**Key insight:** The store remembers across sessions; working memory doesn't. When you resume, read context first:

```python
ctx = kp.get_context()
# ctx.metadata["state"] tells you where you left off
# ctx.metadata["commitments"] tells you what's still owed
# ctx.active_items tells you what to look at
```

---

## Hierarchical Context Model

The store supports O(log(log(N))) context retrieval through a hierarchy:

```
Level 3:  [  Working Context  ]           ← "What are we doing?" (~100 tokens)
Level 2:  [ Topic Summaries   ]           ← "What about X?" (~5-10 topics)
Level 1:  [ Cluster Summaries ]           ← √N aggregated summaries
Level 0:  [ Source Items      ]           ← N indexed documents
```

**Agent handoff pattern:**
```python
# New agent/session starts
ctx = kp.get_context()           # Instant: what are we working on?
recent = kp.top_of_mind(limit=5) # Associative: what's relevant now?

# ... work happens ...

# Before ending session, update context for next agent
kp.set_context(
    summary="Completed OAuth2 flow. Token refresh working. Next: add tests.",
    active_items=["file:///src/auth.py", "file:///src/oauth_client.py"],
    topics=["authentication", "testing"]
)
```

**Top-of-mind retrieval:**
```python
# Combines: recency + context similarity + topic relevance + session
items = kp.top_of_mind()                    # What's relevant right now?
items = kp.top_of_mind("authentication")    # What's relevant about auth?
items = kp.recent(limit=10)                 # Just the latest items
items = kp.recent(since="2026-01-30")       # Items from today
```

**Topic summaries (Level 2):**
```python
topics = kp.list_topics()                   # ["authentication", "database", ...]
summary = kp.get_topic_summary("authentication")
# → TopicSummary with aggregate overview, item count, key items
```

---

## Data Model

An item has
* A unique identifier (URI or custom ID for inline content)
* A `created` timestamp (when first indexed)
* A `updated` timestamp (when last indexed)
* A summary of the content, generated when indexed
* A collection of tags (`{key: value, ...}`)

The full original document is not stored in this service.

The services that implement embedding, summarization and tagging are configured at initialization time. This skill itself is provider-agnostic.

## Use Cases

* Keep track of every document or file that is referenced during any task.
* Remember conversation insights, decisions, and notes inline.
* Retrieve by semantic similarity, full-text search, or tags.
* Transfer context between agents or sessions seamlessly.

The data is partitioned by *collection*. Collection names are lowercase ASCII with underscores.

## Functionality

within a collection:

`update(id: URI, source_tags: dict)` - inserts or updates the document at `URI` into the store.  This process delegates the work of embedding, summarization and tagging, then updates the store.  Any `source_tags` are stored alongside the "derived tags" produced by the tagging service.

> NOTE: update tasks are serialized to avoid any concurrency issues.

> NOTE: there is no `delete` operation.

`find(query: str)` - locate items using a semantic-similarity query for any text

`find_similar(id: URI)` - locate nearest neighbors of an existing item using a semantic-similarity query

`query_fulltext(query: str)` - locate using a fulltext search of the *summary* text

`query_tag(key: str, value: str = None)` - locate items that have a given tag, and optionally that have the given value for that tag

### Tagging

There are three domains of tags:

1. **Source tags.**  Key/value pairs provided when calling `update()` or `remember()`.  For example, an object from an AWS bucket has a URI, and also a collection of tags that were applied in AWS.

2. **System tags.**  These have special meaning for this service and are managed automatically.
   * System tags have keys that begin with underscore (`_`).
   * **Source tags and generated tags cannot set system tag values** — any tag starting with `_` in source_tags is filtered out before storage.
   * The tagging provider does not produce system tags.

   | System Tag | Description | Example |
   |------------|-------------|---------|
   |------------|-------------|---------|
   | `_created` | ISO timestamp when first indexed | `2026-01-30T14:22:00Z` |
   | `_updated` | ISO timestamp when last indexed | `2026-01-30T15:30:00Z` |
   | `_updated_date` | Date portion for easier queries | `2026-01-30` |
   | `_content_type` | MIME type if known | `text/markdown` |
   | `_source` | How content was obtained | `uri`, `inline` |
   | `_session` | Session that last touched this item | `2026-01-30:abc123` |

3. **Generated tags.**  Produced by the tagging provider based on content analysis at index time.

**Temporal queries using system tags:**
```python
# Find items updated today
kp.query_tag("_updated_date", "2026-01-30")

# Find all inline content (from remember())
kp.query_tag("_source", "inline")
```

---

## Visibility Conventions

Knowledge has an interior/exterior dimension. Some items are working notes; others are settled knowledge ready to share. This is signaled through **convention**, not enforcement.

**Suggested source tags for visibility:**

| Tag | Values | Meaning |
|-----|--------|---------|
| `_visibility` | `draft`, `private`, `shared`, `public` | Intent for who should see this |
| `_for` | `self`, `team`, `anyone` | Intended audience |
| `_reviewed` | `true`, `false` | Has this been checked before sharing? |

**Example usage:**
```python
# Working hypothesis — routes to private store
kp.remember(
    "I think the bug is in token refresh, but need to verify.",
    source_tags={"_visibility": "draft", "_for": "self"}
)

# Confirmed learning — routes to shared store
kp.remember(
    "Token refresh fails when clock skew exceeds 30s. Fix: use server time.",
    source_tags={"_visibility": "shared", "_for": "team", "_reviewed": "true"}
)
```

**Why this matters:**

The shared layer protects the private. When items route to the private store:
- They are physically separate — cannot be seen or deduced from outside
- Working notes, drafts, dead ends stay truly interior
- Settled knowledge graduates to shared through explicit re-tagging

### Physical Separation via Routing

Private isn't just convention — it's enforced by routing to a separate store.

```
Keeper (facade)
    │
    ├── reads: _system:routing (document in shared store)
    │         ├── summary: "Items tagged draft/private route separately"
    │         └── private_patterns: [{"_visibility": "draft"}, {"_for": "self"}, ...]
    │
    ├── Private Store (physically separate)
    │   └── items matching private_patterns
    │   └── invisible from shared store queries
    │
    └── Shared Store
        └── everything else
        └── includes the _system:routing document itself
```

The routing context is itself a document with:
- **summary**: Natural language description of the privacy model
- **private_patterns**: Tag patterns that route to private (e.g., `{"_visibility": "draft"}`)
- **metadata**: Additional configuration as needed

The facade reads the routing document and makes physical routing decisions. Queries against the shared store cannot see private items — not by convention, but by physical separation.

**Default private patterns:**
- `{"_visibility": "draft"}`
- `{"_visibility": "private"}`
- `{"_for": "self"}`

**Customizing routing:**
The `_system:routing` document can be updated to change what routes privately. The patterns are associative — described in the document, not hardcoded.

---

## Domain Patterns

See [patterns/domains.md](../patterns/domains.md) for suggested collection and tag organization for common use cases:
- Software Development
- Market Research
- Personal Reflection & Growth
- Healthcare Tracking

---

## System Documents

The store's guiding metadata is itself stored as documents — like Oracle's data dictionary stored in tables. This enables agents to query and update the system's behavior.

**Well-known system documents:**

| ID | Purpose | Updatable |
|----|---------|-----------|
| `_system:routing` | Private/shared routing patterns | Yes |
| `_system:context` | Current working context | Yes |
| `_system:guidance` | Local behavioral guidance | Yes |

**Querying system documents:**
```python
# Read the routing configuration
routing = kp.get("_system:routing")
print(routing.summary)  # Natural language description
print(routing.tags)     # Includes private_patterns

# Find all system documents
system_docs = kp.query_tag("_system", "true")
```

**Updating behavior through documents:**
```python
# User says: "Research best practices for code review and update guidance"

# 1. Agent researches (web, existing patterns, etc.)
# 2. Agent updates the guidance document
kp.remember(
    content="""
    Code Review Guidance (updated based on research):

    - Review for correctness first, style second
    - Small PRs (<400 lines) get better reviews
    - Use checklist: security, error handling, tests, docs
    - Prefer synchronous review for complex changes

    Source: Team retrospective + industry research.
    """,
    id="_system:guidance:code_review",
    source_tags={"_system": "true", "domain": "code_review"}
)

# 3. Future sessions read this guidance when doing code review
```

**The pattern:** Agents evolve the system by writing documents, not changing code. This includes:
- Routing rules (what's private vs shared)
- Domain patterns (how to organize for this project)
- Process knowledge (how to do tasks well)
- Local preferences (user-specific guidance)

All queryable. All updateable. All associative.

---

## Implementation Overview

Components:
* A configuration file (toml) for details of the database settings and supporting services (embeddings, summarization, tagging).  This configuration file is written at initialization time.  It contains everything necessary to open the datastore for querying any collection.
* A vector database (ChromaDb).
* An embeddings provider that produces a vectorization of the original content.  This enables associative recall and similarity search.
* A summarization provider that produces accurate short summaries of the original content.  This enables consistent fast recall of summary information.
* A tagging provider that produces structured identifiers that describe the original content.  This enables traditional indexing and navigation strategies.
* A document provider that fetches content from URIs (file://, https://, etc.)

### Provider Options

| Type | Local (Apple Silicon) | Local (other) | API-based |
|------|----------------------|---------------|-----------|
| Embedding | `mlx` | `sentence-transformers` | `openai` |
| Summarization | `mlx` | `passthrough` | `openai`, `ollama` |
| Tagging | `mlx` | `noop` | `openai`, `ollama` |

Providers are auto-detected at initialization based on platform and available API keys.

## Error Handling

| Situation | Behavior |
|-----------|----------|
| Store path doesn't exist | Created automatically |
| Collection doesn't exist | Created on first `update()` |
| URI unreachable | `IOError` raised from `update()` |
| Item not found | `get()` returns `None`, `find_similar()` raises `KeyError` |
| No results | Empty list returned |

## Initialization

See [initialize.md](../initialize.md) for details.

```python
from keep import Keeper

kp = Keeper("/path/to/store")
```
