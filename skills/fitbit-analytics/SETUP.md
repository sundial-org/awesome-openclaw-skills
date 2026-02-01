# Fitbit Analytics Skill Setup Guide

## 1. Create a Fitbit Developer App
1.  Go to [dev.fitbit.com/apps](https://dev.fitbit.com/apps) and log in.
2.  Click **"Register an App"**.
3.  Fill in the details:
    *   **Application Name:** `Personal Assistant`
    *   **Description:** `Personal AI assistant integration for health data analytics.`
    *   **Application Website:** `https://github.com/kesslerio` (or your Gist URL)
    *   **Organization:** `Personal`
    *   **Organization Website:** `https://kessler.io`
    *   **Terms of Service URL:** `https://gist.github.com/kesslerio/99a2490a11549a6b848a5f7cc672fb8f`
    *   **Privacy Policy URL:** `https://gist.github.com/kesslerio/cd1692d15e9286682e3c4ea2d0d979cf`
    *   **OAuth 2.0 Application Type:** `Personal`
    *   **Redirect URL:** `http://localhost:8080/`
    *   **Default Access Type:** `Read & Write`
4.  **Save** the app.

## 2. Get Credentials
1.  Note the **OAuth 2.0 Client ID** and **Client Secret**.
2.  Add them to your `~/.config/systemd/user/secrets.conf`:
    ```bash
    FITBIT_CLIENT_ID="YOUR_CLIENT_ID"
    FITBIT_CLIENT_SECRET="YOUR_CLIENT_SECRET"
    ```

## 3. Authorize & Get Tokens
1.  Construct the authorization URL (replace `CLIENT_ID`):
    ```
    https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=CLIENT_ID&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2F&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800
    ```
2.  Open the URL in a browser, log in, and authorize.
3.  You will be redirected to `http://localhost:8080/?code=YOUR_CODE_HERE...`.
4.  Copy the **code** from the URL.

## 4. Exchange Code for Tokens
Run this command (replace values):

```bash
curl -X POST https://api.fitbit.com/oauth2/token \
  -u "CLIENT_ID:CLIENT_SECRET" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_CODE" \
  -d "redirect_uri=http://localhost:8080/"
```

## 5. Save Tokens
Copy the `access_token` and `refresh_token` from the JSON response to `secrets.conf`:

```bash
FITBIT_ACCESS_TOKEN="eyJ..."
FITBIT_REFRESH_TOKEN="x8z..."
```

## 6. Run
The skill is now ready. The script will automatically refresh the token when it expires.
```bash
python scripts/fitbit_api.py report --type weekly
```
