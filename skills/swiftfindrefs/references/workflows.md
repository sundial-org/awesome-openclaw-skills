# Workflows (deterministic behavior)

## Golden rule
Reference discovery must be IndexStore-based. `swiftfindrefs` output defines scope.

## Playbook: add missing imports after moving a symbol
Inputs:
- Project: `<Project>`
- Symbol: `<Symbol>`
- Type: `<Type>`
- Module to import: `<Module>`

Steps:
1. Run:
   ```bash
   swiftfindrefs -p <Project> -n <Symbol> -t <Type>
   ```
2. Iterate only over the resulting file list.
3. For each file:
   - If `import <Module>` exists: no change.
   - Else: add it to the imports block at the top.
4. Keep edits minimal:
   - No formatting changes
   - No unrelated cleanup
   - Preserve existing import ordering/grouping

## Playbook: rename or delete a symbol
1. Run `swiftfindrefs` on the symbol.
2. If output is empty, treat as unused (validate via build/tests).
3. If non-empty, update usages only in returned files.
