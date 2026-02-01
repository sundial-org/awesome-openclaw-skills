# Scripts Reference

All scripts are TypeScript and run via `npx tsx`:

| Script | Purpose | Example |
|--------|---------|---------|
| `manage_habit.ts` | CRUD operations | `npx tsx scripts/manage_habit.ts create --name "Meditation"` |
| `log_habit.ts` | Record completions | `npx tsx scripts/log_habit.ts --habit-id h_123 --status completed` |
| `view_habits.ts` | Query habits | `npx tsx scripts/view_habits.ts --active --format markdown` |
| `calculate_streaks.ts` | Recalculate streaks | `npx tsx scripts/calculate_streaks.ts --habit-id h_123` |
| `get_stats.ts` | Generate statistics | `npx tsx scripts/get_stats.ts --habit-id h_123 --period 30` |
| `parse_natural_language.ts` | Parse user input | `npx tsx scripts/parse_natural_language.ts --text "I meditated"` |
| `sync_reminders.ts` | Sync to cron | `npx tsx scripts/sync_reminders.ts --sync-all` |
| `proactive_coaching.ts` | Coaching checks | `npx tsx scripts/proactive_coaching.ts --send` |
| `init_skill.ts` | Initial setup | `npx tsx scripts/init_skill.ts` |
| `check_cron_jobs.ts` | Verify cron status | `npx tsx scripts/check_cron_jobs.ts --auto-fix` |

## Detailed Command Options

### manage_habit.ts

**Create a habit:**
```bash
npx tsx scripts/manage_habit.ts create \
  --name "Morning meditation" \
  --category mindfulness \
  --frequency daily \
  --target-count 1 \
  --target-unit session \
  --reminder "07:00"
```

**Update a habit:**
```bash
npx tsx scripts/manage_habit.ts update \
  --habit-id h_abc123 \
  --name "Evening meditation" \
  --reminder "20:00"
```

**Archive a habit:**
```bash
npx tsx scripts/manage_habit.ts archive --habit-id h_abc123
```

### log_habit.ts

**Single day:**
```bash
npx tsx scripts/log_habit.ts \
  --habit-id h_abc123 \
  --date 2026-01-28 \
  --status completed
```

**Bulk logging:**
```bash
npx tsx scripts/log_habit.ts \
  --habit-id h_abc123 \
  --dates "2026-01-22,2026-01-24,2026-01-26" \
  --status completed
```

**With count and notes:**
```bash
npx tsx scripts/log_habit.ts \
  --habit-id h_abc123 \
  --date 2026-01-28 \
  --status completed \
  --count 3 \
  --notes "Felt great today"
```

**Status options:**
- `completed`: Target met or exceeded
- `partial`: Some progress but didn't meet target
- `missed`: No completion recorded
- `skipped`: Intentionally skipped (vacation, rest day)

### sync_reminders.ts

**Sync all reminders:**
```bash
npx tsx scripts/sync_reminders.ts --sync-all
```

**Add reminder for one habit:**
```bash
npx tsx scripts/sync_reminders.ts --habit-id h_abc123 --add
```

**Remove reminder:**
```bash
npx tsx scripts/sync_reminders.ts --habit-id h_abc123 --remove
```

**Sync coaching jobs:**
```bash
# Add/update all proactive coaching cron jobs
npx tsx scripts/sync_reminders.ts sync-coaching

# Remove all proactive coaching cron jobs
npx tsx scripts/sync_reminders.ts sync-coaching --remove
```

### proactive_coaching.ts

**Dry run - see what would be sent:**
```bash
npx tsx scripts/proactive_coaching.ts
```

**Check specific habit:**
```bash
npx tsx scripts/proactive_coaching.ts --habit-id h_abc123
```

**Actually send messages:**
```bash
npx tsx scripts/proactive_coaching.ts --send
```

**Check only milestones:**
```bash
npx tsx scripts/proactive_coaching.ts --check-milestones
```

**Check only risks:**
```bash
npx tsx scripts/proactive_coaching.ts --check-risks
```

**Generate weekly check-in:**
```bash
npx tsx scripts/proactive_coaching.ts --weekly-checkin
```

**Detect pattern insights:**
```bash
npx tsx scripts/proactive_coaching.ts --detect-insights
```

### Canvas Visualizations

**Streak chart:**
```bash
npx tsx assets/canvas-dashboard.ts streak \
  --habit-id h_abc123 \
  --theme light \
  --output ./streak.png
```

**Completion heatmap:**
```bash
npx tsx assets/canvas-dashboard.ts heatmap \
  --habit-id h_abc123 \
  --days 90 \
  --output ./heatmap.png
```

**Weekly trends:**
```bash
npx tsx assets/canvas-dashboard.ts trends \
  --habit-id h_abc123 \
  --weeks 8 \
  --output ./trends.png
```

**Multi-habit dashboard:**
```bash
npx tsx assets/canvas-dashboard.ts dashboard \
  --theme light \
  --output ./dashboard.png
```
