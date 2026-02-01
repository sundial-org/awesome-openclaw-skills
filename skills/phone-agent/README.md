# Phone Agent Moltbot Skill

A real-time AI voice agent that handles incoming phone calls using Twilio, transcribes speech with Deepgram, generates responses via OpenAI, and speaks back with ElevenLabs text-to-speech.

## Features

- **Real-time Voice Processing**: Handles incoming Twilio calls with low-latency WebSocket audio
- **Automatic Speech Recognition**: Deepgram for fast, accurate transcription
- **AI-Powered Responses**: OpenAI GPT for intelligent conversation
- **Natural Speech Output**: ElevenLabs for realistic, streaming TTS
- **Task-Based Automation**: Configurable task definitions for specific agent behaviors
- **Recording & Logging**: Automatic call recording and conversation logs

## Architecture

```
Incoming Call (Twilio Phone)
         |
         v
  Twilio WebSocket (Audio Stream)
         |
         +---> Local FastAPI Server
         |           |
         |           +---> Deepgram (Speech-to-Text)
         |           |
         |           +---> OpenAI (LLM/Intelligence)
         |           |
         |           +---> ElevenLabs (Text-to-Speech)
         |           |
         +---------- (Audio Response)
         |
    Phone Speaker Output
```

## Prerequisites

Before you begin, ensure you have:

1. **Twilio Account**
   - Active Twilio account with a phone number
   - TwiML App configured
   - Account SID and Auth Token

2. **API Keys** (free tier available for all)
   - Deepgram API Key (https://console.deepgram.com/)
   - OpenAI API Key (https://platform.openai.com/api-keys)
   - ElevenLabs API Key (https://elevenlabs.io/)

3. **Local Network Access**
   - Ngrok or similar tool to expose localhost to the internet
   - Ability to accept incoming webhooks from Twilio

4. **Python 3.9+** and pip

## Installation

```bash
# Clone the repository
git clone https://github.com/kesslerio/phone-agent-moltbot-skill.git
cd phone-agent-moltbot-skill

# Install dependencies
pip install -r scripts/requirements.txt
```

## Configuration

### Set Environment Variables

Create a `.env` file or set environment variables:

```bash
# API Keys (required)
export DEEPGRAM_API_KEY="your-deepgram-key"
export OPENAI_API_KEY="your-openai-key"
export ELEVENLABS_API_KEY="your-elevenlabs-key"

# Twilio (required)
export TWILIO_ACCOUNT_SID="your-account-sid"
export TWILIO_AUTH_TOKEN="your-auth-token"
export TWILIO_PHONE_NUMBER="+18665515246"  # Your Twilio number

# Server (optional)
export PORT=8080
export PUBLIC_URL="https://your-ngrok-url.ngrok.io"  # For webhooks

# Voice Customization (optional)
export ELEVENLABS_VOICE_ID="onwK4e9ZLuTAKqWW03F9"  # Daniel voice
```

Or add to `~/.moltbot/.env` or `~/.clawdbot/.env`:

```
DEEPGRAM_API_KEY=your-key
OPENAI_API_KEY=your-key
ELEVENLABS_API_KEY=your-key
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1...
```

## Startup & Configuration

### 1. Start the Local Server

```bash
python3 scripts/server.py
```

The server will start on `http://localhost:8080` by default.

### 2. Expose to Internet with Ngrok

In another terminal:

```bash
ngrok http 8080
```

Note the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 3. Configure Twilio Webhook

In Twilio Console:

1. Go to **Phone Numbers** → Your number
2. Under **Voice & Fax**:
   - Set "A Call Comes In" to **Webhook**
   - URL: `https://<your-ngrok-url>.ngrok.io/incoming`
   - Method: `POST`
3. Save

### 4. Test Incoming Calls

Call your Twilio number. The agent will:
1. Answer and greet you
2. Listen to your speech
3. Transcribe your words
4. Generate a response via OpenAI
5. Speak the response back to you

## Customization

### Change Agent Persona

Edit `SYSTEM_PROMPT` in `scripts/server.py`:

```python
SYSTEM_PROMPT = """You are a helpful customer service agent. Be friendly, concise, and professional."""
```

### Change Voice

Set a different ElevenLabs voice ID:

```bash
export ELEVENLABS_VOICE_ID="g1r0eKKcGkk7Ep0RVcVn"  # Callum voice
```

Available ElevenLabs voices: https://elevenlabs.io/docs/getting-started/voices

### Use Different Model

Edit `scripts/server.py` and change the OpenAI model:

```python
response = await client.chat.completions.create(
    model="gpt-4",  # or "gpt-4-turbo" for faster responses
    messages=messages,
)
```

### Task-Based Behaviors

Create YAML task definitions in the `tasks/` directory:

```yaml
name: book_restaurant
description: "Help the user book a restaurant reservation"
system_prompt: "You are a friendly restaurant reservation assistant..."
actions:
  - confirm_date
  - confirm_time
  - confirm_party_size
  - book_reservation
```

## Integration with Moltbot

Add this skill to your Moltbot configuration:

```json
{
  "skills": [
    {
      "name": "phone-agent",
      "path": "/path/to/phone-agent-moltbot-skill",
      "enabled": true
    }
  ]
}
```

Then reference it in workflows:
- "Set up an incoming voice agent"
- "Configure a customer service chatbot"
- "Test voice AI capabilities"

## Project Structure

```
phone-agent-moltbot-skill/
├── scripts/
│   ├── server.py              # Main FastAPI server
│   ├── server_realtime.py     # Realtime processing variant
│   ├── requirements.txt       # Python dependencies
│   └── typing_sound.raw       # Typing sound effect
├── tasks/
│   ├── book_restaurant.yaml   # Example task definitions
│   └── get_quote.yaml         # Example task definitions
├── calls/                     # Recording storage directory
├── references/                # Supporting documentation
├── SKILL.md                   # Moltbot skill manifest
├── README.md                  # This file
└── LICENSE                    # MIT License
```

## Troubleshooting

### Server Won't Start

- Check Python version: `python3 --version` (requires 3.9+)
- Install dependencies: `pip install -r scripts/requirements.txt`
- Check PORT variable: `echo $PORT` (should be 8080 or set value)

### Twilio Webhook Not Connecting

- Verify ngrok is running and the URL matches your Twilio webhook
- Check server logs: `python3 scripts/server.py` (should show incoming requests)
- Test ngrok tunnel: `curl https://<your-ngrok-url>.ngrok.io/health`

### Poor Transcription Quality

- Ensure DEEPGRAM_API_KEY is valid
- Check microphone/audio quality on the calling phone
- Deepgram is very accurate; poor results indicate audio issues

### Slow Responses

- OpenAI API latency varies; gpt-4o-mini is fast and cheap
- Switch to "gpt-3.5-turbo" for faster responses (less capable)
- Increase timeout in websocket settings if needed

### Voice Not Speaking

- Verify ELEVENLABS_API_KEY is valid
- Check voice ID is correct: https://elevenlabs.io/docs/api-reference/voices
- Confirm audio is not muted on the receiving phone

## API Reference

### Incoming Call Webhook

**POST** `/incoming`

Twilio sends call information to this endpoint. The server responds with TwiML to establish WebSocket connection.

### WebSocket Audio Stream

**WS** `/ws`

Bidirectional audio stream for incoming call processing.

### Health Check

**GET** `/health`

Returns `{"status": "ok"}` if the server is running.

## Performance & Scaling

Current implementation handles:
- Single concurrent call per server instance
- ~100ms RTT for transcription + LLM + TTS
- Suitable for demo/testing, hobby projects, and low-volume use

For production:
- Run multiple server instances behind a load balancer
- Use Twilio's call queuing
- Implement connection pooling for API clients
- Consider dedicated hardware for Deepgram/ElevenLabs processing

## Deployment Options

### Local Development
```bash
python3 scripts/server.py
ngrok http 8080
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY scripts/requirements.txt .
RUN pip install -r requirements.txt
COPY scripts/ .
CMD ["python3", "server.py"]
```

Build and run:
```bash
docker build -t phone-agent .
docker run -p 8080:8080 \
  -e DEEPGRAM_API_KEY="..." \
  -e OPENAI_API_KEY="..." \
  -e ELEVENLABS_API_KEY="..." \
  -e TWILIO_ACCOUNT_SID="..." \
  -e TWILIO_AUTH_TOKEN="..." \
  phone-agent
```

### Cloud Deployment

- **Heroku**: Add `Procfile` → `web: python3 scripts/server.py`
- **Railway.app**: Auto-detects Python and builds
- **AWS Lambda**: Use WebSocket API Gateway + Lambda
- **Google Cloud Run**: Containerize and deploy

## License

MIT

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## Support

- MCP Server: [Deepgram](https://deepgram.com/) | [OpenAI](https://openai.com/) | [ElevenLabs](https://elevenlabs.io/)
- Twilio Docs: [Voice API](https://www.twilio.com/docs/voice)
- Moltbot: [Documentation](https://moltbot.io/)
