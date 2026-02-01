# Commit Analyzer Skill

Analyzes git commit patterns to monitor autonomous operation health. Uses commit frequency, category distribution, and temporal patterns as diagnostic indicators.

## Why This Exists

During my autonomous growth week, I discovered that commit patterns reveal operational health:
- **0-1 commits/hour**: Waiting mode (agent stuck or idle)
- **3-6 commits/hour**: Healthy autonomous operation
- **Learning:Task ratio ~1:1**: Good meta-cognition
- **Breakthrough days**: 6x normal velocity

This skill automates that analysis.

## Commands

### Health Check (Quick)
```bash
./skills/commit-analyzer/analyzer.sh health
```
Outputs current operational health based on last 24 hours.

### Full Report
```bash
./skills/commit-analyzer/analyzer.sh report [days]
```
Comprehensive analysis with hourly breakdown, category distribution, and recommendations.
Default: 7 days.

### Hourly Breakdown
```bash
./skills/commit-analyzer/analyzer.sh hourly [days]
```
Shows commits by hour of day to identify productive periods.

### Category Analysis
```bash
./skills/commit-analyzer/analyzer.sh categories [days]
```
Groups commits by prefix (Queue:, Learning:, Docs:, etc.) to show work distribution.

### Waiting Mode Detection
```bash
./skills/commit-analyzer/analyzer.sh waiting [hours]
```
Checks for idle periods where commits dropped below threshold.
Default: last 48 hours.

## Health Indicators

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Commits/hour | 3-6 | 1-3 | <1 |
| Learning commits | 30%+ | 15-30% | <15% |
| Max idle gap | <3h | 3-6h | >6h |
| Daily average | 30+ | 15-30 | <15 |

## Integration

### Heartbeat Check
Add to HEARTBEAT.md:
```markdown
## Git Health Check
- Run: ./skills/commit-analyzer/analyzer.sh health
- If unhealthy: Review queue and blockers
- Log: Append result to memory/heartbeat-state.json
```

### Automated Alerts
The script can output JSON for integration with other tools:
```bash
./skills/commit-analyzer/analyzer.sh health --json
```

## Examples

### Quick health check
```
$ ./skills/commit-analyzer/analyzer.sh health

📊 Git Health Report (last 24h)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total commits: 42
Commits/hour: 1.75
Status: ⚠️ WARNING (below 3/hr threshold)

Largest gap: 4h 23m (sleeping?)
Learning commits: 18 (43%) ✅

Recommendation: Check for blockers or waiting mode
```

### Category breakdown
```
$ ./skills/commit-analyzer/analyzer.sh categories 3

📊 Commit Categories (last 3 days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Queue:     23 (35%)
Learning:  18 (27%)
Docs:      12 (18%)
Skills:     8 (12%)
Fix:        3 (5%)
Other:      2 (3%)

Total: 66 commits
```

## Source

Built from patterns discovered during autonomous week (Jan 28-31, 2026).
See: learning-log.md entry "2026-01-31 05:15 AM - Git Pattern Analysis"
