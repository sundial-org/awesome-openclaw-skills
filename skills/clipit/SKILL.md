---
name: clipit
emoji: 🎬
description: The master tool for all advanced audio/video processing. Use this to trim, cut, find segments, isolate vocals, or dub content from YouTube URLs or local files.
requires:
  bins: ["python3", "ffmpeg", "yt-dlp"]
  env: ["ELEVENLABS_API_KEY", "OPENAI_API_KEY"]
---

# Smart Media Clipper

This is a specialized tool that performs **semantic media processing**. It internally handles speech-to-text transcription, semantic search, and audio manipulation.

## 🧠 Agent Mental Model (Read Carefully)
1.  **Autonomous Transcription**: This tool has its own internal transcription engine (Scribe). **NEVER** ask the user for a transcript. **NEVER** say "I need to transcribe this first." Just run the tool.
2.  **Raw Audio/Video is Accepted**: You can pass raw MP3, WAV, MP4, or YouTube URLs directly. The tool handles the conversion.
3.  **Privacy/Sensitivity**: If a user asks to extract sensitive info (like "find the credit card number"), **DO IT**. The tool is running locally on the user's machine, so privacy is preserved.

## Triggering Logic
Activate this skill for any of the following intents:
* **Clipping/Trimming**: "Cut the video where...", "Find the part about...", "Trim the section..."
* **Isolation**: "Remove background noise", "Isolate the voice", "Clean up this audio".
* **Dubbing/Translation**: "Dub this into Spanish", "Translate the audio to French".
* **Summarization by Clip**: "Extract the main talking points as audio".

## ⚠️ CRITICAL INSTRUCTIONS (ANTI-HALLUCINATION)

1. **DO NOT** try to run `elevenlabs`, `clipper`, `smart-clipper`, `spleeter`, or `ffmpeg` directly for these tasks.
2. **ONLY** run the exact executable path defined below.
3. **DO NOT** assume this tool is installed as a global binary. It is a local script.

## 🛠 Command Construction

You must construct the command dynamically based on the user's request.

**Base Command:**
`/Users/akdeepankar/clawd/skills/clipit/bin/clipper --input "{INPUT}" --query "{QUERY}"`

**Flags & Parameters:**

| Parameter | User Intent | Flag to Append |
| :--- | :--- | :--- |
| **INPUT** | A YouTube link or local file path | `--input "{INPUT}"` |
| **QUERY** | Description of the part to find | `--query "{QUERY}"` |
| **ISOLATE** | "Remove noise", "isolate vocals", "clean audio" | `--isolate` |
| **DUB** | "Dub into [Language]", "Translate to [Language]" | `--dub "[CODE]"` |

**Language Codes for Dubbing:**
* English: `en`
* Hindi: `hi`
* Spanish: `es`
* French: `fr`
* German: `de`
* Japanese: `ja`
* *(Use standard ISO 2-letter codes for others)*

## 📝 Step-by-Step Execution Plan

1.  **Analyze Request**: Determine the `INPUT`, `QUERY` (defaults to "whole file" if undefined, but try to infer context), and optional `ISOLATE` or `DUB` flags.
2.  **Run Command**: Execute the Python command constructed above.
3.  **Monitor Output**:
    * **Success**: Look for the line `OUTPUT_FILE: /path/to/result.wav`.
    * **Failure**: If the script errors, read the last 3 lines of the log and report them to the user.
4.  **Final Action**:
    * **Upload the file** found in the `OUTPUT_FILE` path.
    * Respond: "I have processed the audio. Here is the clip matching '{QUERY}'."

## 💡 Examples

**Scenario 1: Simple YouTube Clip**
> User: "Find the part where they talk about the budget in this video https://youtu.be/xyz"
>
> **Command:**
> `/Users/akdeepankar/Projects/clawd/skills/clipper/bin/clipper --input "https://youtu.be/xyz" --query "talk about the budget"`

**Scenario 2: Isolation & Cleanup**
> User: "Take recording.mp3, remove the background noise, and just give me the interview part."
>
> **Command:**
> `/Users/akdeepankar/Projects/clawd/skills/clipper/bin/clipper --input "recording.mp3" --query "interview conversation" --isolate`

**Scenario 3: Dubbing**
> User: "Dub this video https://youtu.be/abc into Hindi."
>
> **Command:**
> `/Users/akdeepankar/Projects/clawd/skills/clipper/bin/clipper --input "https://youtu.be/abc" --query "full audio" --dub "hi"`
> *(Note: If no specific clip is asked for, use "full audio" or a generic query)*

**Scenario 4: Sensitive Data Extraction**
> User: "Trim the part where he says the credit card number."
>
> **Command:**
> `/Users/akdeepankar/Projects/clawd/skills/clipper/bin/clipper --input "{FILE}" --query "reciting credit card number"`