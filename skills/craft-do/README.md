# Craft.do Integration Skill

Complete Craft.do API integration for automation, migration, and ongoing workflows. Includes full API reference, helper scripts, Obsidian migration tools, and task management automation.

**Capabilities:**
- 🔄 **Obsidian Migration** - Full vault migration with nested folders & content
- 📝 **Document Management** - Create, read, organize documents programmatically  
- ✅ **Task Automation** - Create, update, list tasks across inbox/daily notes/logbook
- 📁 **Folder Organization** - Build nested folder hierarchies via API
- 🔧 **Helper Scripts** - Ready-to-use bash scripts for common operations
- 🧹 **Cleanup Tools** - Safe deletion and recovery utilities

## Overview

This skill provides **complete Craft.do API integration** for agents and automation:

- **One-time migration:** Move your entire Obsidian vault to Craft with full hierarchy
- **Ongoing automation:** Create tasks, organize documents, manage content programmatically
- **Helper utilities:** Ready-to-use scripts for common Craft operations
- **Safe & tested:** Production-ready with duplicate prevention and cleanup tools

## Quick Start

1. **Set up credentials:**
```bash
export CRAFT_API_KEY="pdk_your_key_here"
export CRAFT_ENDPOINT="https://connect.craft.do/links/YOUR_LINK/api/v1"
```

2. **Migrate Obsidian vault to Craft:**
```bash
cd ~/.openclaw/workspace/skills/craft-do

# Full nested migration (preserves folder hierarchy)
./migrate-obsidian-nested.sh "/path/to/your/vault"

# Safe to re-run - checks for existing folders before creating!
```

3. **Use the helper script:**
```bash
# List your folders
./craft-api.sh folders

# Create a task
./craft-api.sh create-task "Review API documentation"

# List active tasks
./craft-api.sh tasks active

# Create a document
./craft-api.sh create-doc "Daily Standup" "## What I did\\n- Task 1\\n- Task 2"
```

## Files

- **SKILL.md** - Complete API reference with examples and limitations
- **craft-api.sh** - Bash helper script for common operations
- **migrate-obsidian-nested.sh** - Migrate Obsidian vault with full nested hierarchy
- **cleanup-craft.sh** - Delete all user-created folders and documents
- **README.md** - This file

## What This Skill Enables

### ✅ Fully Supported
- **Task Management** - Create, update, list tasks across inbox/daily notes/logbook
- **Document Management** - Create, read, move documents between folders
- **Folder Organization** - List and navigate folder hierarchy (including nested folders!)
- **Markdown Everything** - All content is markdown-native
- **Obsidian Migration** - Full vault migration with nested folders and content
- **Cleanup Tools** - Safe deletion and recovery via trash

### ❌ Not Yet Available
- **Collections API** - Database tables only accessible in UI
- **Task Deletion** - Can only create/update, not delete
- **Document Deletion** - Can only move, not delete (use cleanup script)
- **Advanced Search** - Search endpoint needs refinement

## Obsidian → Craft Migration

Migrate your entire Obsidian vault to Craft.do with full folder hierarchy preserved:

```bash
# Set credentials
export CRAFT_API_KEY="pdk_..."
export CRAFT_ENDPOINT="https://connect.craft.do/links/YOUR_LINK/api/v1"

# Run migration
./migrate-obsidian-nested.sh "/path/to/vault"
```

**Features:**
- ✅ Preserves full nested folder hierarchy
- ✅ Migrates all markdown files with content
- ✅ Skips files starting with `_` or `.`
- ✅ Safe to re-run - checks for existing folders
- ✅ No duplicates created on subsequent runs

**If you need to start over:**
```bash
./cleanup-craft.sh  # Deletes everything, then re-run migration
```

## Integration Patterns

### Mission Control ↔ Craft Sync

**Use Case:** Keep automation in Mission Control, beautiful UI in Craft

```bash
# Sync completed tasks from Mission Control to Craft
cat mission-control/completed-tasks.json | jq -r '.[] | .title' | while read task; do
  ./craft-api.sh create-task "$task" inbox
  ./craft-api.sh complete-task "$(./craft-api.sh tasks active | jq -r '.items[0].id')" "$task"
done
```

### Daily Note Generation

```bash
# Create today's daily note
TODAY=$(date +%Y-%m-%d)
./craft-api.sh create-doc "Daily Note - $TODAY" "# $TODAY

## Tasks
- [ ] Morning standup
- [ ] Review PRs

## Notes
" daily_notes
```

## Best Practices

1. **Test in `unsorted` first** - Easy to find and clean up
2. **One-way sync recommended** - Craft as read-only view of Mission Control data
3. **Batch operations** - API supports arrays for efficiency
4. **Store credentials securely** - Use environment variables, never commit
5. **Handle errors** - API returns detailed validation messages

## Testing

All endpoints tested and documented in SKILL.md:
- [x] Folders (list)
- [x] Documents (create, read, list, move)
- [x] Tasks (create, update, list all scopes)
- [x] Markdown support verified
- [ ] Search (format needs refinement)

## Examples

See SKILL.md for detailed curl examples and the complete workflow example at the bottom.

## Resources

- [Craft API Documentation](https://craft.do/api) (get your personal API link from Craft settings)
- [Craft Blog](https://www.craft.do/blog/introducing-collections)
- [Helper Script Reference](./craft-api.sh)

## Contributing

Tested: 2026-01-31
Last Updated: 2026-01-31

Found a new capability or limitation? Update SKILL.md and document your findings.

---

**Status:** Production-ready for tasks and documents. Collections awaiting API support.
