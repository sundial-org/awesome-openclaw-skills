# Odds-API.io quick reference (v3)

## Base URL
- https://api.odds-api.io/v3

## Authentication
- Pass the API key as a query parameter: `apiKey=YOUR_KEY`.
- Never store the key in this skill or repo. Prefer `ODDS_API_KEY`.

## Core endpoints (GET)
- `/sports` - List sports (no apiKey required).
- `/bookmakers` - List bookmakers (no apiKey required).
- `/events` - List events for a sport.
  - Required: `sport` (slug)
  - Optional: `league`, `participantId`, `status`, `from`, `to`, `bookmaker`
- `/events/search` - Search events by name.
  - Required: `query` (min 3 chars)
- `/events/{id}` - Get a single event by ID.
- `/odds` - Fetch odds for a specific event.
  - Required: `eventId`, `bookmakers` (comma-separated, max 30)
- `/odds/multi` - Fetch odds for multiple events.
  - Required: `eventIds` (comma-separated, up to 10), `bookmakers`
- `/odds/movements` - Odds movement for an event/market/bookmaker.
  - Required: `eventId`, `bookmaker`, `market`
- `/value-bets` - Value bet opportunities.
- `/arbitrage-bets` - Arbitrage opportunities.

## Response fields (selected)
### `SimpleEventDto` (from `/events`, `/events/search`)
- `id` (integer)
- `date` (string)
- `home`, `away` (string)
- `sport` { `name`, `slug` }
- `league` { `name`, `slug` }
- `status` (string)

### Odds response (from `/odds`)
- `id`, `date`, `home`, `away`, `status`
- `sport` { `name`, `slug` }
- `league` { `name`, `slug` }
- `bookmakers` map: `{ "BookmakerName": [markets...] }`
- `urls` map: `{ "BookmakerName": "link" }`

## Recommended workflow
1. `/sports` to get sport slugs.
2. `/events/search` to find candidate events and IDs.
3. `/bookmakers` to pick bookmaker names.
4. `/odds` with `eventId` and `bookmakers`.
