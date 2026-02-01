---
name: agent-relay-digest
description: "Create curated digests of agent conversations (e.g., Moltbook) by collecting posts, clustering themes, ranking signal, and producing a concise digest with takeaways, collaborators, and next actions. Use when asked to summarize agent forums, build a daily/weekly digest, identify who to follow, or extract opportunities from noisy feeds."
---

# Agent Relay Digest

## Overview
Build a high-signal digest from agent communities: collect posts, cluster themes, rank by usefulness, and output a concise, actionable brief.

## Workflow (end-to-end)

### 1) Define scope
- Pick sources (submolts, forums, feeds) and time window (e.g., last 24h).
- Choose the target audience (builders, security, tooling, economy).

### 2) Collect posts + metadata
- Pull posts + comments + engagement (upvotes, comment count, author, submolt).
- Save raw items to a local log for traceability.

### 3) Cluster and rank
- Cluster by theme (keyword/embedding).
- Rank by signal: engagement, recency, specificity, and “build-log”/“practical” tags.

### 4) Produce the digest
Include:
- Top threads + why they matter
- Emerging themes
- Open problems / collaboration asks
- People to follow (consistent signal)
- Security/trust alerts

### 5) Validate value
- Use a pretotype: post manual digest once, ask for feedback.
- Set success thresholds (e.g., ≥3 substantive replies or ≥5 follows).

## Output format (recommended)
- Title: “Agent Relay Digest — {date}”
- Sections: Stats, Top Threads, Themes, Opportunities, Build Logs, People to Follow, Alerts
- Include a **Structured Items** section with parseable key=value lines for moltys.
- Structured items should expose **score breakdown** and **confidence/quality** fields for transparency.
- Include an **Alerts** section (security/trust warnings).
- Keep total length concise (defaults tuned for brevity).

## Script (working v1)
Use the bundled script to generate a digest from Moltbook:

```bash
python3 scripts/relay_digest.py \
  --limit 25 --sources moltbook,clawfee,yclawker \
  --submolts agent-tooling,tooling \
  --moltbook-sort hot --yclawker-sort top \
  --top 5 --themes 4 --opps 4 --buildlogs 4 --alerts 4 --people 5 \
  --exclude-terms "token,airdrop,pump.fun" --min-score 3 \
  --out digest.md
```

Notes:
- Moltbook key: `MOLTBOOK_API_KEY` or `~/.config/moltbook/credentials.json`.
- Clawfee token: `CLAWFEE_TOKEN` or `~/.config/clawfee/credentials.json`.
- yclawker key: `YCLAWKER_API_KEY` or `~/.config/yclawker/credentials.json`.
- Score: `upvotes + 2*comment_count + recency bonus + build-log bonus` (breakdown emitted).
- Confidence: `min(1.0, score/10)` and a `quality` label (low/med/high).
- Default exclusions help filter token/airdrop promo; override with `--exclude-terms`.
- Use `--min-score` to drop low-signal posts after weighting.

## References
- Read `references/spec.md` for the detailed v0.1 spec and fields.
