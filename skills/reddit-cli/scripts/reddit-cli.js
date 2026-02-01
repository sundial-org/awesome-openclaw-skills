#!/usr/bin/env node

const https = require('https');

// Read cookies from env
const REDDIT_SESSION = process.env.REDDIT_SESSION || '';
const TOKEN_V2 = process.env.TOKEN_V2 || '';

const COOKIES = [
  REDDIT_SESSION && `reddit_session=${REDDIT_SESSION}`,
  TOKEN_V2 && `token_v2=${TOKEN_V2}`,
].filter(Boolean).join('; ');

const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';

function request(url) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: 'GET',
      headers: {
        'User-Agent': USER_AGENT,
        'Cookie': COOKIES,
        'Accept': 'application/json',
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(new Error(`Failed to parse JSON: ${data.substring(0, 200)}`));
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

async function getPosts(subreddit, limit = 10, sort = 'hot') {
  const url = `https://www.reddit.com/r/${subreddit}/${sort}.json?limit=${limit}`;
  const data = await request(url);
  
  if (data.error) {
    throw new Error(`Reddit error: ${data.error} - ${data.message}`);
  }

  const posts = data.data?.children || [];
  return posts.map(p => ({
    title: p.data.title,
    author: p.data.author,
    score: p.data.score,
    comments: p.data.num_comments,
    url: p.data.url,
    permalink: `https://reddit.com${p.data.permalink}`,
    created: new Date(p.data.created_utc * 1000).toISOString(),
    selftext: p.data.selftext?.substring(0, 300) || '',
  }));
}

async function search(query, subreddit = null, limit = 10) {
  let url = `https://www.reddit.com/search.json?q=${encodeURIComponent(query)}&limit=${limit}&sort=relevance&t=month`;
  if (subreddit) {
    url = `https://www.reddit.com/r/${subreddit}/search.json?q=${encodeURIComponent(query)}&limit=${limit}&restrict_sr=on&sort=relevance&t=month`;
  }
  
  const data = await request(url);
  
  if (data.error) {
    throw new Error(`Reddit error: ${data.error} - ${data.message}`);
  }

  const posts = data.data?.children || [];
  return posts.map(p => ({
    title: p.data.title,
    author: p.data.author,
    subreddit: p.data.subreddit,
    score: p.data.score,
    comments: p.data.num_comments,
    permalink: `https://reddit.com${p.data.permalink}`,
    created: new Date(p.data.created_utc * 1000).toISOString(),
  }));
}

async function getSubredditInfo(subreddit) {
  const url = `https://www.reddit.com/r/${subreddit}/about.json`;
  const data = await request(url);
  
  if (data.error) {
    throw new Error(`Reddit error: ${data.error} - ${data.message}`);
  }

  const d = data.data;
  return {
    name: d.display_name,
    title: d.title,
    subscribers: d.subscribers,
    active: d.accounts_active,
    description: d.public_description,
    created: new Date(d.created_utc * 1000).toISOString(),
  };
}

function formatPost(post, index) {
  let out = `${index}. ${post.title}\n`;
  out += `   👤 u/${post.author} | ⬆️ ${post.score} | 💬 ${post.comments}\n`;
  if (post.subreddit) out += `   📍 r/${post.subreddit}\n`;
  out += `   🔗 ${post.permalink}\n`;
  if (post.selftext) out += `   📝 ${post.selftext.substring(0, 150)}...\n`;
  return out;
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === 'help' || command === '--help') {
    console.log(`
reddit-cli - Reddit CLI using cookies

Usage:
  reddit-cli posts <subreddit> [limit] [sort]   Get posts from subreddit
  reddit-cli search <query> [--sub <subreddit>] Search Reddit
  reddit-cli info <subreddit>                   Get subreddit info
  reddit-cli check                              Check if cookies work

Environment:
  REDDIT_SESSION    reddit_session cookie value
  TOKEN_V2          token_v2 cookie value (optional)

Examples:
  reddit-cli posts programming 10 hot
  reddit-cli search "python tutorial" --sub learnpython
  reddit-cli info AskReddit
`);
    return;
  }

  try {
    if (command === 'check') {
      console.log('Checking cookies...');
      console.log(`REDDIT_SESSION: ${REDDIT_SESSION ? '✓ set' : '✗ not set'}`);
      console.log(`TOKEN_V2: ${TOKEN_V2 ? '✓ set' : '✗ not set'}`);
      
      // Try a simple request
      const info = await getSubredditInfo('reddit');
      console.log(`\n✓ Connection works! r/reddit has ${info.subscribers.toLocaleString()} subscribers`);
      return;
    }

    if (command === 'posts') {
      const subreddit = args[1];
      const limit = parseInt(args[2]) || 10;
      const sort = args[3] || 'hot';
      
      if (!subreddit) {
        console.error('Usage: reddit-cli posts <subreddit> [limit] [sort]');
        process.exit(1);
      }

      console.log(`📮 r/${subreddit} - ${sort} posts\n${'─'.repeat(50)}\n`);
      const posts = await getPosts(subreddit, limit, sort);
      posts.forEach((p, i) => console.log(formatPost(p, i + 1)));
      return;
    }

    if (command === 'search') {
      const query = args[1];
      let subreddit = null;
      let limit = 10;
      
      for (let i = 2; i < args.length; i++) {
        if (args[i] === '--sub' || args[i] === '-s') {
          subreddit = args[++i];
        } else if (!isNaN(args[i])) {
          limit = parseInt(args[i]);
        }
      }

      if (!query) {
        console.error('Usage: reddit-cli search <query> [--sub <subreddit>] [limit]');
        process.exit(1);
      }

      console.log(`🔍 Search: "${query}"${subreddit ? ` in r/${subreddit}` : ''}\n${'─'.repeat(50)}\n`);
      const posts = await search(query, subreddit, limit);
      posts.forEach((p, i) => console.log(formatPost(p, i + 1)));
      return;
    }

    if (command === 'info') {
      const subreddit = args[1];
      if (!subreddit) {
        console.error('Usage: reddit-cli info <subreddit>');
        process.exit(1);
      }

      const info = await getSubredditInfo(subreddit);
      console.log(`📮 r/${info.name}`);
      console.log(`   ${info.title}`);
      console.log(`   👥 ${info.subscribers.toLocaleString()} subscribers`);
      console.log(`   🟢 ${info.active?.toLocaleString() || '?'} online`);
      console.log(`   📅 Created: ${info.created}`);
      if (info.description) console.log(`   📝 ${info.description}`);
      return;
    }

    console.error(`Unknown command: ${command}`);
    process.exit(1);

  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
