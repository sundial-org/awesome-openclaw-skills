---
name: whatsapp-voice-talk
description: Real-time WhatsApp voice message processing. Transcribe voice notes to text via Whisper, detect intent, execute handlers, and send responses. Use when building conversational voice interfaces for WhatsApp. Supports English and Hindi, customizable intents (weather, status, commands), automatic language detection, and streaming responses via TTS.
---

# WhatsApp Voice Talk

Turn WhatsApp voice messages into real-time conversations. This skill provides a complete pipeline: **voice → transcription → intent detection → response generation → text-to-speech**.

Perfect for:
- Voice assistants on WhatsApp
- Hands-free command interfaces  
- Multi-lingual chatbots
- IoT voice control (drones, smart home, etc.)

## Quick Start

### 1. Install Dependencies

```bash
pip install openai-whisper soundfile numpy
```

### 2. Process a Voice Message

```javascript
const { processVoiceNote } = require('./scripts/voice-processor');
const fs = require('fs');

// Read a voice message (OGG, WAV, MP3, etc.)
const buffer = fs.readFileSync('voice-message.ogg');

// Process it
const result = await processVoiceNote(buffer);

console.log(result);
// {
//   status: 'success',
//   response: "Current weather in Delhi is 19°C, haze. Humidity is 56%.",
//   transcript: "What's the weather today?",
//   intent: 'weather',
//   language: 'en',
//   timestamp: 1769860205186
// }
```

### 3. Run Auto-Listener

For automatic processing of incoming WhatsApp voice messages:

```bash
node scripts/voice-listener-daemon.js
```

This watches `~/.clawdbot/media/inbound/` every 5 seconds and processes new voice files.

## How It Works

```
Incoming Voice Message
        ↓
    Transcribe (Whisper API)
        ↓
  "What's the weather?"
        ↓
  Detect Language & Intent
        ↓
   Match against INTENTS
        ↓
   Execute Handler
        ↓
   Generate Response
        ↓
   Convert to TTS
        ↓
  Send back via WhatsApp
```

## Key Features

✅ **Zero Setup Complexity** - No FFmpeg, no complex dependencies. Uses soundfile + Whisper.

✅ **Multi-Language** - Automatic English/Hindi detection. Extend easily.

✅ **Intent-Driven** - Define custom intents with keywords and handlers.

✅ **Real-Time Processing** - 5-10 seconds per message (after first model load).

✅ **Customizable** - Add weather, status, commands, or anything else.

✅ **Production Ready** - Built from real usage in Clawdbot.

## Common Use Cases

### Weather Bot
```javascript
// User says: "What's the weather in Bangalore?"
// Response: "Current weather in Delhi is 19°C..."

// (Built-in intent, just enable it)
```

### Smart Home Control
```javascript
// User says: "Turn on the lights"
// Handler: Sends signal to smart home API
// Response: "Lights turned on"
```

### Task Manager
```javascript
// User says: "Add milk to shopping list"
// Handler: Adds to database
// Response: "Added milk to your list"
```

### Status Checker
```javascript
// User says: "Is the system running?"
// Handler: Checks system status
// Response: "All systems online"
```

## Customization

### Add a Custom Intent

Edit `voice-processor.js`:

1. **Add to INTENTS map:**
```javascript
const INTENTS = {
  'shopping': {
    keywords: ['shopping', 'list', 'buy', 'खरीद'],
    handler: 'handleShopping'
  }
};
```

2. **Add handler:**
```javascript
const handlers = {
  async handleShopping(language = 'en') {
    return {
      status: 'success',
      response: language === 'en' 
        ? "What would you like to add to your shopping list?"
        : "आप अपनी शॉपिंग लिस्ट में क्या जोड़ना चाहते हैं?"
    };
  }
};
```

### Support More Languages

1. Update `detectLanguage()` for your language's Unicode:
```javascript
const urduChars = /[\u0600-\u06FF]/g; // Add this
```

2. Add language code to returns:
```javascript
return language === 'ur' ? 'Urdu response' : 'English response';
```

3. Set language in `transcribe.py`:
```python
result = model.transcribe(data, language="ur")
```

### Change Transcription Model

In `transcribe.py`:
```python
model = whisper.load_model("tiny")    # Fastest, 39MB
model = whisper.load_model("base")    # Default, 140MB  
model = whisper.load_model("small")   # Better, 466MB
model = whisper.load_model("medium")  # Good, 1.5GB
```

## Architecture

**Scripts:**
- `transcribe.py` - Whisper transcription (Python)
- `voice-processor.js` - Core logic (intent parsing, handlers)
- `voice-listener-daemon.js` - Auto-listener watching for new messages

**References:**
- `SETUP.md` - Installation and configuration
- `API.md` - Detailed function documentation

## Integration with Clawdbot

If running as a Clawdbot skill, hook into message events:

```javascript
// In your Clawdbot handler
const { processVoiceNote } = require('skills/whatsapp-voice-talk/scripts/voice-processor');

message.on('voice', async (audioBuffer) => {
  const result = await processVoiceNote(audioBuffer, message.from);
  
  // Send response back
  await message.reply(result.response);
  
  // Or send as voice (requires TTS)
  await sendVoiceMessage(result.response);
});
```

## Performance

- **First run:** ~30 seconds (downloads Whisper model, ~140MB)
- **Typical:** 5-10 seconds per message
- **Memory:** ~1.5GB (base model)
- **Languages:** English, Hindi (easily extended)

## Supported Audio Formats

OGG (Opus), WAV, FLAC, MP3, CAF, AIFF, and more via libsndfile.

WhatsApp uses Opus-coded OGG by default — works out of the box.

## Troubleshooting

**"No module named 'whisper'"**
```bash
pip install openai-whisper
```

**"No module named 'soundfile'"**
```bash
pip install soundfile
```

**Voice messages not processing?**
1. Check: `clawdbot status` (is it running?)
2. Check: `~/.clawdbot/media/inbound/` (files arriving?)
3. Run daemon manually: `node scripts/voice-listener-daemon.js` (see logs)

**Slow transcription?**
Use smaller model: `whisper.load_model("base")` or `"tiny"`

## Further Reading

- **Setup Guide:** See `references/SETUP.md` for detailed installation and configuration
- **API Reference:** See `references/API.md` for function signatures and examples
- **Examples:** Check `scripts/` for working code

## License

MIT - Use freely, customize, contribute back!

---

Built for real-world use in Clawdbot. Battle-tested with multiple languages and use cases.
