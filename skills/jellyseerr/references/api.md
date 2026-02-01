# Jellyseerr API Reference

## Base URL

```
https://your-jellyseerr-server.com/api/v1
```

## Authentication

Use API key in header:
```
X-Api-Key: your-api-key
```

## Key Endpoints

### Search

```
GET /search?query={query}
```

Returns movies and TV shows matching the query.

**Response:**
```json
{
  "results": [
    {
      "id": 12345,
      "mediaType": "movie" | "tv",
      "title": "Movie Title",
      "name": "TV Show Name",
      "releaseDate": "2020-01-01",
      "firstAirDate": "2020-01-01",
      "overview": "Description",
      "mediaInfo": {
        "status": 0-5
      }
    }
  ]
}
```

### Request Media

```
POST /request
Content-Type: application/json
```

**Movie Request:**
```json
{
  "mediaId": 12345,
  "mediaType": "movie"
}
```

**TV Request (all seasons):**
```json
{
  "mediaId": 12345,
  "mediaType": "tv",
  "seasons": "all"
}
```

**TV Request (specific seasons):**
```json
{
  "mediaId": 12345,
  "mediaType": "tv",
  "seasons": [1, 2, 3]
}
```

### Media Status Codes

- 0: NOT_REQUESTED
- 1: PENDING
- 2: PROCESSING
- 3: PARTIALLY_AVAILABLE
- 4: AVAILABLE
- 5: AVAILABLE (alternative)

### Get Status

```
GET /status
```

Returns server status and version info.

## Rate Limits

Standard rate limits apply. Be respectful with API usage.

## Documentation

Full API docs: https://github.com/Fallenbagel/jellyseerr
