#!/usr/bin/env node
/**
 * Voice Processor - Handles WhatsApp voice notes
 * Transcribes → Detects intent → Executes → Responds via TTS
 * 
 * Part of: whatsapp-voice-talk skill
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Intent definitions (customize for your use case)
const INTENTS = {
  'greeting': {
    keywords: ['hello', 'hi', 'hey', 'howdy', 'namaste', 'नमस्ते', 'सुप्रभात'],
    handler: 'handleGreeting'
  },
  'weather': {
    keywords: ['weather', 'temperature', 'rain', 'forecast', 'मौसम', 'तापमान', 'बारिश'],
    handler: 'handleWeather'
  },
  'status': {
    keywords: ['status', 'check', 'how', 'system', 'active', 'स्थिति', 'कैसा'],
    handler: 'handleStatus'
  }
};

/**
 * Transcribe voice note to text
 * @param {string} audioFilePath - Path to audio file (OGG, WAV, MP3, etc.)
 * @returns {string|null} Transcribed text or null on error
 */
async function transcribeVoiceNote(audioFilePath) {
  try {
    const scriptDir = path.dirname(__filename);
    const transcribeScript = path.join(scriptDir, 'transcribe.py');
    
    const { stdout, stderr } = require('child_process').execSync(
      `python "${transcribeScript}" "${audioFilePath}"`,
      { maxBuffer: 10 * 1024 * 1024, encoding: 'utf8' }
    );
    
    // Extract JSON from output (ignore debug messages)
    const jsonMatch = stdout.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      console.error('[VOICE] No JSON in transcription response');
      return null;
    }
    
    const result = JSON.parse(jsonMatch[0]);
    if (result.error) {
      console.error('[VOICE] Transcription error:', result.error);
      return null;
    }
    
    const text = result.text.trim();
    if (!text) {
      console.log('[VOICE] Empty transcription');
      return null;
    }
    
    console.log(`[VOICE] ✅ Transcribed: "${text}"`);
    return text;
    
  } catch (e) {
    console.error('[VOICE] Transcription error:', e.message);
    return null;
  }
}

/**
 * Detect language from text
 * @param {string} text - Input text
 * @returns {string} Language code ('en' or 'hi')
 */
function detectLanguage(text) {
  const hindiChars = /[\u0900-\u097F]/g;
  const englishChars = /[a-zA-Z]/g;
  
  const hindiCount = (text.match(hindiChars) || []).length;
  const englishCount = (text.match(englishChars) || []).length;
  
  return hindiCount > englishCount && hindiCount > 0 ? 'hi' : 'en';
}

/**
 * Parse command/intent from transcribed text
 * @param {string} text - Transcribed text
 * @returns {object} Parsed intent with handler
 */
function parseCommand(text) {
  const lowerText = text.toLowerCase();
  
  for (const [intentName, intentDef] of Object.entries(INTENTS)) {
    for (const keyword of intentDef.keywords) {
      if (lowerText.includes(keyword)) {
        console.log(`[INTENT] Matched: ${intentName}`);
        return {
          intent: intentName,
          handler: intentDef.handler,
          rawText: text,
          confidence: 0.8
        };
      }
    }
  }
  
  return {
    intent: 'unknown',
    handler: null,
    rawText: text,
    confidence: 0.0
  };
}

/**
 * Handler functions for intents
 */
const handlers = {
  async handleGreeting(language = 'en') {
    const responses = {
      en: "Hey! I'm doing great. How can I help you today?",
      hi: "नमस्ते! मैं ठीक हूँ। मैं आपकी कैसे मदद कर सकता हूँ?"
    };
    return { status: 'success', response: responses[language] };
  },
  
  async handleWeather(language = 'en') {
    try {
      const res = await fetch('https://wttr.in/Delhi?format=j1');
      const data = await res.json();
      const current = data.current_condition[0];
      
      const responses = {
        en: `Current weather in Delhi is ${current.temp_C}°C, ${current.weatherDesc[0].value.toLowerCase()}. Humidity is ${current.humidity}%.`,
        hi: `दिल्ली में मौसम ${current.temp_C}°C है, ${current.weatherDesc[0].value}। नमी ${current.humidity}% है।`
      };
      
      return { status: 'success', response: responses[language] };
    } catch (e) {
      const responses = {
        en: 'Sorry, I could not fetch weather data.',
        hi: 'माफ़ करें, मौसम की जानकारी प्राप्त नहीं कर सके।'
      };
      return { status: 'error', response: responses[language] };
    }
  },
  
  async handleStatus(language = 'en') {
    const responses = {
      en: 'All systems online and operational.',
      hi: 'सभी सिस्टम ऑनलाइन और कार्यरत हैं।'
    };
    return { status: 'success', response: responses[language] };
  }
};

/**
 * Execute command handler
 * @param {object} parsed - Parsed intent object
 * @param {string} language - Language code
 * @returns {object} Result with status and response
 */
async function executeCommand(parsed, language = 'en') {
  if (!parsed.handler) {
    const messages = {
      en: `I didn't understand that. You said "${parsed.rawText}". Try asking about weather, greeting, or status.`,
      hi: `मुझे समझ नहीं आया। आपने "${parsed.rawText}" कहा। मौसम, नमस्कार, या स्थिति के बारे में पूछने का प्रयास करें।`
    };
    return {
      status: 'error',
      response: messages[language]
    };
  }
  
  const handler = handlers[parsed.handler];
  if (!handler) {
    return { status: 'error', response: 'Handler not found' };
  }
  
  return await handler(language);
}

/**
 * Main voice processing function
 * @param {Buffer} audioBuffer - Audio file buffer
 * @param {string} sender - Sender identifier
 * @returns {object} Result with transcript, response, language, etc.
 */
async function processVoiceNote(audioBuffer, sender = 'user') {
  try {
    // Save to temp file
    const timestamp = Date.now();
    const tempPath = path.join(process.env.TEMP || '/tmp', `voice-${timestamp}.ogg`);
    fs.writeFileSync(tempPath, audioBuffer);
    console.log(`[VOICE] Saved temp file: ${tempPath}`);
    
    // 1. Transcribe
    const transcript = await transcribeVoiceNote(tempPath);
    if (!transcript) {
      throw new Error('Transcription failed');
    }
    
    // 2. Detect language
    const language = detectLanguage(transcript);
    console.log(`[LANGUAGE] Detected: ${language}`);
    
    // 3. Parse intent
    const parsed = parseCommand(transcript);
    
    // 4. Execute
    const result = await executeCommand(parsed, language);
    
    // 5. Return result
    const finalResult = {
      status: result.status,
      response: result.response,
      transcript: transcript,
      intent: parsed.intent,
      language: language,
      sender: sender,
      timestamp: timestamp
    };
    
    console.log('[RESULT]', finalResult);
    
    // Cleanup
    try { fs.unlinkSync(tempPath); } catch (e) {}
    
    return finalResult;
    
  } catch (e) {
    console.error('[ERROR]', e.message);
    return {
      status: 'error',
      error: e.message,
      response: 'Failed to process voice note'
    };
  }
}

// Export for use as module or CLI
module.exports = { processVoiceNote, transcribeVoiceNote, parseCommand, detectLanguage };

// CLI usage
if (require.main === module) {
  const audioFile = process.argv[2];
  if (!audioFile) {
    console.error('Usage: node voice-processor.js <audio-file>');
    process.exit(1);
  }
  
  const buffer = fs.readFileSync(audioFile);
  processVoiceNote(buffer).then(result => {
    console.log(JSON.stringify(result, null, 2));
  });
}
