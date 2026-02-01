---
name: google-home
description: Control smart home devices (lights, TV, etc.) via the Google Assistant SDK. Use when the user wants to trigger home automation commands.
author: Mathew Pittard (Mat)
---

# Google Home Control (N.O.V.A.)

Created by: **Mathew Pittard (Mat)**  
Portfolio: [mathewpittard.vercel.app](https://mathewpittard.vercel.app)

This skill allows **Clawdbot** to control your smart home devices (lights, TVs, appliances) directly using a Python-based bridge to the Google Assistant SDK.

## 🛠️ Step-by-Step Setup

To get this skill working, you'll need to link it to your own Google account. Follow these steps:

### 1. Create a Google Cloud Project
1.  Go to the [Google Cloud Console](https://console.developers.google.com/).
2.  Create a new project (e.g., "My Smart Home").
3.  Enable the **Google Assistant API**.

### 2. Configure OAuth
1.  Go to **APIs & Services > Credentials**.
2.  Configure your **OAuth Consent Screen** (set User Type to "External" and add yourself as a test user).
3.  Create an **OAuth 2.0 Client ID** with the type **Desktop app**.
4.  Download the JSON file and rename it to `client_secret.json`.

### 3. Prepare the Python Environment
This skill requires a Python virtual environment with specific dependencies:
```bash
# Create and activate environment
python3 -m venv google_home_env
source google_home_env/bin/activate

# Install requirements
pip install google-assistant-sdk[samples] google-auth-oauthlib[tool] tenacity
```

### 4. Authorize and Generate Credentials
Run the following command in your terminal to authorize the SDK:
```bash
google-oauthlib-tool --client-secrets /path/to/your/client_secret.json --scope https://www.googleapis.com/auth/assistant-sdk-prototype --save
```
*   This will open a browser window. Log in and grant permissions.
*   It will save a `credentials.json` file to `~/.config/google-oauthlib-tool/credentials.json`.

### 5. Final Configuration
Ensure the `google_home_env` is accessible to Clawdbot. When Clawdbot runs the skill, it will look for your credentials in the standard `~/.config` path automatically.

---

## 🚀 Usage
Simply tell the agent what to do:
- "Turn off the office lights."
- "Set the TV volume to 20."

The agent will use the `control.py` script inside this skill to execute the command via Google Assistant.
