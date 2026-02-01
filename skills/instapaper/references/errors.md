# Errors and exit codes

## Exit codes

- `0` success
- `1` generic failure
- `2` invalid usage
- `10` rate limited
- `11` premium required
- `12` application suspended
- `13` invalid request
- `14` server error

## Structured error codes (stderr JSON)

When using `--stderr-json`, errors include a stable `code` and `exit_code`:

- `rate_limited`, `premium_required`, `app_suspended`
- `invalid_request`, `server_error`, `api_error`
- `auth_error`, `config_error`
- `timeout`, `network_error`
- `invalid_usage`, `unknown`

