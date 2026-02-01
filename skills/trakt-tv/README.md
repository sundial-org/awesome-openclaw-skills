# Trakt AgentSkill for OpenClaw

An [AgentSkills](https://agentskills.io/)-compatible skill that enables OpenClaw agents to interact with the Trakt API for managing watchlists, tracking viewing history, maintaining collections, rating content, and discovering movies and shows.

## What is AgentSkills?

AgentSkills is a standardized format for teaching AI agents how to use tools. Each skill is a folder containing a `SKILL.md` file with YAML frontmatter and usage instructions. OpenClaw loads these skills and makes them available to the agent.

This is **NOT** an MCP server - it's a simple skill file that teaches the agent how to use the Trakt API via curl commands.

## Installation

### Option 1: Install via ClawHub (Recommended)

```bash
npm install -g clawhub
clawhub install trakt
```

### Option 2: Manual Installation

1. Clone or download this repository to your OpenClaw skills directory:

```bash
# For workspace-specific (highest priority)
cd your-workspace
git clone https://github.com/yourusername/trakt-openclaw.git skills/trakt

# For user-wide (shared across all agents)
git clone https://github.com/yourusername/trakt-openclaw.git ~/.openclaw/skills/trakt
```

2. OpenClaw will automatically detect the skill in the next session.

## Setup

### Step 1: Create a Trakt Application

1. Go to https://trakt.tv/oauth/applications
2. Click "New Application"
3. Fill in:
   - **Name**: OpenClaw Trakt Integration (or your preferred name)
   - **Description**: AI agent access to Trakt
   - **Redirect URI**: `urn:ietf:wg:oauth:2.0:oob`
4. Save and note your **Client ID** and **Client Secret**

### Step 2: Get OAuth Access Token

Run the included helper script:

```bash
chmod +x get_trakt_token.sh
./get_trakt_token.sh
```

Follow the prompts to:
1. Open the authorization URL
2. Approve the application
3. Copy the code
4. Paste it into the script

The script will output the configuration you need.

### Step 3: Configure OpenClaw

Add the configuration to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "trakt": {
        "enabled": true,
        "env": {
          "TRAKT_CLIENT_ID": "your_client_id_here",
          "TRAKT_CLIENT_SECRET": "your_client_secret_here",
          "TRAKT_ACCESS_TOKEN": "your_access_token_here",
          "TRAKT_REFRESH_TOKEN": "your_refresh_token_here"
        }
      }
    }
  }
}
```

### Step 4: Restart OpenClaw

Skills are loaded at session start, so restart your OpenClaw agent to pick up the new skill.

## Usage

Once configured, you can ask your OpenClaw agent to interact with Trakt:

**Watchlist:**
- "Add Inception to my Trakt watchlist"
- "Show me my Trakt watchlist"
- "Remove The Matrix from my watchlist"

**Search:**
- "Search Trakt for movies about space"
- "Find shows similar to Breaking Bad on Trakt"

**History:**
- "Mark Dune as watched on Trakt"
- "Show my Trakt watch history"

**Collection:**
- "Add Blade Runner 2049 to my Trakt collection as 4K Blu-ray"
- "Show my movie collection on Trakt"

**Ratings:**
- "Rate The Shawshank Redemption 10/10 on Trakt"
- "Show my Trakt ratings"

**Discovery:**
- "What movies are trending on Trakt?"
- "Get personalized movie recommendations from Trakt"
- "Show me popular shows on Trakt"

## Features

- ✅ **Watchlist Management**: Add, remove, and view watchlist items
- ✅ **Search**: Find movies and shows by title
- ✅ **History Tracking**: Mark items as watched and view history
- ✅ **Collection Management**: Track your physical and digital media
- ✅ **Ratings**: Rate content on a 1-10 scale
- ✅ **Discovery**: Get trending, popular, and personalized recommendations
- ✅ **OAuth Authentication**: Secure API access
- ✅ **Rate Limiting**: Respects Trakt API limits

## How It Works

The skill teaches the OpenClaw agent to:
1. Use `curl` commands with proper Trakt API headers
2. Format requests with correct JSON payloads
3. Handle authentication using OAuth tokens
4. Parse responses and present information to users

The agent automatically:
- Injects environment variables into commands
- Constructs appropriate API requests
- Handles errors and rate limits
- Formats responses in a user-friendly way

## Skill Structure

```
trakt-openclaw/
├── SKILL.md              # Main skill file (AgentSkills format)
├── get_trakt_token.sh    # OAuth helper script
└── README.md             # This file
```

## API Endpoints

The skill covers these main Trakt API endpoints:

- **Sync**: `/sync/watchlist`, `/sync/history`, `/sync/collection`, `/sync/ratings`
- **Search**: `/search/movie`, `/search/show`
- **Discovery**: `/movies/trending`, `/movies/popular`, `/recommendations/movies`
- **Shows**: `/shows/trending`, `/shows/popular`, `/recommendations/shows`

Full API documentation: https://trakt.docs.apiary.io/

## Rate Limits

- **Authenticated (per user)**: 1000 GET requests per 5 minutes, 1 POST/PUT/DELETE per second
- **Unauthenticated (per app)**: 1000 GET requests per 5 minutes

## Token Refresh

Access tokens expire after 3 months. To refresh:

```bash
curl -X POST https://api.trakt.tv/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "'"$TRAKT_REFRESH_TOKEN"'",
    "client_id": "'"$TRAKT_CLIENT_ID"'",
    "client_secret": "'"$TRAKT_CLIENT_SECRET"'",
    "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
    "grant_type": "refresh_token"
  }'
```

Update your config with the new tokens.

## Publishing to ClawHub

To share this skill with the community:

```bash
npm install -g clawhub
clawhub login
clawhub publish . --slug trakt --name "Trakt" --version 1.0.0 --tags latest
```

## Troubleshooting

**Skill not loading:**
- Check `~/.openclaw/skills/trakt/SKILL.md` exists
- Verify permissions: `chmod +r SKILL.md`
- Restart OpenClaw session

**Authentication errors:**
- Verify environment variables are set in config
- Check token hasn't expired (3 month lifetime)
- Re-run `get_trakt_token.sh` if needed

**Rate limiting:**
- Wait 5 minutes before retrying
- Reduce request frequency
- Check Trakt API status

## Resources

- [Trakt API Documentation](https://trakt.docs.apiary.io/)
- [Trakt Applications](https://trakt.tv/oauth/applications)
- [AgentSkills Specification](https://agentskills.io/)
- [OpenClaw Documentation](https://docs.openclaw.ai/tools/skills)
- [ClawHub Registry](https://clawhub.com/)

## License

MIT

## Contributing

Contributions welcome! This is an AgentSkill, so improvements to the `SKILL.md` file - better examples, clearer instructions, or additional API coverage - are most valuable.
