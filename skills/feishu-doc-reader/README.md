# Feishu Document Reader - Blocks Extraction

This skill provides comprehensive Feishu (Lark) document reading capabilities with full blocks extraction support.

## Features

- **Full blocks extraction**: Get complete document structure including text, tables, images, headings, and more
- **Multiple document types**: Support for Docx (new), Doc (legacy), Sheets, and Slides
- **Secure authentication**: Proper token management with caching and refresh
- **Error handling**: Comprehensive error messages and diagnostics
- **Easy integration**: Simple command-line interface and Python API

## Quick Start

### 1. Configuration

Create `./reference/feishu_config.json`:

```json
{
  "app_id": "your_feishu_app_id",
  "app_secret": "your_feishu_app_secret"
}
```

Set proper permissions:
```bash
chmod 600 ./reference/feishu_config.json
```

### 2. Usage

#### Get full document blocks (recommended):
```bash
# Using shell wrapper
./scripts/get_blocks.sh "docx_your_document_token"

# Using Python directly  
python scripts/get_feishu_doc_blocks.py --doc-token "docx_your_document_token" --output-format json
```

#### Get simplified text only:
```bash
python scripts/get_feishu_doc_blocks.py --doc-token "docx_your_document_token" --extract-text-only
```

### 3. Output Format

The full blocks output includes:
- `document`: Document metadata (title, revision, etc.)
- `blocks`: Complete block hierarchy with all content types
- `text_content`: Extracted plain text (when requested)

## Integration with AI Agents

This skill can be used as a standalone tool or integrated into AI agent workflows:

1. **Direct execution**: Call the script from any AI agent
2. **Extension tool**: Register as an extension for seamless document processing
3. **Pipeline integration**: Combine with other tools for advanced document analysis

## API Permissions Required

Your Feishu app needs these permissions in Open Platform:
- `docx:document:readonly` (for new documents)
- `doc:document:readonly` (for legacy documents)
- `sheets:spreadsheet:readonly` (for spreadsheets)

## Security Notes

- Credentials are never logged or exposed in output
- Access tokens are cached and refreshed automatically
- File system access is restricted to prevent path traversal
- Use minimal required permissions for your use case

## Troubleshooting

### Common Issues

**Authentication Failed (401)**:
- Verify App ID and App Secret in Feishu Open Platform
- Ensure app is published with required permissions

**Document Not Found (404)**:
- Check document token format (should start with `docx_`, `doc_`, or `sheet_`)
- Ensure document is shared with your app

**Permission Denied (403)**:
- Verify required API permissions are granted
- Check if document requires additional sharing settings

### Debugging

Enable debug logging:
```bash
DEBUG=1 python scripts/get_feishu_doc_blocks.py --doc-token "your_token"
```

## Examples

See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for detailed examples.

## References

- [Feishu Open API Documentation](https://open.feishu.cn/document)
- [Document Blocks API](https://open.feishu.cn/document/server-docs/docs/docx-v1/document-block)
- [Authentication Guide](https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal)