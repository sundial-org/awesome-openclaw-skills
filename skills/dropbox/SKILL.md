# Dropbox Manager Skill

Manage Dropbox files via MCP server and CLI. Swift-native implementation using SwiftyDropbox SDK with OAuth 2.0 PKCE and secure Keychain token storage.

## Setup

### Prerequisites

```bash
# Clone and build Dropbook
git clone https://github.com/RyanLisse/Dropbook.git
cd Dropbook
make build
```

### Authentication

#### Option 1: OAuth Login with Keychain (Recommended)

Use the interactive OAuth flow with secure Keychain storage:

```bash
export DROPBOX_APP_KEY="your_dropbox_app_key"
export DROPBOX_APP_SECRET="your_dropbox_app_secret"
make login
# or: swift run dropbook login
```

This will:
1. Generate PKCE code verifier and challenge (SHA256, RFC 7636)
2. Open an authorization URL with state parameter (CSRF protection)
3. Prompt you to paste the authorization code
4. Exchange code for access and refresh tokens
5. **Save tokens to macOS Keychain** (hardware-backed encryption)
6. Fall back to `~/.dropbook/auth.json` if Keychain unavailable
7. Enable automatic token refreshing

**Security Features (RFC 9700 compliant):**
- PKCE with S256 challenge method
- State parameter for CSRF protection
- Keychain storage with `kSecAttrAccessibleWhenUnlocked`
- CryptoKit for cryptographic operations

#### Option 2: Environment Variables (Legacy)

```bash
export DROPBOX_APP_KEY="your_dropbox_app_key"
export DROPBOX_APP_SECRET="your_dropbox_app_secret"
export DROPBOX_ACCESS_TOKEN="your_dropbox_access_token"
```

**Note**: Manual tokens don't support automatic refreshing. Use OAuth login for production use.

### Logout

Clear stored tokens from both Keychain and file storage:

```bash
make logout
# or: swift run dropbook logout
```

## MCP Server (Recommended)

Start the MCP server:

```bash
make mcp
# or: ./.build/debug/dropbook mcp
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `list_directory` | List files and folders in a Dropbox directory |
| `search` | Search for files by name or content |
| `upload` | Upload a file to Dropbox |
| `download` | Download a file from Dropbox |
| `delete` | Delete a file or folder (moves to trash) |
| `get_account_info` | Get account name and email |
| `read_file` | Read contents of a text file |

#### list_directory

List files and folders in a Dropbox directory.

**Parameters:**
- `path` (string, optional): Directory path. Default: "/"

**Response:**
```json
{
  "files": [
    {"type": "file", "name": "doc.pdf", "path": "/Docs/doc.pdf", "size": 1024},
    {"type": "folder", "name": "Projects", "path": "/Projects"}
  ]
}
```

#### search

Search for files by name or content.

**Parameters:**
- `query` (string, required): Search term
- `path` (string, optional): Path to search within. Default: "/"

**Response:**
```json
{
  "count": 2,
  "results": [
    {"matchType": "filename", "metadata": {"name": "report.pdf", "path": "/Docs/report.pdf"}}
  ]
}
```

#### upload

Upload a file to Dropbox.

**Parameters:**
- `localPath` (string, required): Absolute path to local file
- `remotePath` (string, required): Destination in Dropbox
- `overwrite` (boolean, optional): Replace if exists. Default: false

**Response:**
```json
{
  "uploaded": true,
  "name": "file.txt",
  "path": "/Uploads/file.txt",
  "size": 5000
}
```

#### download

Download a file from Dropbox.

**Parameters:**
- `remotePath` (string, required): File path in Dropbox
- `localPath` (string, required): Local destination path

**Response:**
```json
{
  "downloaded": true,
  "to": "/tmp/report.pdf"
}
```

#### delete

Delete a file or folder from Dropbox (moves to trash).

**Parameters:**
- `path` (string, required): Path to delete in Dropbox

**Response:**
```json
{
  "deleted": true,
  "path": "/Docs/old-file.pdf"
}
```

#### get_account_info

Get Dropbox account information.

**Parameters:** None

**Response:**
```json
{
  "name": "Ryan Lisse",
  "email": "user@example.com"
}
```

#### read_file

Read and return the contents of a text file from Dropbox.

**Parameters:**
- `path` (string, required): Path to file in Dropbox

**Response:**
Returns the file contents as text. Only works with UTF-8 encoded text files.

## CLI Commands

```bash
# Authentication
make login                 # OAuth login with Keychain storage
make logout                # Clear stored tokens

# File operations
make list                  # List root directory
swift run dropbook list /path

# Search files
swift run dropbook search "query" [path]

# Upload file
swift run dropbook upload /local/path /remote/path [--overwrite]

# Download file
swift run dropbook download /remote/path /local/path

# Start MCP server
make mcp
```

## MCP Client Configuration

### Claude Code (Project-level)

The project includes a `.mcp.json` file that configures the MCP server:

```json
{
  "mcpServers": {
    "dropbox": {
      "command": "/path/to/Dropbook/.build/debug/dropbook",
      "args": ["mcp"],
      "env": {
        "DROPBOX_APP_KEY": "${DROPBOX_APP_KEY}",
        "DROPBOX_APP_SECRET": "${DROPBOX_APP_SECRET}"
      }
    }
  }
}
```

Enable project MCP servers in Claude Code settings.json:
```json
{
  "enableAllProjectMcpServers": true
}
```

### Claude Desktop

```json
{
  "mcpServers": {
    "dropbox": {
      "command": "/path/to/dropbook/.build/debug/dropbook",
      "args": ["mcp"],
      "env": {
        "DROPBOX_APP_KEY": "${DROPBOX_APP_KEY}",
        "DROPBOX_APP_SECRET": "${DROPBOX_APP_SECRET}"
      }
    }
  }
}
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `notConfigured` | Missing env vars | Set DROPBOX_APP_KEY, DROPBOX_APP_SECRET |
| `invalidArguments` | Missing required params | Check tool parameters |
| `notFound` | Path doesn't exist | Use `list_directory` to verify paths |
| `itemNotFound` | No token in Keychain | Run `make login` to authenticate |

## Architecture

```
Dropbook/
├── Sources/
│   ├── DropbookCore/           # Business logic (actor-based)
│   │   ├── Auth/               # Keychain & file token storage
│   │   ├── Config/             # Configuration management
│   │   ├── Models/             # Domain models
│   │   └── Services/           # DropboxService actor
│   ├── DropbookCLI/            # CLI adapter
│   │   └── Commands/           # Login, logout, file commands
│   └── DropbookMCP/            # MCP server
├── dropbox-skill/              # Skill documentation
├── Makefile                    # Build automation
├── .mcp.json                   # MCP server configuration
└── Package.swift
```

## Bulk Operations with rclone

For large-scale operations like backups, syncing, or bulk transfers, use [rclone](https://rclone.org/) - a powerful cloud sync tool with native Dropbox support.

### Install rclone

```bash
brew install rclone
```

### Configure rclone for Dropbox

```bash
# Interactive setup (opens browser for OAuth)
rclone authorize dropbox

# Save the token output to config
mkdir -p ~/.config/rclone
cat > ~/.config/rclone/rclone.conf << 'EOF'
[dropbox]
type = dropbox
token = {"access_token":"...paste token here..."}
EOF
```

### Backup to Network Drive / Time Capsule

```bash
# Full backup with progress
rclone copy dropbox: /Volumes/TimeCapsule/Dropbox-Backup \
    --progress \
    --transfers 4 \
    --checkers 8 \
    --retries 10 \
    --log-file /tmp/dropbox-backup.log

# Sync (mirror - deletes files not in source)
rclone sync dropbox: /Volumes/Backup/Dropbox --progress

# Check what would be copied (dry run)
rclone copy dropbox: /Volumes/Backup --dry-run
```

### Common rclone Commands

```bash
# List remote contents
rclone lsd dropbox:              # List directories
rclone ls dropbox:               # List all files
rclone size dropbox:             # Calculate total size

# Copy operations
rclone copy dropbox:folder /local/path    # Download folder
rclone copy /local/path dropbox:folder    # Upload folder

# Sync (bidirectional)
rclone bisync dropbox: /local/path --resync

# Mount as filesystem (macOS - requires macFUSE)
rclone mount dropbox: /mnt/dropbox --vfs-cache-mode full
```

### rclone Flags for Reliability

| Flag | Description |
|------|-------------|
| `--progress` | Show real-time transfer progress |
| `--transfers 4` | Number of parallel transfers |
| `--checkers 8` | Number of parallel checkers |
| `--retries 10` | Retry failed operations |
| `--low-level-retries 20` | Retry low-level errors |
| `--log-file path` | Write logs to file |
| `--dry-run` | Show what would be done |
| `--checksum` | Verify with checksums |

### Rate Limiting

Dropbox has strict API rate limits. If you see `too_many_requests` errors:

```bash
# Use bandwidth limiting
rclone copy dropbox: /backup --bwlimit 1M

# Or add delays between operations
rclone copy dropbox: /backup --tpslimit 2
```

rclone handles rate limits automatically with exponential backoff.

## Best Practices

1. **Use OAuth login** - Secure Keychain storage with automatic token refresh
2. **Use MCP for agents** - More reliable for programmatic access
3. **Use rclone for bulk ops** - Better for backups and large transfers
4. **Validate paths first** - Use `list_directory` before operations
5. **Handle errors gracefully** - Check responses for error fields
6. **Respect rate limits** - Add delays between bulk operations
7. **Use absolute paths** - Always provide full paths for file operations

## Security

- **Keychain Storage**: Tokens stored with hardware-backed encryption
- **PKCE**: Proof Key for Code Exchange prevents authorization code interception
- **State Parameter**: CSRF protection for OAuth flow
- **Token Refresh**: Automatic refresh before expiration
- **CryptoKit**: Modern Swift cryptographic library

## Dependencies

- **SwiftyDropbox** (v10.2.4+): Official Dropbox Swift SDK
- **MCP (swift-sdk)**: Model Context Protocol SDK
- **CryptoKit**: Apple's cryptographic framework
- **rclone** (optional): For bulk operations and backups (`brew install rclone`)

## See Also

- [Dropbook GitHub](https://github.com/RyanLisse/Dropbook)
- [CLAUDE.md](../CLAUDE.md) - Full project documentation
- [Dropbox API Docs](https://www.dropbox.com/developers/documentation)
- [rclone Dropbox Docs](https://rclone.org/dropbox/) - Bulk sync and backup
- [RFC 7636 - PKCE](https://datatracker.ietf.org/doc/html/rfc7636)
- [RFC 9700 - OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/rfc9700)
