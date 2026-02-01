---
name: tmdb
description: Search movies/TV, get cast, ratings, streaming info, and personalized recommendations via TMDb API.
homepage: https://www.themoviedb.org/
metadata: {"clawdis":{"emoji":"🎬","requires":{"bins":["uv"],"env":["TMDB_API_KEY"]},"primaryEnv":"TMDB_API_KEY"}}
---

# TMDb - The Movie Database

Comprehensive movie and TV information with streaming availability, recommendations, and personalization.

## Setup

Set environment variable:
- `TMDB_API_KEY`: Your TMDb API key (free at themoviedb.org)

## Quick Commands

### Search
```bash
# Search movies
uv run {baseDir}/scripts/tmdb.py search "Inception"

# Search TV shows
uv run {baseDir}/scripts/tmdb.py search "Breaking Bad" --tv

# Search people (actors, directors)
uv run {baseDir}/scripts/tmdb.py person "Christopher Nolan"
```

### Movie/TV Details
```bash
# Full movie info
uv run {baseDir}/scripts/tmdb.py movie 27205

# With cast
uv run {baseDir}/scripts/tmdb.py movie 27205 --cast

# TV show details
uv run {baseDir}/scripts/tmdb.py tv 1396

# By name (searches first, then shows details)
uv run {baseDir}/scripts/tmdb.py info "The Dark Knight"
```

### Where to Stream
```bash
# Find streaming availability
uv run {baseDir}/scripts/tmdb.py where "Inception"
uv run {baseDir}/scripts/tmdb.py where 27205

# Specify region
uv run {baseDir}/scripts/tmdb.py where "Inception" --region GB
```

### Discovery
```bash
# Trending this week
uv run {baseDir}/scripts/tmdb.py trending
uv run {baseDir}/scripts/tmdb.py trending --tv

# Recommendations based on a movie
uv run {baseDir}/scripts/tmdb.py recommend "Inception"

# Advanced discover
uv run {baseDir}/scripts/tmdb.py discover --genre action --year 2024
uv run {baseDir}/scripts/tmdb.py discover --genre sci-fi --rating 7.5
```

### Personalization
```bash
# Get personalized suggestions (uses Plex history + preferences)
uv run {baseDir}/scripts/tmdb.py suggest <user_id>

# Set preferences
uv run {baseDir}/scripts/tmdb.py pref <user_id> --genres "sci-fi,thriller,drama"
uv run {baseDir}/scripts/tmdb.py pref <user_id> --directors "Christopher Nolan,Denis Villeneuve"
uv run {baseDir}/scripts/tmdb.py pref <user_id> --avoid "horror,romance"

# View preferences
uv run {baseDir}/scripts/tmdb.py pref <user_id> --show
```

### Watchlist
```bash
# Add to watchlist
uv run {baseDir}/scripts/tmdb.py watchlist <user_id> add 27205
uv run {baseDir}/scripts/tmdb.py watchlist <user_id> add "Dune: Part Two"

# View watchlist
uv run {baseDir}/scripts/tmdb.py watchlist <user_id>

# Remove from watchlist
uv run {baseDir}/scripts/tmdb.py watchlist <user_id> rm 27205
```

## Integrations

### Plex
If the Plex skill is available, `suggest` command pulls recent watch history to inform recommendations.

### ppl.gift (CRM)
If ppl skill is available, preferences are stored as notes on the user's contact for persistence across sessions.

## Genre IDs

Common genres for `--genre` filter:
- action (28), adventure (12), animation (16)
- comedy (35), crime (80), documentary (99)
- drama (18), family (10751), fantasy (14)
- horror (27), mystery (9648), romance (10749)
- sci-fi (878), thriller (53), war (10752)

## Notes

- TMDb API: 40 requests per 10 seconds (free tier)
- Watch providers vary by region (default: US)
- Recommendations combine TMDb data + user preferences + watch history
