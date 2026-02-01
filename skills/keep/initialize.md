# Initialization

The store initializes automatically when you create an `Keeper` instance.

## Default Store Location

The store defaults to `.keep/` at the git repository root:
- Walks up from current directory to find `.git/`
- Creates `.keep/` there if it doesn't exist
- Falls back to `.keep/` in cwd if not in a git repo

Override with `KEEP_STORE_PATH` environment variable or explicit path argument.

**Note:** Add `.keep/` to your `.gitignore` if the store should not be committed.

## Quick Start

```bash
# Install in a venv
python -m venv .venv
source .venv/bin/activate
pip install keep[local]
```

```python
from keep import Keeper

# Uses .keep/ at repo root by default
kp = Keeper()
```

## CLI

```bash
# Initialize and verify
keep init

# Or specify store explicitly
keep init --store /path/to/store
```

## Configuration

On first run, `keep.toml` is created in the store directory with auto-detected providers:

- **Apple Silicon**: MLX for embedding/summarization/tagging
- **With OpenAI key**: OpenAI for summarization/tagging, sentence-transformers for embedding
- **Fallback**: sentence-transformers for embedding, passthrough summarization, no tagging

Edit the TOML to override provider choices.
