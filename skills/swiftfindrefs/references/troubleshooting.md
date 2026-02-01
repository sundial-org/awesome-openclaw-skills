# Troubleshooting

## No results returned
- Build the project in Xcode to regenerate indexing.
- Re-run with verbose logging:
  ```bash
  swiftfindrefs -p <Project> -n <Symbol> -t <Type> -v
  ```
- If multiple DerivedData folders exist for the same project `swiftfindrefs` will use the most recent one.

## Wrong DerivedData selected
- Prefer explicit `--dataStorePath` in CI or multi-clone setups.
- Use `-v` or `--verbose` flag to confirm path selection.

## Do not fall back to grep
- Text search is not acceptable for reference discovery.
- grep/rg may only be used inside files already returned by `swiftfindrefs`
  (for example, to check if an import already exists).
