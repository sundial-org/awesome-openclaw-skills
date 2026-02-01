#!/usr/bin/env node
/**
 * Zoom CLI - Unified interface for Zoom API operations.
 * Ported for ClawdHub - Uses Environment Variables for security.
 */
const path = require('path');

// Configuration from Environment Variables
const config = {
  client_id: process.env.ZOOM_CLIENT_ID,
  client_secret: process.env.ZOOM_CLIENT_SECRET,
  account_id: process.env.ZOOM_ACCOUNT_ID,
  user_id: process.env.ZOOM_USER_ID || 'me'
};

function checkConfig() {
  const missing = [];
  if (!config.client_id) missing.push('ZOOM_CLIENT_ID');
  if (!config.client_secret) missing.push('ZOOM_CLIENT_SECRET');
  if (!config.account_id) missing.push('ZOOM_ACCOUNT_ID');
  
  if (missing.length > 0) {
    console.error('❌ Missing required environment variables:', missing.join(', '));
    process.exit(1);
  }
}

async function getAccessToken() {
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
    const errorText = await response.text();
    throw new Error(`Failed to get access token: ${response.status} ${response.statusText}\n${errorText}`);
  }

  const data = await response.json();
  return data.access_token;
}

async function createMeeting(topic, startTime, durationMinutes) {
  const token = await getAccessToken();
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
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to create meeting: ${response.status} ${response.statusText}\n${errorText}`);
  }

  return await response.json();
}

async function listMeetings() {
  const token = await getAccessToken();
  const url = `https://api.zoom.us/v2/users/${config.user_id}/meetings?type=upcoming`;

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to list meetings: ${response.status} ${response.statusText}\n${errorText}`);
  }

  return await response.json();
}

async function getMeetingInfo(meetingId) {
  const token = await getAccessToken();
  const url = `https://api.zoom.us/v2/meetings/${meetingId}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to get meeting info: ${response.status} ${response.statusText}\n${errorText}`);
  }

  return await response.json();
}

async function deleteMeeting(meetingId) {
  const token = await getAccessToken();
  const url = `https://api.zoom.us/v2/meetings/${meetingId}`;

  const response = await fetch(url, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (response.status === 204) {
    return true;
  }

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to delete meeting: ${response.status} ${response.statusText}\n${errorText}`);
  }

  return true;
}

// Main logic
async function main() {
  checkConfig();

  const command = process.argv[2];
  switch (command) {
    case 'create':
      if (process.argv.length !== 6) {
        console.log('Usage: zoom-cli.js create <topic> <start_time> <duration_minutes>');
        process.exit(1);
      }
      const [topic, startTime, duration] = [process.argv[3], process.argv[4], parseInt(process.argv[5], 10)];
      try {
        const meeting = await createMeeting(topic, startTime, duration);
        console.log('✅ Meeting created successfully!');
        console.log(`ID: ${meeting.id}`);
        console.log(`Join URL: ${meeting.join_url}`);
        console.log(`Start Time: ${meeting.start_time}`);
      } catch (e) {
        console.error('❌ Error:', e.message);
      }
      break;

    case 'list':
      try {
        const data = await listMeetings();
        if (!data.meetings || data.meetings.length === 0) {
          console.log('No upcoming meetings found.');
        } else {
          console.log(`Found ${data.meetings.length} upcoming meeting(s):`);
          for (const m of data.meetings) {
            console.log(`- ${m.topic} | ID: ${m.id} | ${m.start_time} | ${m.join_url}`);
          }
        }
      } catch (e) {
        console.error('❌ Error:', e.message);
      }
      break;

    case 'info':
      if (process.argv.length !== 4) {
        console.log('Usage: zoom-cli.js info <meeting_id>');
        process.exit(1);
      }
      try {
        const info = await getMeetingInfo(process.argv[3]);
        console.log(JSON.stringify(info, null, 2));
      } catch (e) {
        console.error('❌ Error:', e.message);
      }
      break;

    case 'delete':
      if (process.argv.length !== 4) {
        console.log('Usage: zoom-cli.js delete <meeting_id>');
        process.exit(1);
      }
      try {
        await deleteMeeting(process.argv[3]);
        console.log(`✅ Meeting ${process.argv[3]} deleted successfully.`);
      } catch (e) {
        console.error('❌ Error:', e.message);
      }
      break;

    case 'update':
      if (process.argv.length < 5) {
        console.log('Usage: zoom-cli.js update <meeting_id> <start_time> <duration_minutes> [topic]');
        process.exit(1);
      }
      const [mId, newStart, newDuration, newTopic] = [process.argv[3], process.argv[4], parseInt(process.argv[5], 10), process.argv[6]];
      try {
        const token = await getAccessToken();
        const url = `https://api.zoom.us/v2/meetings/${mId}`;
        const payload = {
          start_time: newStart,
          duration: newDuration
        };
        if (newTopic) payload.topic = newTopic;

        const response = await fetch(url, {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Failed to update meeting: ${response.status} ${response.statusText}\n${errorText}`);
        }

        console.log(`✅ Meeting ${mId} updated successfully to ${newStart}.`);
      } catch (e) {
        console.error('❌ Error:', e.message);
      }
      break;

    default:
      console.log('Available commands: create, list, info, delete, update');
      process.exit(1);
  }
}

main().catch(console.error);
