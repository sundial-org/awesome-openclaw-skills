---
name: proton-pass
description: Manage Proton Pass vaults, items (logins, SSH keys, aliases, notes), passwords, SSH agent integration, and secret injection into applications. Use when working with Proton Pass for password management, SSH key storage, secret injection (run commands with secrets, inject into templates), environment variable injection, or generating secure passwords. Supports vault/item CRUD, sharing, member management, SSH agent operations, TOTP generation, secret references (pass://vault/item/field), template injection, and command execution with secrets.
---

# Proton Pass CLI

Comprehensive password and secret management via the Proton Pass CLI. Manage vaults, items, SSH keys, share credentials, inject secrets, and integrate with SSH workflows.

## Installation

### Quick install

macOS/Linux:
```bash
curl -fsSL https://proton.me/download/pass-cli/install.sh | bash
```

Windows:
```powershell
Invoke-WebRequest -Uri https://proton.me/download/pass-cli/install.ps1 -OutFile install.ps1; .\install.ps1
```

### Homebrew (macOS)

```bash
brew install protonpass/tap/pass-cli
```

**Note:** Package manager installations (Homebrew, etc.) do not support `pass-cli update` command or track switching.

### Verify installation

```bash
pass-cli --version
```

## Authentication

### Web login (recommended)

Default authentication method supporting all login flows (SSO, U2F):

```bash
pass-cli login
# Open the URL displayed in your browser and complete authentication
```

### Interactive login

Terminal-based authentication (supports password + TOTP, but not SSO or U2F):

```bash
pass-cli login --interactive user@proton.me
```

#### Environment variables for automation

```bash
# Credentials as plain text (less secure)
export PROTON_PASS_PASSWORD='your-password'
export PROTON_PASS_TOTP='123456'
export PROTON_PASS_EXTRA_PASSWORD='your-extra-password'

# Or from files (more secure)
export PROTON_PASS_PASSWORD_FILE='/secure/password.txt'
export PROTON_PASS_TOTP_FILE='/secure/totp.txt'
export PROTON_PASS_EXTRA_PASSWORD_FILE='/secure/extra-password.txt'

pass-cli login --interactive user@proton.me
```

### Verify session

```bash
pass-cli info          # Show session info
pass-cli test          # Test connection
```

### Logout

```bash
pass-cli logout        # Normal logout
pass-cli logout --force  # Force local cleanup if remote fails
```

## Vault Management

### List vaults

```bash
pass-cli vault list
pass-cli vault list --output json
```

### Create vault

```bash
pass-cli vault create --name "Vault Name"
```

### Update vault

```bash
# By share ID
pass-cli vault update --share-id "abc123def" --name "New Name"

# By name
pass-cli vault update --vault-name "Old Name" --name "New Name"
```

### Delete vault

⚠️ **Warning:** Permanently deletes vault and all items.

```bash
# By share ID
pass-cli vault delete --share-id "abc123def"

# By name
pass-cli vault delete --vault-name "Old Vault"
```

### Share vault

```bash
# Share with viewer access (default)
pass-cli vault share --share-id "abc123def" colleague@company.com

# Share with specific role
pass-cli vault share --vault-name "Team Vault" colleague@company.com --role editor

# Roles: viewer, editor, manager
```

### Manage vault members

```bash
# List members
pass-cli vault member list --share-id "abc123def"
pass-cli vault member list --vault-name "Team Vault" --output json

# Update member role
pass-cli vault member update --share-id "abc123def" --member-share-id "member123" --role editor

# Remove member
pass-cli vault member remove --share-id "abc123def" --member-share-id "member123"
```

### Transfer vault ownership

```bash
pass-cli vault transfer --share-id "abc123def" "member_share_id_xyz"
pass-cli vault transfer --vault-name "My Vault" "member_share_id_xyz"
```

## Item Management

### List items

```bash
# List from specific vault
pass-cli item list "Vault Name"
pass-cli item list --share-id "abc123def"

# List with default vault (if configured)
pass-cli item list
```

### View item

```bash
# By IDs
pass-cli item view --share-id "abc123def" --item-id "item456"

# By names
pass-cli item view --vault-name "MyVault" --item-title "MyItem"

# Using Pass URI
pass-cli item view "pass://abc123def/item456"
pass-cli item view "pass://MyVault/MyItem"

# View specific field
pass-cli item view "pass://abc123def/item456/password"
pass-cli item view --share-id "abc123def" --item-id "item456" --field "username"

# Output format
pass-cli item view --share-id "abc123def" --item-id "item456" --output json
```

### Create login item

```bash
# Basic login
pass-cli item create login \
  --share-id "abc123def" \
  --title "GitHub Account" \
  --username "myuser" \
  --password "mypassword" \
  --url "https://github.com"

# With vault name
pass-cli item create login \
  --vault-name "Personal" \
  --title "Account" \
  --username "user" \
  --email "user@example.com" \
  --url "https://example.com"

# With generated password
pass-cli item create login \
  --share-id "abc123def" \
  --title "New Account" \
  --username "myuser" \
  --generate-password \
  --url "https://example.com"

# Custom password generation: "length,uppercase,symbols"
pass-cli item create login \
  --vault-name "Work" \
  --title "Secure Account" \
  --username "myuser" \
  --generate-password="20,true,true" \
  --url "https://example.com"

# Generate passphrase
pass-cli item create login \
  --share-id "abc123def" \
  --title "Account" \
  --username "user" \
  --generate-passphrase="5" \
  --url "https://example.com"
```

#### Login template

```bash
# Get template structure
pass-cli item create login --get-template > template.json

# Create from template
pass-cli item create login --from-template template.json --share-id "abc123def"

# Create from stdin
echo '{"title":"Test","username":"user","password":"pass","urls":["https://test.com"]}' | \
  pass-cli item create login --share-id "abc123def" --from-template -
```

Template format:
```json
{
  "title": "Item Title",
  "username": "optional_username",
  "email": "optional_email@example.com",
  "password": "optional_password",
  "urls": ["https://example.com", "https://app.example.com"]
}
```

### Create SSH key items

#### Generate new SSH key

```bash
# Generate Ed25519 key (recommended)
pass-cli item create ssh-key generate \
  --share-id "abc123def" \
  --title "GitHub Deploy Key"

# Using vault name
pass-cli item create ssh-key generate \
  --vault-name "Development Keys" \
  --title "GitHub Deploy Key"

# Generate RSA 4096 key with comment
pass-cli item create ssh-key generate \
  --share-id "abc123def" \
  --title "Production Server" \
  --key-type rsa4096 \
  --comment "prod-server-deploy"

# Key types: ed25519 (default), rsa2048, rsa4096

# With passphrase protection
pass-cli item create ssh-key generate \
  --share-id "abc123def" \
  --title "Secure Key" \
  --password

# Passphrase from environment
PROTON_PASS_SSH_KEY_PASSWORD="my-passphrase" \
  pass-cli item create ssh-key generate \
  --share-id "abc123def" \
  --title "Automated Key" \
  --password
```

#### Import existing SSH key

```bash
# Import unencrypted key
pass-cli item create ssh-key import \
  --from-private-key ~/.ssh/id_ed25519 \
  --share-id "abc123def" \
  --title "My SSH Key"

# Import with vault name
pass-cli item create ssh-key import \
  --from-private-key ~/.ssh/id_rsa \
  --vault-name "Personal Keys" \
  --title "Old RSA Key"

# Import passphrase-protected key (will prompt)
pass-cli item create ssh-key import \
  --from-private-key ~/.ssh/id_ed25519 \
  --share-id "abc123def" \
  --title "Protected Key" \
  --password

# Passphrase from environment
PROTON_PASS_SSH_KEY_PASSWORD="my-key-passphrase" \
  pass-cli item create ssh-key import \
  --from-private-key ~/.ssh/id_ed25519 \
  --share-id "abc123def" \
  --title "Automated Import" \
  --password
```

**Recommendation:** For importing passphrase-protected keys, consider removing the passphrase first since keys will be encrypted in your vault:

```bash
# Create unencrypted copy
cp ~/.ssh/id_ed25519 /tmp/id_ed25519_temp
ssh-keygen -p -f /tmp/id_ed25519_temp -N ""

# Import
pass-cli item create ssh-key import \
  --from-private-key /tmp/id_ed25519_temp \
  --share-id "abc123def" \
  --title "My SSH Key"

# Securely delete temp copy
shred -u /tmp/id_ed25519_temp  # Linux
rm -P /tmp/id_ed25519_temp     # macOS
```

### Create email alias

```bash
# Create alias
pass-cli item alias create --share-id "abc123def" --prefix "newsletter"
pass-cli item alias create --vault-name "Personal" --prefix "shopping"

# With JSON output
pass-cli item alias create --vault-name "Personal" --prefix "temp" --output json
```

### Update item

```bash
# Update single field
pass-cli item update \
  --share-id "abc123def" \
  --item-id "item456" \
  --field "password=newpassword123"

# By vault name and item title
pass-cli item update \
  --vault-name "Personal" \
  --item-title "GitHub Account" \
  --field "password=newpassword123"

# Update multiple fields
pass-cli item update \
  --share-id "abc123def" \
  --item-id "item456" \
  --field "username=newusername" \
  --field "password=newpassword" \
  --field "email=newemail@example.com"

# Rename item
pass-cli item update \
  --vault-name "Work" \
  --item-title "Old Title" \
  --field "title=New Title"

# Create/update custom fields
pass-cli item update \
  --share-id "abc123def" \
  --item-id "item456" \
  --field "api_key=sk_live_abc123" \
  --field "environment=production"
```

**Note:** Item update does not support TOTP or time fields. Use another Proton Pass client for those.

### Delete item

⚠️ **Warning:** Permanent deletion.

```bash
pass-cli item delete --share-id "abc123def" --item-id "item456"
```

### Share item

```bash
# Share with viewer access (default)
pass-cli item share --share-id "abc123def" --item-id "item456" colleague@company.com

# Share with editor access
pass-cli item share --share-id "abc123def" --item-id "item456" colleague@company.com --role editor
```

### Generate TOTP codes

```bash
# Generate all TOTPs for an item
pass-cli item totp "pass://TOTP vault/WithTOTPs"

# Specific TOTP field
pass-cli item totp "pass://TOTP vault/WithTOTPs/TOTP 1"

# JSON output
pass-cli item totp "pass://TOTP vault/WithTOTPs" --output json

# Extract specific value
pass-cli item totp "pass://TOTP vault/WithTOTPs/TOTP 1" --output json | jq -r '.["TOTP 1"]'
```

## Password Generation & Analysis

### Generate passwords

```bash
# Random password (default settings)
pass-cli password generate random

# Custom random password
pass-cli password generate random --length 20 --numbers true --uppercase true --symbols true

# Simple password without symbols
pass-cli password generate random --length 16 --symbols false

# Generate passphrase
pass-cli password generate passphrase

# Custom passphrase
pass-cli password generate passphrase --count 5
pass-cli password generate passphrase --count 4 --separator hyphens
pass-cli password generate passphrase --count 4 --capitalize true --numbers true
```

### Analyze password strength

```bash
# Score a password
pass-cli password score "mypassword123"

# JSON output
pass-cli password score "MySecureP@ssw0rd*" --output json
```

Example JSON output:
```json
{
  "numeric_score": 51.666666666666664,
  "password_score": "Vulnerable",
  "penalties": [
    "ContainsCommonPassword",
    "Consecutive"
  ]
}
```

## SSH Agent Integration

### Load SSH keys into existing agent

Load Proton Pass SSH keys into your existing SSH agent:

```bash
# Load all SSH keys
pass-cli ssh-agent load

# Load from specific vault
pass-cli ssh-agent load --share-id MY_SHARE_ID
pass-cli ssh-agent load --vault-name MySshKeysVault
```

**Prerequisite:** Ensure `SSH_AUTH_SOCK` environment variable is defined.

### Run Proton Pass CLI as SSH agent

Start Proton Pass CLI as a standalone SSH agent:

```bash
# Start agent
pass-cli ssh-agent start

# From specific vault
pass-cli ssh-agent start --share-id MY_SHARE_ID
pass-cli ssh-agent start --vault-name MySshKeysVault

# Custom socket path
pass-cli ssh-agent start --socket-path /custom/path/agent.sock

# Custom refresh interval (default 3600 seconds)
pass-cli ssh-agent start --refresh-interval 7200  # 2 hours
```

After starting, export the socket:
```bash
export SSH_AUTH_SOCK=/Users/youruser/.ssh/proton-pass-agent.sock
```

#### Auto-create SSH key items (v1.3.0+)

Automatically save SSH keys added via `ssh-add`:

```bash
# Enable auto-creation
pass-cli ssh-agent start --create-new-identities MySshKeysVault

# In another terminal
export SSH_AUTH_SOCK=$HOME/.ssh/proton-pass-agent.sock
ssh-add ~/.ssh/my_new_key
# Key is now automatically saved to Proton Pass!
```

### Troubleshooting SSH

#### ssh-copy-id fails with many keys

Force password authentication:
```bash
ssh-copy-id -o PreferredAuthentications=password -o PubkeyAuthentication=no user@server
```

## Pass URI Syntax (Secret References)

Reference secrets using the format: `pass://vault/item/field`

### Syntax

```
pass://<vault-identifier>/<item-identifier>/<field-name>
```

- **vault-identifier:** Vault's Share ID or name
- **item-identifier:** Item's ID or title
- **field-name:** Specific field to retrieve (required)

### Examples

```bash
# By names
pass://Work/GitHub Account/password
pass://Personal/Email Login/username

# By IDs
pass://AbCdEf123456/XyZ789/password
pass://ShareId123/ItemId456/api_key

# Mixed (vault by name, item by ID)
pass://Work/XyZ789/password

# Custom fields (case-sensitive)
pass://Work/API Keys/api_key
pass://Production/Database/connection_string
```

### Common fields

- `username` - Username/login name
- `password` - Password
- `email` - Email address
- `url` - Website URL
- `note` - Additional notes
- `totp` - TOTP secret (for 2FA)
- Custom fields with any name (case-sensitive)

### Rules

- All three components (vault/item/field) are required
- Names with spaces are supported
- Resolution is case-sensitive
- If duplicates exist, first match is used (prefer IDs for precision)

**Invalid formats:**
```bash
pass://vault/item              # Missing field name
pass://vault/item/             # Trailing slash
pass://vault/                  # Missing item and field
```

## Secret Injection

### Run commands with secrets (`run`)

Execute commands with secrets from Proton Pass injected as environment variables.

**Synopsis:**
```bash
pass-cli run [--env-file FILE]... [--no-masking] -- COMMAND [ARGS...]
```

**How it works:**
1. Collects environment variables from current process and `.env` files
2. Scans for `pass://` URIs in variable values
3. Resolves secrets from Proton Pass
4. Replaces URIs with actual secret values
5. Masks secrets in output (unless `--no-masking`)
6. Executes command with resolved environment
7. Forwards stdin/stdout/stderr and signals (SIGTERM/SIGINT)

**Arguments:**
- `--env-file FILE` - Load environment variables from dotenv file (can specify multiple, processed in order)
- `--no-masking` - Disable automatic masking of secrets in output
- `COMMAND [ARGS...]` - Command to execute (must come after `--`)

#### Basic usage

```bash
# Set secret reference in environment
export DB_PASSWORD='pass://Production/Database/password'

# Run application with injected secret
pass-cli run -- ./my-app
```

#### Using .env files

Create `.env`:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=admin
DB_PASSWORD=pass://Production/Database/password
API_KEY=pass://Work/External API/api_key
```

Run:
```bash
pass-cli run --env-file .env -- ./my-app

# Multiple env files (later override earlier)
pass-cli run \
  --env-file base.env \
  --env-file secrets.env \
  --env-file local.env \
  -- ./my-app
```

#### Multiple secrets in single value

```bash
# Mix secrets with plain text
DATABASE_URL="postgresql://user:pass://vault/db/password@localhost/db"
API_ENDPOINT="https://api.example.com?key=pass://vault/api/key"
```

#### Secret masking

**Default (masked):**
```bash
pass-cli run -- ./my-app
# If app logs: API_KEY: sk_live_abc123
# Output shows: API_KEY: <concealed by Proton Pass>
```

**Unmasked:**
```bash
pass-cli run --no-masking -- ./my-app
```

#### Running with arguments

```bash
pass-cli run -- ./my-app --config production --verbose
```

#### CI/CD integration

```bash
#!/bin/bash
# Load production secrets
pass-cli run --env-file .env.production -- ./deploy.sh
```

### Inject secrets into templates (`inject`)

Process template files and replace secret references with actual values using handlebars-style syntax.

**Synopsis:**
```bash
pass-cli inject [--in-file FILE] [--out-file FILE] [--force] [--file-mode MODE]
```

**How it works:**
1. Reads template from `--in-file` or stdin
2. Finds `{{ pass://vault/item/field }}` patterns
3. Resolves secrets from Proton Pass
4. Replaces references with actual values
5. Outputs to `--out-file` or stdout
6. Sets file permissions (Unix)

**Arguments:**
- `--in-file`, `-i` - Path to template file (or stdin)
- `--out-file`, `-o` - Path to write output (or stdout)
- `--force`, `-f` - Overwrite output file without prompting
- `--file-mode` - Set file permissions (Unix, default: `0600`)

#### Template syntax

**Important:** Use double braces `{{ }}` (unlike `run` which uses bare `pass://`)

```yaml
# config.yaml.template
database:
  host: localhost
  username: {{ pass://Production/Database/username }}
  password: {{ pass://Production/Database/password }}

api:
  key: {{ pass://Work/API Keys/api_key }}
  secret: {{ pass://Work/API Keys/secret }}

# This comment with pass://fake/uri is ignored
# Only {{ }} wrapped references are processed
```

#### Inject to stdout

```bash
pass-cli inject --in-file config.yaml.template
```

#### Inject to file

```bash
pass-cli inject \
  --in-file config.yaml.template \
  --out-file config.yaml

# Overwrite existing
pass-cli inject \
  --in-file config.yaml.template \
  --out-file config.yaml \
  --force
```

#### Read from stdin

```bash
cat template.txt | pass-cli inject

# Or with heredoc
pass-cli inject << EOF
{
  "database": {
    "password": "{{ pass://Production/Database/password }}"
  }
}
EOF
```

#### Custom file permissions

```bash
pass-cli inject \
  --in-file template.txt \
  --out-file config.txt \
  --file-mode 0644
```

#### JSON template example

```json
{
  "database": {
    "host": "localhost",
    "password": "{{ pass://Production/Database/password }}"
  },
  "api": {
    "key": "{{ pass://Work/API/key }}"
  }
}
```

## Settings Management

Configure persistent preferences:

### View settings

```bash
pass-cli settings view
```

### Set default vault

```bash
# By name
pass-cli settings set default-vault --vault-name "Personal Vault"

# By share ID
pass-cli settings set default-vault --share-id "3GqM1RhVZL8uXR_abc123"
```

**Affected commands:** `item list`, `item view`, `item totp`, `item create`, `item update`, etc.

### Set default output format

```bash
pass-cli settings set default-format human
pass-cli settings set default-format json
```

**Affected commands:** `item list`, `item view`, `item totp`, `vault list`, etc.

### Unset defaults

```bash
pass-cli settings unset default-vault
pass-cli settings unset default-format
```

## Share Management

### List all shares

```bash
pass-cli share list
pass-cli share list --output json
```

Shows all resources (vaults and items) shared with you and your role.

## Invitation Management

### List pending invitations

```bash
pass-cli invite list
pass-cli invite list --output json
```

### Accept invitation

```bash
pass-cli invite accept --invite-token "abc123def456"
```

### Reject invitation

```bash
pass-cli invite reject --invite-token "abc123def456"
```

## User & Session Info

### View session info

```bash
pass-cli info
```

Shows: Release track, User ID, Username, Email.

### View detailed user info

```bash
pass-cli user info
pass-cli user info --output json
```

Shows: Account details, subscription, storage usage.

### Test connection

```bash
pass-cli test
```

Verifies session validity and API connectivity.

## Updates

**Note:** Only for manual installations (not package managers).

### Update to latest version

```bash
pass-cli update
pass-cli update --yes  # Skip confirmation
```

### Change release track

```bash
# Switch to beta
pass-cli update --set-track beta
pass-cli update

# Switch back to stable
pass-cli update --set-track stable
pass-cli update
```

### Disable automatic update checks

```bash
export PROTON_PASS_NO_UPDATE_CHECK=1
```

## Object Types

### Share

A Share represents the relationship between a user and a resource (vault or item). Defines access and permissions.

- **Vault shares:** Access to entire vault and all items within it
- **Item shares:** Access to a single specific item only
- **Roles:**
  - **Viewer:** Read-only access
  - **Editor:** Read and write, can manage items (but not share or manage members)
  - **Manager:** Full control including sharing and member management
  - **Owner:** Created the vault, only one who can delete it

### Vault

A container that organizes items. Items exist in exactly one vault.

### Item Types

- **Login:** Username/password credentials with URLs, TOTP support
- **Note:** Secure text notes
- **Credit Card:** Payment card information (encrypted)
- **Identity:** Personal information about a person
- **Alias:** Email aliases for privacy protection
- **SSH Key:** SSH private keys for authentication
- **Wifi:** Credentials to access a WiFi network

**Note:** Items are identified by Item ID, but this ID is only unique when combined with Share ID (ShareID + ItemID = globally unique).

## Best Practices

### Security

- Use web login for maximum compatibility (SSO, U2F)
- Generate unique passwords for each account
- Use SSH keys stored in Pass instead of local filesystem
- Logout on shared systems
- Regularly review share permissions

### Organization

- Create separate vaults for different contexts (work, personal)
- Use descriptive titles for items and vaults
- Set default vault for frequently used vault
- Configure default output format (JSON for scripts, human for interactive)

### Automation

- Store credentials in files (not env vars) for better security
- Use Pass URIs for programmatic secret access
- Leverage JSON output for scripting
- Include `pass-cli logout` in automation cleanup

### Sharing

- Use principle of least privilege (start with viewer)
- Prefer vault shares for ongoing collaboration
- Use item shares for specific, limited access
- Regularly audit members and permissions

## Docker Usage

Running in Docker containers requires filesystem key storage (keyring unavailable):

```bash
# 1. Ensure logged out
pass-cli logout --force

# 2. Set filesystem key provider
export PROTON_PASS_KEY_PROVIDER=fs

# 3. Login as normal
pass-cli login
```

**Why filesystem storage?**
- Containers cannot access kernel secret service
- D-Bus unavailable in headless environments
- Filesystem storage is the only option

⚠️ **Security note:** Key stored side-by-side with encrypted data. Secure your container environment.

## Troubleshooting

### Authentication issues

```bash
# Check session status
pass-cli info
pass-cli test

# Re-authenticate
pass-cli logout
pass-cli login
```

### Network issues

- Verify internet connectivity
- Check firewall settings for Proton domains
- Test with `pass-cli test`

### Permission errors

- Verify your role: `pass-cli share list`
- Ensure you have required permissions for the operation
- Contact vault owner to adjust permissions

### Missing resources

- Check you're looking in the right vault
- Verify resource hasn't been deleted
- Confirm access hasn't been revoked
- Check pending invitations: `pass-cli invite list`

### Secret reference resolution errors

**"Invalid reference format":**
- Ensure format is `pass://vault/item/field`
- Check for trailing slashes
- Verify all three components present

**"Secret reference requires a field name":**
- Add field name: `pass://vault/item/field` (not `pass://vault/item`)

**"Field not found":**
- Verify field exists: `pass-cli item view --share-id <id> --item-id <id>`
- Check field name spelling (case-sensitive)

**Reference not found:**
1. Check vault access: `pass-cli vault list`
2. Verify item exists: `pass-cli item list --share-id <id>`
3. Confirm field name: `pass-cli item view <uri>`

## Configuration

### Logging

```bash
# Levels: trace, debug, info, warn, error, off
export PASS_LOG_LEVEL=debug
```

**Note:** Logs are sent to `stderr` (won't interfere with piping/command integration).

### Session storage

**Default locations:**
- macOS: `~/Library/Application Support/proton-pass-cli/.session/`
- Linux: `~/.local/share/proton-pass-cli/.session/`

**Override:**
```bash
export PROTON_PASS_SESSION_DIR='/custom/path'
```

### Key storage providers

Control how encryption keys are stored with `PROTON_PASS_KEY_PROVIDER`:

#### 1. Keyring storage (default, most secure)

```bash
export PROTON_PASS_KEY_PROVIDER=keyring  # or unset
```

Uses OS secure storage:
- **macOS:** macOS Keychain
- **Linux:** Kernel-based secret storage (kernel keyring)
- **Windows:** Windows Credential Manager

**How it works:**
- Generates random 256-bit key on first run
- Stores in system keyring
- Retrieves on subsequent runs
- If keyring unavailable but session exists, forces logout for security

**Linux note:** Uses kernel keyring (no D-Bus required), works in headless environments. **Secrets cleared on reboot.**

**Docker limitation:** Containers cannot access kernel secret service. Use filesystem storage instead.

#### 2. Filesystem storage

⚠️ **Warning:** Less secure - key stored side-by-side with encrypted data.

```bash
export PROTON_PASS_KEY_PROVIDER=fs
```

Stores key in `<session-dir>/local.key` with permissions `0600`.

**Advantages:**
- Works in all environments (headless, containers)
- Survives reboots
- No dependency on system services

**When to use:**
- Docker containers
- Development/testing
- When system keyring unavailable

#### 3. Environment variable storage

⚠️ **Warning:** Key visible to other processes in same session.

```bash
export PROTON_PASS_KEY_PROVIDER=env
export PROTON_PASS_ENCRYPTION_KEY=your-secret-key
```

Derives encryption key from `PROTON_PASS_ENCRYPTION_KEY` (must be set and non-empty).

**Generate safe key:**
```bash
dd if=/dev/urandom bs=1 count=2048 2>/dev/null | sha256sum | awk '{print $1}'
```

**Advantages:**
- Portable across all environments
- No filesystem/keyring dependency
- User controls key value
- Works in CI/CD, containers, headless

**When to use:**
- CI/CD pipelines
- Containers where filesystem persistence undesirable
- Automation scripts
- Explicit control over encryption key needed

### Telemetry

**Disable telemetry:**
```bash
export PROTON_PASS_DISABLE_TELEMETRY=1
```

Or globally: [Account security settings](https://account.proton.me/pass/security) → Disable "Collect usage diagnostics"

**What's sent:** Anonymized usage data (e.g., "item created of type note") - **never** personal/sensitive data.

## Environment Variables

### Login credentials (interactive login)

```bash
export PROTON_PASS_PASSWORD='password'
export PROTON_PASS_PASSWORD_FILE='/path/to/file'
export PROTON_PASS_TOTP='123456'
export PROTON_PASS_TOTP_FILE='/path/to/file'
export PROTON_PASS_EXTRA_PASSWORD='extra-password'
export PROTON_PASS_EXTRA_PASSWORD_FILE='/path/to/file'
```

### SSH key passphrase

```bash
export PROTON_PASS_SSH_KEY_PASSWORD='passphrase'
export PROTON_PASS_SSH_KEY_PASSWORD_FILE='/path/to/file'
```

### Update checks

```bash
export PROTON_PASS_NO_UPDATE_CHECK=1
```

### Installation

```bash
export PROTON_PASS_CLI_INSTALL_DIR=/custom/path
export PROTON_PASS_CLI_INSTALL_CHANNEL=beta
```

## Common Workflows

### Create and populate a new vault

```bash
# Create vault
pass-cli vault create --name "Project Alpha"

# List to get share ID
pass-cli vault list

# Create login items
pass-cli item create login \
  --share-id "new_vault_id" \
  --title "API Key" \
  --username "api_user" \
  --generate-password \
  --url "https://api.example.com"

# Share with team
pass-cli vault share --share-id "new_vault_id" alice@team.com --role editor
```

### Import and use SSH keys

```bash
# Import existing key
pass-cli item create ssh-key import \
  --from-private-key ~/.ssh/id_ed25519 \
  --vault-name "SSH Keys" \
  --title "GitHub Key"

# Load into SSH agent
pass-cli ssh-agent load --vault-name "SSH Keys"

# Or start Pass as SSH agent
pass-cli ssh-agent start --vault-name "SSH Keys"
export SSH_AUTH_SOCK=$HOME/.ssh/proton-pass-agent.sock
```

### Scripted access to secrets

```bash
#!/bin/bash
# Automated login
export PROTON_PASS_PASSWORD_FILE="$HOME/.secrets/pass-password"
pass-cli login --interactive user@proton.me

# Retrieve secret
DB_PASSWORD=$(pass-cli item view "pass://Production/Database/password" --output json | jq -r '.password')

# Use secret
connect-to-db --password "$DB_PASSWORD"

# Cleanup
pass-cli logout
```

### Application deployment with secrets

```bash
#!/bin/bash
# Create .env.production with secret references
cat > .env.production << EOF
NODE_ENV=production
DATABASE_URL=pass://Production/Database/connection_string
API_KEY=pass://Production/API/key
STRIPE_SECRET=pass://Production/Stripe/secret_key
EOF

# Deploy application with secrets injected
pass-cli run --env-file .env.production -- npm start

# Or generate config file from template
pass-cli inject \
  --in-file config.yaml.template \
  --out-file config.yaml \
  --force

# Then run app with generated config
./app --config config.yaml
```

### CI/CD pipeline integration

```bash
#!/bin/bash
# Login with environment variable key storage
export PROTON_PASS_KEY_PROVIDER=env
export PROTON_PASS_ENCRYPTION_KEY="${CI_PASS_ENCRYPTION_KEY}"
export PROTON_PASS_PASSWORD_FILE=/run/secrets/pass-password

pass-cli login --interactive user@proton.me

# Run tests with secrets
pass-cli run --env-file .env.test -- npm test

# Deploy with secrets
pass-cli run --env-file .env.production -- ./deploy.sh

# Cleanup
pass-cli logout
```

## Notes

- **Beta status:** Proton Pass CLI is currently in beta
- **Track switching:** Only available for manual installations (not package managers)
- **Item update limitations:** Cannot update TOTP or time fields via CLI
- **Passphrase recommendations:** Passphrases optional for generated keys (already encrypted in vault)
- **SSH agent refresh:** Default 1 hour, customizable with `--refresh-interval`
- **Docker containers:** Must use filesystem key storage (`PROTON_PASS_KEY_PROVIDER=fs`)
- **Linux keyring:** Uses kernel keyring (no D-Bus), secrets cleared on reboot
- **Telemetry:** Anonymized only (no personal data), can be disabled
- **Secret masking:** Automatically masks secrets in `run` command output
- **Template syntax:** `inject` requires `{{ }}` braces, `run` uses bare `pass://` URIs
- **Item ID uniqueness:** Item ID only unique when combined with Share ID

## Command Reference Quick List

**Authentication:**
- `login`, `logout`, `info`, `test`

**Vault:**
- `vault list`, `vault create`, `vault update`, `vault delete`, `vault share`, `vault member`, `vault transfer`

**Item:**
- `item list`, `item view`, `item create`, `item update`, `item delete`, `item share`, `item totp`, `item alias`, `item attachment`

**Secret Injection:**
- `run` - Execute commands with secrets injected as environment variables
- `inject` - Process template files with secret references

**Password:**
- `password generate`, `password score`

**SSH:**
- `ssh-agent load`, `ssh-agent start`

**Settings:**
- `settings view`, `settings set`, `settings unset`

**Share & Invite:**
- `share list`, `invite list`, `invite accept`, `invite reject`

**User:**
- `user info`

**Update:**
- `update`
