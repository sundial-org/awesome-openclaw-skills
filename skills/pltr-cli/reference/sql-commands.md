# SQL Commands

SQL query functionality for executing queries against Foundry datasets.

**Note**: SQL API is in preview mode. All commands default to `--preview`.

## Execute Query (Synchronous)

```bash
pltr sql execute QUERY [OPTIONS]

# Options:
#   --timeout INTEGER         Query timeout in seconds [default: 300]
#   --fallback-branches TEXT  Comma-separated fallback branch IDs
#   --format, -f TEXT         Output format (table, json, csv)
#   --output, -o TEXT         Output file path
#   --profile, -p TEXT        Profile name

# Examples
pltr sql execute "SELECT COUNT(*) FROM my_dataset"
pltr sql execute "SELECT * FROM dataset WHERE category = 'A'" --format csv
pltr sql execute "SELECT * FROM large_table" --timeout 600 --output results.csv
```

## Submit Query (Asynchronous)

For long-running queries, submit without waiting:

```bash
pltr sql submit QUERY [OPTIONS]

# Returns: Query ID

# Example
pltr sql submit "SELECT * FROM huge_dataset"
# Output: Query submitted with ID: abc-123-def
```

## Check Query Status

```bash
pltr sql status QUERY_ID

# Example
pltr sql status abc-123-def
```

## Get Query Results

```bash
pltr sql results QUERY_ID [--format FORMAT] [--output FILE]

# Example
pltr sql results abc-123-def --format json --output results.json
```

## Wait for Query Completion

```bash
pltr sql wait QUERY_ID [--timeout SECONDS] [--format FORMAT]

# Example
pltr sql wait abc-123-def --timeout 3600 --format csv --output results.csv
```

## Cancel Query

```bash
pltr sql cancel QUERY_ID

# Example
pltr sql cancel abc-123-def
```

## Export Query Results

Execute and export in one command:

```bash
pltr sql export QUERY OUTPUT_FILE [OPTIONS]

# Example
pltr sql export "SELECT * FROM dataset WHERE date > '2025-01-01'" analysis.csv
```

## Common Query Patterns

### Count rows
```bash
pltr sql execute "SELECT COUNT(*) FROM my_dataset"
```

### Describe table structure
```bash
pltr sql execute "DESCRIBE my_dataset"
```

### Sample data
```bash
pltr sql execute "SELECT * FROM my_dataset LIMIT 10"
```

### Aggregation with grouping
```bash
pltr sql execute "
  SELECT category, COUNT(*) as count, AVG(value) as avg_value
  FROM my_dataset
  GROUP BY category
  ORDER BY count DESC
" --format csv --output category_stats.csv
```

### Async pattern for large queries
```bash
# Submit query
QUERY_ID=$(pltr sql submit "SELECT * FROM huge_table WHERE complex_condition")
echo "Query ID: $QUERY_ID"

# Check status periodically
pltr sql status $QUERY_ID

# Get results when ready
pltr sql wait $QUERY_ID --format csv --output results.csv
```

### Parallel query execution
```bash
# Submit multiple queries
Q1=$(pltr sql submit "SELECT * FROM table1")
Q2=$(pltr sql submit "SELECT * FROM table2")
Q3=$(pltr sql submit "SELECT * FROM table3")

# Wait for all in parallel
pltr sql wait $Q1 --output results1.csv &
pltr sql wait $Q2 --output results2.csv &
pltr sql wait $Q3 --output results3.csv &
wait
```

### Date filtering
```bash
pltr sql execute "
  SELECT date, metric, value
  FROM time_series_data
  WHERE date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)
  ORDER BY date
" --format csv --output last_30_days.csv
```

## Best Practices

1. **Start simple**: Test with `LIMIT` before running full queries
2. **Use async for large datasets**: `submit` + `wait` prevents timeouts
3. **Set appropriate timeouts**: Default is 300s, increase for complex queries
4. **Export results**: Use `--output` to save for further analysis
5. **Use JSON for programmatic processing**: `--format json` for parsing
