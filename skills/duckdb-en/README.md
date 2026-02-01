# DuckDB CLI AI Skill

A comprehensive AI skill for [Claude Code](https://claude.ai/code) that provides expert assistance with DuckDB CLI operations.

## What is this?

This is a **skill file** for Claude Code (Anthropic's CLI tool). When activated, it gives Claude deep knowledge about DuckDB CLI, enabling it to help you with:

- SQL queries on CSV, Parquet, and JSON files
- Data conversion between formats
- Database operations and analysis
- Command-line arguments and dot commands
- Output formatting and configuration

## Installation

### Claude Code (recommended)

Copy `SKILL.md` to your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills/duckdb
cp SKILL.md ~/.claude/skills/duckdb/
```

Then use `/duckdb` in Claude Code to activate the skill.

### Other AI Tools

The `SKILL.md` file follows standard markdown conventions and can be adapted for use with other AI assistants that support custom instructions or system prompts.

## What's Included

The skill covers all official DuckDB CLI documentation:

- **Quick Start** - Read files directly with SQL
- **Command Line Arguments** - All flags and options
- **Data Conversion** - CSV, Parquet, JSON transformations
- **Dot Commands** - Schema inspection, output control
- **Output Formats** - All 18 available formats
- **Keyboard Shortcuts** - Navigation, history, editing
- **Autocomplete** - Context-aware completion
- **Configuration** - ~/.duckdbrc settings
- **Safe Mode** - Restricted file access mode

## Example Usage

Once the skill is activated, you can ask Claude things like:

- "Convert this CSV to Parquet"
- "Show me statistics for sales.csv"
- "Join these two files on customer_id"
- "What's the DuckDB command to export as JSON?"

## Documentation Sources

Based on official DuckDB documentation:
- [CLI Overview](https://duckdb.org/docs/stable/clients/cli/overview)
- [Arguments](https://duckdb.org/docs/stable/clients/cli/arguments)
- [Dot Commands](https://duckdb.org/docs/stable/clients/cli/dot_commands)
- [Output Formats](https://duckdb.org/docs/stable/clients/cli/output_formats)
- [Editing](https://duckdb.org/docs/stable/clients/cli/editing)
- [Autocomplete](https://duckdb.org/docs/stable/clients/cli/autocomplete)
- [Syntax Highlighting](https://duckdb.org/docs/stable/clients/cli/syntax_highlighting)
- [Safe Mode](https://duckdb.org/docs/stable/clients/cli/safe_mode)

## License

MIT
