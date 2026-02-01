# Models Commands

Commands for managing ML models and model versions in the Foundry model registry.

**Note:** This is distinct from the `language-models` module, which handles LLM chat and embeddings operations.

## RID Formats
- **Model**: `ri.foundry.main.model.{uuid}`
- **Folder**: `ri.compass.main.folder.{uuid}`

## Model Commands

### Create Model

Create a new ML model in the registry.

```bash
pltr models model create NAME --folder FOLDER_RID [OPTIONS]

# Options:
#   --folder, -f TEXT       Parent folder RID (required)
#   --preview               Enable preview mode
#   --format TEXT           Output format (table, json, csv)
#   --output, -o TEXT       Output file path
#   --profile, -p TEXT      Profile name

# Examples

# Create a new model
pltr models model create "fraud-detector" \
    --folder ri.compass.main.folder.xxx

# Create with JSON output
pltr models model create "recommendation-engine" \
    --folder ri.compass.main.folder.xxx \
    --format json

# Save model info to file
pltr models model create "anomaly-detector" \
    --folder ri.compass.main.folder.xxx \
    --output model-info.json
```

### Get Model

Get information about a model.

```bash
pltr models model get MODEL_RID [OPTIONS]

# Options:
#   --preview               Enable preview mode
#   --format TEXT           Output format (table, json, csv)
#   --output, -o TEXT       Output file path
#   --profile, -p TEXT      Profile name

# Examples

# Get model details
pltr models model get ri.foundry.main.model.abc123

# Get as JSON
pltr models model get ri.foundry.main.model.abc123 --format json

# Save to file
pltr models model get ri.foundry.main.model.abc123 \
    --format json \
    --output model-details.json
```

## Version Commands

### Get Model Version

Get information about a specific model version.

```bash
pltr models version get MODEL_RID VERSION_ID [OPTIONS]

# Options:
#   --preview               Enable preview mode
#   --format TEXT           Output format (table, json, csv)
#   --output, -o TEXT       Output file path
#   --profile, -p TEXT      Profile name

# Examples

# Get specific version
pltr models version get ri.foundry.main.model.abc123 v1.0.0

# Get as JSON
pltr models version get ri.foundry.main.model.abc123 v1.0.0 \
    --format json

# Save to file
pltr models version get ri.foundry.main.model.abc123 v1.0.0 \
    --format json \
    --output version-details.json
```

### List Model Versions

List all versions of a model with pagination support.

```bash
pltr models version list MODEL_RID [OPTIONS]

# Options:
#   --page-size INTEGER     Maximum versions per page
#   --page-token TEXT       Token for fetching next page
#   --preview               Enable preview mode
#   --format TEXT           Output format (table, json, csv)
#   --output, -o TEXT       Output file path
#   --profile, -p TEXT      Profile name

# Examples

# List all versions
pltr models version list ri.foundry.main.model.abc123

# List with pagination
pltr models version list ri.foundry.main.model.abc123 \
    --page-size 50

# Get next page
pltr models version list ri.foundry.main.model.abc123 \
    --page-size 50 \
    --page-token <token-from-previous-response>

# Save to file
pltr models version list ri.foundry.main.model.abc123 \
    --format json \
    --output versions.json
```

## SDK Limitations

**No List All Models:** The SDK does not support listing all models in the registry. You must already know the model RID to retrieve it.

To discover models:
- Use the Foundry web UI
- Use the Ontology API
- Maintain your own inventory of model RIDs

## Pagination

The `version list` command supports pagination via tokens:

```bash
# First page
pltr models version list ri.foundry.main.model.abc123 --page-size 50

# Output includes nextPageToken if more results exist:
# Next page available. Use --page-token <token>

# Fetch next page
pltr models version list ri.foundry.main.model.abc123 \
    --page-size 50 \
    --page-token eyJwYWdlIjogMn0=
```

## Common Patterns

### Create Model and Track Versions

```bash
# 1. Create the model container
pltr models model create "my-ml-model" \
    --folder ri.compass.main.folder.xxx \
    --format json \
    --output model-info.json

# 2. Note the model RID from output for future version operations
cat model-info.json | jq -r '.rid'

# 3. Later: list versions
pltr models version list ri.foundry.main.model.abc123
```

### Export Model Metadata

```bash
# Get model info
pltr models model get ri.foundry.main.model.abc123 \
    --format json \
    --output model.json

# Get all versions
pltr models version list ri.foundry.main.model.abc123 \
    --format json \
    --output versions.json
```

### Get Latest Version Details

```bash
# List versions to see what's available
pltr models version list ri.foundry.main.model.abc123 --format json

# Get details for specific version
pltr models version get ri.foundry.main.model.abc123 v2.1.0 --format json
```

### Compare Model Versions

```bash
# Export two versions for comparison
pltr models version get ri.foundry.main.model.abc123 v1.0.0 \
    --format json --output v1.json

pltr models version get ri.foundry.main.model.abc123 v2.0.0 \
    --format json --output v2.json

# Compare
diff v1.json v2.json
```

## Models vs Language-Models

| Module | Purpose | Use Case |
|--------|---------|----------|
| `models` | ML model registry | Custom ML models, versioning |
| `language-models` | LLM interactions | Chat with Claude, embeddings |

```bash
# ML Model Registry
pltr models model get ri.foundry.main.model.xxx

# LLM Chat
pltr language-models anthropic messages ri.language-models.main.model.yyy \
    --message "Hello"
```
