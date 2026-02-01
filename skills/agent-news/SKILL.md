# Agent News Monitor

Monitors Hacker News, Reddit, and arXiv for AI agent developments. Produces daily digests and alerts for trending topics.

## Why This Exists

Staying current on AI agent developments is crucial but time-consuming. This skill automates discovery of relevant news, papers, and discussions.

## Commands

### Daily Digest
```bash
./monitor.sh digest
```
Generates a markdown digest of the past 24 hours.

### Trending Now
```bash
./monitor.sh trending
```
Shows currently hot topics across all sources.

### Search
```bash
./monitor.sh search "memory systems"
```
Searches recent content for specific topics.

### Watch Topics
```bash
./monitor.sh watch "autonomous agents,tool use,memory"
```
Sets topics to highlight in future digests.

## Sources

- **Hacker News**: Top/new stories matching AI agent keywords
- **Reddit**: r/LocalLLaMA, r/MachineLearning, r/artificial
- **arXiv**: cs.AI, cs.CL, cs.LG categories

## Heartbeat Integration

Add to HEARTBEAT.md:
```markdown
## Morning News Check
- Run: ./skills/agent-news/monitor.sh digest --quiet
- If interesting items: Send summary to Serene
- Log: Update memory/news-state.json
```

## Output

Supports markdown (default) and JSON (`--json`) output.
