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

async function getAccessToken(config) {
  const url = 'https://api.zoom.us/oauth/token';
  const params = new URLSearchParams({
    grant_type: 'account_credentials',
    account_id: config.account_id
  });

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': `Basic ${Buffer.from(`${config.client_id}:${config.client_secret}`).toString('base64')}`
    },
    body: params.toString()
  });

  if (!response.ok) {
    throw new Error(`Failed to get access token: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  return data.access_token;
}

async function listMeetings(config, accessToken) {
  const url = `https://api-us.zoom.us/v2/users/${config.user_id}/meetings?type=upcoming`;
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to list meetings: ${response.status} ${response.statusText}`);
  }

  return await response.json();
}

async function main() {
  try {
    const config = await loadConfig();
    const token = await getAccessToken(config);
    const meetings = await listMeetings(config, token);

    if (!meetings.meetings || meetings.meetings.length === 0) {
      console.log('No upcoming meetings found.');
      return;
    }

    console.log(`Found ${meetings.meetings.length} upcoming meeting(s):`);
    for (const meeting of meetings.meetings) {
      console.log(`- ID: ${meeting.id}`);
      console.log(`  Topic: ${meeting.topic}`);
      console.log(`  Start: ${meeting.start_time}`);
      console.log(`  Join URL: ${meeting.join_url}\n`);
    }
  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();