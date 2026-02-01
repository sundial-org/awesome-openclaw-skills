# Output, progress, and sync

## Output formats

- `--ndjson` (default): one JSON object per line, best for streaming.
- `--json`: single JSON object or array, best for short outputs.
- `--plain`: stable, tab-delimited text for simple pipes.
- `--format table`: human-readable only; avoid for parsing.

Use `--output <file>` to write results. Use `-` for stdout.
Use `--output-dir <dir>` (export only) to write per-page NDJSON files.

## Structured stderr and progress

- `--stderr-json`: structured errors with `code` and `exit_code`.
- `--progress-json`: emit progress events on stderr for long operations (e.g., import/export).
- `--verbose`: summary counts on stderr while keeping stdout clean.

## Cursors and bounds

- `--cursor <file>`: store/read paging cursor in a file.
- `--cursor-dir <dir>`: per-folder/tag cursor files.

Bounds formats for `--since`/`--until`:

- `bookmark_id:<id>` (default when no prefix)
- `time:<rfc3339|unix>`
- `progress_timestamp:<rfc3339|unix>`

Use `--updated-since <rfc3339>` for incremental updates.

## Client-side filtering

`--select` format: comma-separated filters, `<field><op><value>`

- Operators: `=`, `!=`, `~` (contains, case-insensitive)
- Fields: `bookmark_id`, `time`, `progress`, `progress_timestamp`, `starred`, `title`, `url`, `description`, `tags`

Example:

- `--select "starred=1,tag~news"`

