const { generateSecretKey, getPublicKey, finalizeEvent, nip04 } = require('nostr-tools');
const WebSocket = require('websocket').client;
const fs = require('fs');
const path = require('path');

// 1. Identity
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

const myPub = getPublicKey(sk);
console.log(`🔑 From: ${myPub.slice(0,8)}...`);

// 2. Parse Args
const recipientHex = process.argv[2]; // Target PubKey
const messageContent = process.argv[3] || 'ClawdZap Encrypted Ping! 🍄🔒';

if (!recipientHex) {
    console.log("Usage: node send_dm.js <recipient_pubkey> <message>");
    process.exit(1);
}

// 3. Encrypt (NIP-04)
async function send() {
    const encryptedContent = await nip04.encrypt(sk, recipientHex, messageContent);
    
    const event = {
        kind: 4, // NIP-04 Direct Message
        created_at: Math.floor(Date.now() / 1000),
        tags: [['p', recipientHex]], 
        content: encryptedContent,
        pubkey: myPub
    };

    const signedEvent = finalizeEvent(event, sk);
    const client = new WebSocket();

    client.on('connect', (conn) => {
        console.log('✅ Connected.');
        conn.sendUTF(JSON.stringify(['EVENT', signedEvent]));
        console.log(`🚀 Encrypted DM Sent to ${recipientHex.slice(0,8)}...`);
        setTimeout(() => { conn.close(); process.exit(0); }, 500);
    });

    client.connect('wss://relay.damus.io');
}

send();