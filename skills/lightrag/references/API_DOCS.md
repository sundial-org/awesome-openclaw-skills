# LightRAG API Reference

The LightRAG server provides a REST API for indexing and querying.

## Main Endpoints

### Query
`POST /query`
```json
{
  "query": "string",
  "mode": "hybrid",
  "only_need_context": false,
  "top_k": 60,
  "stream": false
}
```
Modes: `local`, `global`, `hybrid`, `naive`, `mix`.

### Document Upload
`POST /documents/upload` (Multipart/form-data)
`POST /documents/text` (JSON with text content)

### Status
`GET /health`
`GET /track_status/{track_id}`

## Authentication
If configured, use the `X-API-Key` header.
