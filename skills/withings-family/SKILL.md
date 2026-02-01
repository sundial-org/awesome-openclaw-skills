---
name: withings-family
description: Fetches health data from the Withings API for multiple family members including weight, body composition (fat, muscle, bone, water), activity, and sleep. Use this skill when the user asks about their or their family's Withings data, weight history, body metrics, daily steps, sleep quality, or any health measurement from Withings devices.
version: 1.0.1
homepage: https://developer.withings.com/
metadata: {"clawdbot":{"emoji":"⚖️","requires":{"bins":["python3"],"env":["WITHINGS_CLIENT_ID","WITHINGS_CLIENT_SECRET"]}}}
---

This skill allows you to interact with Withings accounts for **multiple family members** to retrieve comprehensive health metrics from Withings devices (smart scales, sleep analyzers, activity trackers, etc.).

## Multi-User Support

This skill natively supports multiple users with per-user token files:

```
tokens-alice.json
tokens-bob.json
tokens-charlie.json
```

Each family member authenticates once via OAuth. Their tokens are stored separately and refreshed automatically. No token copying or switching required — just pass the user ID as the first argument.

```bash
python3 scripts/withings.py alice weight
python3 scripts/withings.py bob sleep
python3 scripts/withings.py charlie activity
```

## When to Use This Skill

Use this skill when the user:
- Asks about their **weight** or weight history
- Wants to see their **body composition** (fat %, muscle mass, bone mass, hydration)
- Requests their **daily activity** (steps, distance, calories burned)
- Asks about their **sleep data** (duration, quality, deep sleep, REM)
- Mentions "Withings" or any Withings device (Body+, Sleep Analyzer, ScanWatch, etc.)
- Wants to track their or their **family's** health progress over time

## Setup: Creating a Withings Developer App

Before using this skill, you need to create a free Withings developer application to get your API credentials.

### Step 1: Create a Withings Developer Account

1. Go to [Withings Developer Portal](https://developer.withings.com/)
2. Click **Sign Up** or **Log In** if you already have a Withings account
3. Accept the Developer Terms of Service

### Step 2: Create Your Application

1. Navigate to **My Apps** → **Create an Application**
2. Fill in the application details:
   - **Application Name**: Choose a name (e.g., "My Clawdbot Health")
   - **Description**: Brief description of your use case
   - **Contact Email**: Your email address
   - **Callback URL**: `http://localhost:18081` (required for OAuth)
   - **Application Type**: Select "Personal Use" or appropriate type
3. Submit the application

### Step 3: Get Your Credentials

Once your application is created:
1. Go to **My Apps** and select your application
2. You'll find:
   - **Client ID** → Set as `WITHINGS_CLIENT_ID` environment variable
   - **Client Secret** → Set as `WITHINGS_CLIENT_SECRET` environment variable

### Step 4: Configure Environment Variables

Add these to your Clawdbot environment:
```bash
export WITHINGS_CLIENT_ID="your_client_id_here"
export WITHINGS_CLIENT_SECRET="your_client_secret_here"
```

Or create a `.env` file in `~/.clawdbot/withings-family/.env`:
```
WITHINGS_CLIENT_ID=your_client_id_here
WITHINGS_CLIENT_SECRET=your_client_secret_here
```

## Configuration

The skill provides two scripts (in `scripts/`):
- **`scripts/withings_oauth_local.py`** — Automatic OAuth with local callback server (recommended)
- **`scripts/withings.py`** — Main CLI + manual OAuth

**Credentials location:** `~/.clawdbot/withings-family/`
- `.env` — Client ID/Secret (optional, can use ENV vars instead)
- `tokens-<userId>.json` — OAuth tokens per user (mode 600)

Before any data retrieval, check if the user is authenticated. If an error mentions "No token found", guide the user through the initial authentication process for that specific user.

## Authentication Methods

### Method A: Automatic OAuth (Recommended)

Uses a local callback server to capture the code automatically:

```bash
python3 {baseDir}/scripts/withings_oauth_local.py <userId>
```

Example:
```bash
python3 {baseDir}/scripts/withings_oauth_local.py alice
```

The script will:
1. Print the authorization URL
2. Start a local server on localhost:18081
3. Wait for the redirect
4. Automatically capture the code and exchange for tokens
5. Save tokens to `tokens-<userId>.json`

### Method B: Manual OAuth

Traditional two-step flow (see "Authentication" command below).

## Available Commands

All commands follow the format:
```bash
python3 {baseDir}/scripts/withings.py <userId> <command> [options]
```

### 1. Authentication

First-time setup for a user — generates the OAuth URL:
```bash
python3 {baseDir}/scripts/withings.py alice auth
```

After the user visits the URL and gets the authorization code:
```bash
python3 {baseDir}/scripts/withings.py alice auth YOUR_CODE_HERE
```

Repeat for each family member who needs access.

### 2. Get Weight

Retrieve the latest weight measurements:
```bash
python3 {baseDir}/scripts/withings.py alice weight
```

Returns the 5 most recent weight entries in JSON format.

**Example output:**
```json
[
  { "date": "2026-01-17T08:30:00.000Z", "weight": "75.40 kg" },
  { "date": "2026-01-16T08:15:00.000Z", "weight": "75.65 kg" }
]
```

### 3. Get Body Composition

Retrieve comprehensive body metrics (fat, muscle, bone, water, BMI):
```bash
python3 {baseDir}/scripts/withings.py alice body
```

Returns the 5 most recent body composition measurements.

**Example output:**
```json
[
  {
    "date": "2026-01-17T08:30:00.000Z",
    "weight": "75.40 kg",
    "fat_percent": "18.5%",
    "fat_mass": "13.95 kg",
    "muscle_mass": "35.20 kg",
    "bone_mass": "3.10 kg",
    "hydration": "55.2%"
  }
]
```

### 4. Get Activity

Retrieve daily activity data (steps, distance, calories):
```bash
python3 {baseDir}/scripts/withings.py alice activity
```

Optionally specify the number of days (default: 7):
```bash
python3 {baseDir}/scripts/withings.py alice activity 30
```

**Example output:**
```json
[
  {
    "date": "2026-01-17",
    "steps": 8542,
    "distance": "6.23 km",
    "calories": 2150,
    "active_calories": 450,
    "soft_activity": "45 min",
    "moderate_activity": "22 min",
    "intense_activity": "8 min"
  }
]
```

### 5. Get Sleep

Retrieve sleep data and quality:
```bash
python3 {baseDir}/scripts/withings.py alice sleep
```

Optionally specify the number of days (default: 7):
```bash
python3 {baseDir}/scripts/withings.py alice sleep 14
```

**Example output:**
```json
[
  {
    "date": "2026-01-17",
    "start": "23:15",
    "end": "07:30",
    "duration": "8h 15min",
    "deep_sleep": "1h 45min",
    "light_sleep": "4h 30min",
    "rem_sleep": "1h 30min",
    "awake": "30min",
    "sleep_score": 82
  }
]
```

## Error Handling

Common errors and how to resolve them:

| Error | Cause | Solution |
|-------|-------|----------|
| "No token found" | User not authenticated | Run `python3 scripts/withings.py <userId> auth` and follow the OAuth flow |
| "Failed to refresh token" | Token expired and refresh failed | Re-authenticate with `python3 scripts/withings.py <userId> auth` |
| "API Error Status: 401" | Invalid or expired credentials | Check your CLIENT_ID and CLIENT_SECRET, re-authenticate |
| "API Error Status: 503" | Withings API temporarily unavailable | Wait and retry later |
| Empty data | No measurements in the requested period | User needs to sync their Withings device |

## Notes

- **Multi-user:** Each family member has their own token file (`tokens-{userId}.json`)
- **Token refresh:** Tokens are automatically refreshed when they expire
- **Scopes:** Withings API scopes used: `user.metrics`, `user.activity`
- **Device support:** Data availability depends on which Withings devices the user owns
- **Body composition:** Requires a compatible smart scale (e.g., Body+, Body Comp)
