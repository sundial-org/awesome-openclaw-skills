# Withings Family (Clawdbot Skill)

Fetch health data from the Withings API for multiple family members (weight, body metrics, activity, sleep).

## Usage

Scripts live in `scripts/`:

```bash
python3 scripts/withings.py <userId> weight
python3 scripts/withings.py <userId> body
python3 scripts/withings.py <userId> activity [days]
python3 scripts/withings.py <userId> sleep [days]
```

## Auth (first time per user)

Recommended (auto OAuth callback):

```bash
python3 scripts/withings_oauth_local.py <userId>
```

Tokens are stored per-user in `~/.clawdbot/withings-family/tokens-<userId>.json`.

## Requirements

- `python3`
- env: `WITHINGS_CLIENT_ID`, `WITHINGS_CLIENT_SECRET`

## Publishing

Version is declared in `SKILL.md`. Tag releases (e.g. `1.0.0`) and publish via ClawdHub:

```bash
clawdhub publish . --slug withings-family --name "Withings Family" --version 1.0.0
```
