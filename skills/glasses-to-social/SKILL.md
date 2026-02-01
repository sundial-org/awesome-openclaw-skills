---
name: glasses-to-social
description: Turn smart glasses photos into social media posts. Monitors a Google Drive folder for new images from Meta Ray-Ban glasses (or any smart glasses), analyzes them with vision AI, drafts tweets/posts in the user's voice, and publishes on approval. Use when setting up a glasses-to-social pipeline, processing smart glasses photos for social media, or creating hands-free content workflows.
---

# Glasses-to-Social

Transform photos from smart glasses into social media posts with AI-generated captions.

## Overview

This skill creates a pipeline from smart glasses (Meta Ray-Ban, etc.) to social media:

1. User snaps photo with glasses
2. Photo syncs to Google Drive folder
3. Agent detects new photo, analyzes with vision
4. Agent drafts post matching user's voice/style
5. User approves, agent publishes

## Setup

### 1. Configure Google Drive Folder

Create a shared Google Drive folder for glasses photos:

```bash
# User creates folder "Glasses-to-Social" in Google Drive
# Share with "Anyone with link can view"
# Copy the folder URL
```

### 2. Set Up Config

Create config file at `glasses-to-social/config.json`:

```json
{
  "googleDriveFolderUrl": "https://drive.google.com/drive/folders/YOUR_FOLDER_ID",
  "folderId": "YOUR_FOLDER_ID",
  "downloadPath": "./glasses-to-social/downloads",
  "processedFile": "./glasses-to-social/data/processed.json",
  "defaultHashtags": ["#MedicalAI", "#HealthTech"],
  "autoPost": false
}
```

### 3. Configure Glasses Auto-Sync

For Meta Ray-Ban glasses:
1. Open Meta View app on phone
2. Settings > Gallery > Enable "Import Automatically"
3. iOS: Enable Google Photos backup (syncs Camera Roll)
4. Create iOS Shortcut to copy new Meta photos to Google Drive folder

## Usage

### Manual Check

Ask the agent to check for new photos:

```
Check my glasses folder for new photos
```

### Automated Monitoring

Set up a cron job to check periodically:

```json
{
  "name": "Glasses-to-Social: Check photos",
  "schedule": {"kind": "cron", "expr": "*/15 * * * *", "tz": "UTC"},
  "payload": {
    "message": "Check the Glasses-to-Social folder for new photos. If found, analyze and draft a tweet."
  }
}
```

### Processing Flow

When a new photo is detected:

1. Download from Google Drive using `gdown`:
   ```bash
   gdown --folder "FOLDER_URL" -O ./downloads/ --remaining-ok
   ```

2. Compare against processed list in `data/processed.json`

3. For new photos, analyze with vision:
   - Describe the scene/subject
   - Identify relevant context for social post
   - Note any text, people, or notable elements

4. Draft post matching user's voice:
   - Keep it concise and authentic
   - Add relevant hashtags
   - First-person perspective works well for glasses content

5. Send draft to user for approval:
   - Include image preview
   - Show proposed caption
   - Wait for "POST" confirmation or edits

6. On approval, publish to configured platform (X/Twitter, etc.)

7. Mark photo as processed in `data/processed.json`

## Scripts

### check-new-photos.sh

Checks Google Drive folder for new images:

```bash
scripts/check-new-photos.sh
```

Output format when new photo found:
```
NEW_PHOTO_PATH:/path/to/downloaded/photo.jpg
```

## File Tracking

Track processed photos in `data/processed.json`:

```json
{
  "processed": ["photo1.jpg", "photo2.jpg"],
  "pending": []
}
```

## Tips

- First-person POV content performs well ("Look what I just saw...")
- Keep captions authentic, not overly polished
- Works great for conferences, interesting sightings, daily moments
- Consider time-of-day context when drafting

## Requirements

- `gdown` Python package for Google Drive access
- Vision-capable model for image analysis
- Twitter/X credentials for posting (optional)
