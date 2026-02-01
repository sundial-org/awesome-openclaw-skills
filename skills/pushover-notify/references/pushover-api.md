# Pushover API quick reference (messages)

Endpoint:
- `POST https://api.pushover.net/1/messages.json`

Required fields:
- `token` (application API token)
- `user` (user key)
- `message`

Common optional fields:
- `title`
- `device`
- `url`, `url_title`
- `priority` (`-1`, `0`, `1`, `2`)
- `sound`
- `timestamp` (unix seconds)

Emergency priority (`priority=2`) also requires:
- `retry` (seconds between retries)
- `expire` (seconds to keep retrying)

Docs:
- https://pushover.net/api
