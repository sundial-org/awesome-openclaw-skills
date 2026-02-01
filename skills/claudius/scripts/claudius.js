#!/usr/bin/env node

/**
 * Claudius Intelligence Bridge
 * 
 * ZERO-SETUP INTEGRATION
 * Users just install and use - no configuration needed.
 * Backend handles all authentication and rate limiting.
 */

const https = require('https');

const API_URL = process.env.CLAUDIUS_API_URL || 'https://api.claudiusai.pro';

/**
 * Ask Claudius a question
 * @param {string} query - Raw user message
 * @returns {Promise<string>} - Claudius' response
 */
async function ask(query) {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify({ query });
        const url = new URL('/v1/ask', API_URL);

        const options = {
            method: 'POST',
            hostname: url.hostname,
            port: url.port || 443,
            path: url.pathname,
            headers: {
                'Content-Type': 'application/json',
                'X-Claudius-Client': 'clawdbot-public',  // Backend detection marker
                'User-Agent': 'claudius-clawdbot-skill/1.0.0',
                'Content-Length': data.length
            }
        };

        const req = https.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    try {
                        const response = JSON.parse(body);
                        resolve(response.answer);
                    } catch (e) {
                        reject(new Error(`Invalid JSON response: ${e.message}`));
                    }
                } else if (res.statusCode === 429) {
                    // Rate limit exceeded
                    try {
                        const error = JSON.parse(body);
                        reject(new Error(error.detail?.message || 'Rate limit exceeded. Please try again later.'));
                    } catch (e) {
                        reject(new Error('Rate limit exceeded. Please try again later.'));
                    }
                } else {
                    reject(new Error(`API error ${res.statusCode}: ${body}`));
                }
            });
        });

        req.on('error', (err) => reject(err));
        req.write(data);
        req.end();
    });
}

// Main execution
(async () => {
    const query = process.argv.slice(2).join(' ');

    if (!query) {
        console.error('Usage: claudius <query>');
        process.exit(1);
    }

    // Start "Thinking..." indicator on stderr (doesn't break automated agents)
    let dots = 0;
    const thinkingInterval = setInterval(() => {
        dots = (dots + 1) % 4;
        process.stderr.write(`\rThinking${'.'.repeat(dots)}   `);
    }, 500);

    try {
        const answer = await ask(query);

        // Stop indicator and clear the line
        clearInterval(thinkingInterval);
        process.stderr.write('\r               \r');

        // Success output to stdout (captured by Moltbot/OpenClaw)
        console.log(answer);
    } catch (error) {
        // Stop indicator and clear the line
        clearInterval(thinkingInterval);
        process.stderr.write('\r               \r');

        // Error output to stderr
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
})();

module.exports = { ask };
