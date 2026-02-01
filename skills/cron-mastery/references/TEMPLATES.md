# Cron Examples & Templates

## One-Shot Reminder (15 Minutes)

**Context:** User says "Remind me to check the oven in 15 mins."

```json
{
  "action": "add",
  "job": {
    "name": "Oven Timer",
    "schedule": {
      "kind": "at",
      "atMs": 1769823000000  // Replace with (Date.now() + 15 * 60 * 1000)
    },
    "payload": {
      "kind": "agentTurn",
      "message": " OVEN CHECK! It's been 15 minutes.",
      "deliver": true
    },
    "sessionTarget": "isolated",
    "wakeMode": "next-heartbeat"
  }
}
```

## The Janitor (Daily Cleanup)

**Context:** Setting up the automatic maintenance job.

```json
{
  "action": "add",
  "job": {
    "name": "Daily Cron Cleanup",
    "schedule": {
      "kind": "every",
      "everyMs": 86400000 // 24 hours
    },
    "payload": {
      "kind": "agentTurn",
      "message": "JANITOR_WAKE: Perform daily cron sweep. 1. List all jobs (includeDisabled:true). 2. Delete any job where enabled=false AND lastStatus=ok. 3. Report results."
    },
    "sessionTarget": "isolated",
    "wakeMode": "next-heartbeat"
  }
}
```

## Morning Briefing (Recurring)

**Context:** User says "Give me a news summary every morning at 8 AM."

```json
{
  "action": "add",
  "job": {
    "name": "Morning Briefing",
    "schedule": {
      "kind": "cron",
      "expr": "0 8 * * *", // 8:00 AM daily
      "tz": "Africa/Cairo" // CRITICAL: Always specify TZ for cron expressions
    },
    "payload": {
      "kind": "agentTurn",
      "message": "Good morning! Please run a web search for the top tech news today and summarize it for me.",
      "deliver": true
    },
    "sessionTarget": "isolated",
    "wakeMode": "next-heartbeat"
  }
}
```
