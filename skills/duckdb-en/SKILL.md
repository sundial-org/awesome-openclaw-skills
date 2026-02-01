---
name: duckdb-en
description: DuckDB CLI specialist for SQL analysis, data processing and file conversion. Use for SQL queries, CSV/Parquet/JSON analysis, database queries, or data conversion. Triggers on "duckdb", "sql", "query", "data analysis", "parquet", "convert data".
---

# DuckDB CLI Specialist

Helps with data analysis, SQL queries and file conversion via DuckDB CLI.

## Quick Start

### Read data files directly with SQL
```bash
# CSV
duckdb -c "SELECT * FROM 'data.csv' LIMIT 10"

# Parquet
duckdb -c "SELECT * FROM 'data.parquet'"

# Multiple files with glob
duckdb -c "SELECT * FROM read_parquet('logs/*.parquet')"

# JSON
duckdb -c "SELECT * FROM read_json_auto('data.json')"
```

### Open persistent databases
```bash
# Create/open database
duckdb my_database.duckdb

# Read-only mode
duckdb -readonly existing.duckdb
```

## Command Line Arguments

### Output formats (as flags)
| Flag | Format |
|------|--------|
| `-csv` | Comma-separated |
| `-json` | JSON array |
| `-table` | ASCII table |
| `-markdown` | Markdown table |
| `-html` | HTML table |
| `-line` | One value per line |

### Execution arguments
| Argument | Description |
|----------|-------------|
| `-c COMMAND` | Run SQL and exit |
| `-f FILENAME` | Run script from file |
| `-init FILE` | Use alternative to ~/.duckdbrc |
| `-readonly` | Open in read-only mode |
| `-echo` | Show commands before execution |
| `-bail` | Stop on first error |
| `-header` / `-noheader` | Show/hide column headers |
| `-nullvalue TEXT` | Text for NULL values |
| `-separator SEP` | Column separator |

## Data Conversion

### CSV to Parquet
```bash
duckdb -c "COPY (SELECT * FROM 'input.csv') TO 'output.parquet' (FORMAT PARQUET)"
```

### Parquet to CSV
```bash
duckdb -c "COPY (SELECT * FROM 'input.parquet') TO 'output.csv' (HEADER, DELIMITER ',')"
```

### JSON to Parquet
```bash
duckdb -c "COPY (SELECT * FROM read_json_auto('input.json')) TO 'output.parquet' (FORMAT PARQUET)"
```

### Convert with filtering
```bash
duckdb -c "COPY (SELECT * FROM 'data.csv' WHERE amount > 1000) TO 'filtered.parquet' (FORMAT PARQUET)"
```

## Dot Commands

### Schema inspection
| Command | Description |
|---------|-------------|
| `.tables [pattern]` | Show tables (with LIKE pattern) |
| `.schema [table]` | Show CREATE statements |
| `.databases` | Show attached databases |

### Output control
| Command | Description |
|---------|-------------|
| `.mode FORMAT` | Change output format |
| `.output file` | Send output to file |
| `.once file` | Next output to file |
| `.headers on/off` | Show/hide column headers |
| `.separator COL ROW` | Set separators |

### Queries
| Command | Description |
|---------|-------------|
| `.timer on/off` | Show execution time |
| `.echo on/off` | Show commands before execution |
| `.bail on/off` | Stop on error |
| `.read file.sql` | Run SQL from file |

### Editing
| Command | Description |
|---------|-------------|
| `.edit` or `\e` | Open query in external editor |
| `.help [pattern]` | Show help |

## Output Formats (18 available)

### Data export
- **csv** - Comma-separated for spreadsheets
- **tabs** - Tab-separated
- **json** - JSON array
- **jsonlines** - Newline-delimited JSON (streaming)

### Readable formats
- **duckbox** (default) - Pretty ASCII with unicode box-drawing
- **table** - Simple ASCII table
- **markdown** - For documentation
- **html** - HTML table
- **latex** - For academic papers

### Specialized
- **insert TABLE** - SQL INSERT statements
- **column** - Columns with adjustable width
- **line** - One value per line
- **list** - Pipe-separated
- **trash** - Discard output

## Keyboard Shortcuts (macOS/Linux)

### Navigation
| Shortcut | Action |
|----------|--------|
| `Home` / `End` | Start/end of line |
| `Ctrl+Left/Right` | Jump word |
| `Ctrl+A` / `Ctrl+E` | Start/end of buffer |

### History
| Shortcut | Action |
|----------|--------|
| `Ctrl+P` / `Ctrl+N` | Previous/next command |
| `Ctrl+R` | Search history |
| `Alt+<` / `Alt+>` | First/last in history |

### Editing
| Shortcut | Action |
|----------|--------|
| `Ctrl+W` | Delete word backward |
| `Alt+D` | Delete word forward |
| `Alt+U` / `Alt+L` | Uppercase/lowercase word |
| `Ctrl+K` | Delete to end of line |

### Autocomplete
| Shortcut | Action |
|----------|--------|
| `Tab` | Autocomplete / next suggestion |
| `Shift+Tab` | Previous suggestion |
| `Esc+Esc` | Undo autocomplete |

## Autocomplete

Context-aware autocomplete activated with `Tab`:
- **Keywords** - SQL commands
- **Table names** - Database objects
- **Column names** - Fields and functions
- **File names** - Path completion

## Database Operations

### Create table from file
```sql
CREATE TABLE sales AS SELECT * FROM 'sales_2024.csv';
```

### Insert data
```sql
INSERT INTO sales SELECT * FROM 'sales_2025.csv';
```

### Export table
```sql
COPY sales TO 'backup.parquet' (FORMAT PARQUET);
```

## Analysis Examples

### Quick statistics
```sql
SELECT
    COUNT(*) as count,
    AVG(amount) as average,
    SUM(amount) as total
FROM 'transactions.csv';
```

### Grouping
```sql
SELECT
    category,
    COUNT(*) as count,
    SUM(amount) as total
FROM 'data.csv'
GROUP BY category
ORDER BY total DESC;
```

### Join on files
```sql
SELECT a.*, b.name
FROM 'orders.csv' a
JOIN 'customers.parquet' b ON a.customer_id = b.id;
```

### Describe data
```sql
DESCRIBE SELECT * FROM 'data.csv';
```

## Pipe and stdin

```bash
# Read from stdin
cat data.csv | duckdb -c "SELECT * FROM read_csv('/dev/stdin')"

# Pipe to another command
duckdb -csv -c "SELECT * FROM 'data.parquet'" | head -20

# Write to stdout
duckdb -c "COPY (SELECT * FROM 'data.csv') TO '/dev/stdout' (FORMAT CSV)"
```

## Configuration

Save common settings in `~/.duckdbrc`:
```sql
.timer on
.mode duckbox
.maxrows 50
.highlight on
```

### Syntax highlighting colors
```sql
.keyword green
.constant yellow
.comment brightblack
.error red
```

## External Editor

Open complex queries in your editor:
```sql
.edit
```

Editor is chosen from: `DUCKDB_EDITOR` → `EDITOR` → `VISUAL` → `vi`

## Safe Mode

Secure mode that restricts file access. When enabled:
- No external file access
- Disables `.read`, `.output`, `.import`, `.sh` etc.
- **Cannot** be disabled in the same session

## Tips

- Use `LIMIT` on large files for quick preview
- Parquet is faster than CSV for repeated queries
- `read_csv_auto` and `read_json_auto` guess column types
- Arguments are processed in order (like SQLite CLI)
- WSL2 may show incorrect `memory_limit` values on some Ubuntu versions
