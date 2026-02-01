/**
 * Example: Custom Intent Configuration
 * 
 * This file shows how to extend voice-processor.js with custom intents
 * for your specific use case.
 * 
 * Copy this pattern into voice-processor.js to add your own handlers.
 */

// ============================================
// CUSTOM INTENTS
// ============================================

const CUSTOM_INTENTS = {
  // Smart Home Control
  'lights': {
    keywords: ['lights', 'light', 'brightness', 'बत्ती', 'रोशनी'],
    handler: 'handleLights'
  },
  
  // Shopping List
  'shopping': {
    keywords: ['shopping', 'list', 'buy', 'add item', 'खरीद', 'सूची'],
    handler: 'handleShopping'
  },
  
  // Drone Control
  'drone': {
    keywords: ['drone', 'launch', 'fly', 'land', 'ड्रोन', 'उड़'],
    handler: 'handleDrone'
  },
  
  // Reminder/Alarm
  'reminder': {
    keywords: ['remind', 'alarm', 'timer', 'notification', 'याद', 'अलर्ट'],
    handler: 'handleReminder'
  },
  
  // Music Control
  'music': {
    keywords: ['music', 'song', 'play', 'pause', 'skip', 'संगीत', 'गाना'],
    handler: 'handleMusic'
  }
};

// ============================================
// CUSTOM HANDLERS
// ============================================

const customHandlers = {
  // Smart Home Example
  async handleLights(language = 'en') {
    // In a real app, you'd control actual smart home devices
    const device = await getSmartHomeDevice('living-room-lights');
    const status = await device.toggle();
    
    const responses = {
      en: status ? 'Lights turned on' : 'Lights turned off',
      hi: status ? 'बत्ती चालू हो गई' : 'बत्ती बंद हो गई'
    };
    
    return {
      status: 'success',
      response: responses[language],
      data: { device: 'lights', status }
    };
  },
  
  // Shopping List Example
  async handleShopping(language = 'en') {
    // Parse what the user wants to add/remove
    const responses = {
      en: "What would you like to add to your shopping list?",
      hi: "आप अपनी शॉपिंग लिस्ट में क्या जोड़ना चाहते हैं?"
    };
    
    return {
      status: 'success',
      response: responses[language],
      action: 'waiting_for_item'
    };
  },
  
  // Drone Control Example
  async handleDrone(language = 'en') {
    // Connect to drone API and execute command
    const droneAPI = require('drone-sdk');
    const drone = new droneAPI.Drone();
    
    const status = await drone.getStatus();
    
    const responses = {
      en: `Drone status: Battery ${status.battery}%, ${status.ready ? 'Ready for launch' : 'Not ready'}`,
      hi: `ड्रोन स्थिति: बैटरी ${status.battery}%, ${status.ready ? 'लॉन्च के लिए तैयार' : 'तैयार नहीं'}`
    };
    
    return {
      status: 'success',
      response: responses[language],
      data: status
    };
  },
  
  // Reminder Example
  async handleReminder(language = 'en') {
    // Set a reminder/timer
    const responses = {
      en: "I'll set a reminder. What should I remind you about?",
      hi: "मैं एक रिमाइंडर सेट करूंगा। मुझे आपको क्या याद दिलाना चाहिए?"
    };
    
    return {
      status: 'success',
      response: responses[language],
      action: 'waiting_for_reminder_text'
    };
  },
  
  // Music Control Example
  async handleMusic(language = 'en') {
    // Control music player
    const musicAPI = require('music-api'); // hypothetical
    const player = new musicAPI.Player();
    
    const current = await player.currentTrack();
    
    const responses = {
      en: `Now playing: ${current.title} by ${current.artist}`,
      hi: `अब बज रहा है: ${current.title} ${current.artist} द्वारा`
    };
    
    return {
      status: 'success',
      response: responses[language],
      data: current
    };
  }
};

// ============================================
// HOW TO INTEGRATE
// ============================================

/*
 * 1. In voice-processor.js, add these to the INTENTS object:
 * 
 *   const INTENTS = {
 *     'greeting': { ... },
 *     'weather': { ... },
 *     'lights': CUSTOM_INTENTS.lights,
 *     'shopping': CUSTOM_INTENTS.shopping,
 *     'drone': CUSTOM_INTENTS.drone,
 *     // ... etc
 *   };
 * 
 * 2. Add handlers to the handlers object:
 * 
 *   const handlers = {
 *     handleGreeting,
 *     handleWeather,
 *     ...customHandlers
 *   };
 * 
 * 3. That's it! Now voice messages like "Turn on the lights" will work.
 */

// ============================================
// TESTING
// ============================================

// Test your custom intents:
const { parseCommand } = require('./scripts/voice-processor');

const testCases = [
  "Turn on the lights",
  "Add milk to my shopping list",
  "What's the drone status?",
  "Set a reminder",
  "Play some music"
];

testCases.forEach(text => {
  const parsed = parseCommand(text);
  console.log(`"${text}" → Intent: ${parsed.intent}, Handler: ${parsed.handler}`);
});

module.exports = {
  CUSTOM_INTENTS,
  customHandlers
};
