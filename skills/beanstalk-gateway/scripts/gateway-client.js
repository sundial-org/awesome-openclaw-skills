#!/usr/bin/env node
/**
 * Beanstalk Gateway Client
 * 
 * Connects local Clawdbot to beans.talk relay server.
 * Reads config from .beanstalk/gateway.json or environment variables.
 */

const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Find config
function loadConfig() {
  // Try environment variables first
  if (process.env.GATEWAY_URL && process.env.GATEWAY_TOKEN) {
    return {
      url: process.env.GATEWAY_URL,
      token: process.env.GATEWAY_TOKEN,
      clawdbotUrl: process.env.CLAWDBOT_URL || 'http://localhost:18789',
    };
  }
  
  // Try workspace config
  const workspacePaths = [
    process.cwd(),
    process.env.CLAWDBOT_WORKSPACE,
    path.join(os.homedir(), '.clawdbot'),
    path.join(os.homedir(), 'clawd'),
  ].filter(Boolean);
  
  for (const base of workspacePaths) {
    const configPath = path.join(base, '.beanstalk', 'gateway.json');
    if (fs.existsSync(configPath)) {
      try {
        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        console.log(`[Gateway] Loaded config from ${configPath}`);
        return {
          url: config.url,
          token: config.token,
          clawdbotUrl: config.clawdbotUrl || 'http://localhost:18789',
        };
      } catch (err) {
        console.error(`[Gateway] Failed to parse ${configPath}:`, err.message);
      }
    }
  }
  
  return null;
}

const config = loadConfig();

if (!config) {
  console.error('[Gateway] No configuration found.');
  console.error('');
  console.error('Set environment variables:');
  console.error('  GATEWAY_URL=wss://beanstalk.fly.dev/ws/gw_xxx');
  console.error('  GATEWAY_TOKEN=gt_xxx');
  console.error('');
  console.error('Or create .beanstalk/gateway.json in your workspace:');
  console.error('  {"url": "wss://...", "token": "gt_..."}');
  process.exit(1);
}

const STATUS_INTERVAL = 10000;
const RECONNECT_DELAY = 5000;

let ws = null;
let reconnectTimer = null;
let statusTimer = null;
let authenticated = false;

/**
 * Fetch status from local Clawdbot
 */
async function getClawdbotStatus() {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);
    
    const response = await fetch(`${config.clawdbotUrl}/status`, {
      signal: controller.signal,
    });
    clearTimeout(timeout);
    
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const data = await response.json();
    
    return {
      timestamp: new Date().toISOString(),
      agents: [{
        id: 'main',
        name: data.agent?.name || 'Clawdbot',
        status: 'running',
        model: data.agent?.model,
        sessions: data.sessions?.active || 0,
      }],
      channels: (data.channels || []).map(ch => ({
        id: ch.id || ch.type,
        name: ch.name || ch.type,
        type: ch.type,
        status: ch.connected ? 'connected' : 'disconnected',
        messagesProcessed: ch.messagesProcessed || 0,
      })),
      system: { uptime: data.uptime },
    };
  } catch {
    return {
      timestamp: new Date().toISOString(),
      agents: [{ id: 'main', name: 'Clawdbot', status: 'stopped' }],
      channels: [],
    };
  }
}

/**
 * Execute command on local Clawdbot
 */
async function executeCommand(commandId, action, payload) {
  console.log(`[Gateway] Executing: ${action}`, payload || '');
  
  try {
    const endpoints = {
      restart: '/restart',
      stop: '/stop', 
      start: '/start',
      status: '/status',
    };
    
    const endpoint = endpoints[action] || '/command';
    const method = action === 'status' ? 'GET' : 'POST';
    const body = endpoints[action] ? null : JSON.stringify({ action, ...payload });
    
    const response = await fetch(`${config.clawdbotUrl}${endpoint}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body,
    });
    
    const result = await response.json().catch(() => ({ ok: response.ok }));
    return { type: 'command_result', commandId, success: response.ok, result };
  } catch (err) {
    return { type: 'command_result', commandId, success: false, result: { error: err.message } };
  }
}

/**
 * Connect to relay
 */
function connect() {
  if (ws) ws.terminate();
  
  console.log(`[Gateway] Connecting to relay...`);
  ws = new WebSocket(config.url);
  authenticated = false;
  
  ws.on('open', () => {
    console.log('[Gateway] Connected, authenticating...');
    ws.send(JSON.stringify({ type: 'auth', token: config.token }));
  });
  
  ws.on('message', async (data) => {
    try {
      const msg = JSON.parse(data.toString());
      
      if (msg.type === 'auth_ok') {
        console.log('[Gateway] ✓ Authenticated');
        authenticated = true;
        startStatusUpdates();
      } else if (msg.type === 'ping') {
        ws.send(JSON.stringify({ type: 'pong' }));
      } else if (msg.type === 'command') {
        const result = await executeCommand(msg.commandId, msg.action, msg.payload);
        ws.send(JSON.stringify(result));
      } else if (msg.type === 'error') {
        console.error('[Gateway] Error:', msg.message);
      }
    } catch (err) {
      console.error('[Gateway] Parse error:', err.message);
    }
  });
  
  ws.on('close', (code, reason) => {
    console.log(`[Gateway] Disconnected (${code})`);
    authenticated = false;
    stopStatusUpdates();
    scheduleReconnect();
  });
  
  ws.on('error', (err) => console.error('[Gateway] Error:', err.message));
}

function scheduleReconnect() {
  if (reconnectTimer) return;
  console.log(`[Gateway] Reconnecting in ${RECONNECT_DELAY/1000}s...`);
  reconnectTimer = setTimeout(() => { reconnectTimer = null; connect(); }, RECONNECT_DELAY);
}

function startStatusUpdates() {
  stopStatusUpdates();
  sendStatus();
  statusTimer = setInterval(sendStatus, STATUS_INTERVAL);
}

function stopStatusUpdates() {
  if (statusTimer) { clearInterval(statusTimer); statusTimer = null; }
}

async function sendStatus() {
  if (!ws || ws.readyState !== WebSocket.OPEN || !authenticated) return;
  ws.send(JSON.stringify({ type: 'status', payload: await getClawdbotStatus() }));
}

process.on('SIGINT', () => { console.log('\n[Gateway] Shutting down...'); stopStatusUpdates(); if (ws) ws.close(); process.exit(0); });
process.on('SIGTERM', () => { stopStatusUpdates(); if (ws) ws.close(); process.exit(0); });

console.log('[Gateway] Beanstalk Gateway Client v1.0.0');
console.log(`[Gateway] Clawdbot: ${config.clawdbotUrl}`);
connect();
