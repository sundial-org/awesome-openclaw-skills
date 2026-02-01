---
name: recgov-availability
description: Check campsite availability on recreation.gov for federal campgrounds (National Parks, USFS, BLM). Requires campground ID(s) — get from ridb-search or recreation.gov URLs.
---

# Recreation.gov Availability Checker

Check campsite availability for federal campgrounds on recreation.gov.

## Quick Start

```bash
cd /Users/doop/moltbot/skills/recgov-availability

# Check availability (campground ID from URL or ridb-search)
python3 scripts/check.py -c 233965 --start 2026-07-10 --nights 2

# Multiple campgrounds
python3 scripts/check.py -c 233965 233900 --start 2026-07-10 --nights 2

# Filter to tent sites, JSON output
python3 scripts/check.py -c 233965 --start 2026-07-10 --nights 2 --type tent --json
```

## Finding Campground IDs

From URL: `recreation.gov/camping/campgrounds/233965` → ID is `233965`

Or use ridb-search:
```bash
python3 ../ridb-search/scripts/search.py -l "Newport, OR" --camping-only
```

## Options

| Option | Description |
|--------|-------------|
| `-c, --campground` | Campground ID(s) to check (required) |
| `-s, --start` | Start date YYYY-MM-DD (required) |
| `-n, --nights` | Consecutive nights needed (default: 1) |
| `-t, --type` | Site type: tent, rv, standard, cabin, group |
| `--electric` | Electric sites only |
| `--nonelectric` | Non-electric sites only |
| `--include-group` | Include group sites |
| `--pets` | Pet-friendly only (slower) |
| `--shade` | Shaded sites only (slower) |
| `--fire-pit` | Sites with fire pits (slower) |
| `--vehicle-length N` | Min vehicle length in feet (slower) |
| `--show-sites` | Show individual sites |
| `--json` | JSON output |

## Status Meanings

| Status | Meaning |
|--------|---------|
| ✅ Available | Book now |
| ❌ Reserved | Already booked |
| ⏳ NYR | Not Yet Released — reservations not open |
| 🚗 FCFS | First-come-first-served (no reservations) |

## Coverage

- National Park Service campgrounds
- USDA Forest Service campgrounds
- BLM recreation sites
- Army Corps of Engineers areas

For state parks, use `reserveamerica`.

## Notes

- No API key needed
- Python 3.8+ (stdlib only)
- Amenity filters (--pets, --shade) require extra API calls
- Booking window is typically 6 months ahead

See README.md for full documentation.
