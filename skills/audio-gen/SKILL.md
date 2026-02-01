---
name: audio-gen
description: Generate audiobooks, podcasts, or educational audio content on demand. User provides an idea or topic, Claude AI writes a script, and ElevenLabs converts it to high-quality audio. Supports multiple formats (audiobook, podcast, educational), custom lengths, and voice effects. Use when asked to create audio content, make a podcast, generate an audiobook, or produce educational audio. Returns MP3 audio file via MEDIA token.
homepage: https://github.com/clawdbot/clawdbot
metadata: {"clawdbot":{"emoji":"🎙️","requires":{"skills":["sag"],"env":["ANTHROPIC_API_KEY","ELEVENLABS_API_KEY"]},"primaryEnv":"ANTHROPIC_API_KEY"}}
---

# 🎙️ Audio Content Generator

Generate high-quality audiobooks, podcasts, or educational audio content on demand using AI-written scripts and ElevenLabs text-to-speech.

## Quick Start

**Create an audiobook chapter:**
```
User: "Create a 5-minute audiobook chapter about a dragon discovering friendship"
```

**Generate a podcast:**
```
User: "Make a 10-minute podcast about the history of coffee"
```

**Produce educational content:**
```
User: "Generate a 15-minute educational audio explaining how neural networks work"
```

## Content Formats

### Audiobook
**Style:** Narrative storytelling with emotional depth
- Clear beginning, middle, and end
- Descriptive language and vivid imagery
- Dramatic pacing with thoughtful pauses
- Emotional tone that matches the story
- Use voice effects like `[whispers]`, `[excited]`, `[serious]` for impact

**Example Structure:**
```
[Opening hook - set the scene]
[long pause]

[Story development with character emotions]
[short pause] between sentences
[long pause] between paragraphs

[Climax with dramatic tension]
[long pause]

[Resolution and emotional closure]
```

### Podcast
**Style:** Conversational and engaging
- Warm, welcoming intro (15-30 seconds)
- Main content with natural flow
- Transitions between topics
- Memorable outro with key takeaways
- Conversational tone throughout

**Example Structure:**
```
**Intro:** "Welcome to [topic]. I'm excited to share..."
[short pause]

**Main Content:** "Let's start with... [topic 1]"
[long pause] between segments

**Outro:** "Thanks for listening! Remember..."
```

### Educational Content
**Style:** Clear explanations for learning
- Simple introductions to complex topics
- Step-by-step breakdowns
- Real-world examples and analogies
- Recap of key concepts at the end
- Enthusiastic delivery with `[excited]` for important points

**Example Structure:**
```
**Introduction:** What is [topic] and why it matters?

**Main Content:**
- Concept 1: Explanation + Example
- Concept 2: Explanation + Example
- Concept 3: Explanation + Example

**Summary:** Key takeaways and next steps
```

## Length Guidelines

**Word Count to Duration Conversion:**
- 5 minutes = ~375 words
- 10 minutes = ~750 words
- 15 minutes = ~1,125 words
- 20 minutes = ~1,500 words
- 30 minutes = ~2,250 words

**Pacing:** Average conversational speed is ~75 words per minute

**Practical Limits:**
- Minimum: 2 minutes (~150 words)
- Maximum: 30 minutes (~2,250 words)
- Sweet spot: 5-15 minutes for best engagement

## Workflow Instructions

### Step 1: Understand the Request

Parse the user's request for:
1. **Content type** (audiobook, podcast, educational, or inferred from topic)
2. **Topic/theme** (what should the content be about)
3. **Target length** (how many minutes)
4. **Tone/style** (dramatic, casual, educational, etc.)
5. **Special requests** (specific voice, emphasis on certain points)

### Step 2: Calculate Word Count

```
target_words = target_minutes × 75
```

Example: 10 minutes = 10 × 75 = 750 words

### Step 3: Generate the Script

Write the complete script following these rules:

**Content Guidelines:**
- Start strong with an engaging hook
- Maintain natural, conversational flow
- Use active voice and simple sentence structure
- Include relevant examples and stories
- End with a satisfying conclusion

**Formatting Rules:**
- Add `[short pause]` after sentences (use sparingly, not every sentence)
- Add `[long pause]` between paragraphs or major sections
- Use voice effects strategically: `[whispers]`, `[shouts]`, `[excited]`, `[serious]`, `[sarcastic]`, `[sings]`, `[laughs]`
- Write numbers as words: "twenty-three" not "23"
- Spell out acronyms first time: "AI, or artificial intelligence"
- Avoid complex punctuation (em-dashes work, but semicolons don't read well)
- Remove markdown formatting before TTS conversion

### Step 4: Present the Script

Show the script to the user and ask:
```
Here's the [format] script I've created (approximately [length] minutes):

[Display the script]

Would you like me to:
1. Generate the audio now
2. Make changes to the script
3. Adjust the length or tone
```

### Step 5: Handle User Feedback

If user requests changes:
- Regenerate the script with adjustments
- Maintain the target word count
- Present the revised version

If user approves:
- Proceed to audio generation

### Step 6: Generate Audio

**Format the script for TTS:**
1. Remove any remaining markdown (headers, bold, italics)
2. Ensure voice effects are in proper `[effect]` format
3. Check that pauses are appropriately placed
4. Verify numbers and acronyms are spelled out

**Invoke the TTS script:**

**IMPORTANT:** The `ELEVENLABS_API_KEY` environment variable is already configured in the system. Simply invoke the TTS script directly.

```bash
uv run /home/clawdbot/clawdbot/skills/sag/scripts/tts.py \
  -o /tmp/audio-gen-[timestamp]-[topic-slug].mp3 \
  -m eleven_multilingual_v2 \
  "[formatted_script]"
```

**For long scripts, use heredoc:**
```bash
uv run /home/clawdbot/clawdbot/skills/sag/scripts/tts.py \
  -o /tmp/audio-gen-[timestamp]-[topic-slug].mp3 \
  -m eleven_multilingual_v2 \
  "$(cat <<'EOF'
[formatted_script]
EOF
)"
```

**Return the result:**
```
MEDIA:/tmp/audio-gen-[timestamp]-[topic-slug].mp3

Your [format] is ready! [Brief description of content]. Duration: approximately [X] minutes.
```

## Voice Effects (SSML Tags)

Available voice modulation effects (use sparingly for impact):

- `[whispers]` - Soft, intimate delivery
- `[shouts]` - Loud, emphatic delivery
- `[excited]` - Enthusiastic, energetic tone
- `[serious]` - Grave, solemn tone
- `[sarcastic]` - Ironic, mocking tone
- `[sings]` - Musical, melodic delivery
- `[laughs]` - Amused, jovial tone
- `[short pause]` - Brief silence (~0.5s)
- `[long pause]` - Extended silence (~1-2s)

**Best Practices:**
- Use effects for emotional moments, not every sentence
- Pauses are your most powerful tool for pacing
- Voice effects work best in audiobooks and dramatic content
- Keep podcasts and educational content mostly natural

## Error Handling

### Script Too Long
If the generated script exceeds target by >20%:
```
The script I generated is [X] words ([Y] minutes), which is longer than your target of [Z] minutes. Would you like me to:
1. Condense it to fit the target length
2. Split it into multiple parts
3. Keep it as is
```

### Script Too Short
If the generated script is under target by >20%:
```
The script is [X] words ([Y] minutes), shorter than your target. Would you like me to:
1. Expand it with more detail
2. Add additional examples or stories
3. Generate as is
```

### TTS Generation Fails
If the TTS script fails:
```
I've created the script, but I'm unable to generate the audio right now. Here's your script:

[Display script]

Error: [specific error message]

You can:
1. Check that ELEVENLABS_API_KEY is configured
2. Use the script with your own text-to-speech tool
3. Try again in a moment
4. Ask me to troubleshoot the audio generation
```

**Common TTS Issues:**
- API key not set: Verify ELEVENLABS_API_KEY in config
- Rate limit: Wait a moment and try again
- Text too long: Break into smaller chunks (max ~5000 characters)

### Invalid Request
For unrealistic requests (e.g., "100-hour audiobook"):
```
That length would require [X] words and take significant time to generate. I recommend:
- Breaking it into multiple episodes/chapters
- Targeting 5-30 minutes per audio file
- Creating a series instead of one long file
```

## Tips for Best Results

### For Engaging Audiobooks
- Focus on character emotions and sensory details
- Use pauses to build dramatic tension
- Vary sentence length for rhythm
- Include internal monologue and reflection

### For Compelling Podcasts
- Start with a question or surprising fact
- Use conversational phrases: "You know what's interesting..."
- Include relatable examples from everyday life
- End with actionable takeaways

### For Effective Educational Content
- Use the "explain like I'm five" approach
- Build from simple to complex concepts
- Repeat key terms and definitions
- Provide multiple examples for clarity

## Technical Notes

**TTS Implementation:**
- Uses Python script: `~/.clawdbot/clawdbot/skills/sag/scripts/tts.py`
- No binary installation required (pure Python + requests)
- Directly calls ElevenLabs API
- Compatible with Linux and macOS

**File Storage:**
- Audio files are saved to `/tmp/audio-gen/`
- Filename format: `audio-gen-[timestamp]-[topic-slug].mp3`
- Files are automatically cleaned up after 24 hours

**API Requirements:**
- Anthropic API for script generation (already configured)
- ElevenLabs API for text-to-speech (configured via ELEVENLABS_API_KEY)
- Both services must be configured and have available credits

**Supported Models:**
- `eleven_multilingual_v2` - Best quality (default)
- `eleven_turbo_v2` - Faster generation
- `eleven_turbo_v2_5` - Fastest generation
- `eleven_multilingual_v1` - Legacy model

**Cost Estimate:**
- 10-minute audio (~750 words): approximately $1.43
  - Claude API: ~$0.075
  - ElevenLabs: ~$1.35
- Longer content scales proportionally

**Generation Time:**
- Script generation: 5-30 seconds (depending on length)
- Audio generation: 5-15 seconds (ElevenLabs processing)
- Total: Usually under 1 minute for 10-minute audio

## Limitations

1. **Maximum Length:** 30 minutes (~2,250 words) per audio file
   - For longer content, create multiple parts/episodes

2. **Single Voice:** Currently supports one narrator voice
   - Cannot do multi-voice dialogue or character voices

3. **No Background Music:** Pure voice narration only
   - No background music, sound effects, or audio mixing

4. **Real-time Generation:** Each request generates fresh content
   - No pre-made templates or cached audio

5. **Language:** Primarily English
   - ElevenLabs supports other languages, but content generation optimized for English

## Example Conversations

### Example 1: Quick Audiobook
```
User: Create a 5-minute audiobook chapter about a lonely robot learning to feel emotions

Agent: I'll create a 5-minute sci-fi audiobook chapter. Let me write the story...

[Generates ~400-word narrative with emotional arc]

Here's the story I've created about Unit-7, a maintenance robot who discovers the meaning of friendship through an unexpected encounter. Would you like me to generate the audio or make changes first?

User: Generate the audio

Agent: [Invokes SAG with formatted script]

MEDIA:/tmp/audio-gen-1234567890-lonely-robot.mp3

Your audiobook chapter is ready! The story follows Unit-7's emotional awakening through a touching encounter with a young engineer. Duration: approximately 5 minutes.
```

### Example 2: Podcast with Revisions
```
User: Make a 10-minute podcast about sustainable living tips

Agent: [Generates podcast script with intro, 5 practical tips, outro]

Here's a 10-minute podcast with 5 actionable sustainable living tips. The tone is encouraging and practical. Would you like me to:
1. Generate audio now
2. Make it more urgent/climate-focused
3. Add more specific examples
4. Adjust the length

User: Add more specific examples for each tip

Agent: [Regenerates with detailed examples]

Better? I've added specific examples like calculating your carbon footprint, composting at home, and choosing sustainable brands. Ready for audio?

User: Perfect!

Agent: MEDIA:/tmp/audio-gen-1234567890-sustainable-living.mp3

Your sustainable living podcast is ready with 5 practical tips, each with concrete examples you can start using today! Duration: 10 minutes.
```

### Example 3: Educational Content
```
User: Create a 15-minute educational audio explaining quantum computing for beginners

Agent: I'll create a beginner-friendly 15-minute explanation of quantum computing...

[Generates ~1,100 words with analogies, examples, and clear structure]

Script preview:
- Introduction: What is quantum computing? (2 min)
- Classical vs Quantum: The key differences (4 min)
- Qubits and Superposition: How it works (5 min)
- Real Applications: What it means for you (3 min)
- Conclusion: The future of computing (1 min)

Should I generate the audio?

User: Yes please

Agent: MEDIA:/tmp/audio-gen-1234567890-quantum-computing.mp3

Your educational podcast on quantum computing is ready! It uses everyday analogies to explain qubits, superposition, and real-world applications. Duration: approximately 15 minutes.
```

## When to Use This Skill

Use the audio-gen skill when users request:
- "Create an audiobook about..."
- "Make a podcast episode about..."
- "Generate audio content explaining..."
- "Record a story about..."
- "Produce an audio guide for..."
- "Create a narrated version of..."
- "Make an audio lesson about..."

**Do NOT use for:**
- Transcribing existing audio (use whisper skills instead)
- Converting user-written text to audio (use SAG skill directly)
- Real-time voice interaction (use voice-call plugin)
- Multi-speaker dialogues or interviews (current limitation)

## Advanced Usage

### Voice Selection
Users can request specific voices:
```
User: Create a podcast with the Rachel voice

Agent: [Checks voice configuration for "Rachel" voice ID and uses it in SAG command]
```

### Series/Episodes
For multi-part content:
```
User: Create a 3-episode series about space exploration

Agent: I'll create Episode 1 first. Each episode will be 10 minutes. Let's start with "The Dawn of the Space Age"...

[After completion]

Episode 1 is ready! Would you like me to continue with Episode 2?
```

### Format Blending
Mix formats for unique styles:
```
User: Create an educational podcast that tells a story

Agent: [Generates content that combines storytelling narrative with educational explanations]
```

## Troubleshooting

**Issue:** Audio sounds robotic or unnatural
**Solution:** Add more pauses and voice effects. Use contractions and conversational language.

**Issue:** Script doesn't match requested length
**Solution:** Regenerate with explicit word count target. Check calculations (75 words/min).

**Issue:** Content is too technical or too simple
**Solution:** Ask user for target audience. Adjust complexity accordingly.

**Issue:** SAG command fails
**Solution:** Check ELEVENLABS_API_KEY is set. Verify SAG skill is installed and working.

**Issue:** User wants to edit the script manually
**Solution:** Provide the plain text script. User can modify it and paste back for audio generation.

---

💡 **Pro Tip:** Always generate the script first and get user approval before creating audio. This saves time and API costs, and ensures the user gets exactly what they want.
