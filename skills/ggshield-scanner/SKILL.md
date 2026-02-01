---
name: ggshield-scanner
description: Detect 500+ types of hardcoded secrets (API keys, credentials, tokens) before they leak into git. Wraps GitGuardian's ggshield CLI.
homepage: https://github.com/GitGuardian/ggshield-skill
metadata:
  clawdbot:
    requires:
      bins: ["ggshield"]
      env: ["GITGUARDIAN_API_KEY"]
---

# ggshield Secret Scanner

## Overview

**ggshield** is a CLI tool that detects hardcoded secrets in your codebase. This Moltbot skill brings secret scanning capabilities to your AI agent.

### What Are "Secrets"?

Secrets are sensitive credentials that should NEVER be committed to version control:
- AWS Access Keys, GCP Service Accounts, Azure credentials
- API tokens (GitHub, Slack, Stripe, etc.)
- Database passwords and connection strings
- Private encryption keys and certificates
- OAuth tokens and refresh tokens
- PayPal/Stripe API keys
- Email server credentials

### Why This Matters

A single leaked secret can:
- 🔓 Compromise your infrastructure
- 💸 Incur massive cloud bills (attackers abuse your AWS account)
- 📊 Expose customer data (GDPR/CCPA violation)
- 🚨 Trigger security incidents and audits

ggshield catches these **before** they reach your repository.

## Features

### Commands Available

#### 1. `scan-repo`
Scans an entire git repository for secrets (including history).

```
@clawd scan-repo /path/to/my/project
```

**Output**:
```
🔍 Scanning repository...
✅ Repository clean: 1,234 files scanned, 0 secrets found
```

**Output on detection**:
```
❌ Found 2 secrets:

- AWS Access Key ID in config/prod.py:42
- Slack API token in .env.backup:8

Use 'ggshield secret ignore --last-found' to ignore, or remove them.
```

#### 2. `scan-file`
Scans a single file for secrets.

```
@clawd scan-file /path/to/config.py
```

#### 3. `scan-staged`
Scans only staged git changes (useful pre-commit check).

```
@clawd scan-staged
```

This runs on your `git add`-ed changes only (fast!).

#### 4. `install-hooks`
Installs ggshield as a git pre-commit hook.

```
@clawd install-hooks
```

After this, every commit is automatically scanned:
```
$ git commit -m "Add config"
🔍 Running ggshield pre-commit hook...
❌ Secrets detected! Commit blocked.
Remove the secrets and try again.
```

#### 5. `scan-docker`
Scans Docker images for secrets in their layers.

```
@clawd scan-docker my-app:latest
```

## Installation

### Prerequisites

1. **ggshield CLI**: Install via pip
   ```bash
   pip install ggshield>=1.15.0
   ```

2. **GitGuardian API Key**: Required for secret detection
   - Sign up: https://dashboard.gitguardian.com (free)
   - Generate API key in Settings
   - Set environment variable:

```bash
export GITGUARDIAN_API_KEY="your-api-key-here"
```

3. **Python 3.8+**: Required by ggshield

### Install Skill

```bash
clawdhub install ggshield-scanner
```

The skill is now available in your Moltbot workspace.

### In Your Moltbot Workspace

Start a new Moltbot session to pick up the skill:

```bash
moltbot start
# or via messaging: @clawd list-skills
```

## Usage Patterns

### Pattern 1: Before Pushing (Security Check)

```
Dev: @clawd scan-repo .
Moltbot: ✅ Repository clean. All good to push!

Dev: git push
```

### Pattern 2: Audit Existing Repo

```
Dev: @clawd scan-repo ~/my-old-project
Moltbot: ❌ Found 5 secrets in history!
         - AWS keys in config/secrets.json
         - Database password in docker-compose.yml
         - Slack webhook in .env.example
Moltbot: Recommendation: Rotate these credentials immediately.
         Consider using git-filter-repo to remove from history.
```

### Pattern 3: Pre-Commit Enforcement

```
Dev: @clawd install-hooks
Moltbot: ✅ Installed pre-commit hook

Dev: echo "SECRET_TOKEN=xyz" > config.py
Dev: git add config.py
Dev: git commit -m "Add config"
Moltbot: ❌ Pre-commit hook detected secret!
Dev: rm config.py && git reset
Dev: (add config to .gitignore and to environment variables instead)
Dev: git commit -m "Add config" # Now works!
```

### Pattern 4: Docker Image Security

```
Dev: @clawd scan-docker my-api:v1.2.3
Moltbot: ✅ Docker image clean
```

## Configuration

### Environment Variables

These are required for the skill to work:

| Variable | Value | Where to Set |
| :-- | :-- | :-- |
| `GITGUARDIAN_API_KEY` | Your API key from https://dashboard.gitguardian.com | `~/.bashrc` or `~/.zshrc` |
| `GITGUARDIAN_ENDPOINT` | `https://api.gitguardian.com` (default, optional) | Usually not needed |

### Optional ggshield Config

Create `~/.gitguardian/.gitguardian.yml` for persistent settings:

```yaml
verbose: false
output-format: json
exit-code: true
```

For details: https://docs.gitguardian.com/ggshield-docs/

## Privacy & Security

### What Data is Sent to GitGuardian?

✅ **ONLY metadata is sent**:

- Hash of the secret pattern (not the actual secret)
- File path (relative path only)
- Line number

❌ **NEVER sent**:

- Your actual secrets or credentials
- File contents
- Private keys
- Credentials

**Reference**: GitGuardian Enterprise customers can use on-premise scanning with no data sent anywhere.

### How Secrets Are Detected

ggshield uses:

1. **Entropy-based detection**: Identifies high-entropy strings (random tokens)
2. **Pattern matching**: Looks for known secret formats (AWS key prefixes, etc.)
3. **Public CVEs**: Cross-references disclosed secrets
4. **Machine learning**: Trained on leaked secrets database

## Troubleshooting

### "ggshield: command not found"

ggshield is not installed or not in your PATH.

**Fix**:

```bash
pip install ggshield
which ggshield  # Should return a path
```

### "GITGUARDIAN_API_KEY not found"

The environment variable is not set.

**Fix**:

```bash
export GITGUARDIAN_API_KEY="your-key"
# For persistence, add to ~/.bashrc or ~/.zshrc:
echo 'export GITGUARDIAN_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

### "401 Unauthorized"

API key is invalid or expired.

**Fix**:

```bash
# Test the API key
ggshield auth status

# If invalid, regenerate at https://dashboard.gitguardian.com → API Tokens
# Then: export GITGUARDIAN_API_KEY="new-key"
```

### "Slow on large repositories"

Scanning a 50GB monorepo takes time. ggshield is doing a lot of work.

**Workaround**:

```bash
# Scan only staged changes (faster):
@clawd scan-staged

# Or specify a subdirectory:
@clawd scan-file ./app/config.py
```

## Advanced Topics

### Ignoring False Positives

Sometimes ggshield flags a string that's NOT a secret (e.g., a test key):

```bash
# Ignore the last secret found
ggshield secret ignore --last-found

# Ignore all in a file
ggshield secret ignore --path ./config-example.py
```

This creates `.gitguardian/config.json` with ignore rules.

### Integrating with CI/CD

You can add secret scanning to GitHub Actions / GitLab CI:

```yaml
# .github/workflows/secret-scan.yml
name: Secret Scan
on: [push]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install ggshield
      - run: ggshield secret scan repo .
        env:
          GITGUARDIAN_API_KEY: ${{ secrets.GITGUARDIAN_API_KEY }}
```

### Enterprise: On-Premise Scanning

If your company uses GitGuardian Enterprise, you can scan without sending data to the cloud:

```bash
export GITGUARDIAN_ENDPOINT="https://your-instance.gitguardian.com"
export GITGUARDIAN_API_KEY="your-enterprise-key"
```

## Related Resources

- **ggshield Documentation**: https://docs.gitguardian.com/ggshield-docs/
- **GitGuardian Dashboard**: https://dashboard.gitguardian.com (view all secrets found)
- **Moltbot Skills**: https://docs.molt.bot/tools/clawdhub
- **Secret Management Best Practices**: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html

## Support

- **Bug reports**: https://github.com/GitGuardian/ggshield-skill/issues
- **Questions**: Open an issue or comment on ClawdHub
- **ggshield issues**: https://github.com/GitGuardian/ggshield/issues

## License

MIT License - See LICENSE file

## Contributors

- GitGuardian Team
- [Your contributions welcome!]

---

**Version**: 1.0.0
**Last updated**: January 2026
**Maintainer**: GitGuardian
