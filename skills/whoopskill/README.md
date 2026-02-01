# WHOOP Skill

[![npm version](https://img.shields.io/npm/v/whoopskill.svg)](https://www.npmjs.com/package/whoopskill)

CLI for fetching WHOOP health data via the WHOOP API v2.

## Install

```bash
npm install -g whoopskill
```

## Quick Start

```bash
# One-liner health snapshot
whoopskill summary
# Output: 2026-01-05 | Recovery: 52% | HRV: 39ms | RHR: 60 | Sleep: 40% | Strain: 6.7

# Human-readable output
whoopskill --pretty

# JSON output (default)
whoopskill
```

## Setup

Before using, you need to configure WHOOP API credentials:

1. Register a WHOOP application at [developer.whoop.com](https://developer.whoop.com)
   - Apps with <10 users don't need WHOOP review (immediate use)

2. Set environment variables:
```bash
export WHOOP_CLIENT_ID=your_client_id
export WHOOP_CLIENT_SECRET=your_client_secret
export WHOOP_REDIRECT_URI=https://your-redirect-uri.com/callback
```

Or create a `.env` file in your working directory.

3. Authenticate:
```bash
whoopskill auth login
```

Tokens are stored in `~/.whoop-cli/tokens.json` and auto-refresh when expired.

## Usage

```bash
# Fetch all today's data
whoopskill

# One-liner health snapshot
whoopskill summary

# Human-readable output
whoopskill --pretty

# Specific data type
whoopskill profile
whoopskill body
whoopskill sleep
whoopskill recovery
whoopskill workout
whoopskill cycle

# Multiple types
whoopskill --sleep --recovery --body

# Specific date (ISO format)
whoopskill --date 2025-01-03

# Pagination
whoopskill workout --limit 50
whoopskill workout --all
```

## Auth Commands

```bash
whoopskill auth login    # OAuth flow (opens browser)
whoopskill auth status   # Check token status
whoopskill auth refresh  # Refresh access token using refresh token
whoopskill auth logout   # Clear tokens
```

## Keeping tokens fresh (recommended for cron/servers)

If you run `whoopskill` from cron/systemd, you may occasionally see authentication failures if a token refresh is missed or the token file becomes stale.

Important:
- `whoopskill auth status` **does not refresh tokens** — it only reports whether they’re expired.
- For automation, you must call `whoopskill auth refresh` periodically.

Recommended pattern:
- Run `whoopskill auth login` once interactively (creates `~/.whoop-cli/tokens.json`).
- Run a small periodic monitor that calls `whoopskill auth refresh` and performs a lightweight fetch.

An example monitor script + systemd timer/cron examples are included here:
- `examples/monitor/whoop-refresh-monitor.sh`
- `examples/monitor/systemd/*`
- `examples/monitor/cron/README-cron.txt`

If refresh fails with an expired refresh token, you must re-authenticate:

```bash
whoopskill auth login
```

## Data Types

| Type | Description |
|------|-------------|
| `profile` | User info (name, email) |
| `body` | Body measurements (height, weight, max HR) |
| `sleep` | Sleep records with stages, efficiency, respiratory rate |
| `recovery` | Recovery score, HRV, RHR, SpO2, skin temp |
| `workout` | Workouts with strain, HR zones, calories |
| `cycle` | Daily physiological cycle (strain, calories) |

## Options

| Flag | Description |
|------|-------------|
| `-d, --date <date>` | Date in ISO format (YYYY-MM-DD) |
| `-l, --limit <n>` | Max results per page (default: 25) |
| `-a, --all` | Fetch all pages |
| `-p, --pretty` | Human-readable output |
| `--profile` | Include profile |
| `--body` | Include body measurements |
| `--sleep` | Include sleep |
| `--recovery` | Include recovery |
| `--workout` | Include workouts |
| `--cycle` | Include cycle |

## Output

JSON to stdout by default. Use `--pretty` for human-readable format.

```json
{
  "date": "2025-01-05",
  "fetched_at": "2025-01-05T12:00:00.000Z",
  "profile": { "user_id": 123, "first_name": "John" },
  "body": { "height_meter": 1.83, "weight_kilogram": 82.5, "max_heart_rate": 182 },
  "recovery": [{ "score": { "recovery_score": 52, "hrv_rmssd_milli": 38.9 }}],
  "sleep": [{ "score": { "sleep_performance_percentage": 40 }}],
  "workout": [{ "sport_name": "hiit", "score": { "strain": 6.2 }}],
  "cycle": [{ "score": { "strain": 6.7 }}]
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Authentication error |
| 3 | Rate limit exceeded |
| 4 | Network error |

## Requirements

- Node.js 22+
- WHOOP membership with API access

## Development

```bash
git clone https://github.com/koala73/whoopskill.git
cd whoopskill
npm install
npm run dev      # Run with tsx
npm run build    # Compile TypeScript
```

## License

MIT
