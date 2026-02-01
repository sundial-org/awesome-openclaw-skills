# Streams Commands

Commands for managing streaming datasets and publishing real-time data records to Foundry.

## Dataset and Stream RID Formats
- **Dataset**: `ri.foundry.main.dataset.{uuid}`
- **Folder**: `ri.compass.main.folder.{uuid}`

## Dataset Commands

### Create Streaming Dataset

Create a new streaming dataset with an initial stream.

```bash
pltr streams dataset create NAME --folder FOLDER_RID --schema SCHEMA [OPTIONS]

# Options:
#   --folder, -f TEXT       Parent folder RID (required)
#   --schema, -s TEXT       Stream schema as JSON or @file.json (required)
#   --branch, -b TEXT       Branch name [default: master]
#   --compressed            Enable compression
#   --partitions INTEGER    Number of partitions [default: 1]
#   --type TEXT             Stream type: HIGH_THROUGHPUT or LOW_LATENCY [default: LOW_LATENCY]
#   --preview               Enable preview mode
#   --format TEXT           Output format (table, json, csv)
#   --profile, -p TEXT      Profile name

# Examples

# Create basic streaming dataset
pltr streams dataset create my-stream \
    --folder ri.compass.main.folder.xxx \
    --schema '{"fieldSchemaList": [{"name": "value", "type": "STRING"}]}'

# Create from schema file with high throughput
pltr streams dataset create sensor-data \
    --folder ri.compass.main.folder.xxx \
    --schema @schema.json \
    --partitions 5 \
    --type HIGH_THROUGHPUT

# With specific branch
pltr streams dataset create my-stream \
    --folder ri.compass.main.folder.xxx \
    --schema @schema.json \
    --branch develop
```

## Stream Commands

### Create Stream

Create a new stream on a branch of an existing streaming dataset.

```bash
pltr streams stream create DATASET_RID --branch BRANCH --schema SCHEMA [OPTIONS]

# Options:
#   --branch, -b TEXT       Branch name to create stream on (required)
#   --schema, -s TEXT       Stream schema as JSON or @file.json (required)
#   --compressed            Enable compression
#   --partitions INTEGER    Number of partitions [default: 1]
#   --type TEXT             Stream type: HIGH_THROUGHPUT or LOW_LATENCY
#   --preview               Enable preview mode
#   --format TEXT           Output format (table, json, csv)
#   --profile, -p TEXT      Profile name

# Examples

# Create stream on new branch
pltr streams stream create ri.foundry.main.dataset.xxx \
    --branch feature-branch \
    --schema '{"fieldSchemaList": [{"name": "id", "type": "INTEGER"}]}'

# High-throughput stream with multiple partitions
pltr streams stream create ri.foundry.main.dataset.xxx \
    --branch production \
    --schema @schema.json \
    --partitions 10 \
    --type HIGH_THROUGHPUT
```

### Get Stream

Get information about a stream.

```bash
pltr streams stream get DATASET_RID --branch BRANCH [OPTIONS]

# Options:
#   --branch, -b TEXT       Stream branch name (required)
#   --preview               Enable preview mode
#   --format TEXT           Output format (table, json, csv)
#   --profile, -p TEXT      Profile name

# Examples

# Get stream on master branch
pltr streams stream get ri.foundry.main.dataset.xxx --branch master

# Get stream as JSON
pltr streams stream get ri.foundry.main.dataset.xxx \
    --branch feature-branch \
    --format json
```

### Publish Single Record

Publish a single record to a stream.

```bash
pltr streams stream publish DATASET_RID --branch BRANCH --record RECORD [OPTIONS]

# Options:
#   --branch, -b TEXT       Stream branch name (required)
#   --record, -r TEXT       Record data as JSON or @file.json (required)
#   --view TEXT             View RID for partitioning
#   --preview               Enable preview mode
#   --profile, -p TEXT      Profile name

# Examples

# Publish inline record
pltr streams stream publish ri.foundry.main.dataset.xxx \
    --branch master \
    --record '{"id": 123, "name": "test", "timestamp": 1234567890}'

# Publish from file
pltr streams stream publish ri.foundry.main.dataset.xxx \
    --branch master \
    --record @record.json
```

### Publish Batch Records

Publish multiple records to a stream in a batch (more efficient than individual publishes).

```bash
pltr streams stream publish-batch DATASET_RID --branch BRANCH --records RECORDS [OPTIONS]

# Options:
#   --branch, -b TEXT       Stream branch name (required)
#   --records, -r TEXT      Records as JSON array or @file.json (required)
#   --view TEXT             View RID for partitioning
#   --preview               Enable preview mode
#   --profile, -p TEXT      Profile name

# Examples

# Publish multiple records inline
pltr streams stream publish-batch ri.foundry.main.dataset.xxx \
    --branch master \
    --records '[{"id": 1, "name": "alice"}, {"id": 2, "name": "bob"}]'

# Publish from file
pltr streams stream publish-batch ri.foundry.main.dataset.xxx \
    --branch master \
    --records @records.json
```

### Reset Stream

Reset a stream, clearing all existing data. **Warning: This is irreversible!**

```bash
pltr streams stream reset DATASET_RID --branch BRANCH [OPTIONS]

# Options:
#   --branch, -b TEXT       Stream branch name to reset (required)
#   --confirm               Skip confirmation prompt
#   --preview               Enable preview mode
#   --format TEXT           Output format (table, json, csv)
#   --profile, -p TEXT      Profile name

# Examples

# Reset with confirmation prompt
pltr streams stream reset ri.foundry.main.dataset.xxx --branch master

# Skip confirmation (use with caution)
pltr streams stream reset ri.foundry.main.dataset.xxx \
    --branch master \
    --confirm
```

## Schema Format

The schema uses `fieldSchemaList` to define record structure:

```json
{
  "fieldSchemaList": [
    {"name": "id", "type": "INTEGER"},
    {"name": "name", "type": "STRING"},
    {"name": "value", "type": "DOUBLE"},
    {"name": "active", "type": "BOOLEAN"},
    {"name": "timestamp", "type": "TIMESTAMP"}
  ]
}
```

### Supported Field Types
- `STRING` - Text data
- `INTEGER` - 32-bit integer
- `LONG` - 64-bit integer
- `DOUBLE` - Floating-point number
- `BOOLEAN` - True/false
- `TIMESTAMP` - Unix timestamp
- `DATE` - Date value
- `BINARY` - Binary data

## Stream Types

| Type | Description | Use Case |
|------|-------------|----------|
| `LOW_LATENCY` | Optimized for real-time processing | Interactive dashboards, alerts |
| `HIGH_THROUGHPUT` | Optimized for volume | Batch ingestion, sensor data |

## Partitioning

- Each partition handles approximately **5 MB/s** of throughput
- Increase partitions for higher data volumes
- Default is 1 partition

```bash
# High-volume stream with 10 partitions
pltr streams dataset create high-volume-stream \
    --folder ri.compass.main.folder.xxx \
    --schema @schema.json \
    --partitions 10 \
    --type HIGH_THROUGHPUT
```

## Common Patterns

### Create and Populate a Stream

```bash
# 1. Create the streaming dataset
pltr streams dataset create events \
    --folder ri.compass.main.folder.xxx \
    --schema '{"fieldSchemaList": [{"name": "event_id", "type": "STRING"}, {"name": "timestamp", "type": "TIMESTAMP"}, {"name": "data", "type": "STRING"}]}'

# 2. Publish initial records
pltr streams stream publish-batch ri.foundry.main.dataset.xxx \
    --branch master \
    --records @initial-events.json
```

### Continuous Data Ingestion Script

```bash
#!/bin/bash
DATASET_RID="ri.foundry.main.dataset.xxx"
BRANCH="master"

while true; do
    # Generate or fetch new records
    RECORD='{"id": '$RANDOM', "timestamp": '$(date +%s)', "value": '$RANDOM'}'

    pltr streams stream publish "$DATASET_RID" \
        --branch "$BRANCH" \
        --record "$RECORD"

    sleep 1
done
```
