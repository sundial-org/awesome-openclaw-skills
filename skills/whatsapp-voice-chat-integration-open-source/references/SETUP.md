# WhatsApp Voice Talk - Setup Guide

## Prerequisites

### Required Software
- Node.js 14+ (for running JavaScript components)
- Python 3.8+ (for transcription)
- Clawdbot (with WhatsApp channel configured)

### Required Python Packages
```bash
pip install whisper soundfile numpy
```

Or install all at once:
```bash
pip install openai-whisper soundfile numpy
```

## Installation Steps

### 1. Extract the Skill
Place the skill in your Clawdbot skills directory or your local project:
```bash
# Option A: System-wide (if using clawdhub)
clawdhub install whatsapp-voice-talk

# Option B: Local project
cp -r whatsapp-voice-talk /path/to/your/project/skills/
```

### 2. Install Python Dependencies
```bash
cd skills/whatsapp-voice-talk/scripts
pip install -r requirements.txt
```

### 3. Configure Clawdbot
Your Clawdbot WhatsApp channel should already be configured. Verify it in `~/.clawdbot/clawdbot.json`:

```json
{
  "channels": {
    "whatsapp": {
      "enabled": true,
      "allowFrom": ["+1234567890"]
    }
  }
}
```

## Usage

### Option 1: Auto-Listener (Recommended)
Run the background daemon to automatically process incoming voice notes:

```bash
node skills/whatsapp-voice-talk/scripts/voice-listener-daemon.js
```

This watches for new voice messages in `~/.clawdbot/media/inbound/` and processes them every 5 seconds.

### Option 2: Manual Processing
Process a voice file on-demand in your code:

```javascript
const { processVoiceNote } = require('./voice-processor');
const fs = require('fs');

const audioBuffer = fs.readFileSync('/path/to/voice.ogg');
const result = await processVoiceNote(audioBuffer);

console.log(result);
// {
//   status: 'success',
//   response: 'Weather in Delhi is 19°C',
//   transcript: "What's the weather?",
//   intent: 'weather',
//   language: 'en'
// }
```

### Option 3: From WhatsApp Message
In a Clawdbot message handler:

```javascript
const { processVoiceNote } = require('./skills/whatsapp-voice-talk/scripts/voice-processor');

// When you receive a WhatsApp voice message:
const audioBuffer = message.mediaBuffer; // Clawdbot provides this
const result = await processVoiceNote(audioBuffer);

// Send response back via WhatsApp
await sendWhatsAppMessage(message.from, result.response);
```

## Customization

### Add Custom Intents

Edit `voice-processor.js` to add new intents:

```javascript
const INTENTS = {
  'your-intent': {
    keywords: ['keyword1', 'keyword2', 'कीवर्ड'],
    handler: 'handleYourIntent'
  }
};

// Add handler
const handlers = {
  async handleYourIntent(language = 'en') {
    const responses = {
      en: 'English response',
      hi: 'हिंदी जवाब'
    };
    return { status: 'success', response: responses[language] };
  }
};
```

### Add Support for More Languages

1. Update `detectLanguage()` function to recognize your language's Unicode range
2. Add language-specific handler responses
3. Optional: Specify language in `transcribe.py` (currently defaults to English):

```python
result = model.transcribe(data, language="es")  # Spanish
```

### Change Transcription Model

Edit `transcribe.py` to use a different Whisper model:

```python
model = whisper.load_model("small")   # Faster, ~500MB
model = whisper.load_model("base")    # Default, ~140MB
model = whisper.load_model("medium")  # Better accuracy, ~1.5GB
```

## Troubleshooting

### "No module named 'soundfile'"
```bash
pip install soundfile
```

### "No module named 'whisper'"
```bash
pip install openai-whisper
```

### Voice messages not being processed
1. Check that Clawdbot is running: `clawdbot status`
2. Check that WhatsApp channel is enabled in config
3. Verify the inbound directory exists: `ls ~/.clawdbot/media/inbound/`
4. Check daemon logs for errors

### Transcription is slow
- Use a smaller model: `whisper.load_model("tiny")` or `"base"` instead of "large"
- First run downloads the model (~140MB for base), subsequent runs are faster

### Wrong language detected
- Language detection is automatic based on character detection
- Override in code: `await processVoiceNote(buffer)` and specify language in handlers

## Architecture

```
voice-listener-daemon.js
  ↓
  Watches ~/.clawdbot/media/inbound/ for .ogg files
  ↓
voice-processor.js
  ├─ transcribeVoiceNote() → transcribe.py (Whisper)
  ├─ detectLanguage()
  ├─ parseCommand() → matches INTENTS
  └─ executeCommand() → runs handler
  ↓
  Returns: { status, response, transcript, intent, language }
  ↓
  Parent process sends response via WhatsApp TTS
```

## Performance Notes

- **First transcription**: ~20-30 seconds (downloads Whisper model)
- **Subsequent**: ~5-10 seconds per message (depends on duration)
- **Memory**: ~1.5GB for base model
- **CPU**: Works on CPU, GPU optional but faster

## API Reference

See [API.md](API.md) for detailed function documentation.
