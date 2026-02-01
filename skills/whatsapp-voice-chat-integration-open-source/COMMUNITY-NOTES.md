# WhatsApp Voice Talk Skill - Community Edition

## Overview

This skill brings real-time voice conversation to WhatsApp, powered by OpenAI Whisper for transcription and customizable intent handlers.

**Built by:** Ateeb (@syeda)  
**Status:** Production-ready  
**License:** MIT (Use freely, share, contribute)

## What's Included

### Core Scripts
- **`transcribe.py`** - Python transcription using Whisper (no FFmpeg needed)
- **`voice-processor.js`** - Intent detection, handler execution, response generation
- **`voice-listener-daemon.js`** - Auto-listener that watches for new voice messages

### Documentation
- **`SKILL.md`** - Main skill documentation (what, how, quick start)
- **`references/SETUP.md`** - Detailed installation and configuration
- **`references/API.md`** - Complete function API and examples
- **`example-custom-intents.js`** - Guide for extending with your own handlers

### Configuration Files
- **`requirements.txt`** - Python dependencies
- **`package.json`** - Node.js project metadata

## Getting Started (2 minutes)

### 1. Install
```bash
pip install openai-whisper soundfile numpy
npm install  # (if needed, minimal dependencies)
```

### 2. Run
```bash
# Auto-listener (recommended)
node scripts/voice-listener-daemon.js

# Or process a file manually
node -e "const {processVoiceNote} = require('./scripts/voice-processor'); 
const fs = require('fs'); 
processVoiceNote(fs.readFileSync('voice.ogg')).then(r => console.log(r.response));"
```

### 3. Customize (optional)
Edit `voice-processor.js` to add your own intents and handlers. See `example-custom-intents.js` for patterns.

## Built-In Features

✅ Automatic transcription (5-10 seconds per message)  
✅ Intent detection from keywords  
✅ Handler-based response generation  
✅ English + Hindi support (easily extended)  
✅ Automatic language detection  
✅ No FFmpeg required (uses soundfile + libsndfile)  
✅ Production-tested in Clawdbot

## Use Cases

- **Voice Assistant** - Natural language commands on WhatsApp
- **IoT Control** - Voice commands for drones, smart home, devices
- **Hands-Free Interface** - Drive safely, work hands-busy
- **Accessibility** - Voice input for users with visual impairments
- **Multilingual Support** - English, Hindi, extensible to any language

## Example Intents

Built-in intents (ready to use):
- `greeting` - "Hello", "Hi", "नमस्ते"
- `weather` - "What's the weather?", "मौसम कैसा है?"
- `status` - "How are you?", "System status?"

Custom intents (you can add):
- Smart home control
- Shopping lists
- Drone operations
- Music playback
- Reminders/alarms
- Custom APIs

See `example-custom-intents.js` for templates.

## Community Contributions

This skill is open for improvements! Consider contributing:

- **New handlers** - Add support for more intents
- **Language support** - Expand beyond English/Hindi
- **Performance optimizations** - Faster transcription, caching
- **Documentation** - Better examples, guides, localization
- **Bug fixes** - Issues or edge cases you've found

To contribute:
1. Test your changes thoroughly
2. Document new features
3. Submit via your community channel

## Troubleshooting

### Whisper module missing?
```bash
pip install openai-whisper
```

### Soundfile missing?
```bash
pip install soundfile
```

### Voice messages not processing?
1. Check Clawdbot is running: `clawdbot status`
2. Verify inbound directory exists: `ls ~/.clawdbot/media/inbound/`
3. Run daemon manually to see logs: `node scripts/voice-listener-daemon.js`

### Transcription is slow (first time)?
This is normal - Whisper model (~140MB) downloads on first run. Subsequent messages are 5-10 seconds.

### Want a faster model?
Edit `transcribe.py` to use `"tiny"` or `"small"` instead of `"base"`.

## Performance

- **First transcription:** ~30 seconds (model download)
- **Typical:** 5-10 seconds per message
- **Memory:** ~1.5GB (base model, adjustable)
- **Languages:** 99+ (Whisper supports them all)

## Architecture

```
WhatsApp Voice Message
  ↓
[voice-listener-daemon.js]
  ↓
Check ~/.clawdbot/media/inbound/
  ↓
[voice-processor.js]
  ├→ Transcribe (transcribe.py + Whisper)
  ├→ Detect Language
  ├→ Parse Intent
  ├→ Execute Handler
  └→ Generate Response
  ↓
{ status, response, transcript, intent, language }
  ↓
Send back via WhatsApp (parent process)
```

## Integration Examples

### In Clawdbot Message Handler
```javascript
const { processVoiceNote } = require('skills/whatsapp-voice-talk/scripts/voice-processor');

// When voice message received
const result = await processVoiceNote(audioBuffer);
await sendWhatsAppMessage(sender, result.response);
```

### Standalone Node.js App
```javascript
const { processVoiceNote } = require('./whatsapp-voice-talk/scripts/voice-processor');
const fs = require('fs');

const audio = fs.readFileSync('message.ogg');
const result = await processVoiceNote(audio);
console.log(result);
```

### CLI Testing
```bash
python scripts/transcribe.py message.ogg
# Output: {"text": "What's the weather?", "success": true}
```

## Why This Skill Works

1. **Zero Complexity** - No FFmpeg, native Python Whisper
2. **Real Code** - Built from production Clawdbot usage
3. **Well Documented** - Setup, API, examples all included
4. **Easy to Extend** - Simple handler pattern for custom logic
5. **Community Ready** - Licensed MIT, encourage contributions

## What's Next?

Potential enhancements (ideas for contributors):
- Real-time TTS response sending
- Database integration for persistence
- Voice emotion detection
- Speaker recognition
- Streaming transcription
- GPU acceleration
- Mobile app companion

## Support

For issues, questions, or ideas:
1. Check `references/SETUP.md` (most common issues)
2. Check `references/API.md` (function signatures)
3. Review `example-custom-intents.js` (custom handlers)
4. Ask in community channels

## Recognition

Built with ❤️ for the Clawdbot community. Thanks to OpenAI Whisper and soundfile maintainers.

---

**Ready to use.** Production-tested. Community-driven.

Questions? Suggestions? Want to contribute? Join the community! 🎤✨
