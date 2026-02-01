---
name: voice-transcribe
description: Transcribe audio files using OpenAI's gpt-4o-mini-transcribe model with vocabulary hints and text replacements. Requires uv (https://docs.astral.sh/uv/).
---

# voice-transcribe

transcribe audio files using openai's gpt-4o-mini-transcribe model.

## when to use

when receiving voice memos (especially via whatsapp), just run:
```bash
uv run /Users/darin/clawd/skills/voice-transcribe/transcribe <audio-file>
```
then respond based on the transcribed content.

## fixing transcription errors

if darin says a word was transcribed wrong, add it to `vocab.txt` (for hints) or `replacements.txt` (for guaranteed fix). see sections below.

## supported formats

- mp3, mp4, mpeg, mpga, m4a, wav, webm, ogg, opus

## examples

```bash
# transcribe a voice memo
transcribe /tmp/voice-memo.ogg

# pipe to other tools
transcribe /tmp/memo.ogg | pbcopy
```

## setup

1. add your openai api key to `/Users/darin/clawd/skills/voice-transcribe/.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```

## custom vocabulary

add words to `vocab.txt` (one per line) to help the model recognize names/jargon:
```
Clawdis
Clawdbot
```

## text replacements

if the model still gets something wrong, add a replacement to `replacements.txt`:
```
wrong spelling -> correct spelling
```

## notes

- assumes english (no language detection)
- uses gpt-4o-mini-transcribe model specifically
- caches by sha256 of audio file
