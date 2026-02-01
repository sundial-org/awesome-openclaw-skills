# Microsoft 365 MCP Server

Full Microsoft 365 integration via Model Context Protocol (MCP).

## Features

### 📧 Mail (Outlook)
- List, read, send, and search emails
- Filter by folder (inbox, sent, drafts)
- HTML email support

### 📅 Calendar
- List and create events
- Teams meeting integration
- Check availability/free-busy

### 📁 OneDrive
- Browse files and folders
- Search files
- Read file content

### ✅ Tasks (Microsoft To-Do)
- List task lists
- Create and manage tasks
- Set importance and due dates

### 💬 Teams
- List chats
- Read and send messages

### 👥 Users
- List organization users
- Get user profiles

## Requirements

- Node.js 18+
- Azure Entra ID App with Microsoft Graph permissions

## Setup

### 1. Create Azure Entra ID App

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Microsoft Entra ID** → **App registrations** → **New registration**
3. Configure:
   - Name: `MCP-Microsoft365`
   - Supported account types: Single tenant (recommended)
   - Redirect URI: `http://localhost:3000/callback`

### 2. Add API Permissions

Add these **Application permissions** for Microsoft Graph:

```
Mail.Read, Mail.Send, Mail.ReadWrite
Calendars.Read, Calendars.ReadWrite
Files.Read.All, Files.ReadWrite.All
Tasks.Read.All, Tasks.ReadWrite.All
Chat.Read.All, Chat.ReadWrite.All
User.Read.All
```

**Important:** Click "Grant admin consent"

### 3. Get Credentials

Save these values:
- Application (client) ID
- Directory (tenant) ID
- Client Secret (create under Certificates & secrets)

### 4. Install

```bash
# Clone/download the skill
cd mcp-microsoft365

# Install dependencies
npm install

# Build
npm run build
```

### 5. Configure mcporter

```bash
mcporter config add m365 --stdio "node /path/to/mcp-microsoft365/dist/index.js"
```

Edit `config/mcporter.json` to add environment variables:

```json
{
  "mcpServers": {
    "m365": {
      "command": "node /path/to/dist/index.js",
      "env": {
        "TENANT_ID": "your-tenant-id",
        "CLIENT_ID": "your-client-id",
        "CLIENT_SECRET": "your-client-secret",
        "DEFAULT_USER": "user@yourdomain.com"
      }
    }
  }
}
```

## Usage

### Email
```bash
# List recent emails
mcporter call m365.m365_mail_list top:5

# Send email
mcporter call m365.m365_mail_send to:"recipient@email.com" subject:"Hello" body:"<p>Hi!</p>"

# Search
mcporter call m365.m365_mail_search query:"important"
```

### Calendar
```bash
# List events
mcporter call m365.m365_calendar_list top:10

# Create event with Teams meeting
mcporter call m365.m365_calendar_create subject:"Team Sync" start:"2026-01-27T10:00:00" end:"2026-01-27T11:00:00" isOnline:true
```

### Files
```bash
# List OneDrive root
mcporter call m365.m365_files_list

# Search files
mcporter call m365.m365_files_search query:"report"
```

### Tasks
```bash
# List task lists
mcporter call m365.m365_tasks_lists
```

### Teams
```bash
# List chats
mcporter call m365.m365_teams_chats top:10
```

## 19 Available Tools

| Tool | Description |
|------|-------------|
| `m365_mail_list` | List emails |
| `m365_mail_read` | Read email by ID |
| `m365_mail_send` | Send email |
| `m365_mail_search` | Search emails |
| `m365_calendar_list` | List events |
| `m365_calendar_create` | Create event |
| `m365_calendar_availability` | Check free/busy |
| `m365_files_list` | List files |
| `m365_files_search` | Search files |
| `m365_files_read` | Read file content |
| `m365_files_info` | Get file metadata |
| `m365_tasks_lists` | List task lists |
| `m365_tasks_list` | List tasks |
| `m365_tasks_create` | Create task |
| `m365_teams_chats` | List chats |
| `m365_teams_messages` | Read messages |
| `m365_teams_send` | Send message |
| `m365_users_list` | List users |
| `m365_user_info` | Get user profile |

## Author

**Mahmoud Alkhatib**
- Website: [malkhatib.com](https://malkhatib.com)
- YouTube: [@malkhatib](https://youtube.com/@malkhatib)
- Twitter: [@malkhateeb](https://twitter.com/malkhateeb)

## License

MIT
