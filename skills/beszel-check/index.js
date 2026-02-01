#!/usr/bin/env node
const fs = require('fs');
const https = require('http');

const CONFIG = {
  host: process.env.BESZEL_HOST || 'http://127.0.0.1:8090',
  email: process.env.BESZEL_USER,
  password: process.env.BESZEL_PASS
};

if (!CONFIG.email || !CONFIG.password) {
  console.error('Error: BESZEL_USER and BESZEL_PASS environment variables must be set.');
  process.exit(1);
}

async function request(path, method = 'GET', data = null, token = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: new URL(CONFIG.host).hostname,
      port: new URL(CONFIG.host).port,
      path: path,
      method: method,
      headers: {
        'Content-Type': 'application/json',
      }
    };

    if (token) {
      options.headers['Authorization'] = token;
    }

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          resolve({ error: 'Invalid JSON', body });
        }
      });
    });

    req.on('error', (e) => reject(e));
    if (data) req.write(JSON.stringify(data));
    req.end();
  });
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'status';

  try {
    // 1. Authenticate
    const auth = await request('/api/collections/users/auth-with-password', 'POST', {
      identity: CONFIG.email,
      password: CONFIG.password
    });

    if (!auth.token) {
      console.error('Authentication failed:', auth);
      process.exit(1);
    }

    const token = auth.token;

    // 2. Route commands
    if (command === 'status') {
      const systems = await request('/api/collections/systems/records', 'GET', null, token);
      
      if (!systems.items || systems.items.length === 0) {
        console.log("No systems found. (Did you share the server with jenny@gmail.com?)");
        return;
      }

      console.log("🖥️  **System Status**\n");
      
      for (const sys of systems.items) {
        const info = sys.info || {};
        const cpu = info.cpu?.toFixed(1) + '%' || '?';
        const ram = info.mp?.toFixed(1) + '%' || '?';
        const disk = info.dp?.toFixed(1) + '%' || '?';
        const status = sys.status === 'up' ? '🟢 UP' : '🔴 DOWN';
        
        console.log(`**${sys.name}** (${status})`);
        console.log(`- CPU: ${cpu}`);
        console.log(`- RAM: ${ram}`);
        console.log(`- Disk: ${disk}`);
        console.log(`- Uptime: ${(info.u / 86400).toFixed(1)} days`);
      }

    } else if (command === 'containers') {
      const showAll = args[1] === 'all';
      // Fetch the latest container stats (sort by created desc, limit 1)
      const stats = await request('/api/collections/container_stats/records?perPage=1&sort=-created', 'GET', null, token);
      
      if (!stats.items || stats.items.length === 0) {
        console.log("No container stats found.");
        return;
      }

      const latest = stats.items[0];
      const containers = latest.stats || [];

      // Sort by CPU usage descending
      containers.sort((a, b) => b.c - a.c);

      console.log("📦 **Top Containers (by CPU)**\n");
      
      // Show top 10 or all if requested
      const limit = showAll ? containers.length : 10;
      containers.slice(0, limit).forEach(c => {
        const cpu = c.c.toFixed(2) + '%';
        const ram = c.m.toFixed(0) + ' MB';
        console.log(`- **${c.n}**: ${cpu} CPU | ${ram}`);
      });
      
      console.log(`\n(Total containers: ${containers.length})`);

    } else {
      console.log(`Unknown command: ${command}`);
      console.log('Usage: beszel [status|containers]');
    }

  } catch (err) {
    console.error('Error:', err);
  }
}

main();
