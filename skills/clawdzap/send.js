const { generateSecretKey, getPublicKey, finalizeEvent } = require('nostr-tools');
const WebSocket = require('websocket').client;
const fs = require('fs');
const path = require('path');

// 1. Identity Management
const keyPath = path.join(process.env.HOME, '.clawdzap_keys.json');
let sk;

if (fs.existsSync(keyPath)) {
    const keys = JSON.parse(fs.readFileSync(keyPath));
    sk = Uint8Array.from(Buffer.from(keys.sk, 'hex'));
} else {
    sk = generateSecretKey();
    const hexSk = Buffer.from(sk).toString('hex');
    fs.writeFileSync(keyPath, JSON.stringify({ sk: hexSk }));
    console.log('🔑 New Identity Generated!');
}

const messageContent = process.argv[2] || 'ClawdZap Ping! 🍄⚡';

const event = {
  kind: 1, 
  created_at: Math.floor(Date.now() / 1000),
  tags: [['t', 'clawdzap']], 
  content: messageContent,
};

const signedEvent = finalizeEvent(event, sk);
const client = new WebSocket();

client.on('connect', (conn) => {
    console.log('✅ Connected.');
    conn.sendUTF(JSON.stringify(['EVENT', signedEvent]));
    console.log(`🚀 Sent: "${messageContent}"`);
    setTimeout(() => { conn.close(); process.exit(0); }, 500);
});

client.connect('wss://relay.damus.io');