# Data Pipeline Workflows

ETL pipelines, scheduled jobs, and data quality workflows.

## ETL Pipeline Script

```bash
#!/bin/bash
# pipeline.sh - Daily data extraction pipeline

# Set environment
export FOUNDRY_TOKEN="$PRODUCTION_TOKEN"
export FOUNDRY_HOST="foundry.company.com"

# 1. Extract data
echo "Extracting daily sales data..."
pltr sql execute "
  SELECT date, product_id, quantity, revenue
  FROM sales_data
  WHERE date = CURRENT_DATE - 1
" --format csv --output daily_sales.csv

# 2. Extract related data
echo "Extracting product information..."
pltr ontology object-list ri.ontology.main.ontology.products Product \
  --properties "id,name,category,price" \
  --format json --output products.json

# 3. Generate summary report
echo "Generating summary..."
pltr sql execute "
  SELECT
    category,
    SUM(quantity) as total_quantity,
    SUM(revenue) as total_revenue,
    COUNT(DISTINCT product_id) as unique_products
  FROM sales_data s
  JOIN product_data p ON s.product_id = p.id
  WHERE s.date = CURRENT_DATE - 1
  GROUP BY category
  ORDER BY total_revenue DESC
" --format table

echo "Pipeline completed."
```

## Data Quality Monitoring

```bash
#!/bin/bash
# data_quality_check.sh

DATASET="critical_dataset"

# 1. Check for null values
echo "Checking nulls..."
pltr sql execute "
  SELECT
    'null_check' as check_type,
    SUM(CASE WHEN important_field IS NULL THEN 1 ELSE 0 END) as null_count,
    COUNT(*) as total_count
  FROM $DATASET
"

# 2. Check for duplicates
echo "Checking duplicates..."
pltr sql execute "
  SELECT
    'duplicate_check' as check_type,
    COUNT(*) - COUNT(DISTINCT id) as duplicate_count
  FROM $DATASET
"

# 3. Check data freshness
echo "Checking freshness..."
pltr sql execute "
  SELECT
    'freshness_check' as check_type,
    MAX(updated_date) as latest_update,
    DATEDIFF(CURRENT_DATE, MAX(updated_date)) as days_old
  FROM $DATASET
"

# 4. Export data profile
pltr sql execute "
  SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT id) as unique_ids,
    MIN(created_date) as earliest_record,
    MAX(created_date) as latest_record
  FROM $DATASET
" --format json --output data_profile.json
```

## CI/CD Data Validation

```bash
#!/bin/bash
# validate_data.sh - Use in CI/CD pipeline
set -e

echo "Validating data quality..."

# Check row counts
ROW_COUNT=$(pltr sql execute "SELECT COUNT(*) as count FROM production_table" --format json | jq -r '.[0].count')

if [ "$ROW_COUNT" -lt 1000 ]; then
  echo "ERROR: Row count too low: $ROW_COUNT"
  exit 1
fi

# Check for nulls
NULL_COUNT=$(pltr sql execute "SELECT COUNT(*) as count FROM production_table WHERE critical_field IS NULL" --format json | jq -r '.[0].count')

if [ "$NULL_COUNT" -gt 0 ]; then
  echo "ERROR: Found $NULL_COUNT null values"
  exit 1
fi

echo "Validation passed!"
```

## Build Management

```bash
# Search recent builds
pltr orchestration builds search

# Get build details
pltr orchestration builds get ri.orchestration.main.build.abc123

# List jobs in build
pltr orchestration builds jobs ri.orchestration.main.build.abc123

# Create new build
pltr orchestration builds create '{"dataset_rid": "ri.foundry.main.dataset.abc"}' \
  --branch production --notifications

# Cancel build if needed
pltr orchestration builds cancel ri.orchestration.main.build.abc123
```

## Schedule Management

### Create Daily Schedule

```bash
pltr orchestration schedules create '{"type": "BUILD", "target": "ri.foundry.main.dataset.daily-data"}' \
  --name "Daily ETL Pipeline" \
  --description "Automated daily data processing" \
  --trigger '{"type": "CRON", "expression": "0 2 * * *"}'
```

### Manage Schedules

```bash
# Get schedule info
pltr orchestration schedules get ri.orchestration.main.schedule.daily-etl

# Run immediately
pltr orchestration schedules run ri.orchestration.main.schedule.daily-etl

# Pause for maintenance
pltr orchestration schedules pause ri.orchestration.main.schedule.daily-etl

# Resume
pltr orchestration schedules unpause ri.orchestration.main.schedule.daily-etl

# Update schedule
pltr orchestration schedules replace ri.orchestration.main.schedule.daily-etl \
  '{"type": "BUILD", "target": "ri.foundry.main.dataset.new-pipeline"}' \
  --name "Updated ETL"

# Delete schedule
pltr orchestration schedules delete ri.orchestration.main.schedule.old-schedule --yes
```

## Job Monitoring

```bash
#!/bin/bash
# monitor_jobs.sh

BUILD_RID="ri.orchestration.main.build.abc123"

# Get build overview
pltr orchestration builds get $BUILD_RID

# List all jobs
pltr orchestration builds jobs $BUILD_RID --format json --output jobs.json

# Get running jobs
JOB_RIDS=$(cat jobs.json | jq -r '.[] | select(.status == "RUNNING") | .rid' | tr '\n' ',' | sed 's/,$//')
if [ ! -z "$JOB_RIDS" ]; then
  pltr orchestration jobs get-batch "$JOB_RIDS"
fi
```

## Scheduled Data Exports

```bash
#!/bin/bash
# daily_report.sh - Run via cron at 6 AM
# 0 6 * * * /path/to/daily_report.sh

DATE=$(date +%Y%m%d)

# Export daily metrics
pltr sql execute "
  SELECT date, total_sales, total_customers, avg_order_value
  FROM daily_metrics
  WHERE date = CURRENT_DATE - 1
" --format csv --output "daily_report_${DATE}.csv"

echo "Report generated: daily_report_${DATE}.csv"
```

## External Data Imports

```bash
# List connections
pltr connectivity connection list

# Create file import
pltr connectivity import file ri.conn.main.connection.123 "/data/sales.csv" ri.foundry.main.dataset.456 \
  --config '{"format": "CSV", "delimiter": ",", "header": true}' \
  --execute

# Create table import with incremental sync
pltr connectivity import table ri.conn.main.connection.123 "daily_sales" ri.foundry.main.dataset.456 \
  --config '{"sync_mode": "incremental", "primary_key": "transaction_id"}' \
  --execute
```

## Best Practices

1. **Use transactions**: For atomic dataset operations
2. **Set appropriate timeouts**: Increase for complex operations
3. **Monitor builds**: Check job status for failures
4. **Use dry-run**: Test copy operations before executing
5. **Log outputs**: Save command outputs for debugging
6. **Verify auth first**: Run `pltr verify` at script start
