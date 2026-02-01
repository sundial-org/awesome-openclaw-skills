---
name: whoopskill
description: WHOOP CLI with health insights, trends analysis, and data fetching (sleep, recovery, HRV, strain).
homepage: https://github.com/koala73/whoopskill
metadata: {"clawdis":{"emoji":"💪","requires":{"bins":["node"],"env":["WHOOP_CLIENT_ID","WHOOP_CLIENT_SECRET","WHOOP_REDIRECT_URI"]},"install":[{"id":"npm","kind":"npm","package":"whoopskill","bins":["whoopskill"],"label":"Install whoopskill (npm)"}]}}
---

# whoopskill

Use `whoopskill` to fetch WHOOP health metrics (sleep, recovery, HRV, strain, workouts).

Install: `npm install -g whoopskill` | [GitHub](https://github.com/koala73/whoopskill)

Quick start
- `whoopskill summary` — one-liner: Recovery: 52% | HRV: 39ms | Sleep: 40% | Strain: 6.7
- `whoopskill summary --color` — color-coded summary with 🟢🟡🔴 status indicators
- `whoopskill trends` — 7-day trends with averages and direction arrows
- `whoopskill trends --days 30 --pretty` — 30-day trend analysis
- `whoopskill insights --pretty` — AI-style health recommendations
- `whoopskill --pretty` — human-readable output with emojis
- `whoopskill recovery` — recovery score, HRV, RHR
- `whoopskill sleep` — sleep performance, stages
- `whoopskill workout` — workouts with strain
- `whoopskill --date 2025-01-03` — specific date

Analysis commands
- `summary` — quick health snapshot (add `--color` for status indicators)
- `trends` — multi-day averages with trend arrows (↑↓→)
- `insights` — personalized recommendations based on your data

Data types
- `profile` — user info (name, email)
- `body` — height, weight, max HR
- `sleep` — sleep stages, efficiency, respiratory rate
- `recovery` — recovery %, HRV, RHR, SpO2, skin temp
- `workout` — strain, HR zones, calories
- `cycle` — daily strain, calories

Combine types
- `whoopskill --sleep --recovery --body`

Auth
- `whoopskill auth login` — OAuth flow (opens browser)
- `whoopskill auth status` — check token status
- `whoopskill auth logout` — clear tokens

Notes
- Output is JSON to stdout (use `--pretty` for human-readable)
- Tokens stored in `~/.whoop-cli/tokens.json` (auto-refresh)
- Uses WHOOP API v2
- Date follows WHOOP day boundary (4am cutoff)
- WHOOP apps with <10 users don't need review (immediate use)

Sample: `whoopskill summary --color`
```
📅 2026-01-25
🟢 Recovery: 85% | HRV: 39ms | RHR: 63bpm
🟡 Sleep: 79% | 6.9h | Efficiency: 97%
🔴 Strain: 0.1 (optimal: ~14) | 579 cal
```

Sample: `whoopskill trends`
```
📊 7-Day Trends

💚 Recovery: 62.1% avg (34-86) →
💓 HRV: 33.8ms avg (26-42) →
❤️ RHR: 63.8bpm avg (60-68) →
😴 Sleep: 75.4% avg (69-79) →
🛏️ Hours: 6.5h avg (5.7-7.8) ↓
🔥 Strain: 5.9 avg (0.1-9.0) ↓
```

Sample: `whoopskill insights`
```
💡 Insights & Recommendations

✅ Green Recovery
   Recovery at 85% — body is primed for high strain.
   → Great day for intense training or competition.

✅ HRV Above Baseline
   Today's HRV (39ms) is 21% above your 7-day average.
   → Excellent recovery. Good day for peak performance.

⚠️ Mild Sleep Debt
   You have 2.0 hours of sleep debt.
   → Consider an earlier bedtime tonight.

✅ Strain Capacity Available
   Current strain: 0.1. Optimal target: ~14.
   → Room for 13.9 more strain today.
```

Sample: `whoopskill --sleep --recovery` (JSON)
```json
{
  "date": "2026-01-05",
  "fetched_at": "2026-01-05T13:49:22.782Z",
  "body": {
    "height_meter": 1.83,
    "weight_kilogram": 82.5,
    "max_heart_rate": 182
  },
  "sleep": [
    {
      "id": "4c311bd4-370f-49ff-b58c-0578d543e9d2",
      "cycle_id": 1236731435,
      "user_id": 245199,
      "created_at": "2026-01-05T00:23:34.264Z",
      "updated_at": "2026-01-05T02:23:54.686Z",
      "start": "2026-01-04T19:51:57.280Z",
      "end": "2026-01-05T01:30:48.660Z",
      "timezone_offset": "+04:00",
      "nap": false,
      "score_state": "SCORED",
      "score": {
        "stage_summary": {
          "total_in_bed_time_milli": 20331380,
          "total_awake_time_milli": 4416000,
          "total_light_sleep_time_milli": 6968320,
          "total_slow_wave_sleep_time_milli": 4953060,
          "total_rem_sleep_time_milli": 3994000,
          "sleep_cycle_count": 4,
          "disturbance_count": 4
        },
        "sleep_needed": {
          "baseline_milli": 26783239,
          "need_from_sleep_debt_milli": 6637715,
          "need_from_recent_strain_milli": 148919
        },
        "respiratory_rate": 14.12,
        "sleep_performance_percentage": 40,
        "sleep_consistency_percentage": 60,
        "sleep_efficiency_percentage": 78.28
      }
    }
  ],
  "workout": [
    {
      "id": "4279883e-3d23-45cd-848c-3afa28dca3f8",
      "user_id": 245199,
      "start": "2026-01-05T03:14:13.417Z",
      "end": "2026-01-05T04:06:45.532Z",
      "sport_name": "hiit",
      "score_state": "SCORED",
      "score": {
        "strain": 6.19,
        "average_heart_rate": 108,
        "max_heart_rate": 144,
        "kilojoule": 819.38,
        "zone_durations": {
          "zone_zero_milli": 167000,
          "zone_one_milli": 1420000,
          "zone_two_milli": 1234980,
          "zone_three_milli": 330000,
          "zone_four_milli": 0,
          "zone_five_milli": 0
        }
      }
    }
  ],
  "profile": {
    "user_id": 245199,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "recovery": [
    {
      "cycle_id": 1236731435,
      "sleep_id": "4c311bd4-370f-49ff-b58c-0578d543e9d2",
      "user_id": 245199,
      "score_state": "SCORED",
      "score": {
        "recovery_score": 52,
        "resting_heart_rate": 60,
        "hrv_rmssd_milli": 38.87,
        "spo2_percentage": 96.4,
        "skin_temp_celsius": 33.19
      }
    }
  ],
  "cycle": [
    {
      "id": 1236731435,
      "user_id": 245199,
      "start": "2026-01-04T19:51:57.280Z",
      "end": null,
      "score_state": "SCORED",
      "score": {
        "strain": 6.66,
        "kilojoule": 6172.94,
        "average_heart_rate": 71,
        "max_heart_rate": 144
      }
    }
  ]
}
```
