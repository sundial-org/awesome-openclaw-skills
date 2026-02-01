# Weekly Refresh Checklist (Excel + Power Query)

1. Drop the new week’s files into the source folder (do not rename unless specified).
2. Open the workbook.
3. Data ➜ Refresh All.
4. Check **Refresh Status** sheet:
   - Row counts match expectations
   - No query errors
   - Latest ISO week exists
5. Review **Exceptions** pivot (if present) and resolve or log issues.
6. Save as `KPI_Weekly_YYYY-WW.xlsx` (ISO week), then archive.

If any query shows errors, stop and investigate; do not export/publish partial results.
