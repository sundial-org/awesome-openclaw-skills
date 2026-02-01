# reddit-cli 📮

A simple Reddit CLI that uses your browser cookies for authentication. No API key needed.

Built for [Clawdbot](https://github.com/clawdbot/clawdbot) but works standalone too.

## Installation

```bash
# Clone the repo
git clone https://github.com/kelsia14/reddit-cli.git

# Or just download the script
curl -o reddit-cli.js https://raw.githubusercontent.com/kelsia14/reddit-cli/main/scripts/reddit-cli.js
```

## Setup

1. Go to [reddit.com](https://reddit.com) (logged in)
2. Open DevTools (F12) → Application → Cookies → reddit.com
3. Copy the `reddit_session` cookie value
4. Set it as an environment variable:

```bash
export REDDIT_SESSION="your_cookie_value_here"
export TOKEN_V2="your_token_v2_here"  # optional, but recommended
```

Add these to your `~/.bashrc` or `~/.zshrc` to persist them.

## Usage

```bash
# Get posts from a subreddit
node reddit-cli.js posts programming 10       # 10 hot posts
node reddit-cli.js posts gaming 5 top         # top 5 posts
node reddit-cli.js posts news 20 new          # 20 newest posts

# Search Reddit
node reddit-cli.js search "python tutorial"           # search all
node reddit-cli.js search "help" --sub linux 10       # search in subreddit

# Get subreddit info
node reddit-cli.js info AskReddit

# Check if your cookies work
node reddit-cli.js check
```

## Commands

| Command | Description |
|---------|-------------|
| `posts <subreddit> [limit] [sort]` | Get posts (sort: hot, new, top, rising) |
| `search <query> [--sub <subreddit>] [limit]` | Search Reddit |
| `info <subreddit>` | Get subreddit info |
| `check` | Verify cookie authentication |

## For Clawdbot Users

Install as a skill:
```bash
# Copy to your skills folder
cp -r reddit-cli /path/to/clawd/skills/
```

The skill will be available once Clawdbot restarts.

## Notes

- Cookies expire periodically, you may need to refresh them
- Be respectful of Reddit's rate limits
- For personal use only

## License

MIT
