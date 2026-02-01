---
name: audio-reply
description: 'Generate audio replies using TTS. Trigger with "read it to me [URL]" to fetch and read content aloud, or "talk to me [topic]" to generate a spoken response. Also responds to "speak", "say it", "voice reply".'
homepage: https://github.com/anthropics/claude-code
metadata: {"clawdbot":{"emoji":"🔊","requires":{"bins":["uv"]}}}
---

# Audio Reply Skill

Generate spoken audio responses using MLX Audio TTS (chatterbox-turbo model).

## Trigger Phrases

- **"read it to me [URL]"** - Fetch content from URL and read it aloud
- **"talk to me [topic/question]"** - Generate a conversational response as audio
- **"speak"**, **"say it"**, **"voice reply"** - Convert your response to audio

## How to Use

### Mode 1: Read URL Content
```
User: read it to me https://example.com/article
```
1. Fetch the URL content using WebFetch
2. Extract readable text (strip HTML, focus on main content)
3. Generate audio using TTS
4. Play the audio and delete the file afterward

### Mode 2: Conversational Audio Response
```
User: talk to me about the weather today
```
1. Generate a natural, conversational response
2. Keep it concise (TTS works best with shorter segments)
3. Convert to audio, play it, then delete the file

## Implementation

### TTS Command
```bash
uv run mlx_audio.tts.generate \
  --model mlx-community/chatterbox-turbo-fp16 \
  --text "Your text here" \
  --play \
  --file_prefix /tmp/audio_reply
```

### Key Parameters
- `--model mlx-community/chatterbox-turbo-fp16` - Fast, natural voice
- `--play` - Auto-play the generated audio
- `--file_prefix` - Save to temp location for cleanup
- `--exaggeration 0.3` - Optional: add expressiveness (0.0-1.0)
- `--speed 1.0` - Adjust speech rate if needed

### Text Preparation Guidelines

**For "read it to me" mode:**
1. Fetch URL with WebFetch tool
2. Extract main content, strip navigation/ads/boilerplate
3. Summarize if very long (>500 words) - keep key points
4. Add natural pauses with periods and commas

**For "talk to me" mode:**
1. Write conversationally, as if speaking
2. Use contractions (I'm, you're, it's)
3. Add filler words sparingly for naturalness ([chuckle], um, anyway)
4. Keep responses under 200 words for best quality
5. Avoid technical jargon unless explaining it

### Audio Generation & Cleanup (IMPORTANT)

Always delete the audio file after playing - it's already in the chat history.

```bash
# Generate with unique filename and play
OUTPUT_FILE="/tmp/audio_reply_$(date +%s)"
uv run mlx_audio.tts.generate \
  --model mlx-community/chatterbox-turbo-fp16 \
  --text "Your response text" \
  --play \
  --file_prefix "$OUTPUT_FILE"

# ALWAYS clean up after playing
rm -f "${OUTPUT_FILE}"*.wav 2>/dev/null
```

### Error Handling

If TTS fails:
1. Check if model is downloaded (first run downloads ~500MB)
2. Ensure `uv` is installed and in PATH
3. Fall back to text response with apology

## Example Workflows

### Example 1: Read URL
```
User: read it to me https://blog.example.com/new-feature

Assistant actions:
1. WebFetch the URL
2. Extract article content
3. Generate TTS:
   uv run mlx_audio.tts.generate \
     --model mlx-community/chatterbox-turbo-fp16 \
     --text "Here's what I found... [article summary]" \
     --play --file_prefix /tmp/audio_reply_1706123456
4. Delete: rm -f /tmp/audio_reply_1706123456*.wav
5. Confirm: "Done reading the article to you."
```

### Example 2: Talk to Me
```
User: talk to me about what you can help with

Assistant actions:
1. Generate conversational response text
2. Generate TTS:
   uv run mlx_audio.tts.generate \
     --model mlx-community/chatterbox-turbo-fp16 \
     --text "Hey! So I can help you with all kinds of things..." \
     --play --file_prefix /tmp/audio_reply_1706123789
3. Delete: rm -f /tmp/audio_reply_1706123789*.wav
4. (No text output needed - audio IS the response)
```

## Notes

- First run may take longer as the model downloads (~500MB)
- Audio quality is best for English; other languages may vary
- For long content, consider chunking into multiple audio segments
- The `--play` flag uses system audio - ensure volume is up
