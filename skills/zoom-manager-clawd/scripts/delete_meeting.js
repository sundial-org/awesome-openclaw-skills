#!/usr/bin/env node
const fs = require('fs').promises;
const path = require('path');
const fetch = require('node-fetch');

// Load config
const configPath = path.join(__dirname, '..', 'config.json');
let config;

async function loadConfig() {
    try {
        const data = await fs.readFile(configPath, 'utf8');
        config = JSON.parse(data);
    } catch (err) {
        console.error('Error loading config:', err.message);
        process.exit(1);
    }
}

async function getAccessToken() {
    const url = 'https://api.zoom.us/oauth/token';
    const params = new URLSearchParams({
        grant_type: 'account_credentials',
        account_id: config.account_id
    });

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: params.toString(),
            auth: `${config.client_id}:${config.client_secret}`
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(`Failed to get token: ${data.reason || response.status}`);
        }
        return data.access_token;
    } catch (err) {
        console.error('Error getting access token:', err.message);
        process.exit(1);
    }
}

async function deleteMeeting(meetingId) {
    const token = await getAccessToken();
    const url = `https://api.zoom.us/v2/meetings/${meetingId}`;

    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            console.log(`Meeting ${meetingId} deleted successfully.`);
        } else {
            const error = await response.json();
            console.error(`Failed to delete meeting ${meetingId}: ${response.status} - ${error.message || 'Unknown error'}`);
        }
    } catch (err) {
        console.error('Error deleting meeting:', err.message);
    }
}

// Main execution
async function main() {
    await loadConfig();
    const meetingId = process.argv[2];
    if (!meetingId) {
        console.error('Usage: node delete_meeting.js <meeting_id>');
        process.exit(1);
    }
    await deleteMeeting(meetingId);
}

main().catch(console.error);