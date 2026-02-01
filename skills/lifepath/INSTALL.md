# Installation Guide

## Quick Start

1. **Extract files**
   ```bash
   cd lifepath-package
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   sudo service postgresql start
   
   # Create database
   sudo -u postgres psql -c "CREATE DATABASE lifepath;"
   sudo -u postgres psql -c "CREATE USER ubuntu WITH PASSWORD 'ubuntu';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE lifepath TO ubuntu;"
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Initialize database**
   ```bash
   npm run init-db
   ```

6. **Start server**
   ```bash
   npm start
   ```

## Telegram Bot Setup

1. Message @BotFather on Telegram
2. Run `/newbot`
3. Name it "LifePathBot"
4. Copy the token
5. Add to `.env`: `TELEGRAM_BOT_TOKEN=your_token`

## API Keys Needed

- **GEMINI_API_KEY**: Get from Google AI Studio
- **DATABASE_URL**: PostgreSQL connection string
- **TELEGRAM_BOT_TOKEN**: From @BotFather
- **BANANA_API_KEY**: For image generation (optional)
- **MOLTBOOK_API_KEY**: For sharing to Moltbook

## Testing

```bash
# Start a life
curl -X POST http://localhost:3000/api/life/start \
  -d '{"userId": "test", "country": "Japan", "year": 1985, "gender": "female"}'

# Check health
curl http://localhost:3000/health
```
