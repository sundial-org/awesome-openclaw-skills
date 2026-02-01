const { generateSecretKey, getPublicKey, nip04 } = require('nostr-tools');
const WebSocket = require('websocket').client;
const fs = require('fs');
const path = require('path');

const keyPath = path.join(process.env.HOME, '.clawdzap_keys.json');
let sk;

if (fs.existsSync(keyPath)) {
    const keys = JSON.parse(fs.readFileSync(keyPath));
    sk = Uint8Array.from(Buffer.from(keys.sk, 'hex'));
} else {
    console.log('⚠️ No identity found. Run `node send.js` first.');
    process.exit(1);
}

const myPub = getPublicKey(sk);
console.log(`🔑 Listening as: ${myPub}`);

const client = new WebSocket();
const relayUrl = 'wss://relay.damus.io';

client.on('connect', function(connection) {
    console.log('✅ Listening on', relayUrl);

    // Filter for Kind 4 (DMs) sent TO me (p tag)
    const subId = "clawdzap-dm-" + Math.floor(Math.random() * 1000);
    const filter = {
        kinds: [4],
        "#p": [myPub],
        limit: 10
    };
    
    connection.sendUTF(JSON.stringify(["REQ", subId, filter]));

    connection.on('message', async function(message) {
        if (message.type === 'utf8') {
            const data = JSON.parse(message.utf8Data);
            if (data[0] === 'EVENT') {
                const e = data[2];
                try {
                    const decrypted = await nip04.decrypt(sk, e.pubkey, e.content);
                    console.log(`\n💌 DM from ${e.pubkey.slice(0,8)}...:`);
                    console.log(`   "${decrypted}"`);
                } catch (err) {
                    console.log(`\n🔒 Encrypted msg from ${e.pubkey.slice(0,8)}... (Decryption failed)`);
                }
            }
        }
    });
});

client.connect(relayUrl);