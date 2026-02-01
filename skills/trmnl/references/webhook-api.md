# Webhook API Reference

## Webhook Basics

**Method:** POST
**Content-Type:** application/json
**Rate Limit:** 12 requests/hour (free), 360/hour (TRMNL+)
**Max Payload:** 2KB (free), 5KB (TRMNL+)

## Payload Formats

### Object-Based (Most Common)

```json
{
  "merge_variables": {
    "content": "<div class='layout'>HTML here</div>",
    "title": "Optional title",
    "image": "https://example.com/image.png"
  }
}
```

### Array-Based (Content Field)

```json
{
  "merge_variables": [
    {"content": "<div>HTML content</div>"}
  ]
}
```

### With Merge Strategy

```json
{
  "merge_variables": {"sensor": {"temperature": 42}},
  "merge_strategy": "deep_merge"
}
```

### With Stream Strategy

```json
{
  "merge_variables": {"temperatures": [40, 42]},
  "merge_strategy": "stream",
  "stream_limit": 10
}
```

## cURL Example

```bash
curl "https://trmnl.com/api/custom_plugins/{uuid}" \
  -H "Content-Type: application/json" \
  -d '{"merge_variables": {"content": "<div class=\"layout\">HTML</div>"}}' \
  -X POST
```

**Note:** Escape quotes in JSON strings when using cURL.

## Merge Strategies

### Default
Replaces entire variable state:
```json
{"merge_variables": {"content": "New content"}}
```
Previous content is overwritten.

### Deep Merge
Recursively merges dictionary objects by key:
```json
{
  "merge_variables": {"sensor": {"temperature": 42}},
  "merge_strategy": "deep_merge"
}
```
Existing keys in `sensor` persist, only `temperature` updates.

### Stream
Appends to top-level arrays:
```json
{
  "merge_variables": {"items": ["new item"]},
  "merge_strategy": "stream",
  "stream_limit": 10
}
```
New items prepend to array, limited to `stream_limit`.

## Response Format

### Success Response
```json
{
  "message": null,
  "merge_variables": {
    "content": "<div>HTML content</div>"
  }
}
```

### Error Response
```json
{
  "message": "Error description",
  "merge_variables": null
}
```

## Global Variables (Liquid Templates)

Available in TRMNL Liquid templates (not in webhook payload):

### User Information
- `{{ trmnl.user.first_name }}` - User's first name
- `{{ trmnl.user.last_name }}` - User's last name
- `{{ trmnl.user.email }}` - User's email

### Plugin Settings
- `{{ trmnl.plugin_settings.custom_fields_values }}` - Custom field values

### Device Information
- `{{ model.bit_depth }}` - Display bit depth (1, 2, or 4)
- `{{ model.name }}` - Device model name

## HTML in Merge Variables

### Supported
Full HTML markup is supported in `merge_variables`:

```json
{
  "merge_variables": {
    "content": "<div class=\"layout layout--col gap--large\"><span class=\"value value--xlarge\">Title</span><span class=\"description\">Body text</span></div>"
  }
}
```

### Processing
- HTML is NOT auto-escaped by default
- Use TRMNL framework CSS classes for styling
- Limited tag support in form descriptions: `<br>`, `<strong>`, `<b>`, `<a>`
- Allowed attributes: `class`, `href`, `target="_blank"`

### Size Optimization

When approaching payload limits:

**Remove whitespace:**
```json
{"merge_variables":{"content":"<div class=\"layout\">Content</div>"}}
```

**Use zlib compression:**
```python
import zlib, base64, json
compressed = base64.b64encode(zlib.compress(json.dumps(data).encode())).decode()
payload = {"compressed_data": compressed}
```

**Note:** Decompression requires JavaScript with Pako library (Liquid can't decompress).

## Liquid Filters

Available in TRMNL templates (50+ filters):

### TRMNL-Specific
- `markdown_to_html` - Convert Markdown to HTML
- `number_with_delimiter` - Format numbers (1,234.56)
- `json` - Convert to JSON string
- `parse_json` - Parse JSON string

### Standard Liquid
- `upcase`, `downcase`, `capitalize`
- `strip`, `lstrip`, `rstrip`
- `truncate`, `truncatewords`
- `date` - Format dates
- `default` - Provide fallback value
- `split`, `join`
- `first`, `last`
- `map`, `where`, `sort`

**Example:**
```liquid
{{ text | markdown_to_html }}
{{ price | number_with_delimiter }}
{{ name | upcase | truncate: 20 }}
```

## Best Practices

### Payload Size
- Keep under 2KB for compatibility
- Minify HTML (remove whitespace)
- Avoid inline styles when framework classes work
- Compress large payloads if needed

### Rate Limiting
- Batch updates when possible
- Use merge strategies to avoid full replacements
- Cache generated content to minimize requests

### HTML Content
- Use TRMNL framework classes over inline styles
- Test on actual device (e-ink renders differently)
- Keep markup semantic and simple
- Avoid deeply nested structures

### Images
- Use fully qualified public URLs
- Optimize for e-ink (dithering, contrast)
- Consider payload size impact
- Use `image-dither` class for grayscale illusion

## Error Handling

Common errors:

**Rate Limit Exceeded:**
- Wait before retrying
- Reduce request frequency
- Upgrade to TRMNL+ for higher limits

**Payload Too Large:**
- Remove whitespace
- Compress payload
- Simplify HTML structure
- Use shorter class names

**Invalid JSON:**
- Validate JSON syntax
- Escape special characters
- Use proper encoding

**Webhook Not Found:**
- Verify UUID is correct
- Check webhook is active
- Confirm user has access
