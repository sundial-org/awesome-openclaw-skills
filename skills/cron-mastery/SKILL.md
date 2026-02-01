---
name: cron-mastery
description: Master OpenClaw's timing systems. Use for scheduling reliable reminders, setting up periodic maintenance (janitor jobs), and understanding when to use Cron vs Heartbeat for time-sensitive tasks.
---

# Cron Mastery

**Rule #1: Heartbeats drift. Cron is precise.**

This skill provides the definitive guide for managing time in OpenClaw. It solves the "I missed my reminder" problem by enforcing a strict separation between casual checks (heartbeat) and hard schedules (cron).

## The Core Principle

| System | Behavior | Best For | Risk |
| :--- | :--- | :--- | :--- |
| **Heartbeat** | "I'll check in when I can" (e.g., every 30-60m) | Email checks, casual news summaries, low-priority polling. | **Drift:** A "remind me in 10m" task will fail if the heartbeat is 30m. |
| **Cron** | "I will run at exactly X time" | Reminders ("in 5 mins"), daily reports, system maintenance. | **Clutter:** Creates one-off jobs that need cleanup. |

## 1. Setting Reliable Reminders

**Never** use `act:wait` or internal loops for long delays (>1 min). Use `cron:add` with a one-shot `at` schedule.

### Standard Reminder Pattern (JSON)

Use this payload structure for "remind me in X minutes" tasks:

```json
{
  "name": "Remind: Drink Water",
  "schedule": {
    "kind": "at",
    "atMs": <CURRENT_MS + DELAY_MS>
  },
  "payload": {
    "kind": "agentTurn",
    "message": "⏰ Reminder: Drink water!",
    "deliver": true
  },
  "sessionTarget": "isolated",
  "wakeMode": "next-heartbeat"
}
```

*Note: Even with `wakeMode: "next-heartbeat"`, the cron system forces an event injection at `atMs`. Use `mode: "now"` in the `cron:wake` tool if you need to force an immediate wake outside of a job payload.*

## 2. The Janitor (Auto-Cleanup)

One-shot cron jobs (kind: `at`) disable themselves after running but stay in the list as "ghosts" (`enabled: false`, `lastStatus: ok`). To prevent clutter, install the **Daily Janitor**.

### Setup Instructions

1.  **Check current jobs:** `cron:list` (includeDisabled: true)
2.  **Create the Janitor:**
    *   **Name:** `Daily Cron Cleanup`
    *   **Schedule:** Every 24 hours (`everyMs: 86400000`)
    *   **Payload:** An agent turn that runs a specific prompt.

### The Janitor Prompt (Agent Turn)

> "Time for the 24-hour cron sweep. List all cron jobs including disabled ones. If you find any jobs that are `enabled: false` and have `lastStatus: ok` (finished one-shots), delete them to keep the list clean. Do not delete active recurring jobs. Log what you deleted."

## 3. Reference: Timezone Lock

For cron to work, the agent **must** know its time.
*   **Action:** Add the user's timezone to `MEMORY.md`.
*   **Example:** `Timezone: Cairo (GMT+2)`
*   **Validation:** If a user says "remind me at 9 PM," confirm: "9 PM Cairo time?" before scheduling.

## 4. The Self-Wake Rule (Behavioral)

**Problem:** If you say "I'll wait 30 seconds" and end your turn, you go to sleep. You cannot wake up without an event.
**Solution:** If you need to "wait" across turns, you **MUST** schedule a Cron job.

*   **Wait < 1 minute (interactive):** Only allowed if you keep the tool loop open (using `act:wait`).
*   **Wait > 1 minute (async):** Use Cron with `wakeMode: "now"`.

**Example Payload for "Checking back in 30s":**
```json
{
  "schedule": { "kind": "at", "atMs": <NOW + 30000> },
  "payload": { "kind": "agentTurn", "message": "⏱️ 30s check-in. Report status." },
  "wakeMode": "now"
}
```

## Troubleshooting

*   **"My reminder didn't fire":** Check `cron:list`. If the job exists but didn't fire, check the system clock vs `atMs`.
*   **"I have 50 old jobs":** Run the Janitor manually immediately.
