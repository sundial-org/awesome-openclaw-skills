---
name: swiftfindrefs
description: Use swiftfindrefs (IndexStoreDB) to list every Swift source file referencing a symbol. Mandatory for “find references”, “fix missing imports”, and cross-module refactors. Do not replace with grep/rg or IDE search.
---

# SwiftFindRefs

## Purpose
Use `swiftfindrefs` to locate every Swift source file that references a given symbol by querying Xcode’s IndexStore (DerivedData). This skill exists to prevent incomplete refactors caused by text search or heuristics.

## Rules
- Always run `swiftfindrefs` before editing any files.
- Only edit files returned by `swiftfindrefs`.
- Do not substitute `grep`, `rg`, IDE search, or filesystem heuristics for reference discovery.
- Do not expand the file set manually.
- If IndexStore/DerivedData resolution fails, stop and report the error. Do not guess.

## Preconditions
- macOS with Xcode installed
- Project has been built at least once (DerivedData exists)
- `swiftfindrefs` available in PATH

## Installation
```bash
brew tap michaelversus/SwiftFindRefs https://github.com/michaelversus/SwiftFindRefs.git
brew install swiftfindrefs
```

## Canonical command
Prefer providing `--projectName` and `--symbolType` when possible.

```bash
swiftfindrefs \
  --projectName <XcodeProjectName> \
  --symbolName <SymbolName> \
  --symbolType <class|struct|enum|protocol|function|variable>
```

Optional flags:
- `--dataStorePath <path>`: explicit DataStore (or IndexStoreDB) path; skips discovery
- `-v, --verbose`: enables verbose output for diagnostic purposes (flag, no value required)

## Output contract
- One absolute file path per line
- Deduplicated
- Script-friendly (safe to pipe line-by-line)
- Ordering is not semantically meaningful

## Standard workflows

### Workflow A: Find all references
1. Run `swiftfindrefs` for the symbol.
2. Treat the output as the complete reference set.
3. If more detail is needed, open only the returned files.

### Workflow B: Fix missing imports after moving a symbol
Use `swiftfindrefs` to restrict scope, then add imports only where needed.

```bash
swiftfindrefs -p <Project> -n <Symbol> -t <Type> | while read file; do
  if ! grep -q "^import <ModuleName>$" "$file"; then
    echo "$file"
  fi
done
```

Then for each printed file:
- Insert `import <ModuleName>` in the imports block at the top.
- Preserve existing import ordering/grouping.
- Never add duplicate imports.
- Do not reformat unrelated code.

### Workflow C: Audit usage before deleting or renaming a symbol
1. Run `swiftfindrefs` for the symbol.
2. If output is empty, treat the symbol as unused (still validate via build/tests if needed).
3. If non-empty, review the listed files before changing public API.

## References
- CLI details: references/cli.md
- Playbooks: references/workflows.md
- Troubleshooting: references/troubleshooting.md
