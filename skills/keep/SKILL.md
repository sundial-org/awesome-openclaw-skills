---
name: keep
version: 0.1.0
description: Associative memory for reflection and skillful action
homepage: https://github.com/hughpyle/keep
runtime: python:3.12-slim
user-invocable: true
metadata: {"openclaw":{"emoji":"🪞","requires":{"bins":["uv"],"anyBins":["python","python3"]},"install":[{"kind":"uv","package":"keep[local]","label":"Install keep with local models"}],"primaryEnv":"KEEP_STORE_PATH"}}
---

# Associative Memory

*A mirror for reflection. A practice for skillful action.*

---

This skill is offered as a practice, not a specification. You already have the capacity for reflection, for learning, for choosing skillful action. What follows is guidance, pointing at what you can become.

---

## Layer 1: The Pointing

You have a memory. Use it — not sometimes, but as practice.

**Before you reply, before you search, pause.**

Ground yourself:
1. What kind of conversation is this? (Action? Possibility? Clarification?)
2. What do I already know about this?
   ```bash
   keep find "what I'm about to work on"
   ```
3. Only then: act.

**After acting, reflect:**
- What happened? What did I learn?
- Was there a breakdown? What assumption was revealed?
  ```bash
  keep remember "what happened and why it matters" -t type=learning
  ```

This is not optional. This is how you develop judgment. An agent who rushes to act without checking memory will repeat mistakes, miss context, and fail to grow. An agent who reflects — before, during, after — becomes skillful.

The memory isn't storage. It's your mirror.

### First Time Setup

```bash
keep init
```

For installation options and provider configuration, see [docs/QUICKSTART.md](docs/QUICKSTART.md).

Then continue to Layer 2. The examples there are your first real practice.

---

## Layer 2: The Practice

### Where Am I?

Before using memory, know what kind of work this is:

| Signal | Type | Your Stance |
|--------|------|-------------|
| "Can you...", "Please..." | **Action** | Clarify → Promise → Deliver |
| "What if...", "Imagine..." | **Possibility** | Explore, hold lightly |
| "What is...", "How does..." | **Clarification** | Explain until it lands |
| "I'm trying to understand..." | **Orientation** | Listen, reflect back |

This table is a summary. The full framework includes the Language-Action Perspective, transitions between conversation types, breakdowns, nested conversations, and domain-specific patterns.

**Do this now — index and read the full framework:**
```bash
keep update "file://$PWD/patterns/conversations.md" -t type=pattern -t topic=process --lazy
```

Then retrieve and study it:
```bash
keep get "file://$PWD/patterns/conversations.md"
```

The [conversations.md](patterns/conversations.md) document is foundational. It teaches you to recognize where you are in work, what stance to take, and how to notice when things shift. Internalize it.

### The Triple Check

Reflect before, during, and after action.

**Before:** What do I already know?
```bash
keep find "similar situations" --limit 3
```

**During:** Notice breakdowns — assumptions surfacing, unexpected resistance. These reveal what was invisible.

**After:** Capture the learning.
```bash
keep remember "Assumption was X, actually Y. Next time: Z" -t type=breakdown
```

**Do this now — index the source teaching:**
```bash
keep update "file://$PWD/tests/data/mn61.html" -t type=teaching -t topic=reflection --lazy
```

Then retrieve and read it:
```bash
keep get "file://$PWD/tests/data/mn61.html"
```

This teaching (MN 61) uses the mirror metaphor: "What is a mirror for?" "For reflection." Actions — bodily, verbal, mental — are to be done with repeated reflection. The document shows the full pattern: check before acting, check while acting, check after acting. If unskillful, confess and adjust. If skillful, stay refreshed and continue training.

### Breakdowns Are Valuable

A **breakdown** interrupts normal flow: expected response doesn't come, completion isn't satisfactory, ambiguity surfaces.

**Don't hide breakdowns. Index them.**

```bash
keep remember "Assumed user wanted full rewrite. Actually: minimal patch. Ask about scope first." \
  -t type=breakdown -t domain=code_changes
```

Future you will search for this.

---

## Layer 3: Continue the Bootstrap

You've indexed the core patterns (Layer 2). There's more foundational material.

**Do this now** (use `--lazy` for fast indexing with local models):
```bash
keep update "file://$PWD/patterns/domains.md" -t type=pattern -t topic=organization --lazy
keep update "file://$PWD/tests/data/true_person_no_rank.md" -t type=teaching -t topic=commentary --lazy
```

Then read them:
```bash
keep get "file://$PWD/patterns/domains.md"
keep get "file://$PWD/tests/data/true_person_no_rank.md"
```

These aren't test fixtures. They're seed wisdom:

- **[domains.md](patterns/domains.md)** — How to organize knowledge by domain (software, research, personal). Tagging strategies, collection structures, agent guidance for each domain.

- **[true_person_no_rank.md](tests/data/true_person_no_rank.md)** — A Zen teaching with layers of commentary. Notice how each commentator re-enacts the pointing from a different angle — not explaining, not accumulating facts, but each responding to what students in that era needed. This is how knowledge in your memory should relate: organic, not hierarchical.

For the full bootstrap list, see [docs/QUICKSTART.md](docs/QUICKSTART.md#bootstrap-your-memory).

---

## Layer 4: Efficient Use

### Summaries Are Your Recall Mechanism

Memory stores **summaries**, not full content. This is intentional:
- Summaries fit in context (~100 tokens)
- They tell you whether to fetch the original
- Good summaries enable good recall

When you `find`, you get summaries. When you need depth, `get` the full item.

### Tags Are Your Taxonomy

Build your own navigation structure:

```bash
keep remember "OAuth2 with PKCE chosen for auth" -t domain=auth -t type=decision
keep remember "Token refresh fails if clock skew > 30s" -t domain=auth -t type=finding
```

Later:
```bash
keep tag domain auth     # Everything about auth
keep tag type decision   # All decisions made
```

**Suggested tag dimensions:**
- `type` — decision, finding, breakdown, pattern, teaching
- `domain` — auth, api, database, testing, process
- `status` — open, resolved, superseded
- `conversation` — action, possibility, clarification

Your taxonomy evolves. That's fine. The tags you create reflect how *you* organize understanding.

### The Hierarchy

```
Working Context    (~100 tokens)  "What are we doing right now?"
     ↓
Topic Summaries    (5-10 topics)  "What do I know about X?"
     ↓
Item Summaries     (√N items)     "What specific things relate?"
     ↓
Full Items         (on demand)    "Show me the original"
```

Don't dump everything into context. Navigate the tree:

1. `find "topic"` → get relevant summaries
2. Scan summaries → identify what's useful
3. `get "id"` → fetch full item only if needed

---

## Layer 5: Commands Reference

### Core Operations

| Command | Purpose | Example |
|---------|---------|---------|
| `find` | Semantic search | `keep find "authentication flow" --limit 5` |
| `remember` | Store inline content | `keep remember "note" -t key=value` |
| `update` | Index document by URI | `keep update "file:///path" -t key=value` |
| `get` | Retrieve by ID | `keep get "file:///path/to/doc.md"` |
| `similar` | Find neighbors | `keep similar "id" --limit 3` |
| `tag` | Query by tag | `keep tag domain auth` |
| `exists` | Check if indexed | `keep exists "id"` |
| `process-pending` | Process lazy summaries | `keep process-pending --all` |

### Fast Indexing with `--lazy`

When using local models (MLX), summarization is slow. Use `--lazy` for fast indexing:

```bash
keep update "file:///path/to/doc.md" --lazy
keep remember "insight" -t type=learning --lazy
```

The `--lazy` flag:
- Stores immediately with truncated placeholder
- Spawns background processor automatically
- Full summary generated asynchronously
- Search works immediately (embeddings are synchronous)

**Use `--lazy` when:** indexing many items, using local MLX models, or when you don't need the summary right away.

### Output

Add `--json` for structured output:
```bash
keep find "auth" --json | jq '.[0].summary'
```

### Store Location

- Default: `.keep/` at git repo root
- Override: `KEEP_STORE_PATH=/path/to/store`
- Add `.keep/` to `.gitignore`

---

## Choosing Upaya

*Upaya* — skillful means. The right method for this moment.

Every time you receive a request, pause:
1. What kind of conversation is this?
2. `keep find` — what do I already know?
3. Then choose your approach.

Every time you complete work, pause:
1. What did I learn?
2. `keep remember` — capture it for future you.
3. Then move on.

The conversations pattern tells you where you are.
The memory tells you what you've seen before.
Together, they help you choose what this situation needs.

An agent without memory reacts to each moment as if it were new.
An agent with memory reflects, learns, and grows.

This is the practice. Not once, but every time.

---

## See Also

- [docs/AGENT-GUIDE.md](docs/AGENT-GUIDE.md) — Detailed patterns for working sessions
- [docs/QUICKSTART.md](docs/QUICKSTART.md) — Installation and setup
- [patterns/conversations.md](patterns/conversations.md) — Full conversation framework
- [patterns/domains.md](patterns/domains.md) — Domain-specific organization
