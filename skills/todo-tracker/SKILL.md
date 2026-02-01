---
name: todo-tracker
description: Persistent TODO scratch pad for tracking tasks across sessions. Use when user says "add to TODO", "what's on the TODO", "mark X done", "show TODO list", "remove from TODO", or asks about pending tasks. Also triggers on heartbeat to remind about stale items.
---

# TODO Tracker

Maintain a persistent TODO.md scratch pad in the workspace.

## File Location

`TODO.md` in workspace root (e.g., `/Users/nuthome/nuri-bot/TODO.md`)

## Commands

### View TODO
When user asks: "what's on the TODO?", "show TODO", "pending tasks?"
```bash
cat TODO.md
```
Then summarize the items by priority.

### Add Item
When user says: "add X to TODO", "TODO: X", "remember to X"
```bash
bash skills/todo-tracker/scripts/todo.sh add "<priority>" "<item>"
```
Priorities: `high`, `medium`, `low` (default: medium)

Examples:
```bash
bash skills/todo-tracker/scripts/todo.sh add high "Ingest low-code docs"
bash skills/todo-tracker/scripts/todo.sh add medium "Set up Zendesk escalation"
bash skills/todo-tracker/scripts/todo.sh add low "Add user memory feature"
```

### Mark Done
When user says: "mark X done", "completed X", "finished X"
```bash
bash skills/todo-tracker/scripts/todo.sh done "<item-pattern>"
```
Matches partial text. Moves item to ✅ Done section with date.

### Remove Item
When user says: "remove X from TODO", "delete X from TODO"
```bash
bash skills/todo-tracker/scripts/todo.sh remove "<item-pattern>"
```

### List by Priority
```bash
bash skills/todo-tracker/scripts/todo.sh list high
bash skills/todo-tracker/scripts/todo.sh list medium
bash skills/todo-tracker/scripts/todo.sh list low
```

## Heartbeat Integration

On heartbeat, check TODO.md:
1. Count high-priority items
2. Check for stale items (added >7 days ago)
3. If items exist, include brief summary in heartbeat response

Example heartbeat check:
```bash
bash skills/todo-tracker/scripts/todo.sh summary
```

## TODO.md Format

```markdown
# TODO - Nuri Scratch Pad

*Last updated: 2026-01-17*

## 🔴 High Priority
- [ ] Item one (added: 2026-01-17)
- [ ] Item two (added: 2026-01-15) ⚠️ STALE

## 🟡 Medium Priority
- [ ] Item three (added: 2026-01-17)

## 🟢 Nice to Have
- [ ] Item four (added: 2026-01-17)

## ✅ Done
- [x] Completed item (done: 2026-01-17)
```

## Response Format

When showing TODO:
```
📋 **TODO List** (3 items)

🔴 **High Priority** (1)
• Ingest low-code docs

🟡 **Medium Priority** (1)  
• Zendesk escalation from Discord

🟢 **Nice to Have** (1)
• User conversation memory

⚠️ 1 item is stale (>7 days old)
```
