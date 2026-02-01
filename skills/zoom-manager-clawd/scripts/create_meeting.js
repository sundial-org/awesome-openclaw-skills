#!/usr/bin/env node
const fs = require('fs').promises;
const path = require('path');

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

// Create a meeting
async function createMeeting(config, topic, startTime, durationMinutes) {
  const accessToken = await getAccessToken(config);
  const url = `https://api.zoom.us/v2/users/${config.user_id}/meetings`;
  const payload = {
    topic: topic,
    type: 2,
    start_time: startTime,
    duration: durationMinutes,
    timezone: 'UTC',
    settings: {
      host_video: true,
      participant_video: true,
      join_before_host: false,
      mute_upon_entry: false,
      approval_type: 0,
      audio: 'both',
      auto_recording: 'cloud'
    }
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Failed to create meeting: ${response.status} ${response.statusText}`);
  }

  return await response.json();
}

// Main
async function main() {
  if (process.argv.length !== 5) {
    console.log('Usage: node create_meeting.js <topic> <start_time> <duration_minutes>');
    process.exit(1);
  }

  try {
    const config = await loadConfig();
    const topic = process.argv[2];
    const startTime = process.argv[3];
    const durationMinutes = parseInt(process.argv[4], 10);

    const meeting = await createMeeting(config, topic, startTime, durationMinutes);
    console.log('✅ Meeting created successfully!');
    console.log(`ID: ${meeting.id}`);
    console.log(`Join URL: ${meeting.join_url}`);
    console.log(`Start Time: ${meeting.start_time}`);
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

main();