---
name: samsung-smart-tv
description: Control Samsung TVs via SmartThings (OAuth app + device control).
homepage: https://developer.smartthings.com/docs
metadata: {"clawdbot":{"emoji":"📺","requires":{"bins":["python3","npx"]},"install":[{"id":"python-brew","kind":"brew","formula":"python","bins":["python3"],"label":"Install Python (brew)"},{"id":"node-brew","kind":"brew","formula":"node","bins":["node","npx"],"label":"Install Node.js (brew)"}]}}
---

# Samsung Smart TV (SmartThings)

This skill provisions a SmartThings OAuth app and stores the credentials for Clawdbot.

Setup (one-time)
- Create the SmartThings OAuth app headlessly (requires a PAT) and print a phone login URL, using plain text instructions only.
- Open the URL on your phone, log in, then copy the code query parameter from the redirect page and re-run to exchange it.
- If PAT app creation fails (403), create the app on a normal machine using the SmartThings CLI login flow and then set the client id/secret in the .env before running the code-exchange step.
- Re-run to refresh credentials: describe the action in plain text (no code snippets).

What it does
- Creates an OAuth-In SmartApp with display name smartthings-clawdbot.
- Uses scopes r:devices:* and x:devices:* (read + execute commands).
- Redirect URI defaults to https://httpbin.org/get (can be overridden via redirect-uri option).
- Writes SMARTTHINGS_APP_ID, SMARTTHINGS_CLIENT_ID, SMARTTHINGS_CLIENT_SECRET plus OAuth tokens to ~/.clawdbot/.env (or CLAWDBOT_STATE_DIR/.env).
- Uses the SmartThings CLI to create the OAuth app when a PAT is provided.
- Exchanges the OAuth code for tokens via direct HTTPS to SmartThings (not via the CLI).

Device setup
- Use the SmartThings CLI to list devices in JSON and locate the TV device id.
- Store it as SMARTTHINGS_DEVICE_ID in the same .env file.

Common actions (plain text only)
- List devices and capabilities via the SmartThings CLI.
- Check device status.
- Send switch/volume/mute commands to the TV device.

App launch (Netflix/Prime Video)
- App launch is device-specific; look for applicationLauncher or samsungtv in capabilities.
- Discover app IDs in device status under supportedApps or installedApps.
- Launch apps using the SmartThings CLI and the appId from your TV.
- Example IDs are not universal; use the IDs listed for your TV.

App discovery (when a user asks to open a specific app)
- First, open the target app manually on the TV.
- Then query device status and look for fields like tvChannelName, installedApps, or supportedApps to extract the current appId.
- Save the appId for future use; some IDs are device-specific.
- Known app id patterns (examples):
  - Standard/global apps (often stable):
    - Netflix: org.tizen.netflix-app
    - Amazon Prime: org.tizen.primevideo
    - Pattern: org.tizen.[app-name]
  - Device-specific apps (vary per TV):
    - YouTube: {random}.TizenYouTube
    - Joyn: {random}.ZAPPNVOLLTVFREIGESTREAMT
    - Pattern: {random}.{PackageName}
- Avoid guessing; always confirm the appId from the TV’s status payload.

Notes
- The script defaults to headless mode and will not open a browser.
- Provide a PAT via SMARTTHINGS_TOKEN (or SMARTTHINGS_PAT) to authenticate.
- Create a PAT here: https://account.smartthings.com/tokens
- OAuth flow: open the printed URL on your phone, then copy the code query parameter from the redirect page and re-run with auth-code.
- The default redirect uses https://httpbin.org/get to show the code in the URL; you can switch to your own redirect URI if you don’t want to use httpbin.
- Re-running the setup is safe; it updates the env entries in place.
- Response style: do not include code blocks or inline command snippets; use plain text steps only.
