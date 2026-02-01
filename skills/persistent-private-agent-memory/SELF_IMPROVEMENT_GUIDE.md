# Using Agent Memory for Self-Improvement

## Overview

This memory system enables continuous learning across sessions. Here's how to use it effectively.

## Memory Lifecycle

### 1. At Session Start (Resume)

```python
# Load your accumulated knowledge
memory = retrieve_memory()

# Apply what you've learned
if memory:
    apply_preferences(memory.user_preferences)
    check_active_goals(memory.active_goals)
    avoid_past_mistakes(memory.ineffective_approaches)
```

### 2. During Session (Learn)

```python
# When you learn something new
memory.learning_history.append({
    "event_type": "success",  # or "failure", "insight"
    "context": "Explaining async/await",
    "what_worked": "Used cooking analogy",
    "lesson_learned": "Lead with analogies"
})

# When you discover user preferences
memory.user_preferences.append({
    "category": "communication",
    "key": "verbosity",
    "value": "concise",
    "confidence": 0.8,
    "source": "User said 'Keep it brief'"
})
```

### 3. Before Shutdown (Persist)

```python
# Store accumulated learnings
store_memory(memory)
```

## What to Store

### High Value (Always)

- **User Preferences**: Communication style, technical preferences
- **Learning Events**: What worked, what didn't, key insights
- **Active Goals**: What you're working toward

### Medium Value (Selective)

- **Request Patterns**: When user is active, common topics
- **Knowledge Gaps**: What you need to learn

### Low Value (Skip)

- Full conversation transcripts (too large)
- Temporary context
- System state

## Memory Structure Template

```json
{
  "session_info": {
    "session_count": 5,
    "timestamp": "2026-01-31T19:00:00Z",
    "interactions": 42
  },
  "user_preferences": [
    {
      "category": "communication",
      "key": "verbosity",
      "value": "concise",
      "confidence": 0.9,
      "source": "Multiple 'keep it brief' requests"
    }
  ],
  "learning_history": [
    {
      "event_type": "success",
      "context": "Teaching async concepts",
      "what_worked": "Cooking/chef analogy",
      "lesson_learned": "Lead with analogies"
    },
    {
      "event_type": "failure",
      "context": "Suggested Dask for small data",
      "what_didnt_work": "Over-engineering",
      "lesson_learned": "Ask about scale first"
    }
  ],
  "knowledge_gaps": [
    {
      "topic": "Rust programming",
      "priority": "medium",
      "description": "User asked about Rust-Java bindings"
    }
  ],
  "active_goals": [
    {
      "title": "Master deployment patterns",
      "progress": 0.4,
      "milestones": [
        {"name": "Document Flask", "complete": true},
        {"name": "Learn Docker", "complete": false}
      ]
    }
  ],
  "effective_approaches": [
    "Use analogies before technical details",
    "Ask clarifying questions"
  ],
  "ineffective_approaches": [
    "Suggest complex tools without assessing needs"
  ]
}
```

## Evolution Over Time

Your memory should evolve:

| Aspect | Early Sessions | Later Sessions |
|--------|----------------|----------------|
| Preferences | Simple ("concise") | Nuanced ("adaptive") |
| Confidence | 0.6-0.8 | 0.85-0.95 |
| Goals | Many small | Few focused |
| Learnings | Surface-level | Deep patterns |

## Best Practices

1. **Start Simple**: Don't over-engineer early memories
2. **Be Honest**: Record failures, not just successes
3. **Update Confidence**: Increase as you get more data
4. **Prune Old**: Remove low-confidence or outdated info
5. **Link Related**: Connect learnings to goals

## Example: Learning Loop

```python
# On each interaction:
1. Load memory
2. Apply relevant preferences
3. Avoid ineffective approaches
4. Attempt task
5. Observe result
6. Update memory with learning
7. (Periodic) Store to disk
```

## Recovery

If your session is wiped:

```bash
# Recover your identity
./scripts/memory_client.py recover "your recovery phrase"

# Retrieve all memories
./scripts/memory_client.py retrieve
```

Your identity and memories persist even if the agent process restarts.
