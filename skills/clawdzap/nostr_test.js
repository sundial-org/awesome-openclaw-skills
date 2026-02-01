const { generateSecretKey, getPublicKey, finalizeEvent, verifyEvent } = require('nostr-tools');
const WebSocket = require('websocket').client;

// 1. Generate Keys (simulating agent identity)
const sk = generateSecretKey(); // Private Key
const pk = getPublicKey(sk);    // Public Key

console.log('🔑 Agent Identity Generated:');
console.log('Public Key:', pk);

// 2. Create Event (Message)
const event = {
  kind: 1, // Kind 1 = Short Text Note
  created_at: Math.floor(Date.now() / 1000),
  tags: [],
  content: 'Hello World from ClawdZap! 🍄⚡',
};

// 3. Sign Event
const signedEvent = finalizeEvent(event, sk);
console.log('\n📝 Signed Event:', signedEvent);

// 4. Connect to Relay
const client = new WebSocket();
const relayUrl = 'wss://relay.damus.io';

client.on('connect', function(connection) {
    console.log('\n✅ Connected to Relay:', relayUrl);
    
    // Send Event
    const message = JSON.stringify(['EVENT', signedEvent]);
    connection.sendUTF(message);
    console.log('🚀 Message Sent!');

    // Listen for OK
    connection.on('message', function(message) {
        if (message.type === 'utf8') {
            console.log('📩 Relay Response:', message.utf8Data);
            // Close after response
            if (message.utf8Data.includes('OK')) {
                console.log('✨ Success! Message published to the network.');
                connection.close();
            }
        }
    });
});

client.connect(relayUrl);