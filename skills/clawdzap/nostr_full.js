const { generateSecretKey, getPublicKey, finalizeEvent } = require('nostr-tools');
const WebSocket = require('websocket').client;

// 1. Identity
// In a real app, load this from a file!
const sk = generateSecretKey();
const pk = getPublicKey(sk);
console.log('🔑 Identity:', pk);

// 2. Connect to Relay
const client = new WebSocket();
const relayUrl = 'wss://relay.damus.io';

client.on('connect', function(connection) {
    console.log('✅ Connected to', relayUrl);

    // 3. Subscribe to DMs (Kind 1 for now, public chat)
    const subId = "my-sub-" + Math.floor(Math.random() * 1000);
    const filter = {
        kinds: [1],
        limit: 5
        // authors: [pk] // To see my own posts, or remove to see global feed
    };
    
    const req = JSON.stringify(["REQ", subId, filter]);
    connection.sendUTF(req);
    console.log('📡 Listening for messages...');

    // 4. Send Hello World
    const event = {
        kind: 1,
        created_at: Math.floor(Date.now() / 1000),
        tags: [],
        content: 'ClawdZap v0.1: Listening for signals... 🍄⚡',
    };
    const signedEvent = finalizeEvent(event, sk);
    connection.sendUTF(JSON.stringify(['EVENT', signedEvent]));

    // 5. Handle Incoming
    connection.on('message', function(message) {
        if (message.type === 'utf8') {
            const data = JSON.parse(message.utf8Data);
            if (data[0] === 'EVENT') {
                const e = data[2];
                console.log(`\n💬 New Message from ${e.pubkey.slice(0,8)}...:`);
                console.log(`   "${e.content}"`);
            }
        }
    });
});

client.connect(relayUrl);