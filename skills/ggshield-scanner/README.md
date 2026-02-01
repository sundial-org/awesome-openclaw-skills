# ggshield Secret Scanner

A MoltHub skill that wraps [GitGuardian's ggshield](https://github.com/GitGuardian/ggshield) CLI for detecting hardcoded secrets in your code.

## What is a MoltHub Skill?

MoltHub skills are **capabilities for AI agents** (like Cursor, Claude Code, Moltbot, etc.). When you install this skill, your AI agent gains the ability to scan code for secrets.

**This is NOT a CLI tool you run in the terminal.** Instead, you ask your AI agent to use it:

```
You: "Scan this repository for secrets"
Agent: [uses ggshield skill] ✅ Repository clean: 0 secrets found
```

The skill provides the AI agent with methods it can call on your behalf.

## What This Skill Does

Scans your code for 500+ types of hardcoded secrets before they're committed to git:

- AWS Access Keys, GCP Service Accounts, Azure credentials
- API tokens (GitHub, Slack, Stripe, OpenAI, etc.)
- Database passwords and connection strings
- Private encryption keys and certificates
- OAuth tokens and refresh tokens

## Prerequisites

This skill **wraps the ggshield CLI** - it doesn't embed it. Users need:

1. **ggshield installed**:
   ```bash
   pip install ggshield
   # or
   uv add ggshield
   ```

2. **GitGuardian API Key** (free):
   - Sign up at https://dashboard.gitguardian.com
   - Generate an API key in Settings
   - Create a `.env` file:
   ```bash
   echo 'GITGUARDIAN_API_KEY=your-api-key-here' > .env
   ```

## Installation

### From MoltHub

```bash
npx molthub@latest install ggshield-scanner
```

### Manual

Clone this repo into your skills directory:
```bash
git clone https://github.com/achillemascia/ggshield-skill.git ~/.moltbot/skills/ggshield-scanner
```

## Available Methods

| Method | Description |
|--------|-------------|
| `scan_repo(path)` | Scan entire git repository for secrets |
| `scan_file(path)` | Scan a single file |
| `scan_staged()` | Scan only staged git changes (fast pre-commit) |
| `install_hooks(type)` | Install git pre-commit or pre-push hook |
| `scan_docker(image)` | Scan Docker image layers for secrets |

## How AI Agents Use This Skill

When an AI agent has this skill installed, you can ask it to scan for secrets in natural language:

| You say | Agent does |
|---------|------------|
| "Scan this repo for secrets" | Calls `scan_repo(".")` |
| "Check if config.py has any hardcoded keys" | Calls `scan_file("config.py")` |
| "Are my staged changes safe to commit?" | Calls `scan_staged()` |
| "Set up a pre-commit hook to catch secrets" | Calls `install_hooks("pre-commit")` |
| "Scan my Docker image for secrets" | Calls `scan_docker("myapp:latest")` |

**Example conversation:**
```
You: Before I push, can you check if there are any secrets in my staged changes?

Agent: I'll scan your staged changes for secrets.

       ✅ Staged changes are clean

       No hardcoded secrets detected. Safe to commit!
```

## Local Development & Testing

### 1. Set up environment

```bash
cd ggshield-skill

# Install dependencies
uv sync

# Create .env file with your API key
echo 'GITGUARDIAN_API_KEY=your-api-key-here' > .env
```

### 2. Test the module imports

```bash
uv run python -c "from ggshield_skill import GGShieldSkill; s = GGShieldSkill(); print(s.name)"
# Output: ggshield
```

### 3. Test scanning

Create a test file with fake secrets:
```bash
mkdir -p test-data
echo 'AWS_KEY="AKIAIOSFODNN7EXAMPLE"' > test-data/secrets.py
echo 'SLACK_TOKEN="xoxb-1234567890-abcdefghij"' >> test-data/secrets.py
```

Run a scan (loads API key from .env):
```bash
export $(cat .env | xargs) && uv run python -c "
import asyncio
from ggshield_skill import GGShieldSkill

async def test():
    skill = GGShieldSkill()
    result = await skill.scan_file('./test-data/secrets.py')
    print(result)

asyncio.run(test())
"
```

### 4. Test all methods

```bash
export $(cat .env | xargs) && uv run python -c "
import asyncio
from ggshield_skill import GGShieldSkill

async def test_all():
    s = GGShieldSkill()

    print('=== scan_repo ===')
    print(await s.scan_repo('.'))

    print('\n=== scan_file ===')
    print(await s.scan_file('./ggshield_skill.py'))

    print('\n=== scan_staged ===')
    print(await s.scan_staged())

    print('\n=== scan_file (missing - should error) ===')
    print(await s.scan_file('/nonexistent.py'))

asyncio.run(test_all())
"
```

### 5. Run with pytest (optional)

```bash
uv add --dev pytest pytest-asyncio

cat > test_skill.py << 'EOF'
import pytest
from ggshield_skill import GGShieldSkill

def test_skill_initialization():
    """
    GIVEN a GGShieldSkill class
    WHEN instantiated
    THEN it should have correct metadata
    """
    skill = GGShieldSkill()
    assert skill.name == "ggshield"
    assert skill.version == "1.0.0"
    assert skill.requires_api_key is True

@pytest.mark.asyncio
async def test_scan_file_not_found():
    """
    GIVEN a non-existent file path
    WHEN scan_file is called
    THEN it should return an error message
    """
    skill = GGShieldSkill()
    result = await skill.scan_file("/nonexistent/file.py")
    assert "File not found" in result
    assert "❌" in result

@pytest.mark.asyncio
async def test_scan_repo_not_found():
    """
    GIVEN a non-existent directory path
    WHEN scan_repo is called
    THEN it should return an error message
    """
    skill = GGShieldSkill()
    result = await skill.scan_repo("/nonexistent/dir")
    assert "Path not found" in result
    assert "❌" in result
EOF

uv run pytest test_skill.py -v
```

## Testing with Moltbot (Local Integration Test)

Before publishing, you can test the skill with a local Moltbot installation.

### 1. Install Moltbot

```bash
# Quick install
curl -fsSL https://molt.bot/install.sh | bash

# Or via npm
npm install -g moltbot@latest

# Run onboarding
moltbot onboard --install-daemon
```

### 2. Set up the API key in your shell

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
export GITGUARDIAN_API_KEY="your-api-key-here"
```

Then reload: `source ~/.zshrc`

This way Moltbot picks up the key from your environment - no need to put it in config files.

### 3. Add your skill locally

```bash
# Create the managed skills folder
mkdir -p ~/.clawdbot/skills

# Symlink your skill for live development
ln -s "$(pwd)" ~/.clawdbot/skills/ggshield-scanner
```

### 4. Verify your skill is recognized

```bash
# List all skills
moltbot skills list

# Check if it's eligible (requirements met)
moltbot skills list --eligible

# Get info about your skill
moltbot skills info ggshield-scanner
```

### 5. Test with the agent

```bash
# Start an interactive chat
moltbot tui

# Or send a message directly
moltbot message "Scan the current directory for secrets"
```

## Publishing to MoltHub

### 1. Login to MoltHub

```bash
npx molthub@latest login
```

This opens a browser for GitHub authentication.

### 2. Publish

```bash
npx molthub@latest publish . \
  --slug ggshield-scanner \
  --name "ggshield Secret Scanner" \
  --version 1.0.0 \
  --changelog "Initial release: secret scanning for AI agents"
```

### 3. Verify

```bash
npx molthub@latest search "ggshield"
```

Visit: https://clawdhub.com/skills/ggshield-scanner

## Project Structure

```
ggshield-skill/
├── SKILL.md           # MoltHub metadata + documentation
├── ggshield_skill.py  # Main Python implementation
├── pyproject.toml     # uv/pip dependencies
├── README.md          # This file
├── .env               # Your API key (not committed)
├── .env.example       # Example .env file
├── .gitignore
└── LICENSE            # MIT
```

## How It Works

The skill is a Python class that:

1. **Wraps ggshield CLI** - Calls `ggshield` via subprocess
2. **Handles errors gracefully** - Missing API key, ggshield not installed, file not found
3. **Returns user-friendly messages** - With emoji indicators (✅ ❌ 🔍)
4. **Async methods** - Compatible with async AI agent frameworks

```python
class GGShieldSkill:
    async def scan_repo(self, path: str) -> str: ...
    async def scan_file(self, path: str) -> str: ...
    async def scan_staged(self) -> str: ...
    async def install_hooks(self, hook_type: str = "pre-commit") -> str: ...
    async def scan_docker(self, image: str) -> str: ...
```

## Privacy & Security

- **Local scanning** - ggshield sends only metadata (hashes, not actual secrets) to GitGuardian
- **Enterprise option** - GitGuardian Enterprise supports on-premise scanning with zero data transmission
- See [ggshield privacy docs](https://docs.gitguardian.com/ggshield-docs/) for details

## Related

- [ggshield GitHub](https://github.com/GitGuardian/ggshield)
- [GitGuardian Dashboard](https://dashboard.gitguardian.com)
- [MoltHub Registry](https://clawdhub.com)

## License

MIT
