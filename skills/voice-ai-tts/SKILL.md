---
name: voice-ai-tts
description: >
  High-quality voice synthesis with 9 personas, 11 languages, streaming, and voice cloning using Voice.ai API.
version: 1.0.0
---

# Voice.ai Voices

## ✨ Features

- **9 Voice Personas** - Carefully curated voices for different use cases
- **11 Languages** - Multi-language synthesis with multilingual model
- **Streaming Mode** - Real-time audio output as it generates
- **Voice Cloning** - Clone voices from audio samples
- **Voice Design** - Customize with temperature and top_p parameters
- **OpenClaw Integration** - Works with OpenClaw's built-in TTS

---

## ⚙️ Configuration

The scripts look for your API key in this order:

1. `VOICE_AI_API_KEY` environment variable
2. OpenClaw config (`~/.openclaw/openclaw.json`)
3. Skill-local `.env` file

**Get your API key:** [Voice.ai Dashboard](https://voice.ai/dashboard)

### Create `.env` file (Recommended)

```bash
echo 'VOICE_AI_API_KEY=your-key-here' > .env
```

### Or export directly

```bash
export VOICE_AI_API_KEY="your-api-key"
```

---

## 🤖 OpenClaw Integration

Add this skill to your OpenClaw configuration at `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "voice-ai-tts": {
      "enabled": true,
      "api_key": "your-voice-ai-api-key",
      "default_voice": "ellie",
      "default_format": "mp3"
    }
  },
  "tts": {
    "skill": "voice-ai-tts",
    "voice_id": "d1bf0f33-8e0e-4fbf-acf8-45c3c6262513",
    "streaming": true
  }
}
```

### YAML config alternative

```yaml
tts:
  skill: voice-ai-tts
  voice_id: d1bf0f33-8e0e-4fbf-acf8-45c3c6262513
  streaming: true
```

---

## 📝 Triggers

These chat commands work with OpenClaw:

| Command | Description |
|---------|-------------|
| `/tts <text>` | Generate speech with default voice |
| `/tts --voice ellie <text>` | Generate speech with specific voice |
| `/tts --stream <text>` | Generate with streaming mode |
| `/voices` | List available voices |
| `/clone <audio_url>` | Clone a voice from audio |

**Examples:**

```
/tts Hello, welcome to Voice.ai!
/tts --voice oliver Good morning, everyone.
/tts --voice lilith --stream This is a long story that will stream as it generates...
```

---

## 🎙️ Available Voices

| Voice   | ID | Gender | Persona     | Best For                   |
|---------|-----|--------|-------------|----------------------------|
| ellie   | `d1bf0f33-8e0e-4fbf-acf8-45c3c6262513` | female | youthful    | Vlogs, social content      |
| oliver  | `f9e6a5eb-a7fd-4525-9e92-75125249c933` | male   | british     | Narration, tutorials       |
| lilith  | `4388040c-8812-42f4-a264-f457a6b2b5b9` | female | soft        | ASMR, calm content         |
| smooth  | `dbb271df-db25-4225-abb0-5200ba1426bc` | male   | deep        | Documentaries, audiobooks  |
| corpse  | `72d2a864-b236-402e-a166-a838ccc2c273` | male   | distinctive | Gaming, entertainment      |
| skadi   | `559d3b72-3e79-4f11-9b62-9ec702a6c057` | female | anime       | Character voices           |
| zhongli | `ed751d4d-e633-4bb0-8f5e-b5c8ddb04402` | male   | deep        | Gaming, dramatic content   |
| flora   | `a931a6af-fb01-42f0-a8c0-bd14bc302bb1` | female | cheerful    | Kids content, upbeat       |
| chief   | `bd35e4e6-6283-46b9-86b6-7cfa3dd409b9` | male   | heroic      | Gaming, action content     |

---

## 🌍 Supported Languages

| Code | Language   |
|------|------------|
| `en` | English    |
| `es` | Spanish    |
| `fr` | French     |
| `de` | German     |
| `it` | Italian    |
| `pt` | Portuguese |
| `pl` | Polish     |
| `ru` | Russian    |
| `nl` | Dutch      |
| `sv` | Swedish    |
| `ca` | Catalan    |

Use the multilingual model for non-English languages:

```javascript
const audio = await client.generateSpeech({
  text: 'Bonjour le monde!',
  voice_id: 'ellie-voice-id',
  model: 'voiceai-tts-multilingual-v1-latest',
  language: 'fr'
});
```

---

## 🎨 Voice Design

Customize voice output with these parameters:

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `temperature` | 0-2 | 1.0 | Higher = more expressive, lower = more consistent |
| `top_p` | 0-1 | 0.8 | Controls randomness in speech generation |

**Example:**

```javascript
const audio = await client.generateSpeech({
  text: 'This will sound very expressive!',
  voice_id: 'ellie-voice-id',
  temperature: 1.8,
  top_p: 0.9
});
```

---

## 📡 Streaming Mode

Generate audio with real-time streaming (recommended for long texts):

```bash
# Stream audio as it generates
node scripts/tts.js --text "This is a long story..." --voice ellie --stream

# Streaming with custom output
node scripts/tts.js --text "Chapter one..." --voice oliver --stream --output chapter1.mp3
```

**SDK streaming:**

```javascript
const stream = await client.streamSpeech({
  text: 'Long text here...',
  voice_id: 'ellie-voice-id'
});

// Pipe to file
stream.pipe(fs.createWriteStream('output.mp3'));

// Or handle chunks
stream.on('data', chunk => {
  // Process audio chunk
});
```

---

## 🔊 Audio Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| `mp3` | Standard MP3 (32kHz) | General use |
| `wav` | Uncompressed WAV | High quality |
| `pcm` | Raw PCM audio | Processing |
| `opus_48000_128` | Opus 128kbps | Streaming |
| `mp3_44100_192` | High-quality MP3 | Professional |

See `voice-ai-tts-sdk.js` for all format options.

---

## 💻 CLI Usage

```bash
# Set API key
echo 'VOICE_AI_API_KEY=your-key-here' > .env

# Generate speech
node scripts/tts.js --text "Hello world!" --voice ellie

# Choose different voice
node scripts/tts.js --text "Good morning!" --voice oliver --output morning.mp3

# Use streaming for long texts
node scripts/tts.js --text "Once upon a time..." --voice lilith --stream

# Show help
node scripts/tts.js --help
```

---

## 🧬 Voice Cloning

Clone any voice from an audio sample:

```javascript
const VoiceAI = require('./voice-ai-tts-sdk');
const client = new VoiceAI(process.env.VOICE_AI_API_KEY);

// Clone from file
const result = await client.cloneVoice({
  file: './my-voice-sample.mp3',
  name: 'My Custom Voice',
  visibility: 'PRIVATE',
  language: 'en'
});

console.log('Voice ID:', result.voice_id);
console.log('Status:', result.status);

// Wait for voice to be ready
const voice = await client.waitForVoice(result.voice_id);
console.log('Voice ready!', voice);
```

**Requirements:**
- Audio sample: 10-30 seconds recommended
- Clear speech, minimal background noise
- Supported formats: MP3, WAV, M4A

---

## 📁 Files

```
voice-ai-tts/
├── SKILL.md              # This documentation
├── voice-ai-tts.yaml     # OpenAPI specification
├── voice-ai-tts-sdk.js   # JavaScript/Node.js SDK
├── scripts/
│   └── tts.js            # CLI tool
└── .env                  # API key (create this)
```

---

## 💰 Cost & Usage

Voice.ai uses a credit-based system. Check your usage:

```javascript
// The SDK tracks usage via API responses
const voices = await client.listVoices();
// Check response headers for rate limit info
```

**Tips to reduce costs:**
- Use streaming for long texts (more efficient)
- Cache generated audio when possible
- Use appropriate audio quality for your use case

---

## 🔗 Links

- **[Get API Key](https://voice.ai/dashboard)** - Sign up and get your key
- **[API Documentation](https://voice.ai/docs)** - Full API reference
- **[Voice Library](https://voice.ai/voices)** - Browse all voices
- **[API Reference](https://voice.ai/docs/api-reference/text-to-speech/generate-speech)** - Endpoint details
- **[Pricing](https://voice.ai/pricing)** - Plans and credits

---

## 📋 Changelog

### v1.0.0 (2025-01-31)
- Initial release
- 9 curated voice personas
- 11 language support
- Streaming mode
- Voice cloning
- Voice design parameters
- Full SDK with error handling
- CLI tool

---

## 🛠️ SDK Quick Reference

```javascript
const VoiceAI = require('./voice-ai-tts-sdk');
const client = new VoiceAI(process.env.VOICE_AI_API_KEY);

// List voices
const voices = await client.listVoices({ limit: 10 });

// Get voice details
const voice = await client.getVoice('voice-id');

// Generate speech
const audio = await client.generateSpeech({
  text: 'Hello, world!',
  voice_id: 'voice-id',
  audio_format: 'mp3'
});

// Generate to file
await client.generateSpeechToFile(
  { text: 'Hello!', voice_id: 'voice-id' },
  'output.mp3'
);

// Stream speech
const stream = await client.streamSpeech({
  text: 'Long text...',
  voice_id: 'voice-id'
});

// Clone voice
const clone = await client.cloneVoice({
  file: './sample.mp3',
  name: 'My Voice'
});

// Delete voice
await client.deleteVoice('voice-id');
```

---

## ❓ Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `AuthenticationError` | Invalid API key | Check your `VOICE_AI_API_KEY` |
| `PaymentRequiredError` | Out of credits | Add credits at voice.ai/dashboard |
| `RateLimitError` | Too many requests | Wait and retry, or upgrade plan |
| `ValidationError` | Invalid parameters | Check text length and voice_id |

---

Made with ❤️ by [Nick Gill](https://github.com/gizmoGremlin)
