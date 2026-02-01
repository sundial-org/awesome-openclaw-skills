---
name: excel-weekly-dashboard
description: Designs refreshable Excel dashboards (Power Query + structured tables + validation + pivot reporting). Use when you need a repeatable weekly KPI workbook that updates from files with minimal manual work.
---

# Excel weekly dashboards at scale

## PURPOSE
Designs refreshable Excel dashboards (Power Query + structured tables + validation + pivot reporting).

## WHEN TO USE
- TRIGGERS:
  - Build me a Power Query pipeline for this file so it refreshes weekly with no manual steps.
  - Turn this into a structured table with validation lists and clean data entry rules.
  - Create a pivot-driven weekly dashboard with slicers for year and ISO week.
  - Fix this Excel model so refresh does not break when new columns appear.
  - Design a reusable KPI pack that updates from a folder of CSVs.
- DO NOT USE WHEN…
  - You need advanced forecasting/valuation modeling (this skill is for repeatable reporting pipelines).
  - You need a BI tool build (Power BI/Tableau) rather than Excel.
  - You need web scraping as the primary ingestion method.

## INPUTS
- REQUIRED:
  - Source data file(s): CSV, XLSX, DOCX-exported tables, or PDF-exported tables (provided by user).
  - Definition of ‘week’ (ISO week preferred) and the KPI fields required.
- OPTIONAL:
  - Data dictionary / column definitions.
  - Known “bad data” patterns to validate (e.g., blank PayNumber, invalid dates).
  - Existing workbook to refactor.
- EXAMPLES:
  - Folder of weekly CSV exports: `exports/2026-W02/*.csv`
  - Single XLSX dump with changing columns month to month

## OUTPUTS
- If asked for **plan only (default)**: a step-by-step build plan + Power Query steps + sheet layout + validation rules.
- If explicitly asked to **generate artifacts**:
  - `workbook_spec.md` (workbook structure and named tables)
  - `power_query_steps.pq` (M code template)
  - `refresh-checklist.md` (from `assets/`)
Success = refresh works after adding a new week’s files without manual edits, and validation catches bad rows.


## WORKFLOW
1. Identify source type(s) (CSV/XLSX/DOCX/PDF-export) and the stable business keys (e.g., PayNumber).
2. Define the canonical table schema:
   - required columns, types, allowed values, and “unknown” handling.
3. Design ingestion with Power Query:
   - Prefer **Folder ingest** + combine, with defensive “missing column” handling.
   - Normalize column names (trim, case, collapse spaces).
4. Design cleansing & validation:
   - Create a **Data_Staging** query (raw-normalized) and **Data_Clean** query (validated).
   - Add validation columns (e.g., `IsValidPayNumber`, `IsValidDate`, `IssueReason`).
5. Build reporting layer:
   - Pivot table(s) off **Data_Clean**
   - Slicers: Year, ISOWeek; plus operational dimensions
6. Add a “Refresh Status” sheet:
   - last refresh timestamp, row counts, query error flags, latest week present
7. STOP AND ASK THE USER if:
   - required KPIs/columns are unspecified,
   - the source files don’t include any stable key,
   - week definition/timezone rules are unclear,
   - PDF/DOCX tables are not reliably extractable without a provided export.


## OUTPUT FORMAT
When producing a **plan**, use this template:

```text
WORKBOOK PLAN
- Sheets:
  - Data_Staging (query output)
  - Data_Clean (query output + validation flags)
  - Dashboard (pivots/charts)
  - Refresh_Status (counts + health checks)
- Canonical Schema:
  - <Column>: <Type> | Required? | Validation
- Power Query:
  - Query 1: Ingest_<name> (Folder/File)
  - Query 2: Clean_<name>
  - Key transforms: <bullets>
- Validation rules:
  - <rule> -> <action>
- Pivot design:
  - Rows/Columns/Values
  - Slicers
```

If asked for artifacts, also output:
- `assets/power-query-folder-ingest-template.pq` (adapted)
- `assets/refresh-checklist.md`


## SAFETY & EDGE CASES
- Read-only by default: provide a plan + snippets unless the user explicitly requests file generation.
- Never delete or overwrite user files; propose new filenames for outputs.
- Prefer “no silent failure”: include row-count checks and visible error flags.
- For PDF/DOCX sources, require user-provided exported tables (CSV/XLSX) or clearly mark extraction risk.


## EXAMPLES
- Input: “Folder of weekly CSVs with PayNumber/Name/Date.”  
  Output: Folder-ingest PQ template + schema + Refresh Status checks + pivot dashboard plan.

- Input: “Refresh breaks when new columns appear.”  
  Output: Defensive missing-column logic + column normalization + typed schema plan.

