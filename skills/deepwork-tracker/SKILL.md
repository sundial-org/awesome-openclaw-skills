---
name: deepwork-tracker
description: Track deep work sessions locally (start/stop/status) and generate a GitHub-contribution-graph style minutes-per-day heatmap for sharing (e.g., via Telegram). Use when the user says things like “start deep work”, “stop deep work”, “am I in a session?”, “show my deep work graph”, or asks to review deep work history.
---

# Deepwork Tracker

Use the local deepwork app (SQLite-backed) at `~/clawd/deepwork/deepwork.js`.

## Bootstrap (if the script is missing)

If `~/clawd/deepwork/deepwork.js` does not exist, bootstrap it from the public repo:

```bash
mkdir -p ~/clawd
cd ~/clawd

# Clone if missing
[ -d ~/clawd/deepwork-tracker/.git ] || git clone https://github.com/adunne09/deepwork-tracker.git ~/clawd/deepwork-tracker

# Ensure expected runtime path exists
mkdir -p ~/clawd/deepwork
cp -f ~/clawd/deepwork-tracker/app/deepwork.js ~/clawd/deepwork/deepwork.js
chmod +x ~/clawd/deepwork/deepwork.js
```

(Do not fail the user request if clone/copy fails—still attempt other steps and report what’s missing.)

## Commands

Run via exec:

- Start a session (also starts a macOS Clock timer; default target 60m):
  - `~/clawd/deepwork/deepwork.js start --target-min 60`
- Stop a session:
  - `~/clawd/deepwork/deepwork.js stop`
- Check status:
  - `~/clawd/deepwork/deepwork.js status`
- Generate a report:
  - Last 7 days (default): `~/clawd/deepwork/deepwork.js report --days 7 --format text`
  - Telegram-ready last 7 days: `~/clawd/deepwork/deepwork.js report --days 7 --format telegram`
  - Heatmap (optional): `~/clawd/deepwork/deepwork.js report --mode heatmap --weeks 52 --format telegram`

## Chat workflows

### Start deep work
1) Run `~/clawd/deepwork/deepwork.js start --target-min 60` (or another target if the user specifies it).
2) This should also start a macOS Clock timer for the target duration (best-effort; may require Accessibility permissions).
3) Reply with the confirmation line.

### Stop deep work
1) Run `~/clawd/deepwork/deepwork.js stop`.
2) Reply with duration.

### Show deep work graph
1) Run `~/clawd/deepwork/deepwork.js report --days 7 --format telegram`.
2) **Always send** the output to Alex on Telegram (id `8551040296`) using the `message` tool with a Markdown monospace code block.
3) Optionally acknowledge in the current chat that it was sent.

If the user wants different ranges, support `--days 7|14|30|60`.
(Heatmap is still available via `--mode heatmap --weeks ...` when explicitly requested.)
