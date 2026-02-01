# CLI reference (agent-focused)

## Preconditions
- macOS with Xcode installed
- Project built at least once (DerivedData exists)
- `swiftfindrefs` is available in PATH

## Flags
- `-p, --projectName`
  Helps infer the correct DerivedData folder when `--dataStorePath` is not provided.

- `-d, --dataStorePath`
  Points directly to a DataStore (or IndexStoreDB) directory and skips discovery.

- `-v, --verbose` (flag, no value required)
  Enables verbose output for diagnostic purposes.

## Search subcommand flags
- `-n, --symbolName` (required)
  The symbol to inspect.

- `-t, --symbolType`
  Narrows matches to a specific kind (recommended when possible).

## Recommended invocations

Most common:
```bash
swiftfindrefs -p MyApp -n SelectionViewController -t class
```

Explicit DerivedData / deterministic runs:
```bash
swiftfindrefs -d ~/Library/Developer/Xcode/DerivedData/MyApp-XXXX/ -n SelectionViewController -t class
```

Debug discovery:
```bash
swiftfindrefs -p MyApp -n SelectionViewController -t class -v
```

## Output
- Absolute file paths, one per line
- Deduplicated

## Non-goals
- The tool reports which files reference a symbol, not line or column positions.
