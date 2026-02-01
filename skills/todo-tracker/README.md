# 📋 TODO Tracker Skill

A persistent TODO scratch pad for [Clawdbot](https://clawdbot.com) that tracks tasks across sessions with priorities, completion tracking, and heartbeat reminders.

## Installation

```bash
# Clone to your skills folder
git clone https://github.com/jdrhyne/todo-tracker-skill.git skills/todo-tracker
```

Or copy `SKILL.md` and `scripts/` to your Clawdbot workspace.

## Usage

Just talk naturally to your agent:

| Say this... | What happens |
|-------------|--------------|
| "Add X to TODO" | Adds item (default: medium priority) |
| "Add X to high priority TODO" | Adds as high priority |
| "What's on the TODO?" | Shows the list |
| "Mark X done" | Moves item to Done section |
| "Remove X from TODO" | Deletes the item |

## Priorities

- 🔴 **High** — Urgent items
- 🟡 **Medium** — Normal priority (default)
- 🟢 **Nice to Have** — Low priority / future ideas

## TODO.md Format

The skill maintains a `TODO.md` file in your workspace:

```markdown
# TODO - Scratch Pad

*Last updated: 2026-01-17*

## 🔴 High Priority
- [ ] Important task (added: 2026-01-17)

## 🟡 Medium Priority
- [ ] Regular task (added: 2026-01-17)

## 🟢 Nice to Have
- [ ] Future idea (added: 2026-01-17)

## ✅ Done
- [x] Completed task (done: 2026-01-17)
```

## CLI Commands

The skill includes a bash script for direct use:

```bash
# Add items
bash scripts/todo.sh add high "Urgent task"
bash scripts/todo.sh add medium "Normal task"
bash scripts/todo.sh add low "Nice to have"

# Mark done (matches partial text)
bash scripts/todo.sh done "Urgent"

# Remove item
bash scripts/todo.sh remove "old task"

# List all
bash scripts/todo.sh list

# Quick summary (great for heartbeats)
bash scripts/todo.sh summary
```

## Heartbeat Integration

Add this to your `HEARTBEAT.md` to get reminders:

```markdown
## Active Monitoring Tasks

### Daily TODO Check
On each heartbeat:
- Run: bash skills/todo-tracker/scripts/todo.sh summary
- If high-priority items exist, mention them
- Flag stale items (>7 days old)
```

## Example Summary Output

```
📋 TODO: 7 items (2 high, 2 medium, 3 low)
🔴 High priority items:
  • Ingest low-code docs
  • Fix critical bug
⚠️ 1 stale item (>7 days old)
```

## License

MIT — use freely!

---

Made for Clawdbot 🤖
