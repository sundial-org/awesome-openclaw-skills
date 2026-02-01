# MCP Microsoft 365 Server

An MCP (Model Context Protocol) server for Microsoft 365 integration.

## Features

### 📧 Mail (Outlook)
- `m365_mail_list` - List emails from inbox/folders
- `m365_mail_read` - Read specific email
- `m365_mail_send` - Send emails
- `m365_mail_search` - Search emails

### 📅 Calendar
- `m365_calendar_list` - List events
- `m365_calendar_create` - Create events (with Teams meeting support)
- `m365_calendar_availability` - Check free/busy status

### 📁 OneDrive
- `m365_files_list` - List files/folders
- `m365_files_search` - Search files
- `m365_files_read` - Read file content
- `m365_files_info` - Get file metadata

### ✅ Tasks (To-Do)
- `m365_tasks_lists` - List task lists
- `m365_tasks_list` - List tasks in a list
- `m365_tasks_create` - Create new task

### 💬 Teams
- `m365_teams_chats` - List chats
- `m365_teams_messages` - Read chat messages
- `m365_teams_send` - Send message to chat

### 👥 Users
- `m365_users_list` - List organization users
- `m365_user_info` - Get user profile

## Setup

### 1. Azure Entra ID App

Create an app in [Azure Portal](https://portal.azure.com):
- Microsoft Entra ID → App registrations → New registration
- Add Application permissions for Microsoft Graph:
  - `Mail.Read`, `Mail.Send`, `Mail.ReadWrite`
  - `Calendars.Read`, `Calendars.ReadWrite`
  - `Files.Read.All`, `Files.ReadWrite.All`
  - `Tasks.Read.All`, `Tasks.ReadWrite.All`
  - `Chat.Read.All`, `Chat.ReadWrite.All`
  - `User.Read.All`
- Grant admin consent

### 2. Configure

Create `.env` file:
```env
TENANT_ID=your-tenant-id
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
DEFAULT_USER=user@domain.com
```

### 3. Install & Build

```bash
npm install
npm run build
```

### 4. Run

```bash
npm start
# or
node dist/index.js
```

### 5. Use with mcporter

```bash
mcporter config add m365 --stdio "node /path/to/dist/index.js"
mcporter call m365.m365_mail_list top:5
```

## Usage Examples

```bash
# List emails
mcporter call m365.m365_mail_list top:5

# Send email
mcporter call m365.m365_mail_send to:someone@example.com subject:"Hello" body:"<p>Hi there!</p>"

# List calendar events
mcporter call m365.m365_calendar_list top:10

# Create event with Teams meeting
mcporter call m365.m365_calendar_create subject:"Meeting" start:"2024-01-30T10:00:00" end:"2024-01-30T11:00:00" isOnline:true

# List OneDrive files
mcporter call m365.m365_files_list path:"Documents"

# Create task
mcporter call m365.m365_tasks_create listId:"xxx" title:"New task" importance:"high"
```

## Author

Mahmoud Alkhatib - [malkhatib.com](https://malkhatib.com)

## License

MIT
