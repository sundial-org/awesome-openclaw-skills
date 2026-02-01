# Connectivity Commands

Manage connections and data imports from external systems.

## Connection Commands

### List Connections

```bash
pltr connectivity connection list [--format FORMAT] [--output FILE]

# Example
pltr connectivity connection list --format json --output connections.json
```

### Get Connection Details

```bash
pltr connectivity connection get CONNECTION_RID [--format FORMAT]

# Example
pltr connectivity connection get ri.conn.main.connection.12345
```

### Create Connection

```bash
pltr connectivity connection create DISPLAY_NAME PARENT_FOLDER_RID [CONFIGURATION] [WORKER] [OPTIONS]

# Options:
#   --config-file TEXT    Path to JSON file with connection configuration
#   --worker-file TEXT    Path to JSON file with worker configuration

# Examples
pltr connectivity connection create "My Database" ri.compass.main.folder.xyz123 \
  '{"type": "jdbc"}' '{"workerType": "default"}'

# Using config files
pltr connectivity connection create "My Database" ri.compass.main.folder.xyz123 \
  --config-file connection-config.json --worker-file worker-config.json
```

### Get Connection Configuration

```bash
pltr connectivity connection get-config CONNECTION_RID [--format FORMAT]

# Example
pltr connectivity connection get-config ri.conn.main.connection.12345 --format json
```

### Update Connection Secrets

```bash
pltr connectivity connection update-secrets CONNECTION_RID --secrets-file FILE

# Secrets must be provided via file for security (avoids shell history exposure)

# Example (secrets.json: {"password": "secret123", "api_key": "abc..."})
pltr connectivity connection update-secrets ri.conn.main.connection.12345 \
  --secrets-file secrets.json
```

### Update Export Settings

```bash
pltr connectivity connection update-export-settings CONNECTION_RID [SETTINGS] [OPTIONS]

# Options:
#   --settings-file TEXT    Path to JSON file with export settings

# Examples
pltr connectivity connection update-export-settings ri.conn.main.connection.12345 \
  '{"enabled": true, "format": "parquet"}'

# Using settings file
pltr connectivity connection update-export-settings ri.conn.main.connection.12345 \
  --settings-file export-settings.json
```

### Upload JDBC Drivers

```bash
pltr connectivity connection upload-jdbc-drivers CONNECTION_RID DRIVER_FILES...

# Upload custom JAR files for JDBC connections

# Example
pltr connectivity connection upload-jdbc-drivers ri.conn.main.connection.12345 \
  driver.jar custom-driver-v2.jar
```

## File Import Commands

### Create File Import

```bash
pltr connectivity import file CONNECTION_RID SOURCE_PATH TARGET_DATASET_RID [OPTIONS]

# Options:
#   --config, -c TEXT    Import config (JSON)
#   --execute            Execute immediately after creation

# Examples
pltr connectivity import file ri.conn.main.connection.123 "/data/sales.csv" ri.foundry.main.dataset.456

pltr connectivity import file ri.conn.main.connection.123 "/data/sales.csv" ri.foundry.main.dataset.456 \
  --config '{"format": "CSV", "delimiter": ",", "header": true}' \
  --execute
```

### List File Imports

```bash
pltr connectivity import list-file [--connection CONNECTION_RID] [--format FORMAT]

# Example
pltr connectivity import list-file --connection ri.conn.main.connection.123
```

### Get File Import Details

```bash
pltr connectivity import get-file IMPORT_RID [--format FORMAT]

# Example
pltr connectivity import get-file ri.import.main.file.12345
```

## Table Import Commands

### Create Table Import

```bash
pltr connectivity import table CONNECTION_RID SOURCE_TABLE TARGET_DATASET_RID [OPTIONS]

# Options:
#   --config, -c TEXT    Import config (JSON)
#   --execute            Execute immediately

# Examples
pltr connectivity import table ri.conn.main.connection.123 "sales_data" ri.foundry.main.dataset.456

pltr connectivity import table ri.conn.main.connection.123 "sales_data" ri.foundry.main.dataset.456 \
  --config '{"sync_mode": "incremental", "primary_key": "id"}' \
  --execute
```

### List Table Imports

```bash
pltr connectivity import list-table [--connection CONNECTION_RID] [--format FORMAT]

# Example
pltr connectivity import list-table --connection ri.conn.main.connection.123
```

### Get Table Import Details

```bash
pltr connectivity import get-table IMPORT_RID [--format FORMAT]

# Example
pltr connectivity import get-table ri.import.main.table.12345
```

## Common Patterns

### Set up daily data import

```bash
# 1. List available connections
pltr connectivity connection list

# 2. Create table import with incremental sync
pltr connectivity import table ri.conn.main.connection.123 "daily_sales" ri.foundry.main.dataset.456 \
  --config '{
    "sync_mode": "incremental",
    "primary_key": "transaction_id",
    "updated_at_column": "last_modified"
  }'

# 3. Execute the import
pltr connectivity import table ri.conn.main.connection.123 "daily_sales" ri.foundry.main.dataset.456 --execute
```

### Bulk file import from S3

```bash
pltr connectivity import file ri.conn.main.s3.123 "/data/2024/sales/*.csv" ri.foundry.main.dataset.456 \
  --config '{
    "format": "CSV",
    "delimiter": ",",
    "compression": "gzip",
    "multiline": true
  }' \
  --execute --format json --output import_results.json
```

### List all imports for a connection

```bash
CONNECTION="ri.conn.main.connection.123"

echo "File imports:"
pltr connectivity import list-file --connection $CONNECTION

echo "Table imports:"
pltr connectivity import list-table --connection $CONNECTION
```

## Import Configuration Options

Common config fields:

```json
{
  "format": "CSV",
  "delimiter": ",",
  "header": true,
  "compression": "gzip",
  "multiline": true,
  "sync_mode": "incremental",
  "primary_key": "id",
  "updated_at_column": "last_modified"
}
```
