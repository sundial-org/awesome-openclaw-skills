#!/usr/bin/env node
const fs = require('fs').promises;
const path = require('path');
const fetch = require('node-fetch');

// Load config
async function loadConfig() {
  const configPath = path.join(__dirname, '..', 'config.json');
  const data = await fs.readFile(configPath, 'utf8');
  return JSON.parse(data);
}

// Get OAuth access token
async function getAccessToken(config) {
  const url = 'https://api.zoom.us/oauth/token';
  const params = new URLSearchParams({
    grant_type: 'account_credentials',
    account_id: config.account_id
  }).toString();

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': `Basic ${Buffer.from(`${config.client_id}:${config.client_secret}`).toString('base64')}`
    },
    body: params
  });

  if (!response.ok) {
    throw new Error(`Failed to get access token: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  return data.access_token;
}

// Get meeting info
async function getMeetingInfo(meetingId, accessToken) {
  const url = `https://api-us.zoom.us/v2/meetings/${meetingId}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to get meeting info: ${response.status} ${response.statusText}`);
  }

  return await response.json();
}

// Main execution
async function main() {
  if (process.argv.length !== 3) {
    console.error('Usage: node get_meeting_info.js <meeting_id>');
    process.exit(1);
  }

  const meetingId = process.argv[2];
  try {
    const config = await loadConfig();
    const token = await getAccessToken(config);
    const info = await getMeetingInfo(meetingId, token);
    console.log(JSON.stringify(info, null, 2));
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();