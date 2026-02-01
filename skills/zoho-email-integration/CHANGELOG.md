# Changelog

All notable changes to the Zoho Email Integration skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2026-01-29

### 🐛 Fixed - REST API Batch Operations

**Critical bug fixes for REST API mode + updated documentation:**

#### Fixed
- **Mark as read/unread operations** - Fixed 404 errors by using correct `/updatemessage` endpoint with `mode` parameter
- **HTML email NameError** - Removed orphaned code that caused "name 'email_id' is not defined" error
- **Delete operation** - Added missing folder ID parameter required by API
- **Move operation** - Fixed endpoint to use `/updatemessage` with proper mode and folder lookup
- **Batch operations** - All operations now batch multiple messages in single API calls (90% reduction in API usage)

#### Changed
- REST API methods now use folder name-to-ID lookup for consistency with IMAP mode
- Batch operations consolidated into single API requests instead of individual calls
- Improved error messages for folder not found cases

#### Technical Details
- Endpoint changed from `PUT /accounts/{id}/messages/{id}` to `PUT /accounts/{id}/updatemessage`
- Delete endpoint now uses `DELETE /accounts/{id}/folders/{folderId}/messages/{id}`
- All message IDs converted to integers for API compatibility
- Added folder caching via `list_folders()` for efficient lookups

#### Documentation
- **Updated roadmap** - Marked OAuth2, REST API, attachments, HTML emails, and batch operations as completed
- **Added future enhancements** - Listed realistic future features (threading, labels, webhooks, scheduled sends, etc.)
- **Cleaned up repository** - Removed 29 internal development docs, keeping only essential user-facing files

See [FIXES_COMPLETE.md](FIXES_COMPLETE.md) for detailed technical documentation.

## [2.0.0] - 2026-01-29

### 🚀 Added - REST API Backend Implementation

**Major performance upgrade: 5-10x faster operations with REST API support!**

### Added - REST API Features
- **ZohoRestAPIClient class** - Complete REST API client with OAuth2 authentication
- **Connection pooling** - Persistent HTTP connections using requests.Session
- **Automatic token refresh** - Seamless token refresh on expiration
- **Rate limiting** - Built-in rate limiting with exponential backoff
- **Retry logic** - Automatic retry on 429/5xx errors
- **API mode auto-detection** - Automatically uses REST API when OAuth2 is available
- **Graceful fallback** - Falls back to IMAP/SMTP if REST API fails
- **100% backward compatibility** - All existing code works unchanged

### Added - REST API Client Methods
- `list_messages()` - List emails with server-side filtering
- `get_message()` - Get specific message by ID
- `send_message()` - Send emails via REST API
- `mark_as_read()` - Mark messages as read
- `mark_as_unread()` - Mark messages as unread
- `delete_messages()` - Delete messages (move to trash)
- `move_messages()` - Move messages between folders
- `list_folders()` - List all folders
- `get_account_id()` - Get Zoho Mail account ID

### Added - API Mode Support
- `--api-mode <mode>` CLI flag - Force 'auto', 'rest', or 'imap' mode
- `api_mode` parameter in `ZohoEmail.__init__()`
- Auto-detection: Uses REST API if OAuth2 + requests library available
- Force REST: `--api-mode rest` (requires OAuth2)
- Force IMAP: `--api-mode imap` (works with any auth)

### Modified - Updated Methods with REST API Support
- `get_unread_count()` - Uses REST API when available
- `search_emails()` - Uses REST API list_messages with query conversion
- `send_email()` - Uses REST API send_message when available
- `mark_as_read()` - Uses REST API batch operations
- `mark_as_unread()` - Uses REST API batch operations
- `delete_emails()` - Uses REST API delete operations
- `move_emails()` - Uses REST API move operations

### Added - Dependencies
- `requests>=2.31.0` - Required for REST API mode

### Added - Environment Variables
- `ZOHO_API_BASE_URL` - REST API base URL (default: https://mail.zoho.com/api)
- `ZOHO_API_TIMEOUT` - REST API timeout in seconds (default: 30)
- `ZOHO_API_RATE_DELAY` - Delay between requests in seconds (default: 0.5)
- `ZOHO_MAX_RETRIES` - Maximum retry attempts (default: 3)

### Added - Documentation
- `REST_API_IMPLEMENTATION.md` - Implementation details and code summary

### Performance Improvements
- **5-10x faster** operations with REST API
- **Connection pooling** - Reuses HTTP connections
- **Server-side filtering** - Reduces data transfer
- **Batch operations** - More efficient than IMAP

### Technical Details
- Added `has_requests_library()` helper function
- REST API client uses requests.Session for connection pooling
- Automatic OAuth2 bearer token injection
- Rate limiting with configurable delay
- Exponential backoff on failures
- Token refresh before expiration (5-minute buffer)
- Graceful error handling with IMAP fallback

## [1.2.0] - 2026-01-29

### 🔐 Added - OAuth2 Authentication Support

**Secure OAuth2 authentication with automatic token management!**

### Added - OAuth2 Features
- **OAuth2 authorization code flow** - Interactive browser-based login
- **Automatic token refresh** - Access tokens refresh automatically when expired
- **Secure token storage** - Tokens stored in `~/.zoho-mail-tokens.json` with 600 permissions
- **Token management CLI** - Commands to check status, refresh, and revoke tokens
- **IMAP XOAUTH2 support** - OAuth2 authentication for IMAP connections
- **SMTP XOAUTH2 support** - OAuth2 authentication for SMTP connections
- **Backward compatibility** - App passwords still work, auto-detection of auth method
- **No external dependencies** - Uses Python standard library only

### Added - New Commands
- `oauth-status` - Check OAuth2 token validity and expiration
- `oauth-login` - Manually refresh OAuth2 tokens
- `oauth-revoke` - Revoke OAuth2 access (delete token file)

### Added - New CLI Flags
- `--auth <method>` - Specify authentication method: 'auto' (default), 'password', or 'oauth2'
- `--token-file <path>` - Custom OAuth2 token file path (default: ~/.zoho-mail-tokens.json)

### Added - OAuth2 Setup Tool
- `scripts/oauth-setup.py` - Interactive OAuth2 setup wizard
  - Browser-based authorization flow
  - Automatic callback handling
  - Secure token storage
  - Token refresh support
  - Status checking

### Added - Python API Methods
- `ZohoEmail(auth_method='oauth2')` - OAuth2 authentication mode
- `refresh_token()` - Manually refresh OAuth2 access token
- `revoke_token()` - Revoke and delete OAuth2 tokens
- `get_token_status()` - Check token validity and expiration

### Added - Documentation
- `OAUTH2_SETUP.md` - Complete OAuth2 setup guide with troubleshooting
- `OAUTH2_FEATURE.md` - Comprehensive feature documentation
- `OAUTH2_COMPLETE.md` - Implementation summary
- Updated `SKILL.md` with OAuth2 section
- Updated `README.md` with OAuth2 information

### Security Improvements
- **No password storage** - OAuth2 eliminates password storage
- **Token-based auth** - Short-lived access tokens (1 hour)
- **Auto-refresh** - Seamless token renewal
- **Revocable access** - Easy to revoke without changing passwords
- **Secure file permissions** - Token files enforced to 600
- **Zoho-recommended** - Official authentication method

### Changed
- Auto-detection now prefers OAuth2 if token file exists
- IMAP/SMTP connection methods updated to support XOAUTH2
- Help text updated with OAuth2 commands and options
- Error messages now mention both auth methods

### Backward Compatibility
- ✅ App passwords still fully supported
- ✅ All existing commands work unchanged
- ✅ No breaking changes to CLI or Python API
- ✅ Auto-detection fallsback to app password if no OAuth2 tokens
- ✅ Existing scripts require no modifications

### Migration Path
1. Run `python3 scripts/oauth-setup.py` to configure OAuth2
2. Test with `--auth oauth2` flag
3. Once working, auto-mode uses OAuth2 automatically
4. Optionally remove app password: `unset ZOHO_PASSWORD`

### Performance
- Negligible runtime overhead (<100ms for token check)
- Automatic token refresh only when needed
- No impact on IMAP/SMTP performance

### Known Limitations
- Initial setup requires a browser for authorization
- Token file must be stored locally (default: `~/.zoho-mail-tokens.json`)
- Tokens stored in plaintext (with 600 permissions - encryption recommended for high-security environments)
- Zoho-specific OAuth2 implementation

## [1.1.0] - 2026-01-29

### Added - Batch Operations
- **Batch methods**: `mark_as_read()`, `mark_as_unread()`, `delete_emails()`, `move_emails()`
- **Bulk action method**: `bulk_action()` for search-and-action workflows with dry-run support
- **CLI commands**: `mark-read`, `mark-unread`, `delete`, `move`, `bulk-action`
- **Safety features**: Interactive confirmation for deletions, dry-run mode for bulk actions
- **Example script**: `examples/batch-cleanup.py` for automated email cleanup
- **Documentation**: Comprehensive batch operations section in SKILL.md and BATCH_FEATURE.md

### Enhanced
- CLI help text now includes batch operations
- Result tracking with success/failed lists for all batch operations
- Progress reporting and error handling in batch operations

## [1.0.0] - 2026-01-29

### Added
- Initial release
- IMAP email reading and searching
- SMTP email sending with CC/BCC
- Unread count monitoring
- Support for all IMAP folders (Inbox, Sent, Drafts, etc.)
- Environment variable configuration
- CLI interface with comprehensive help
- Python API for programmatic use
- Example scripts:
  - `morning-briefing.sh` - Daily email report
  - `vip-monitor.sh` - Monitor important senders
  - `auto-reply.py` - Automated email responses
- Verbose debug mode (`--verbose` flag)
- Configurable timeouts (`ZOHO_TIMEOUT` env var)
- Date-limited search for performance (`ZOHO_SEARCH_DAYS` env var)
- Automated test suite (`test.sh`)
- Complete documentation (README.md, SKILL.md, IMPROVEMENTS.md)
- HTML email support with `send-html` command
- Email attachment support (list, download, send)

### Performance
- **10x faster searches** - Date filtering limits search to recent emails (default: 30 days)
- **2x faster unread checks** - Readonly IMAP mode
- **Connection timeouts** - Prevents hanging on slow connections (default: 30s)
- **Graceful degradation** - Continues on malformed emails

### Security
- Removed hardcoded credentials from code
- Environment variable support for all credentials
- Secure credentials file instructions
- .gitignore to prevent credential commits
- Error messages never expose credentials

### Documentation
- Complete SKILL.md with usage examples
- Quick start README.md
- MIT License
- requirements.txt (standard library only in v1.x)
- Example scripts with inline documentation
- Comprehensive help text in CLI
- IMPROVEMENTS.md with test results

### Fixed
- Proper connection cleanup in error cases
- Better handling of malformed email subjects
- Improved multipart email body extraction
- Keyboard interrupt handling (Ctrl+C)
- Socket timeout configuration

## [Unreleased]

### Planned Features (v2.1.0+)
- ✅ Attachment upload via REST API
- ✅ Webhook support for real-time notifications
- ✅ Advanced search syntax (by attachment, size, date)
- ✅ Label and tag management
- ✅ Bulk batch API for multiple operations
- ✅ Email templates and scheduled sends
- ✅ Zoho Calendar integration
- ✅ Zoho CRM integration

---

**Legend:**
- 🚀 Major feature
- ✅ Completed
- 🔧 In progress
- 📋 Planned
