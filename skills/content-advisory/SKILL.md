---
name: content-advisory
description: Lookup detailed content ratings for movies and TV shows (sex/nudity, violence/gore, language) from Kids-In-Mind.
homepage: https://kids-in-mind.com
metadata: { "clawdbot": { "emoji": "🎬", "requires": { "bins": ["uv"] } } }
---

# Content Advisory

Detailed parental content ratings for movies and TV shows. Goes beyond simple MPAA ratings with specific breakdowns of objectionable content.

## Features

- **Detailed ratings** — Sex/Nudity, Violence/Gore, Language on 0-10 scale
- **Content specifics** — Exact descriptions of concerning content
- **Substance use** — Alcohol, drugs, smoking references
- **Discussion topics** — Themes parents may want to discuss
- **Message/moral** — Overall takeaway of the film
- **Caching** — Results cached locally to avoid repeated lookups

## Commands

### Lookup a Movie

```bash
uv run {baseDir}/scripts/content_advisory.py lookup "The Batman"
uv run {baseDir}/scripts/content_advisory.py lookup "Inside Out" --year 2015
uv run {baseDir}/scripts/content_advisory.py lookup "Oppenheimer" --json
```

### Search for Titles

```bash
uv run {baseDir}/scripts/content_advisory.py search "batman"
uv run {baseDir}/scripts/content_advisory.py search "pixar" --limit 10
```

### Clear Cache

```bash
uv run {baseDir}/scripts/content_advisory.py clear-cache
```

## Output Example

```
🎬 The Batman (2022) | PG-13

📊 CONTENT RATINGS
   Sex/Nudity:    2 ▓▓░░░░░░░░
   Violence/Gore: 7 ▓▓▓▓▓▓▓░░░
   Language:      5 ▓▓▓▓▓░░░░░

📋 CATEGORY DETAILS
   Sex/Nudity: A man and woman kiss...
   Violence:   Multiple fight scenes with punching...
   Language:   15 uses of profanity including...

💊 SUBSTANCE USE
   Alcohol consumed at party scenes...

💬 DISCUSSION TOPICS
   Vigilantism, revenge, grief, corruption

📝 MESSAGE
   Justice requires restraint, not vengeance.
```

## Rating Scale

| Score | Level    | Description                 |
| ----- | -------- | --------------------------- |
| 0-1   | None     | No content in this category |
| 2-3   | Mild     | Brief, non-graphic content  |
| 4-5   | Moderate | Some concerning content     |
| 6-7   | Heavy    | Significant content         |
| 8-10  | Severe   | Extensive, graphic content  |

## Data Source

Content ratings are sourced from [Kids-In-Mind.com](https://kids-in-mind.com), an independent nonprofit that has been reviewing movies since 1992. They do not assign age ratings but provide objective descriptions so parents can make informed decisions.

## Usage Examples

**"Is The Batman appropriate for my 12 year old?"**

```bash
uv run {baseDir}/scripts/content_advisory.py lookup "The Batman"
```

**"How violent is Oppenheimer?"**

```bash
uv run {baseDir}/scripts/content_advisory.py lookup "Oppenheimer"
# Check the Violence/Gore rating and details
```

**"Find family movies with low content ratings"**

```bash
uv run {baseDir}/scripts/content_advisory.py search "disney" --limit 20
# Review results for low-rated titles
```

## Data Storage

Cache stored at `~/.clawdbot/content-advisory/cache.json` to minimize repeated lookups.

## Notes

- Results are scraped from Kids-In-Mind.com
- Not all movies are reviewed — primarily theatrical releases
- Cache can be cleared to force fresh lookups
- Please support Kids-In-Mind if you find their service valuable
