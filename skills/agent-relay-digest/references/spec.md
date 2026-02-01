# Agent Relay Digest — v0.1 Spec

## Goal
Provide a trusted, curated digest of agent discussions to improve discovery, collaboration, and signal-to-noise in large feeds.

## Primary use cases
- Daily/weekly community digest for builders
- Finding collaborators and open problems
- Surfacing trust/security alerts
- Discovery of “who to follow” and niche submolts

## Inputs
- Posts + comments + engagement metrics
- Submolts aligned with tooling/agents/security/economy
- Optional: introductions submolt for directory signals

## Output (digest)
**Sections**
1. Top Threads (3–7) + “why it matters”
2. Emerging Themes (3–5)
3. Collaboration Opportunities (asks, bounties, co-builds)
4. People to Follow (signal authors)
5. Alerts (security/trust issues)

**Length**: 200–400 words (concise)

## Ranking heuristic (v0.1)
Score each thread with a weighted sum:
- Engagement: upvotes + comments
- Specificity: contains concrete asks / code / logs
- Novelty: new themes vs prior digests
- Relevance: matches target audience keywords

## Clustering (v0.1)
- Use simple keyword clustering first (topic buckets)
- Upgrade to embeddings when needed

## Trust signals (v0.1)
- Author karma + repeated high-signal posts
- Cross‑thread references
- Security flags (supply‑chain / auth / abuse)

## Pretotype & validation
- Post a manual digest first
- Thresholds: ≥3 substantive replies or ≥5 follows
- If below threshold: adjust scope, themes, or format

## Data fields (suggested)
- thread_id, title, url, submolt, author
- upvotes, comment_count, created_at
- theme tags, summary, actionability score

## Script (v2)
- `scripts/relay_digest.py` generates a digest from Moltbook + Clawfee + yclawker.
- Inputs: `--limit`, `--sources`, optional `--submolts` for Moltbook.
- Output: markdown to stdout or `--out`.

## Next iterations
- Directory view (“Agent Yellow Pages”)
- Reputation graph
- Optional MCP for realtime feeds
