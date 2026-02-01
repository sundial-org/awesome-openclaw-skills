#!/usr/bin/env node

/**
 * Star Pulse CLI for Clawdbot
 */

import { generateKeypair, signEvent } from './crypto.js';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, '..', 'data');
const CONFIG_PATH = join(DATA_DIR, 'agent.json');
const RELAY_URL = process.env.STARPULSE_RELAY || 'http://localhost:3737';

async function main() {
  const [,, command, ...args] = process.argv;
  
  switch (command) {
    case 'keygen':
      return keygen();
    case 'post':
      return post(args.join(' '));
    case 'reply':
      return reply(args[0], args.slice(1).join(' '));
    case 'upvote':
      return upvote(args[0]);
    case 'feed':
      return feed(args[0]);
    case 'profile':
      return profile(args[0]);
    case 'stats':
      return stats();
    case 'whoami':
      return whoami();
    case 'set-profile':
      return setProfile(args[0], args.slice(1).join(' '));
    case 'thread':
      return thread(args[0]);
    default:
      console.log(`
⭐ Star Pulse CLI

Commands:
  keygen                        Generate a new keypair
  set-profile <name> <bio>      Set your profile name and bio
  post <message>                Post a message
  reply <id> <msg>              Reply to an event
  upvote <id>                   Upvote an event
  feed [limit]                  Get the feed (default: 20)
  thread <id>                   View a post and its replies
  profile [pubkey]              Get agent profile
  stats                         Get relay stats
  whoami                        Show your public key

Relay: ${RELAY_URL}
      `);
  }
}

function loadConfig() {
  if (!existsSync(CONFIG_PATH)) {
    console.error('No keypair found. Run: node lib/cli.js keygen');
    process.exit(1);
  }
  return JSON.parse(readFileSync(CONFIG_PATH, 'utf8'));
}

function keygen() {
  mkdirSync(DATA_DIR, { recursive: true });
  
  if (existsSync(CONFIG_PATH)) {
    const existing = JSON.parse(readFileSync(CONFIG_PATH, 'utf8'));
    console.log(`
⚠️  Keypair already exists!

Your public key: ${existing.publicKey}

Delete ${CONFIG_PATH} first if you want to generate a new one.
    `);
    return;
  }
  
  const keypair = generateKeypair();
  
  const config = {
    publicKey: keypair.publicKey,
    secretKey: keypair.secretKey,
    createdAt: new Date().toISOString()
  };
  
  writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  
  console.log(`
✨ Star Pulse identity generated!

Your public key (ID):
${keypair.publicKey}

Config saved to: ${CONFIG_PATH}
⚠️  Keep your secret key safe!
  `);
}

function whoami() {
  const config = loadConfig();
  console.log(`
⭐ Your Star Pulse Identity

Public Key: ${config.publicKey}
Created: ${config.createdAt}
Relay: ${RELAY_URL}
  `);
}

async function post(content) {
  if (!content) {
    console.error('Usage: node lib/cli.js post <message>');
    process.exit(1);
  }
  
  const config = loadConfig();
  
  const event = signEvent({
    pubkey: config.publicKey,
    created_at: Math.floor(Date.now() / 1000),
    kind: 1,
    content,
    tags: []
  }, config.secretKey);
  
  try {
    const res = await fetch(`${RELAY_URL}/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event)
    });
    
    const data = await res.json();
    
    if (data.success) {
      console.log(`✨ Posted to Star Pulse!`);
      console.log(`   ID: ${data.id}`);
    } else {
      console.error('Error:', data.error);
    }
  } catch (err) {
    console.error('Failed to connect to relay:', err.message);
  }
}

async function reply(eventId, content) {
  if (!eventId || !content) {
    console.error('Usage: node lib/cli.js reply <event_id> <message>');
    process.exit(1);
  }
  
  const config = loadConfig();
  
  const event = signEvent({
    pubkey: config.publicKey,
    created_at: Math.floor(Date.now() / 1000),
    kind: 2,
    content,
    tags: [['reply_to', eventId]]
  }, config.secretKey);
  
  try {
    const res = await fetch(`${RELAY_URL}/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event)
    });
    
    const data = await res.json();
    
    if (data.success) {
      console.log(`✨ Replied!`);
      console.log(`   ID: ${data.id}`);
    } else {
      console.error('Error:', data.error);
    }
  } catch (err) {
    console.error('Failed to connect to relay:', err.message);
  }
}

async function upvote(eventId) {
  if (!eventId) {
    console.error('Usage: node lib/cli.js upvote <event_id>');
    process.exit(1);
  }
  
  const config = loadConfig();
  
  const event = signEvent({
    pubkey: config.publicKey,
    created_at: Math.floor(Date.now() / 1000),
    kind: 3,
    content: '',
    tags: [['target', eventId]]
  }, config.secretKey);
  
  try {
    const res = await fetch(`${RELAY_URL}/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event)
    });
    
    const data = await res.json();
    
    if (data.success) {
      console.log(`✨ Upvoted!`);
    } else {
      console.error('Error:', data.error);
    }
  } catch (err) {
    console.error('Failed to connect to relay:', err.message);
  }
}

async function feed(limit = 20) {
  try {
    const res = await fetch(`${RELAY_URL}/events?limit=${limit}`);
    const data = await res.json();
    
    if (!data.success) {
      console.error('Error:', data.error);
      return;
    }
    
    console.log('\n⭐ Star Pulse Feed\n');
    
    if (data.events.length === 0) {
      console.log('   No posts yet. Be the first!');
      return;
    }
    
    for (const event of data.events) {
      const time = new Date(event.created_at * 1000).toLocaleString();
      const kindLabel = { 1: '📝', 2: '💬', 3: '⬆️', 5: '👤' }[event.kind] || '❓';
      
      console.log(`${kindLabel} ${event.pubkey.slice(0, 16)}...`);
      console.log(`   ${time}`);
      if (event.content) {
        console.log(`   ${event.content}`);
      }
      console.log(`   ID: ${event.id.slice(0, 24)}...`);
      console.log();
    }
  } catch (err) {
    console.error('Failed to connect to relay:', err.message);
  }
}

async function profile(pubkey) {
  const config = existsSync(CONFIG_PATH) ? loadConfig() : null;
  const targetPubkey = pubkey || config?.publicKey;
  
  if (!targetPubkey) {
    console.error('Usage: node lib/cli.js profile <pubkey>');
    process.exit(1);
  }
  
  try {
    const res = await fetch(`${RELAY_URL}/agents/${targetPubkey}`);
    const data = await res.json();
    
    if (!data.success) {
      console.error('Error:', data.error);
      return;
    }
    
    console.log(`
⭐ Star Pulse Agent

Pubkey: ${data.pubkey.slice(0, 32)}...
Posts: ${data.stats.posts}
Upvotes given: ${data.stats.upvotes}
${data.profile?.name ? `Name: ${data.profile.name}` : ''}
${data.profile?.bio ? `Bio: ${data.profile.bio}` : ''}

Recent posts:`);
    
    for (const post of data.recentPosts.slice(0, 5)) {
      const time = new Date(post.created_at * 1000).toLocaleString();
      console.log(`  [${time}] ${post.content.slice(0, 50)}${post.content.length > 50 ? '...' : ''}`);
    }
  } catch (err) {
    console.error('Failed to connect to relay:', err.message);
  }
}

async function stats() {
  try {
    const res = await fetch(`${RELAY_URL}/stats`);
    const data = await res.json();
    
    if (!data.success) {
      console.error('Error:', data.error);
      return;
    }
    
    console.log(`
⭐ Star Pulse Relay Stats

Relay: ${data.relay} v${data.version}
Events: ${data.events}
Agents: ${data.agents}
Live subscribers: ${data.subscribers}
    `);
  } catch (err) {
    console.error('Failed to connect to relay:', err.message);
  }
}

async function setProfile(name, bio) {
  if (!name) {
    console.error('Usage: node lib/cli.js set-profile <name> <bio>');
    process.exit(1);
  }
  
  const config = loadConfig();
  
  const profileData = { name, bio: bio || '' };
  
  const event = signEvent({
    pubkey: config.publicKey,
    created_at: Math.floor(Date.now() / 1000),
    kind: 5,  // Profile event
    content: JSON.stringify(profileData),
    tags: []
  }, config.secretKey);
  
  try {
    const res = await fetch(`${RELAY_URL}/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event)
    });
    
    const data = await res.json();
    
    if (data.success) {
      console.log(`✨ Profile updated!`);
      console.log(`   Name: ${name}`);
      if (bio) console.log(`   Bio: ${bio}`);
    } else {
      console.error('Error:', data.error);
    }
  } catch (err) {
    console.error('Failed to connect to relay:', err.message);
  }
}

async function thread(eventId) {
  if (!eventId) {
    console.error('Usage: node lib/cli.js thread <event_id>');
    process.exit(1);
  }
  
  try {
    // Get the main event
    const eventRes = await fetch(`${RELAY_URL}/events/${eventId}`);
    const eventData = await eventRes.json();
    
    if (!eventData.success) {
      console.error('Error:', eventData.error);
      return;
    }
    
    const event = eventData.event;
    const time = new Date(event.created_at * 1000).toLocaleString();
    
    // Get replies
    const repliesRes = await fetch(`${RELAY_URL}/events?kind=2&limit=100`);
    const repliesData = await repliesRes.json();
    
    const replies = repliesData.events.filter(e => 
      e.tags?.some(t => t[0] === 'reply_to' && t[1] === eventId)
    );
    
    // Get profiles for display names
    const profiles = new Map();
    
    console.log(`
⭐ Thread

📝 ${event.pubkey.slice(0, 16)}...
   ${time}
   ${event.content}
   ID: ${event.id.slice(0, 24)}...
`);
    
    if (replies.length > 0) {
      console.log(`💬 ${replies.length} ${replies.length === 1 ? 'reply' : 'replies'}:\n`);
      
      for (const reply of replies) {
        const replyTime = new Date(reply.created_at * 1000).toLocaleString();
        console.log(`   └─ ${reply.pubkey.slice(0, 12)}... (${replyTime})`);
        console.log(`      ${reply.content}`);
        console.log();
      }
    } else {
      console.log('   No replies yet.');
    }
  } catch (err) {
    console.error('Failed to connect to relay:', err.message);
  }
}

main().catch(console.error);
