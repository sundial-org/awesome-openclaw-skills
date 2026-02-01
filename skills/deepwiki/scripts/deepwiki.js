#!/usr/bin/env node
const http = require('https');

const args = process.argv.slice(2);
const command = args[0];
const repo = args[1];
const extra = args[2];

if (!command || !repo) {
  console.log('Usage: deepwiki.js <command> <repo> [args]');
  console.log('Commands: ask, structure, contents');
  process.exit(0);
}

const SSE_URL = 'https://mcp.deepwiki.com/sse';

async function run() {
  let sessionId = null;
  let messageUrl = null;

  // 1. Establish SSE connection
  const sseReq = http.get(SSE_URL, (res) => {
    let buffer = '';
    res.on('data', (chunk) => {
      buffer += chunk.toString();
      
      // Parse SSE events
      const lines = buffer.split('\n');
      buffer = lines.pop(); // Keep incomplete line

      let currentEvent = null;
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.substring(7).trim();
        } else if (line.startsWith('data: ')) {
          const data = line.substring(6).trim();
          
          if (currentEvent === 'endpoint') {
            messageUrl = 'https://mcp.deepwiki.com' + data;
            const url = new URL(messageUrl);
            sessionId = url.searchParams.get('sessionId');
            
            // Now that we have the session, send the tool call
            sendToolCall(messageUrl);
          } else if (currentEvent === 'message') {
            try {
              const msg = JSON.parse(data);
              // Check if this is the response to our request (id: 1)
              if (msg.id === 1) {
                if (msg.error) {
                  console.error('Error:', msg.error.message);
                } else {
                  handleResult(msg.result);
                }
                sseReq.destroy();
                process.exit(0);
              }
            } catch (e) {
              // Ignore non-JSON or other messages
            }
          }
        } else if (line === '') {
          currentEvent = null;
        }
      }
    });
  });

  sseReq.on('error', (err) => {
    console.error('SSE Error:', err.message);
    process.exit(1);
  });

  // Timeout after 30s
  setTimeout(() => {
    console.error('Request timed out');
    sseReq.destroy();
    process.exit(1);
  }, 30000);
}

function sendToolCall(url) {
  let name, params;
  if (command === 'ask') {
    name = 'ask_question';
    params = { repoName: repo, question: extra };
  } else if (command === 'structure') {
    name = 'read_wiki_structure';
    params = { repoName: repo };
  } else if (command === 'contents') {
    name = 'read_wiki_contents';
    params = { repoName: repo, path: extra };
  }

  const body = JSON.stringify({
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/call',
    params: {
      name,
      arguments: params
    }
  });

  const req = http.request(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': body.length
    }
  }, (res) => {
    if (res.statusCode !== 200 && res.statusCode !== 202) {
      console.error(`Post failed: ${res.statusCode}`);
      process.exit(1);
    }
  });

  req.on('error', (err) => {
    console.error('Post Error:', err.message);
    process.exit(1);
  });

  req.write(body);
  req.end();
}

function handleResult(result) {
  if (result && result.content) {
    console.log(result.content.map(c => c.text).join('\n'));
  } else {
    console.log(JSON.stringify(result, null, 2));
  }
}

run();
