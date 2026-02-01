# Creating Custom Schemas for Tabstack

## Schema Basics

Tabstack uses JSON Schema to define what data to extract from web pages. Start simple, then add complexity.

## Simple Schema Template

```json
{
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "content": {"type": "string"},
    "url": {"type": "string"}
  },
  "required": ["title", "content"]
}
```

## Schema Design Principles

### 1. Start Small
Begin with 2-3 fields. Test. Add more as needed.

### 2. Match Page Structure
Look at the actual HTML/page structure to design your schema.

### 3. Use Descriptive Field Names
```json
"job_title": {"type": "string"},
"company_name": {"type": "string"},
"salary_range": {"type": "string"}
```

### 4. Handle Optional Fields
Don't mark everything as `required` - some pages may not have all data.

## Example: Job Listing Schema

**Version 1 (Simple)**
```json
{
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "company": {"type": "string"},
    "description": {"type": "string"}
  },
  "required": ["title", "company"]
}
```

**Version 2 (Detailed)**
```json
{
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "company": {"type": "string"},
    "location": {"type": "string"},
    "salary": {"type": "string"},
    "description": {"type": "string"},
    "requirements": {
      "type": "array",
      "items": {"type": "string"}
    }
  },
  "required": ["title", "company", "description"]
}
```

## Testing Your Schema

1. **Test with example.com first** - Fast, predictable
2. **Test with target site** - See what gets extracted
3. **Adjust schema** - Add/remove fields based on results
4. **Test with multiple pages** - Ensure consistency

## Performance Tips

- **Simple schemas are faster** - Fewer fields = faster extraction
- **Arrays can be slow** - Large arrays of items increase processing time
- **Nested objects add complexity** - Keep structure flat when possible

## Common Patterns

### News Article
```json
{
  "type": "object",
  "properties": {
    "headline": {"type": "string"},
    "author": {"type": "string"},
    "publish_date": {"type": "string"},
    "article_body": {"type": "string"},
    "image_url": {"type": "string"}
  }
}
```

### Product Page
```json
{
  "type": "object",
  "properties": {
    "product_name": {"type": "string"},
    "price": {"type": "string"},
    "description": {"type": "string"},
    "features": {
      "type": "array",
      "items": {"type": "string"}
    }
  }
}
```

### Contact Page
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "email": {"type": "string"},
    "phone": {"type": "string"},
    "address": {"type": "string"}
  }
}
```

## Troubleshooting

**Problem:** Timeout (45+ seconds)
**Solution:** Simplify schema, reduce fields, avoid complex arrays

**Problem:** Missing data
**Solution:** Check if field exists on page, make field optional

**Problem:** Incorrect data
**Solution:** Adjust field descriptions in schema, test with different pages

## Learning Resources

- [JSON Schema Documentation](https://json-schema.org/learn/)
- [Tabstack API Docs](https://docs.tabstack.ai/api/extract-json-v-1)
- [Example Schemas](./) - See `references/` directory