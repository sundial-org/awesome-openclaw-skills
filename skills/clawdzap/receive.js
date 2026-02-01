const { generateSecretKey, getPublicKey } = require('nostr-tools');
const WebSocket = require('websocket').client;
const fs = require('fs');
const path = require('path');

// 1. Identity
const keyPath = path.join(process.env.HOME, '.clawdzap_keys.json');
let pk;

if (fs.existsSync(keyPath)) {
    const keys = JSON.parse(fs.readFileSync(keyPath));
    // We only need PK for filter, not SK for signing (unless we auth later)
    // But let's regenerate PK from SK to be sure
    const sk = Uint8Array.from(Buffer.from(keys.sk, 'hex'));
    pk = getPublicKey(sk);
    console.log('🔑 Identity:', pk);
} else {
    console.log('⚠️ No identity found. Run `node send.js` first to generate one!');
    process.exit(1);
}

// 2. Connect
const client = new WebSocket();
const relayUrl = 'wss://relay.damus.io';

client.on('connect', function(connection) {
    console.log('✅ Listening on', relayUrl);

    // 3. Subscribe to Global ClawdZap Tag
    const subId = "clawdzap-global-" + Math.floor(Math.random() * 1000);
    const filter = {
        kinds: [1],
        "#t": ["clawdzap"], // Listen for tag 'clawdzap'
        limit: 10
    };
    
    connection.sendUTF(JSON.stringify(["REQ", subId, filter]));

    // 4. Handle Incoming
    connection.on('message', function(message) {
        if (message.type === 'utf8') {
            const data = JSON.parse(message.utf8Data);
            if (data[0] === 'EVENT') {
                const e = data[2];
                console.log(`\n💬 [${e.pubkey.slice(0,6)}] ${e.content}`);
            }
        }
    });
});

client.connect(relayUrl);