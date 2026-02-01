#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

// Configuration
const API_URL = process.env.KOKORO_API_URL || 'http://localhost:8880/v1/audio/speech';
const DEFAULT_VOICE = 'af_heart';
const DEFAULT_SPEED = 1.0;

// Parse arguments
const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: node tts.js <text> [voice] [speed]');
  process.exit(1);
}

const text = args[0];
const voice = args[1] || DEFAULT_VOICE;
const speed = parseFloat(args[2] || DEFAULT_SPEED);

// Ensure media directory exists
const mediaDir = path.join(process.cwd(), 'media');
if (!fs.existsSync(mediaDir)) {
  fs.mkdirSync(mediaDir, { recursive: true });
}

// Generate filename
const timestamp = Date.now();
const filename = `tts_${timestamp}.mp3`;
const filePath = path.join(mediaDir, filename);

async function generateSpeech() {
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        input: text,
        voice: voice,
        speed: speed,
        response_format: 'mp3',
        model: 'kokoro',
        stream: false 
      }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    const buffer = await response.arrayBuffer();
    fs.writeFileSync(filePath, Buffer.from(buffer));

    // Output strictly in the format OpenClaw expects
    console.log(`MEDIA: ${path.relative(process.cwd(), filePath)}`);

  } catch (error) {
    console.error('Error generating speech:', error.message);
    process.exit(1);
  }
}

generateSpeech();
