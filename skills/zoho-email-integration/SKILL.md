---
name: zoho-email-integration
description: Complete Zoho Mail integration with OAuth2, REST API (5-10x faster), HTML emails, attachments, and batch operations. Perfect for email automation and workflows.
homepage: https://github.com/briansmith80/clawdbot-zoho-email
---

# Zoho Email Integration

**v2.0** - Complete Zoho Mail integration with OAuth2 authentication and REST API backend (5-10x faster than IMAP/SMTP). Supports HTML emails, attachments, batch operations, and advanced automation workflows.

Choose your authentication: OAuth2 (recommended, secure) or app password (simple setup).

## ✨ Features

### 🔐 Authentication & Performance
- **OAuth2 authentication** - Secure token-based auth with automatic refresh
- **REST API backend** - 5-10x faster operations than IMAP/SMTP
- **Graceful fallback** - Automatically falls back to IMAP if REST API unavailable
- **App password support** - Simple alternative to OAuth2

### 📧 Email Operations
- **📥 Read emails** - Fetch from any folder (Inbox, Sent, Drafts, etc.)
- **🔍 Smart search** - Search by subject, sender, keywords with REST API speed
- **📊 Monitor inbox** - Real-time unread count for notifications
- **📤 Send emails** - Plain text or HTML with CC/BCC support
- **🎨 HTML emails** - Rich formatting with professional templates included
- **📎 Attachments** - Send and download file attachments

### ⚡ Batch & Bulk Operations
- **Batch operations** - Mark, delete, or move multiple emails efficiently
- **Bulk actions** - Search and act on hundreds of emails at once
- **Dry-run mode** - Preview actions before executing for safety

### 🔒 Security
- **No hardcoded credentials** - OAuth2 tokens or environment variables only
- **Automatic token refresh** - Seamless token renewal
- **Encrypted connections** - SSL/TLS for all operations

## 📦 Installation

```bash
clawdhub install zoho-email-integration
```

**Requirements:**
- Python 3.x
- `requests` library (install: `pip3 install requests`)
- Zoho Mail account

## ⚙️ Setup

### 1. Get an App-Specific Password

**Important:** Don't use your main Zoho password!

1. Log in to Zoho Mail
2. Go to **Settings** → **Security** → **App Passwords**
3. Generate a new app password for "Clawdbot" or "IMAP/SMTP Access"
4. Copy the password (you'll need it next)

### 2. Configure Credentials

**Option A: Environment Variables**

Export your Zoho credentials:

```bash
export ZOHO_EMAIL="your-email@domain.com"
export ZOHO_PASSWORD="your-app-specific-password"
```

**Option B: Credentials File**

Create `~/.clawdbot/zoho-credentials.sh`:

```bash
#!/bin/bash
export ZOHO_EMAIL="your-email@domain.com"
export ZOHO_PASSWORD="your-app-specific-password"
```

Make it executable and secure:
```bash
chmod 600 ~/.clawdbot/zoho-credentials.sh
```

Then source it before running:
```bash
source ~/.clawdbot/zoho-credentials.sh
```

### 3. Test Connection

```bash
python3 scripts/zoho-email.py unread
```

Expected output:
```json
{"unread_count": 5}
```

## 🚀 Usage

All commands require credentials set via environment variables.

### Send HTML Emails

Send rich, formatted HTML emails with multipart/alternative support (both HTML and plain text versions):

**CLI Command:**
```bash
# Send HTML from a file
python3 scripts/zoho-email.py send-html recipient@example.com "Newsletter" examples/templates/newsletter.html

# Send HTML from inline text
python3 scripts/zoho-email.py send-html recipient@example.com "Welcome" "<h1>Hello!</h1><p>Welcome to our service.</p>"

# Preview HTML email before sending
python3 scripts/zoho-email.py preview-html examples/templates/newsletter.html
```

**Python API:**
```python
from scripts.zoho_email import ZohoEmail

zoho = ZohoEmail()

# Method 1: Send HTML with auto-generated plain text fallback
zoho.send_html_email(
    to="recipient@example.com",
    subject="Newsletter",
    html_body="<h1>Hello!</h1><p>Welcome!</p>"
)

# Method 2: Send HTML with custom plain text version
zoho.send_email(
    to="recipient@example.com",
    subject="Newsletter",
    body="Plain text version of your email",
    html_body="<h1>Hello!</h1><p>HTML version of your email</p>"
)

# Load HTML from template file
with open('examples/templates/newsletter.html', 'r') as f:
    html_content = f.read()

zoho.send_html_email(
    to="recipient@example.com",
    subject="Monthly Newsletter",
    html_body=html_content
)
```

**Features:**
- ✅ Multipart/alternative emails (HTML + plain text)
- ✅ Auto-generated plain text fallback
- ✅ Load HTML from files or inline strings
- ✅ Preview mode to test before sending
- ✅ Full CSS styling support
- ✅ Works with all email clients

**Templates:**
Pre-built templates available in `examples/templates/`:
- `newsletter.html` - Professional newsletter layout
- `announcement.html` - Important announcements with banners
- `welcome.html` - Onboarding welcome email
- `simple.html` - Basic HTML template for quick customization

### Check Unread Count

```bash
python3 scripts/zoho-email.py unread
```

Perfect for morning briefings or notification systems.

### Search Inbox

```bash
python3 scripts/zoho-email.py search "invoice"
```

Returns last 10 matching emails with subject, sender, date, and body preview.

### Search Sent Emails

```bash
python3 scripts/zoho-email.py search-sent "client name"
```

Returns last 5 matching sent emails.

### Get Specific Email

```bash
python3 scripts/zoho-email.py get Inbox 4590
python3 scripts/zoho-email.py get Sent 1234
```

Returns full email content including complete body.

### Send Email

```bash
python3 scripts/zoho-email.py send "client@example.com" "Subject" "Email body here"
```

### Send Email with Attachments

```bash
python3 scripts/zoho-email.py send "client@example.com" "Invoice" "Please find the invoice attached" --attach invoice.pdf --attach receipt.jpg
```

Supports multiple attachments with `--attach` flag.

### List Email Attachments

```bash
python3 scripts/zoho-email.py list-attachments Inbox 4590
```

Returns JSON with attachment details:
```json
[
  {
    "index": 0,
    "filename": "invoice.pdf",
    "content_type": "application/pdf",
    "size": 52341
  },
  {
    "index": 1,
    "filename": "receipt.jpg",
    "content_type": "image/jpeg",
    "size": 128973
  }
]
```

### Download Attachment

```bash
# Download first attachment (index 0) with original filename
python3 scripts/zoho-email.py download-attachment Inbox 4590 0

# Download second attachment (index 1) with custom filename
python3 scripts/zoho-email.py download-attachment Inbox 4590 1 my-receipt.jpg
```

Returns JSON with download details:
```json
{
  "filename": "invoice.pdf",
  "output_path": "invoice.pdf",
  "size": 52341,
  "content_type": "application/pdf"
}
```

## 🤖 Clawdbot Integration Examples

### Morning Briefing

Check unread emails and report:

```bash
UNREAD=$(python3 scripts/zoho-email.py unread | jq -r '.unread_count')
echo "📧 You have $UNREAD unread emails"
```

### Email Monitoring

Watch for VIP emails:

```bash
RESULTS=$(python3 scripts/zoho-email.py search "Important Client")
COUNT=$(echo "$RESULTS" | jq '. | length')

if [ $COUNT -gt 0 ]; then
  echo "⚠️ New email from Important Client!"
fi
```

### Automated Responses

Search and reply workflow:

```bash
# Find latest invoice inquiry
EMAIL=$(python3 scripts/zoho-email.py search "invoice" | jq -r '.[0]')
FROM=$(echo "$EMAIL" | jq -r '.from')

# Send reply
python3 scripts/zoho-email.py send "$FROM" "Re: Invoice" "Thanks for your inquiry..."
```

### Attachment Workflows

Download invoice attachments automatically:

```bash
# Search for invoice emails
EMAILS=$(python3 scripts/zoho-email.py search "invoice")

# Get latest email ID
EMAIL_ID=$(echo "$EMAILS" | jq -r '.[0].id')

# List attachments
ATTACHMENTS=$(python3 scripts/zoho-email.py list-attachments Inbox "$EMAIL_ID")

# Download all PDF attachments
echo "$ATTACHMENTS" | jq -r '.[] | select(.content_type == "application/pdf") | .index' | while read INDEX; do
  python3 scripts/zoho-email.py download-attachment Inbox "$EMAIL_ID" "$INDEX" "invoice_${INDEX}.pdf"
  echo "Downloaded invoice_${INDEX}.pdf"
done
```

Send report with attachments:

```bash
# Generate report
python3 generate_report.py > report.txt

# Send with attachment
python3 scripts/zoho-email.py send "manager@example.com" "Weekly Report" "Please see attached report" --attach report.txt --attach chart.png
```

## 📚 Python API

Import the module for programmatic use:

```python
from scripts.zoho_email import ZohoEmail

zoho = ZohoEmail()

# Search emails
results = zoho.search_emails(folder="INBOX", query='SUBJECT "invoice"', limit=10)

# Get specific email
email = zoho.get_email(folder="Sent", email_id="4590")

# Send plain text email
zoho.send_email(
    to="client@example.com",
    subject="Hello",
    body="Message text",
    cc="manager@example.com"  # optional
)

# Send HTML email (auto-generated plain text fallback)
zoho.send_html_email(
    to="client@example.com",
    subject="Newsletter",
    html_body="<h1>Welcome!</h1><p>Rich HTML content here</p>",
    text_body="Welcome! Plain text version here"  # optional, auto-generated if not provided
)

# Send multipart email (HTML + custom plain text)
zoho.send_email(
    to="client@example.com",
    subject="Update",
    body="Plain text version",
    html_body="<h1>HTML version</h1>",
    cc="manager@example.com"
)

# Send email with attachments
zoho.send_email_with_attachment(
    to="client@example.com",
    subject="Invoice",
    body="Please find the invoice attached",
    attachments=["invoice.pdf", "receipt.jpg"],
    cc="manager@example.com"  # optional
)

# List attachments
attachments = zoho.get_attachments(folder="INBOX", email_id="4590")
for att in attachments:
    print(f"{att['index']}: {att['filename']} ({att['size']} bytes)")

# Download attachment
result = zoho.download_attachment(
    folder="INBOX",
    email_id="4590",
    attachment_index=0,
    output_path="downloaded_file.pdf"  # optional, uses original filename if not provided
)

# Check unread count
count = zoho.get_unread_count()
```

## 📖 HTML Email Examples

Check out the complete example in `examples/send-html-newsletter.py`:

```bash
# Run the HTML email examples
python3 examples/send-html-newsletter.py
```

This demonstrates:
- Sending simple inline HTML
- Loading and sending HTML templates
- Custom plain text fallbacks
- Professional email layouts

**Quick Start:**
```python
#!/usr/bin/env python3
from scripts.zoho_email import ZohoEmail

zoho = ZohoEmail()

# Load a template
with open('examples/templates/welcome.html', 'r') as f:
    html = f.read()

# Send to recipient
zoho.send_html_email(
    to="newuser@example.com",
    subject="🎉 Welcome to Our Platform!",
    html_body=html
)
```

## 📁 Folder Reference

Common Zoho Mail folders:

- `INBOX` - Main inbox
- `Sent` - Sent emails
- `Drafts` - Draft emails
- `Spam` - Spam folder
- `Trash` - Deleted emails
- Custom folders (e.g., `INBOX/ClientName`)

## 🔧 Advanced Configuration

Override default IMAP/SMTP servers (if using Zoho Mail self-hosted):

```bash
export ZOHO_IMAP="imap.yourdomain.com"
export ZOHO_SMTP="smtp.yourdomain.com"
export ZOHO_IMAP_PORT="993"
export ZOHO_SMTP_PORT="465"
```

## ❓ Troubleshooting

### Authentication Failed

- Ensure IMAP is enabled in Zoho Mail settings
- Use an **app-specific password**, not your main password
- Verify credentials are properly exported

### Connection Timeout

- Check firewall allows port 993 (IMAP) and 465 (SMTP)
- Verify Zoho Mail server status
- Try with a different network (corporate firewalls may block IMAP)

### Search Returns No Results

- IMAP search is case-insensitive
- Try broader keywords
- Verify folder name is correct (case-sensitive)

### "ZOHO_EMAIL and ZOHO_PASSWORD must be set"

You forgot to export credentials! Run:

```bash
export ZOHO_EMAIL="your-email@domain.com"
export ZOHO_PASSWORD="your-app-password"
```

## 🛣️ Roadmap

### ✅ Completed (v2.0.0)

- [x] **OAuth2 authentication** - Secure token-based auth with auto-refresh
- [x] **Zoho Mail REST API** - 5-10x faster than IMAP/SMTP
- [x] **Attachment support** - Download and send attachments
- [x] **HTML email composition** - Rich formatting with templates
- [x] **Batch operations** - Mark, delete, move multiple emails
- [x] **Bulk actions** - Search and act on many emails at once

### 🔮 Future Enhancements

- [ ] **Email threading/conversations** - Group related emails together
- [ ] **Label management** - Create and manage Zoho Mail labels
- [ ] **Draft email management** - Create, edit, and send drafts
- [ ] **Scheduled sends** - Schedule emails to send later
- [ ] **Email templates** - Reusable email templates with variables
- [ ] **Webhooks** - Real-time notifications for new emails
- [ ] **Advanced search** - Filter by size, has-attachment, date ranges
- [ ] **Zoho Calendar integration** - Create events from emails
- [ ] **Zoho CRM integration** - Sync contacts and activities

## 📝 Notes

- **Search limit:** Returns last 5-10 emails by default (configurable in code)
- **Body truncation:** Search results show first 500 characters
- **Encoding:** Handles UTF-8 and various email encodings
- **Security:** Credentials never leave your system except to Zoho servers

## 🤝 Contributing

Found a bug or want to contribute? Submit issues or PRs on GitHub!

## 📄 License

MIT License - free to use, modify, and distribute.

---

**Created:** 2026-01-29  
**Status:** Production-ready ✅  
**Requires:** Python 3.x (standard library only)

## 🔄 Batch Operations

New in v1.1! Process multiple emails efficiently with batch commands.

### Mark Multiple Emails as Read

```bash
python3 scripts/zoho-email.py mark-read INBOX 1001 1002 1003
```

Mark several emails as read in one command. Perfect for clearing notifications.

### Mark Multiple Emails as Unread

```bash
python3 scripts/zoho-email.py mark-unread INBOX 1004 1005
```

Flag important emails to revisit later.

### Delete Multiple Emails

```bash
python3 scripts/zoho-email.py delete INBOX 2001 2002 2003
```

**Safety:** Asks for confirmation before deleting. Emails are moved to Trash (not permanently deleted).

### Move Emails Between Folders

```bash
python3 scripts/zoho-email.py move INBOX "Archive/2024" 3001 3002 3003
```

Organize emails by moving them to custom folders.

### Bulk Actions with Search

Perform actions on all emails matching a search query:

```bash
# Dry run first - see what would be affected
python3 scripts/zoho-email.py bulk-action \
  --folder INBOX \
  --search 'SUBJECT "newsletter"' \
  --action mark-read \
  --dry-run

# Execute the action
python3 scripts/zoho-email.py bulk-action \
  --folder INBOX \
  --search 'SUBJECT "newsletter"' \
  --action mark-read
```

**Available actions:**
- `mark-read` - Mark all matching emails as read
- `mark-unread` - Mark all matching emails as unread
- `delete` - Move all matching emails to Trash

**Search query examples:**
```bash
# By subject
--search 'SUBJECT "invoice"'

# By sender
--search 'FROM "sender@example.com"'

# Unread emails
--search 'UNSEEN'

# Combine criteria (AND)
--search '(SUBJECT "urgent" FROM "boss@company.com")'

# Date range
--search 'SINCE 01-Jan-2024'
```

### Batch Operations in Python

```python
from scripts.zoho_email import ZohoEmail

zoho = ZohoEmail()

# Mark multiple emails as read
result = zoho.mark_as_read(['1001', '1002', '1003'], folder="INBOX")
print(f"Success: {len(result['success'])}, Failed: {len(result['failed'])}")

# Delete multiple emails
result = zoho.delete_emails(['2001', '2002'], folder="INBOX")

# Move emails to another folder
result = zoho.move_emails(
    email_ids=['3001', '3002'],
    target_folder="Archive/2024",
    source_folder="INBOX"
)

# Bulk action with search
result = zoho.bulk_action(
    query='SUBJECT "newsletter"',
    action='mark-read',
    folder="INBOX",
    dry_run=True  # Preview first
)

print(f"Found {result['total_found']} emails")
print(f"Will process {result['to_process']} emails")

# Execute for real
result = zoho.bulk_action(
    query='SUBJECT "newsletter"',
    action='mark-read',
    folder="INBOX",
    dry_run=False
)
```

### Batch Cleanup Example

Clean up old newsletters automatically:

```bash
# 1. Preview what will be deleted
python3 scripts/zoho-email.py bulk-action \
  --folder INBOX \
  --search 'SUBJECT "newsletter"' \
  --action delete \
  --dry-run

# 2. Review the preview output

# 3. Execute if satisfied
python3 scripts/zoho-email.py bulk-action \
  --folder INBOX \
  --search 'SUBJECT "newsletter"' \
  --action delete
```

See `examples/batch-cleanup.py` for a complete automated cleanup script.

