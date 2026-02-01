---
name: bitcoin-daily
description: Daily digest of the Bitcoin Development mailing list and Bitcoin Core commits. Use when asked about recent bitcoin-dev discussions, mailing list activity, Bitcoin Core code changes, or to set up daily summaries. Fetches threads from groups.google.com/g/bitcoindev and commits from github.com/bitcoin/bitcoin.
metadata: {"clawdbot":{"emoji":"📰"}}
---

# Bitcoin Dev Digest (📰)

![Bitcoin Daily](https://files.catbox.moe/v0zvnj.png)

Daily summary of bitcoindev mailing list + Bitcoin Core commits.

*Made in 🤠 Texas ❤️ [PlebLab](https://pleblab.dev)*

## Commands

Run via: `node ~/workspace/skills/bitcoin-daily/scripts/digest.js <command>`

| Command | Description |
|---------|-------------|
| `digest [YYYY-MM-DD]` | Fetch & summarize (default: yesterday) |
| `archive` | List all archived digests |
| `read <YYYY-MM-DD>` | Read a past summary |

## Output

The digest script fetches raw data. The agent then summarizes it for the user in this format:

**Mailing list:** Numbered list, each item with:
- **Bold title** — 1-2 sentence ELI10 explanation with a touch of dry humor
- Thread link

**Commits:** Bullet list of notable merges with PR links.

Keep summaries accessible — explain like the reader is smart but not a Bitcoin Core contributor. Dry humor welcome, not forced.

## Archive

Raw data archived to `~/workspace/bitcoin-dev-archive/YYYY-MM-DD/`:
- `mailing-list/*.json` — full thread content per topic
- `mailing-list/_index.json` — thread index
- `commits.json` — raw commit data
- `summary.md` — generated summary

## Daily Cron

Set up via Clawdbot cron to run every morning. The digest script fetches, archives, and outputs a summary that the agent then sends to the user.

## Sources

- Mailing list: https://groups.google.com/g/bitcoindev
- Bitcoin Core: https://github.com/bitcoin/bitcoin/commits/master/
