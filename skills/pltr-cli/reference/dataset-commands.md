# Dataset Commands

## Dataset RID Format
`ri.foundry.main.dataset.{uuid}`

## Get Dataset Info

```bash
pltr dataset get DATASET_RID [--profile PROFILE] [--format FORMAT] [--output FILE]

# Example
pltr dataset get ri.foundry.main.dataset.abc123
pltr dataset get ri.foundry.main.dataset.abc123 --format json --output info.json
```

## Create Dataset

```bash
pltr dataset create NAME [--parent-folder FOLDER_RID] [--profile PROFILE]

# Example
pltr dataset create "My New Dataset"
pltr dataset create "Analysis Results" --parent-folder ri.compass.main.folder.xyz789
```

## Branch Operations

```bash
# List branches
pltr dataset branches list DATASET_RID

# Create branch
pltr dataset branches create DATASET_RID BRANCH_NAME [--parent PARENT_BRANCH]

# Examples
pltr dataset branches list ri.foundry.main.dataset.abc123
pltr dataset branches create ri.foundry.main.dataset.abc123 "feature-branch"
pltr dataset branches create ri.foundry.main.dataset.abc123 "hotfix" --parent development
```

## File Operations

```bash
# List files in dataset
pltr dataset files list DATASET_RID [--branch BRANCH]

# Download file from dataset
pltr dataset files get DATASET_RID FILE_PATH OUTPUT_PATH [--branch BRANCH]

# Examples
pltr dataset files list ri.foundry.main.dataset.abc123
pltr dataset files list ri.foundry.main.dataset.abc123 --branch development

pltr dataset files get ri.foundry.main.dataset.abc123 "/data/results.csv" "./results.csv"
pltr dataset files get ri.foundry.main.dataset.abc123 "/report.pdf" "./report.pdf" --branch feature
```

## Schema Operations

**Note:** `schema get` requires API preview access. If you encounter `ApiFeaturePreviewUsageOnly` errors, use `schema apply` instead.

```bash
# Get dataset schema (requires preview access)
pltr dataset schema get DATASET_RID [--branch BRANCH]

# Apply/infer schema (works for all users)
pltr dataset schema apply DATASET_RID

# Example
pltr dataset schema get ri.foundry.main.dataset.abc123
pltr dataset schema apply ri.foundry.main.dataset.abc123
```

## Preview Data

```bash
# Preview dataset contents
pltr dataset preview DATASET_RID [--limit N]

# Examples
pltr dataset preview ri.foundry.main.dataset.abc123
pltr dataset preview ri.foundry.main.dataset.abc123 --limit 50
pltr dataset preview ri.foundry.main.dataset.abc123 --format csv --output preview.csv
```

## Transaction Operations

Transactions provide atomic operations with rollback capability.

```bash
# List transactions
pltr dataset transactions list DATASET_RID [--branch BRANCH]

# Start transaction
pltr dataset transactions start DATASET_RID [--branch BRANCH]

# Check transaction status
pltr dataset transactions status DATASET_RID TRANSACTION_RID

# Commit transaction
pltr dataset transactions commit DATASET_RID TRANSACTION_RID

# Abort transaction
pltr dataset transactions abort DATASET_RID TRANSACTION_RID
```

## View Operations

```bash
# List views
pltr dataset views list DATASET_RID

# Create view
pltr dataset views create DATASET_RID VIEW_NAME [--description TEXT]

# Examples
pltr dataset views list ri.foundry.main.dataset.abc123
pltr dataset views create ri.foundry.main.dataset.abc123 "analysis-view" --description "Monthly analysis"
```

## Copy Datasets

```bash
# Copy dataset to another folder
pltr cp SOURCE_RID TARGET_FOLDER_RID [OPTIONS]

# Options:
#   --branch, -b TEXT     Dataset branch [default: master]
#   --recursive, -r       Required for folders
#   --name-suffix TEXT    Suffix for cloned names [default: -copy]
#   --schema/--no-schema  Copy schemas [default: true]
#   --dry-run             Preview without writing
#   --fail-fast           Stop on first error

# Examples
pltr cp ri.foundry.main.dataset.abc123 ri.compass.main.folder.dest456
pltr cp ri.compass.main.folder.source789 ri.compass.main.folder.dest456 --recursive
pltr cp ri.foundry.main.dataset.abc123 ri.compass.main.folder.dest456 --dry-run
```

## Common Patterns

### Download all files from a dataset
```bash
# List files, then download each
for file in $(pltr dataset files list ri.foundry.main.dataset.abc123 --format json | jq -r '.[].path'); do
  pltr dataset files get ri.foundry.main.dataset.abc123 "$file" "./${file##*/}"
done
```

### Export dataset info to JSON
```bash
pltr dataset get ri.foundry.main.dataset.abc123 --format json --output dataset-info.json
```
