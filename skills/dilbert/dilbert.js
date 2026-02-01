#!/usr/bin/env node
/**
 * Dilbert Skill for Clawdbot
 * Fetches and sends random Dilbert comics
 */

const { spawn } = require('child_process');
const path = require('path');

const SKILL_NAME = 'dilbert';
const SKILL_DIR = __dirname;

/**
 * Execute the skill.sh script to fetch a Dilbert comic
 * @returns {Promise<string>} Path to the downloaded comic image
 */
async function fetchDilbertComic() {
    return new Promise((resolve, reject) => {
        const scriptPath = path.join(SKILL_DIR, 'skill.sh');
        
        const process = spawn(scriptPath, [], {
            cwd: SKILL_DIR,
            env: process.env
        });

        let stdout = '';
        let stderr = '';

        process.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        process.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        process.on('close', (code) => {
            if (code === 0) {
                const imagePath = stdout.trim();
                resolve(imagePath);
            } else {
                reject(new Error(`Failed to fetch Dilbert comic. Exit code: ${code}. Stderr: ${stderr}`));
            }
        });

        process.on('error', (err) => {
            reject(err);
        });
    });
}

/**
 * Main skill handler - called by Clawdbot
 * @param {Object} args - Arguments from Clawdbot (may include context, message info, etc.)
 * @returns {Promise<Object>} Result object with image path and metadata
 */
async function skillHandler(args) {
    try {
        console.log(`[${SKILL_NAME}] Fetching random Dilbert comic...`);
        
        const imagePath = await fetchDilbertComic();
        
        return {
            success: true,
            skill: SKILL_NAME,
            imagePath: imagePath,
            message: 'Here\'s a random Dilbert comic for you!',
            type: 'image'
        };
    } catch (error) {
        console.error(`[${SKILL_NAME}] Error:`, error.message);
        
        return {
            success: false,
            skill: SKILL_NAME,
            error: error.message,
            message: 'Sorry, I couldn\'t fetch a Dilbert comic at this time.'
        };
    }
}

// Export for Clawdbot
module.exports = {
    name: SKILL_NAME,
    handler: skillHandler,
    fetch: fetchDilbertComic
};

// If run directly (for testing)
if (require.main === module) {
    skillHandler({})
        .then((result) => {
            console.log('Result:', JSON.stringify(result, null, 2));
            process.exit(result.success ? 0 : 1);
        })
        .catch((err) => {
            console.error('Fatal error:', err);
            process.exit(1);
        });
}
