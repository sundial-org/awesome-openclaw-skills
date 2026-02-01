#!/usr/bin/env node
/**
 * Voice.ai TTS CLI
 * Usage: node scripts/tts.js --text "Hello!" --voice ellie --output hello.mp3
 */

const VoiceAI = require('../voice-ai-tts-sdk');
const fs = require('fs');

const VOICES = {
  ellie: 'd1bf0f33-8e0e-4fbf-acf8-45c3c6262513',
  oliver: 'f9e6a5eb-a7fd-4525-9e92-75125249c933',
  lilith: '4388040c-8812-42f4-a264-f457a6b2b5b9',
  smooth: 'dbb271df-db25-4225-abb0-5200ba1426bc',
  corpse: '72d2a864-b236-402e-a166-a838ccc2c273',
  skadi: '559d3b72-3e79-4f11-9b62-9ec702a6c057',
  zhongli: 'ed751d4d-e633-4bb0-8f5e-b5c8ddb04402',
  flora: 'a931a6af-fb01-42f0-a8c0-bd14bc302bb1',
  chief: 'bd35e4e6-6283-46b9-86b6-7cfa3dd409b9'
};

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { output: 'output.mp3', stream: false };
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--text' && args[i + 1]) opts.text = args[++i];
    else if (args[i] === '--voice' && args[i + 1]) opts.voice = args[++i];
    else if (args[i] === '--output' && args[i + 1]) opts.output = args[++i];
    else if (args[i] === '--stream') opts.stream = true;
    else if (args[i] === '--help') {
      console.log(`
Voice.ai TTS CLI

Usage:
  node scripts/tts.js --text "Hello!" --voice ellie
  node scripts/tts.js --text "Long text..." --voice oliver --stream
  node scripts/tts.js --text "Custom output" --output custom.mp3

Options:
  --text     Text to convert to speech (required)
  --voice    Voice name: ellie, oliver, lilith, smooth, corpse, skadi, zhongli, flora, chief
  --output   Output file (default: output.mp3)
  --stream   Use streaming mode (good for long texts)

Environment:
  VOICE_AI_API_KEY  Your Voice.ai API key
`);
      process.exit(0);
    }
  }
  return opts;
}

async function main() {
  const opts = parseArgs();
  
  if (!opts.text) {
    console.error('Error: --text is required');
    process.exit(1);
  }
  
  const apiKey = process.env.VOICE_AI_API_KEY;
  if (!apiKey) {
    console.error('Error: VOICE_AI_API_KEY environment variable required');
    process.exit(1);
  }
  
  const client = new VoiceAI(apiKey);
  const voiceId = opts.voice ? VOICES[opts.voice.toLowerCase()] : undefined;
  
  console.log(`Generating speech${opts.stream ? ' (streaming)' : ''}...`);
  
  if (opts.stream) {
    await client.streamSpeechToFile({ text: opts.text, voice_id: voiceId }, opts.output);
  } else {
    await client.generateSpeechToFile({ text: opts.text, voice_id: voiceId }, opts.output);
  }
  
  console.log(`✅ Saved to ${opts.output}`);
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
