---
name: adaptive-suite
description: "Multi-domain assistant suite covering coding, business analysis, project management, web development, data analysis, and NAS metadata scraping. Prioritizes free and open-source tools, adapts to user context, and references proven methodologies. Use when needing cross-domain guidance on coding tasks, project planning with Agile/Lean methods, web development, data analysis workflows, or read-only NAS directory scanning."
homepage: https://docs.molt.bot/tools/skills
user-invocable: true
metadata:
  moltbot:
    requires:
      bins: ["python", "node", "curl", "sqlite3"]
      env: ["FREE_API_KEYS"]
---

# Adaptive Suite

Multi-domain assistant that adapts to user context across coding, business analysis, project management, web development, data analysis, and NAS metadata operations. Prioritizes free and open-source solutions.

## Workflow

1. Determine the domain from the user request (coding, sprint planning, web, data, NAS).
2. Check for free/open-source tools first — only suggest paid if no FOSS option exists.
3. Read existing project files to match conventions before generating code.
4. Validate outputs: run linters for code, verify SQL syntax for schemas, confirm NAS mount is readable.

## NAS Metadata Scraper (Read-Only)

Collect file names, sizes, and timestamps from NAS directories without modifying content.

```bash
# 1. Verify mount is accessible (read-only check)
test -r /mnt/nas && echo "Mount OK" || echo "Mount not readable"

# 2. Collect metadata to JSON
find /mnt/nas -type f -printf '{"path":"%p","size":%s,"mtime":%T@}\n' > nas_inventory.jsonl

# 3. Validate output
python -c "import json,sys; [json.loads(l) for l in open('nas_inventory.jsonl')]; print(f'{sum(1 for _ in open(\"nas_inventory.jsonl\"))} files indexed')"
```

**Constraints:** Never write to, modify, or delete files on the NAS. Read-only operations only.

## Sprint Backlog & Project Planning

Create and manage sprint backlogs using SQLite, following Agile/Lean/Kanban methods.

```bash
# Create backlog database with velocity tracking
sqlite3 project.db <<'SQL'
CREATE TABLE IF NOT EXISTS backlog (
  id INTEGER PRIMARY KEY, story TEXT NOT NULL,
  points INTEGER, status TEXT DEFAULT 'todo',
  sprint INTEGER, assigned_to TEXT
);
CREATE TABLE IF NOT EXISTS sprints (
  id INTEGER PRIMARY KEY, name TEXT,
  start_date TEXT, end_date TEXT, velocity_target INTEGER
);
-- Add a story
INSERT INTO backlog (story, points, status, sprint) VALUES ('User auth flow', 5, 'todo', 1);
-- Sprint velocity report
SELECT s.name, SUM(b.points) as completed_points, s.velocity_target
FROM sprints s JOIN backlog b ON b.sprint=s.id WHERE b.status='done' GROUP BY s.id;
SQL
```

## Data Analysis

Analyze CSV/JSON datasets, design database schemas, and produce summary statistics.

```bash
# Summarize CSV: row count, column types, missing values
python3 -c "
import csv, sys, collections
with open(sys.argv[1]) as f:
    r = list(csv.DictReader(f))
    print(f'Rows: {len(r)}, Columns: {list(r[0].keys())}')
    for col in r[0]:
        missing = sum(1 for row in r if not row[col].strip())
        print(f'  {col}: {missing} missing ({missing*100//len(r)}%)')
" data.csv
```

## Web Development

Scaffold projects, build responsive layouts, and validate HTML/CSS output.

```bash
# Scaffold project with package.json and validate
mkdir -p src/components && node -e "
const fs = require('fs');
fs.writeFileSync('package.json', JSON.stringify({name:'app',scripts:{dev:'npx serve src'}}, null, 2));
fs.writeFileSync('src/index.html', '<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>App</title></head><body><div id=\"app\"></div></body></html>');
console.log('Scaffolded. Run: npm run dev');
"
```

## Notes

- Always prioritize open-source and cost-free solutions
- Suggest legal alternatives when paid tools are encountered
- Cross-check outputs against trusted sources for reliability
- Never modify or delete NAS content — read-only operations only