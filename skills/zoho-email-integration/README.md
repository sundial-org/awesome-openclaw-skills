# Zoho Email Integration for Clawdbot

[![GitHub](https://img.shields.io/badge/GitHub-clawdbot--zoho--email-blue?logo=github)](https://github.com/briansmith80/clawdbot-zoho-email)
[![ClawdHub](https://img.shields.io/badge/ClawdHub-Install-green)](https://clawdhub.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.1-blue)](https://github.com/briansmith80/clawdbot-zoho-email/releases)

**v2.0.1** - Complete Zoho Mail integration with OAuth2, REST API backend, and advanced email automation features. Perfect for email workflows, monitoring, and bulk operations in your Clawdbot projects.

## 🚀 Quick Start

```bash
# Install from MoltHub
clawdhub install zoho-email

# Option 1: OAuth2 (recommended - more secure)
python3 scripts/oauth-setup.py

# Option 2: App password (simple)
export ZOHO_EMAIL="your-email@domain.com"
export ZOHO_PASSWORD="your-app-specific-password"

# Test connection
python3 scripts/zoho-email.py unread
```

## ✨ Features

### Core Features
✅ **OAuth2 Authentication** - Secure authentication with automatic token refresh  
✅ **REST API Backend** - 5-10x faster than IMAP/SMTP (auto-enabled with OAuth2)  
✅ **Read & Search** - Search emails with advanced filters  
✅ **Send Emails** - Plain text, HTML, CC/BCC support  
✅ **Attachments** - Send and download attachments  
✅ **HTML Emails** - Send rich-formatted emails with templates  
✅ **Batch Operations** - Mark, delete, move multiple emails efficiently  
✅ **Folder Management** - Access all folders (Inbox, Sent, Drafts, etc.)  

### Performance
⚡ **5-10x faster** operations with REST API mode  
⚡ **Connection pooling** for persistent HTTP connections  
⚡ **Server-side filtering** reduces data transfer  
⚡ **Automatic fallback** to IMAP if REST API unavailable  

## 📚 Documentation

- **[SKILL.md](SKILL.md)** - Complete guide with examples
- **[OAUTH2_SETUP.md](OAUTH2_SETUP.md)** - OAuth2 setup instructions
- **[REST_API_MIGRATION.md](REST_API_MIGRATION.md)** - REST API features and migration
- **[BATCH_FEATURE.md](BATCH_FEATURE.md)** - Batch operations guide
- **[HTML_FEATURE.md](HTML_FEATURE.md)** - HTML email documentation
- **[ATTACHMENT_FEATURE.md](ATTACHMENT_FEATURE.md)** - Attachment handling guide

## 📖 Quick Examples

### Basic Operations
```bash
# Get unread count
python3 scripts/zoho-email.py unread

# Search emails
python3 scripts/zoho-email.py search "important meeting"

# Send email
python3 scripts/zoho-email.py send recipient@example.com "Subject" "Message body"
```

### HTML Emails (v1.1.0+)
```bash
# Send HTML email from template
python3 scripts/zoho-email.py send-html user@example.com "Newsletter" templates/newsletter.html

# Preview HTML before sending
python3 scripts/zoho-email.py preview-html templates/welcome.html
```

### Attachments (v1.1.0+)
```bash
# Send with attachments
python3 scripts/zoho-email.py send user@example.com "Report" "See attached" --attach report.pdf --attach data.xlsx

# List attachments in an email
python3 scripts/zoho-email.py list-attachments Inbox 4590

# Download attachment
python3 scripts/zoho-email.py download-attachment Inbox 4590 0 ./report.pdf
```

### Batch Operations (v1.1.0+)
```bash
# Mark multiple emails as read
python3 scripts/zoho-email.py mark-read INBOX 1001 1002 1003

# Delete multiple emails (with confirmation)
python3 scripts/zoho-email.py delete INBOX 2001 2002 2003

# Move emails to folder
python3 scripts/zoho-email.py move INBOX "Archive/2024" 3001 3002

# Bulk action with search
python3 scripts/zoho-email.py bulk-action \
  --folder INBOX \
  --search 'SUBJECT "newsletter"' \
  --action mark-read \
  --dry-run
```

### OAuth2 & REST API (v1.2.0+, v2.0.0+)
```bash
# Set up OAuth2 (one-time)
python3 scripts/oauth-setup.py

# Check OAuth2 status
python3 scripts/zoho-email.py oauth-status

# Force REST API mode (5-10x faster)
python3 scripts/zoho-email.py unread --api-mode rest --verbose

# Force IMAP mode (compatibility)
python3 scripts/zoho-email.py unread --api-mode imap
```

## 💡 Use Cases

- **Morning briefings** - Automated unread email summaries
- **Email monitoring** - Watch for VIP senders or keywords
- **Newsletter cleanup** - Bulk-mark newsletters as read
- **Automated responses** - Search and reply to specific emails
- **Email archiving** - Move old emails to archive folders
- **Notifications** - Alert when important emails arrive
- **HTML campaigns** - Send rich-formatted newsletters
- **Attachment workflows** - Download invoices, reports automatically

## 🔧 Requirements

**Minimum:**
- Python 3.x
- Zoho Mail account
- App-specific password OR OAuth2 setup

**Optional (for REST API):**
- `requests>=2.31.0` (install: `pip install requests`)
- OAuth2 credentials (automatic 5-10x performance boost)

## 📦 Version History

- **v2.0.0** (2025-01-29) - REST API backend with 5-10x performance boost
- **v1.2.0** (2025-01-29) - OAuth2 authentication with automatic token refresh
- **v1.1.0** (2025-01-29) - HTML emails, attachments, batch operations
- **v1.0.0** (2025-01-29) - Initial IMAP/SMTP implementation

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

- 🐛 **Report bugs:** [Open an issue](https://github.com/briansmith80/clawdbot-zoho-email/issues)
- 💡 **Request features:** [Open an issue](https://github.com/briansmith80/clawdbot-zoho-email/issues)
- 🔧 **Submit PRs:** [Pull requests](https://github.com/briansmith80/clawdbot-zoho-email/pulls)
- ⭐ **Star the repo:** Show your support!

This is an open-source Clawdbot skill maintained by the community.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Part of the Clawdbot ecosystem** | [ClawdHub](https://clawdhub.com) | [Documentation](SKILL.md)
