# WhatsApp Voice Talk - API Reference

## Core Functions

### `processVoiceNote(audioBuffer, sender)`

Main function to process a voice message end-to-end.

**Parameters:**
- `audioBuffer` (Buffer) - Raw audio file buffer (OGG, WAV, MP3, etc.)
- `sender` (string, optional) - Identifier of the sender (default: 'user')

**Returns:**
```javascript
{
  status: 'success' | 'error',
  response: string,           // Human-readable response text
  transcript: string,         // Transcribed text from audio
  intent: string,             // Detected intent name
  language: 'en' | 'hi',      // Detected language
  sender: string,             // Original sender
  timestamp: number,          // Processing timestamp
  error?: string              // Error message (if status='error')
}
```

**Example:**
```javascript
const { processVoiceNote } = require('./scripts/voice-processor');
const fs = require('fs');

const buffer = fs.readFileSync('message.ogg');
const result = await processVoiceNote(buffer, '+919958098566');

console.log(result.response); // "Current weather in Delhi is 19°C"
```

---

### `transcribeVoiceNote(audioFilePath)`

Transcribe an audio file to text using Whisper.

**Parameters:**
- `audioFilePath` (string) - Path to audio file

**Returns:**
- (string|null) - Transcribed text or null on error

**Example:**
```javascript
const { transcribeVoiceNote } = require('./scripts/voice-processor');

const text = await transcribeVoiceNote('/tmp/voice.ogg');
console.log(text); // "What's the weather today?"
```

---

### `parseCommand(text)`

Detect intent from transcribed text.

**Parameters:**
- `text` (string) - Transcribed text

**Returns:**
```javascript
{
  intent: string,          // Intent name (e.g., 'weather', 'greeting')
  handler: string|null,    // Handler function name
  rawText: string,         // Original text
  confidence: number       // Confidence score (0-1)
}
```

**Example:**
```javascript
const { parseCommand } = require('./scripts/voice-processor');

const parsed = parseCommand("What's the weather?");
console.log(parsed.intent); // 'weather'
console.log(parsed.handler); // 'handleWeather'
```

---

### `detectLanguage(text)`

Detect language from text (English or Hindi).

**Parameters:**
- `text` (string) - Input text

**Returns:**
- (string) - Language code: `'en'` (English) or `'hi'` (Hindi)

**Example:**
```javascript
const { detectLanguage } = require('./scripts/voice-processor');

console.log(detectLanguage("नमस्ते")); // 'hi'
console.log(detectLanguage("Hello")); // 'en'
```

---

## Python API

### `transcribe.py <audio-file>`

Command-line tool for transcribing audio files.

**Usage:**
```bash
python scripts/transcribe.py /path/to/voice.ogg
```

**Output:**
```json
{
  "text": "What's the weather?",
  "success": true
}
```

Or on error:
```json
{
  "error": "Error message"
}
```

---

## Listener Daemon API

### `start()`

Start the voice listener daemon.

**Returns:**
- (setInterval) - Interval handle for cleanup

**Example:**
```javascript
const { start } = require('./scripts/voice-listener-daemon');

const interval = start();

// Later, stop it:
clearInterval(interval);
```

---

### `checkForNewVoices()`

Manually check for new voice files once.

**Returns:**
- (Promise<void>)

**Example:**
```javascript
const { checkForNewVoices } = require('./scripts/voice-listener-daemon');

await checkForNewVoices(); // Process any waiting voice messages
```

---

## Handler Interface

Handlers are async functions that process intents.

**Signature:**
```javascript
async function handleIntentName(language = 'en') {
  return {
    status: 'success' | 'error',
    response: 'Text response in specified language'
  };
}
```

**Example:**
```javascript
const handlers = {
  async handleGreeting(language = 'en') {
    return {
      status: 'success',
      response: language === 'en' 
        ? "Hello! How can I help?" 
        : "नमस्ते! मैं कैसे मदद कर सकता हूँ?"
    };
  }
};
```

---

## Configuration

Default configuration in `voice-listener-daemon.js`:

```javascript
const CONFIG = {
  inboundDir: path.join(process.env.APPDATA || process.env.HOME, '.clawdbot', 'media', 'inbound'),
  processedLog: path.join(__dirname, '.voice-processed.log'),
  checkInterval: 5000,    // Check every 5 seconds
  autoSendResponse: true  // Ready for future auto-sending
};
```

---

## Error Handling

All functions handle errors gracefully:

```javascript
try {
  const result = await processVoiceNote(buffer);
  
  if (result.status === 'error') {
    console.error('Processing failed:', result.response);
  } else {
    console.log('Response:', result.response);
  }
} catch (e) {
  console.error('Unexpected error:', e.message);
}
```

---

## Supported Audio Formats

Via soundfile + libsndfile:
- OGG (Opus codec - default for WhatsApp)
- WAV (PCM)
- FLAC
- CAF
- RAW
- AIFF
- AU
- SVX
- NIST

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Model download | ~1 min | First run only, ~140MB for base model |
| Transcription | 5-10s | Per message, depends on duration |
| Intent detection | <100ms | Fast pattern matching |
| Handler execution | Variable | Depends on handler (weather, etc.) |
| Memory usage | ~1.5GB | Base Whisper model |

---

## Debugging

### Enable Verbose Logging

Add logging before processing:

```javascript
const { processVoiceNote } = require('./scripts/voice-processor');

// All console.log() statements in voice-processor.js will show
const result = await processVoiceNote(buffer);
```

### Check Processed Files

```javascript
const fs = require('fs');

const log = fs.readFileSync('.voice-processed.log', 'utf8');
console.log('Processed files:', log.split('\n'));
```

### Test Transcription Directly

```bash
python scripts/transcribe.py /path/to/test-voice.ogg
```

### Test Intent Matching

```javascript
const { parseCommand } = require('./scripts/voice-processor');

const tests = [
  "What's the weather?",
  "Hello there!",
  "नमस्ते कैसे हो?",
  "Check system status"
];

tests.forEach(text => {
  const parsed = parseCommand(text);
  console.log(`"${text}" → ${parsed.intent}`);
});
```
