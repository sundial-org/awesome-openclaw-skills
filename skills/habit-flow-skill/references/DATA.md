# Data Storage Reference

## Data Location

All data is stored in:
- **Habits & Config:** `~/clawd/habit-flow-data/`
- **Logs:** `~/clawd/habit-flow-data/logs/`

## File Structure

```
~/clawd/habit-flow-data/
├── habits.json              # All habits metadata
├── logs/                    # One JSONL file per habit per year
│   ├── h_abc123_2026.jsonl
│   └── h_def456_2026.jsonl
└── config.json              # User config (timezone, persona, userId)
```

## Configuration File

**config.json structure:**
```json
{
  "timezone": "Europe/Lisbon",
  "activePersona": "flex",
  "userId": "default-user",
  "phoneNumber": "+351912345678"
}
```

**Fields:**
- `timezone` - User's timezone (e.g., "America/New_York", "Europe/London")
- `activePersona` - Active coaching persona ID (flex, coach-blaze, luna, ava, max, sofi, the-monk)
- `userId` - User identifier for multi-user mode
- `phoneNumber` - Optional E.164 phone number for reminders

## Data Schema

For detailed information about the data schema, including habit structure, log entries, and field definitions, see [data-schema.md](data-schema.md).

## First-Time Setup

When user first mentions habits:

1. Check if data directory exists
2. If not, initialize:
```bash
mkdir -p ~/clawd/habit-flow-data/logs
```
3. Create default config.json with Flex persona:
```json
{
  "timezone": "YOUR_TIMEZONE",
  "activePersona": "flex",
  "userId": "default-user"
}
```

## Backup and Migration

All data is stored as human-readable JSON/JSONL files, making backup and migration straightforward:

**Backup:**
```bash
cp -r ~/clawd/habit-flow-data ~/backups/habit-flow-backup-$(date +%Y%m%d)
```

**Restore:**
```bash
cp -r ~/backups/habit-flow-backup-YYYYMMDD ~/clawd/habit-flow-data
```
