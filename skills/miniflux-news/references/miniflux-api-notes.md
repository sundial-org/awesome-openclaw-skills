# Miniflux API notes (quick)

This skill uses:
- `GET /v1/entries?status=unread&limit=20&order=published_at&direction=desc`
- `GET /v1/entries/{id}`

Auth:
- Header: `X-Auth-Token: <token>`

Common fields:
- `entries[].id` (integer)
- `entries[].title`
- `entries[].url`
- `entries[].content` (HTML)
- `entries[].published_at`
- `entries[].feed.title`
