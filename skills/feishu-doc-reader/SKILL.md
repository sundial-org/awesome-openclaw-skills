---
name: feishu-doc-reader
description: Read and extract content from Feishu (Lark) documents using the official Feishu Open API
metadata: {"moltbot":{"emoji":"📄","requires":{"bins":["python3","curl"]}}}
---

# Feishu Document Reader

This skill enables reading and extracting content from Feishu (Lark) documents using the official Feishu Open API.

## Configuration

### Set Up the Skill

1. Create the configuration file at `./reference/feishu_config.json` with your Feishu app credentials:

```json
{
  "app_id": "your_feishu_app_id_here",
  "app_secret": "your_feishu_app_secret_here"
}
```

2. Make sure the scripts are executable:
```bash
chmod +x scripts/read_doc.sh
chmod +x scripts/get_blocks.sh
```

**Security Note**: The configuration file should be kept secure and not committed to version control. Consider using proper file permissions (`chmod 600 ./reference/feishu_config.json`).

## Usage

### Basic Document Reading

To read a Feishu document, you need the document token (found in the URL: `https://example.feishu.cn/docx/DOC_TOKEN`).

**Using the shell script (recommended):**
```bash
# Make sure environment variables are set first
./scripts/read_doc.sh "your_doc_token_here"

# Or specify document type explicitly
./scripts/read_doc.sh "docx_token" "doc"
./scripts/read_doc.sh "sheet_token" "sheet"
```

### Get Detailed Document Blocks (NEW)

For complete document structure with all blocks, use the dedicated blocks script:

```bash
# Get full document blocks structure
./scripts/get_blocks.sh "docx_AbCdEfGhIjKlMnOpQrStUv"

# Get specific block by ID
./scripts/get_blocks.sh "docx_token" "block_id"

# Get blocks with children
./scripts/get_blocks.sh "docx_token" "" "true"
```

**Using Python directly for blocks:**
```bash
python scripts/get_feishu_doc_blocks.py --doc-token "your_doc_token_here"
python scripts/get_feishu_doc_blocks.py --doc-token "docx_token" --block-id "block_id"
python scripts/get_feishu_doc_blocks.py --doc-token "docx_token" --include-children
```

### Supported Document Types

- **Docx documents** (new Feishu docs): Full content extraction with blocks, metadata, and structure
- **Doc documents** (legacy): Basic metadata and limited content  
- **Sheets**: Full spreadsheet data extraction with sheet navigation
- **Slides**: Basic metadata (content extraction requires additional permissions)

## Features

### Enhanced Content Extraction
- **Structured output**: Clean JSON with document metadata, content blocks, and hierarchy
- **Complete blocks access**: Full access to all document blocks including text, tables, images, headings, lists, etc.
- **Block hierarchy**: Proper parent-child relationships between blocks
- **Text extraction**: Automatic text extraction from complex block structures
- **Table support**: Proper table parsing with row/column structure
- **Image handling**: Image URLs and metadata extraction
- **Link resolution**: Internal and external link extraction

### Block Types Supported
- **text**: Plain text and rich text content
- **heading1/2/3**: Document headings with proper hierarchy
- **bullet/ordered**: List items with nesting support
- **table**: Complete table structures with cells and formatting
- **image**: Image blocks with tokens and metadata
- **quote**: Block quotes
- **code**: Code blocks with language detection
- **equation**: Mathematical equations
- **divider**: Horizontal dividers
- **page**: Page breaks (in multi-page documents)

### Error Handling & Diagnostics
- **Detailed error messages**: Clear explanations for common issues
- **Permission validation**: Checks required permissions before making requests
- **Token validation**: Validates document tokens before processing
- **Retry logic**: Automatic retries for transient network errors
- **Rate limiting**: Handles API rate limits gracefully

### Security Features
- **Secure credential storage**: Supports both environment variables and secure file storage
- **No credential logging**: Credentials never appear in logs or output
- **Minimal permissions**: Uses only required API permissions
- **Access token caching**: Efficient token reuse to minimize API calls

## Command Line Options

### Main Document Reader
```bash
# Python script options
python scripts/read_feishu_doc.py --help

# Shell script usage
./scripts/read_doc.sh <doc_token> [doc|sheet|slide]
```

### Blocks Reader (NEW)
```bash
# Get full document blocks
./scripts/get_blocks.sh <doc_token>

# Get specific block
./scripts/get_blocks.sh <doc_token> <block_id>

# Include children blocks
./scripts/get_blocks.sh <doc_token> "" true

# Python options
python scripts/get_feishu_doc_blocks.py --help
```

## API Permissions Required

Your Feishu app needs the following permissions:
- `docx:document:readonly` - Read document content
- `doc:document:readonly` - Read legacy document content  
- `sheets:spreadsheet:readonly` - Read spreadsheet content

## Error Handling

Common errors and solutions:
- **403 Forbidden**: Check app permissions and document sharing settings
- **404 Not Found**: Verify document token is correct and document exists
- **Token expired**: Access tokens are valid for 2 hours, refresh as needed
- **App ID/Secret invalid**: Double-check your credentials in Feishu Open Platform
- **Insufficient permissions**: Ensure your app has the required API permissions
- **99991663**: Application doesn't have permission to access the document
- **99991664**: Document doesn't exist or has been deleted
- **99991668**: Token expired, need to refresh

## Examples

### Extract document with full structure
```bash
# Read document
./scripts/read_doc.sh "docx_AbCdEfGhIjKlMnOpQrStUv"
```

### Get complete document blocks (NEW)
```bash
# Get all blocks with full structure
./scripts/get_blocks.sh "docx_AbCdEfGhIjKlMnOpQrStUv"

# Get specific block details
./scripts/get_blocks.sh "docx_AbCdEfGhIjKlMnOpQrStUv" "blk_xxxxxxxxxxxxxx"
```

### Process spreadsheet data
```bash
./scripts/read_doc.sh "sheet_XyZ123AbCdEfGhIj" "sheet"
```

### Extract only text content (Python script)
```bash
python scripts/read_feishu_doc.py --doc-token "docx_token" --extract-text-only
```

## Security Notes

- **Never commit credentials**: Keep app secrets out of version control
- **Use minimal permissions**: Only request permissions your use case requires
- **Secure file permissions**: Set proper file permissions on secret files (`chmod 600`)
- **Environment isolation**: Use separate apps for development and production
- **Audit access**: Regularly review which documents your app can access

## Troubleshooting

### Authentication Issues
1. Verify your App ID and App Secret in Feishu Open Platform
2. Ensure the app has been published with required permissions  
3. Check that environment variables or config files are properly set
4. Test with the `test_auth.py` script to verify credentials

### Document Access Issues
1. Ensure the document is shared with your app or in an accessible space
2. Verify the document token format (should start with `docx_`, `doc_`, or `sheet_`)
3. Check if the document requires additional sharing permissions

### Network Issues
1. Ensure your server can reach `open.feishu.cn`
2. Check firewall rules if running in restricted environments
3. The script includes retry logic for transient network failures

### Blocks-Specific Issues
1. **Empty blocks response**: Document might be empty or have no accessible blocks
2. **Missing block types**: Some block types require additional permissions
3. **Incomplete hierarchy**: Use `--include-children` flag for complete block tree

## References

- [Feishu Open API Documentation](https://open.feishu.cn/document)
- [Document API Reference](https://open.feishu.cn/document/server-docs/docs/docx-v1/document)
- [Blocks API Reference](https://open.feishu.cn/document/server-docs/docs/docx-v1/block)
- [Authentication Guide](https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal)
- [Sheet API Reference](https://open.feishu.cn/document/server-docs/sheets-v3/introduction)
