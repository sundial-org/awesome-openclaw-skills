---
name: snow-report
description: Get snow conditions, forecasts, and ski reports for any mountain resort worldwide. Use when asked about snow, powder, ski conditions, or mountain weather. Supports 1000+ resorts via OpenSnow. Users can set favorite mountains for quick access. Supports SnowTick 4-letter codes (JHMR, TARG, MMTH) for quick lookups.
---

# Snow Report

Fetch live snow conditions from OpenSnow for any ski resort worldwide.

## SnowTick — Mountain Tickers

4-letter codes for quick mountain lookups, like stock tickers:

| Ticker | Resort |
|--------|--------|
| `JHMR` | Jackson Hole |
| `TARG` | Grand Targhee |
| `MMTH` | Mammoth |
| `BIRD` | Snowbird |
| `ALTA` | Alta |
| `BOAT` | Steamboat |
| `WHIS` | Whistler |

Full list in `references/resorts.md`. Use tickers anywhere you'd use a resort name.

## Commands

| User Says | Action |
|-----------|--------|
| "snowtick" | Quick ticker tape of all favorites |
| "snow report" / "how's the snow" | Pull default mountain from user config |
| "snow at Mammoth" / "Jackson snow" | Pull specific resort |
| "JHMR" / "what's TARG at" | Pull by SnowTick code |
| "compare Jackson and Targhee" | Multi-mountain comparison |
| "compare JHMR TARG MMTH" | Compare by tickers |
| "powder alert" / "where's it snowing" | Check forecasts across favorites |

## User Configuration

Check `memory/snow-preferences.md` for user settings:

```markdown
# Snow Preferences

## Default Mountain
JHMR

## Favorites
- JHMR (Jackson Hole)
- TARG (Grand Targhee)
- MMTH (Mammoth)
- ALTA (Alta)

## Report Style
- compact (default) | detailed
- skip: parking
```

Tickers or slugs both work. If no config exists, ask user for their home mountain and create the file.

## Resolving Tickers

When user provides a ticker (4 uppercase letters):
1. Look up in `references/resorts.md`
2. Get the corresponding slug
3. Use slug for OpenSnow URL

Example: `JHMR` → `jacksonhole` → `opensnow.com/location/jacksonhole/snow-summary`

## Quick Usage

### SnowTick Command
```
1. Read user favorites from memory/snow-preferences.md
2. Open all favorite resort tabs in parallel
3. Snapshot each tab for snow data
4. Extract: base depth, 5-day forecast, current conditions
5. Format as ticker tape with best bet arrow
6. Close all tabs
```

### Single Mountain
```
1. browser action=open targetUrl=https://opensnow.com/location/{slug}/snow-summary
2. browser action=snapshot compact=true
3. Extract key data, close tab
```

### Multi-Mountain Comparison
```
1. Open all resort tabs in parallel (browser action=open for each)
2. Snapshot all tabs
3. Extract and format comparison table
4. Close all tabs
```

## Data Extraction

From OpenSnow snapshot, find:

### Snow Summary
- `Last 24 Hours` — reported snowfall + timestamp
- `Next 1-5 Days` — forecasted snow
- `Next 6-10 Days` — extended forecast
- `Next 11-15 Days` — long range

### Current Conditions (under "Right Now")
- Temperature + feels-like
- Wind speed, direction, gusts
- Conditions (Sunny, Snowy, etc.)

### Local Expert (Daily Snow)
- Expert name
- Forecast narrative

### AI Overview
- Quick conditions summary

## Output Formats

### SnowTick (favorites dashboard)
```
📈 SnowTick — {date}

JHMR  12"  ▲ 6"   ❄️ snowing
FISH   8"  ▲ 2"   ☀️ clear  
SGAR  24"  ▲ 12"  ❄️ snowing ←
BALD  36"  ▲ 8"   🌨️ flurries
BRDG   6"  ▲ 0"   ☀️ clear
ROCK   2"  — 0"   ☀️ clear

▲ = next 5 days | ← = best bet
```

Columns: Ticker | Base depth | 5-day forecast | Current conditions

### Compact (default)
```
🏔️ {Resort} [{TICK}] — {date}

**Snow:** {24hr}" | Next 5d: {forecast}"
**Now:** {temp}°F, {conditions}, wind {speed} mph
**Daily Snow:** {1 sentence summary}
```

### Detailed
```
🏔️ {Resort} [{TICK}] — {date}

**Now:** {temp}°F ({feels}°F), {conditions}, wind {speed} mph {dir}

| Period | Snow |
|--------|------|
| Last 24hr | X" |
| Next 5 days | X" |
| Next 6-10 days | X" |
| Next 11-15 days | X" |

**Daily Snow ({expert}):** {full summary}

**AI Overview:** {summary}
```

### Comparison Table
```
📊 Snow Comparison — {date}

| Ticker | Resort | 24hr | Next 5d | Next 10d | Temp |
|--------|--------|------|---------|----------|------|
| JHMR | Jackson Hole | 0" | 0" | 8" | 11°F |
| TARG | Grand Targhee | 0" | 2" | 12" | 8°F |
| ALTA | Alta | 0" | 1" | 6" | 15°F |

**Best Bet:** TARG — most snow coming
```

### Powder Alert
```
🚨 Powder Alert — {date}

Checking your favorites for incoming snow...

| Ticker | Resort | Next 5d | Next 10d |
|--------|--------|---------|----------|
| TARG | Grand Targhee | 6" | 18" | ← Best
| JHMR | Jackson Hole | 0" | 8" |
| ALTA | Alta | 2" | 10" |

**Verdict:** TARG looking best for next week
```

## Resort Slugs & SnowTick Codes

See `references/resorts.md` for full list with tickers.

**Quick reference:**
| Region | Tickers |
|--------|---------|
| Wyoming | `JHMR` `TARG` `SNWK` |
| Utah | `ALTA` `BIRD` `PCMR` `DEER` |
| Colorado | `VAIL` `AJAX` `TELL` `BOAT` |
| California | `MMTH` `PALI` `KIRK` `HVLY` |
| Montana | `BSKY` `FISH` `BRDG` |
| BC | `WHIS` `RVLK` |
| Japan | `NSKO` `HAKU` |

For unlisted resorts: search opensnow.com and grab slug from URL, then add ticker to references.

## First-Time Setup

If user asks for snow report with no config:

1. Ask: "What's your home mountain? I'll set it as your default."
2. Create `memory/snow-preferences.md` with their answer
3. Ask: "Any other favorites to add for comparisons?"
4. Pull their first report

## Notes

- OpenSnow is JS-rendered; browser required
- Data updates throughout day; morning reports freshest
- 11-15 day forecast may be paywalled (show what's visible)
- For resort-specific data (lifts, groomed runs), check resort's own site
