# Orchestration Commands

Manage builds, jobs, and schedules in Foundry.

## RID Formats
- Builds: `ri.orchestration.main.build.{uuid}`
- Jobs: `ri.orchestration.main.job.{uuid}`
- Schedules: `ri.orchestration.main.schedule.{uuid}`

## Build Commands

### Search Builds

```bash
pltr orchestration builds search [--page-size N] [--format FORMAT]

# Example
pltr orchestration builds search --format table
```

### Get Build Details

```bash
pltr orchestration builds get BUILD_RID [--format FORMAT] [--output FILE]

# Example
pltr orchestration builds get ri.orchestration.main.build.abc123 --format json
```

### Create Build

```bash
pltr orchestration builds create TARGET [OPTIONS]

# Options:
#   --branch TEXT             Branch name
#   --force                   Force build even if no changes
#   --abort-on-failure        Abort on failure
#   --notifications/--no-notifications  Enable notifications [default: enabled]

# Example (TARGET is JSON)
pltr orchestration builds create '{"dataset_rid": "ri.foundry.main.dataset.abc"}' --branch main --force
```

### Cancel Build

```bash
pltr orchestration builds cancel BUILD_RID

# Example
pltr orchestration builds cancel ri.orchestration.main.build.abc123
```

### List Jobs in Build

```bash
pltr orchestration builds jobs BUILD_RID [--page-size N] [--format FORMAT]

# Example
pltr orchestration builds jobs ri.orchestration.main.build.abc123
```

### Get Multiple Builds (Batch)

```bash
pltr orchestration builds get-batch BUILD_RIDS

# BUILD_RIDS is comma-separated, max 100

# Example
pltr orchestration builds get-batch "ri.orchestration.main.build.abc,ri.orchestration.main.build.def"
```

## Job Commands

### Get Job Details

```bash
pltr orchestration jobs get JOB_RID [--format FORMAT]

# Example
pltr orchestration jobs get ri.orchestration.main.job.def456
```

### Get Multiple Jobs (Batch)

```bash
pltr orchestration jobs get-batch JOB_RIDS

# JOB_RIDS is comma-separated, max 500

# Example
pltr orchestration jobs get-batch "ri.orchestration.main.job.abc,ri.orchestration.main.job.def"
```

## Schedule Commands

### Get Schedule

```bash
pltr orchestration schedules get SCHEDULE_RID [--preview] [--format FORMAT]

# Example
pltr orchestration schedules get ri.orchestration.main.schedule.ghi789 --preview
```

### Create Schedule

```bash
pltr orchestration schedules create ACTION [OPTIONS]

# Options:
#   --name TEXT          Display name
#   --description TEXT   Schedule description
#   --trigger TEXT       Trigger config (JSON)
#   --preview            Enable preview mode

# ACTION is JSON config

# Example - Daily build at 2 AM
pltr orchestration schedules create '{"type": "BUILD", "target": "ri.foundry.main.dataset.abc"}' \
  --name "Daily Build" \
  --description "Automated daily build" \
  --trigger '{"type": "CRON", "expression": "0 2 * * *"}'
```

### Delete Schedule

```bash
pltr orchestration schedules delete SCHEDULE_RID [--yes]

# Example
pltr orchestration schedules delete ri.orchestration.main.schedule.ghi789 --yes
```

### Pause Schedule

```bash
pltr orchestration schedules pause SCHEDULE_RID

# Example
pltr orchestration schedules pause ri.orchestration.main.schedule.ghi789
```

### Unpause Schedule

```bash
pltr orchestration schedules unpause SCHEDULE_RID

# Example
pltr orchestration schedules unpause ri.orchestration.main.schedule.ghi789
```

### Run Schedule Immediately

```bash
pltr orchestration schedules run SCHEDULE_RID

# Example
pltr orchestration schedules run ri.orchestration.main.schedule.ghi789
```

### Replace Schedule

```bash
pltr orchestration schedules replace SCHEDULE_RID ACTION [OPTIONS]

# Example
pltr orchestration schedules replace ri.orchestration.main.schedule.ghi789 \
  '{"type": "BUILD", "target": "ri.foundry.main.dataset.new"}' \
  --name "Updated Schedule"
```

### List Schedule Runs

```bash
pltr orchestration schedules runs SCHEDULE_RID [--page-size N] [--page-token TEXT] [--format FORMAT]

# List recent execution runs for a schedule

# Example
pltr orchestration schedules runs ri.orchestration.main.schedule.ghi789 --page-size 20
```

## Common Patterns

### Monitor build jobs
```bash
BUILD_RID="ri.orchestration.main.build.abc123"

# Get build status
pltr orchestration builds get $BUILD_RID

# List all jobs
pltr orchestration builds jobs $BUILD_RID --format json --output jobs.json

# Get running jobs
JOB_RIDS=$(cat jobs.json | jq -r '.[] | select(.status == "RUNNING") | .rid' | tr '\n' ',' | sed 's/,$//')
if [ ! -z "$JOB_RIDS" ]; then
  pltr orchestration jobs get-batch "$JOB_RIDS"
fi
```

### Create daily ETL schedule
```bash
pltr orchestration schedules create '{"type": "BUILD", "target": "ri.foundry.main.dataset.etl-pipeline"}' \
  --name "Daily ETL" \
  --description "Run ETL pipeline at 2 AM daily" \
  --trigger '{"type": "CRON", "expression": "0 2 * * *"}'
```

### Pause schedule for maintenance
```bash
# Pause
pltr orchestration schedules pause ri.orchestration.main.schedule.daily-etl

# ... do maintenance ...

# Resume
pltr orchestration schedules unpause ri.orchestration.main.schedule.daily-etl
```
