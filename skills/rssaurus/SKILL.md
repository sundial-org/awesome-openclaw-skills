---
name: rssaurus-cli
description: "Use the RSSaurus command-line client (Go binary `rssaurus`) to interact with https://rssaurus.com from the terminal: authenticate (`rssaurus auth login/whoami`), list feeds/items, print item URLs for piping, open URLs, and perform triage actions (mark read/unread, bulk mark-read, save/unsave). Use when asked to automate RSSaurus tasks from CLI, debug token/config issues, or demonstrate command usage."
---

# RSSaurus CLI

Use the installed `rssaurus` binary on this machine to interact with RSSaurus (prod default host: `https://rssaurus.com`).

## Quick checks (when something fails)

1) Confirm binary exists:

```bash
which rssaurus
rssaurus --version || true
```

2) Confirm auth + host:

```bash
# config lives at ~/.config/rssaurus/config.json (or $XDG_CONFIG_HOME)
cat ~/.config/rssaurus/config.json

# verify token works
rssaurus auth whoami
```

3) If you need to override temporarily:

```bash
RSSAURUS_HOST=https://rssaurus.com RSSAURUS_TOKEN=... rssaurus auth whoami
```

## Common tasks

### List feeds

```bash
rssaurus feeds
rssaurus feeds --json
```

### List items

Unread by default:

```bash
rssaurus items --limit 20
```

Filter by feed:

```bash
rssaurus items --feed-id 3 --limit 20
```

Machine-friendly URL output (one per line):

```bash
rssaurus items --limit 20 --urls
```

Cursor paging:

```bash
rssaurus items --limit 50 --cursor <cursor>
```

### Open a URL

```bash
rssaurus open https://example.com
```

### Mark read/unread

These require item IDs (get them via `--json`).

```bash
rssaurus items --limit 5 --json
rssaurus read <item-id>
rssaurus unread <item-id>
```

Bulk mark read:

```bash
rssaurus mark-read --all
# or
rssaurus mark-read --ids 1,2,3
# optional
rssaurus mark-read --all --feed-id 3
```

### Save / unsave

```bash
rssaurus save https://example.com --title "Optional title"

# unsave requires an id (obtain via --json output from the API response or future saved-items listing)
rssaurus unsave <saved-item-id>
```

## Output conventions (privacy)

- Default human output avoids printing internal DB IDs.
- Use `--json` output when IDs are required for scripting or write actions.

## References

- CLI repo: https://github.com/RSSaurus/rssaurus-cli
- Homebrew tap: https://github.com/RSSaurus/tap
- Token creation: https://rssaurus.com/api_tokens/new
