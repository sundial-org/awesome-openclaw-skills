# Feishu Doc Reader Integration Guide

## How to Use with AI Agents

### 1. Basic Setup

Ensure your Feishu app has the required permissions:
- `docx:document:readonly` 
- `doc:document:readonly`
- `sheets:spreadsheet:readonly`

Store your credentials in `./reference/feishu_config.json`:

```json
{
  "app_id": "cli_your_app_id",
  "app_secret": "your_app_secret"
}
```

### 2. Using with External Tools

The skill provides two main entry points:

#### Get Full Document Structure (with blocks)
```bash
# Shell script
./scripts/get_blocks.sh "docx_document_token"

# Python directly  
python scripts/get_feishu_doc_blocks.py --doc-token "docx_document_token" --format full
```

#### Get Simplified Text Content
```bash
# Shell script
./scripts/read_doc.sh "docx_document_token"

# Python directly
python scripts/read_feishu_doc.py --doc-token "docx_document_token" --format simple
```

### 3. Integration with AI Agents

To use this skill in your AI agent:

1. **Call the script from your agent code**:
   ```javascript
   const { exec } = require('child_process');
   exec('./scripts/get_blocks.sh "docx_token"', 
        { cwd: '/path/to/feishu-doc-reader' },
        (error, stdout, stderr) => {
     if (error) {
       console.error('Error:', error);
       return;
     }
     const docData = JSON.parse(stdout);
     // Process the document blocks
   });
   ```

2. **Handle the JSON response**:
   The response contains:
   - `document`: Document metadata (title, owner, created time, etc.)
   - `blocks`: Complete block structure with all content elements
   - `text_content`: Extracted plain text for easy processing

3. **Error handling**:
   - Check exit code (0 = success, non-zero = error)
   - Parse stderr for detailed error messages
   - Handle common errors like permission denied, document not found, etc.

### 4. Blocks Structure Reference

The `blocks` field contains a hierarchical structure where each block has:
- `block_id`: Unique identifier
- `block_type`: Type of block (text, heading1, table, image, etc.)
- `children`: Array of child block IDs
- `content`: Type-specific content data

Example block types:
- `text`: Paragraph text with rich formatting
- `heading1/2/3`: Headings with different levels
- `table`: Table with cells and structure
- `image`: Image with token and metadata
- `bullet/ordered`: List items
- `quote`: Block quotes
- `equation`: Mathematical equations

### 5. Performance Considerations

- **Large documents**: The full blocks structure can be large; consider using `--format simple` for just text
- **Rate limiting**: Feishu API has rate limits; implement caching when possible
- **Token expiration**: Access tokens expire after 2 hours; the script handles automatic refresh

### 6. Security Best Practices

- Never log or expose app secrets
- Use file permissions (`chmod 600`) on config files
- Validate document tokens before processing
- Implement proper error handling to avoid information leakage

### 7. Troubleshooting Common Issues

**"Document not found" errors**:
- Verify the document token is correct
- Ensure the document is shared with your app
- Check if the document requires additional permissions

**Authentication errors**:
- Verify app ID and secret are correct
- Ensure the app has been published with required permissions
- Check if the app secret has been rotated

**Permission errors**:
- Confirm required API permissions are granted
- Ensure the document is accessible to your app
- Check if the document is in a space your app can access