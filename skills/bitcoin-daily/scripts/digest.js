#!/usr/bin/env node
/**
 * Bitcoin Dev Daily Digest
 * Fetches yesterday's bitcoindev mailing list posts + Bitcoin Core commits,
 * archives raw data, outputs a summary.
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const ARCHIVE_DIR = path.join(process.env.HOME, 'workspace', 'bitcoin-dev-archive');
const GROUPS_URL = 'https://groups.google.com/g/bitcoindev';
const GITHUB_API = 'https://api.github.com/repos/bitcoin/bitcoin/commits';

// ── Helpers ──

function fetch(url, headers = {}) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const options = {
      hostname: parsed.hostname,
      path: parsed.pathname + parsed.search,
      headers: {
        'User-Agent': 'BitcoinDevDigest/1.0',
        'Accept': 'text/html,application/json',
        ...headers
      }
    };
    https.get(options, (res) => {
      // Follow redirects
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return fetch(res.headers.location, headers).then(resolve).catch(reject);
      }
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, data }));
    }).on('error', reject);
  });
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function getYesterday() {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return d;
}

function formatDate(d) {
  return d.toISOString().split('T')[0];
}

// ── Mailing List ──

async function fetchMailingList() {
  // Use clawdbot's web_fetch which handles JS-rendered pages better
  try {
    const { execSync } = require('child_process');
    const raw = execSync(
      `node -e "
        const https = require('https');
        const url = 'https://groups.google.com/g/bitcoindev';
        https.get(url, {headers:{'User-Agent':'Mozilla/5.0'}}, res => {
          let d=''; res.on('data',c=>d+=c); res.on('end',()=>console.log(d));
        });
      "`,
      { encoding: 'utf8', timeout: 15000, maxBuffer: 1024 * 1024 }
    );

    const threads = [];
    const linkRegex = /\/g\/bitcoindev\/c\/([A-Za-z0-9_-]+)/g;
    let match;
    const seen = new Set();

    while ((match = linkRegex.exec(raw)) !== null) {
      const threadId = match[1];
      if (seen.has(threadId)) continue;
      seen.add(threadId);
      threads.push({
        id: threadId,
        url: `https://groups.google.com/g/bitcoindev/c/${threadId}`
      });
    }

    // Also try the gnusha.org public-inbox mirror which is plaintext
    if (threads.length === 0) {
      console.log('  Trying gnusha.org mirror...');
      const mirrorRes = await fetch('https://gnusha.org/pi/bitcoindev/');
      if (mirrorRes.status === 200) {
        const mirrorLinks = /href="([^"]+)"/g;
        while ((match = mirrorLinks.exec(mirrorRes.data)) !== null) {
          const href = match[1];
          if (href.includes('@') && !href.startsWith('http')) {
            threads.push({
              id: href.replace(/\//g, ''),
              url: `https://gnusha.org/pi/bitcoindev/${href}`
            });
          }
        }
      }
    }

    return threads;
  } catch (e) {
    console.error(`⚠️ Mailing list fetch error: ${e.message}`);
    return [];
  }
}

async function fetchThread(thread) {
  try {
    const res = await fetch(thread.url);
    if (res.status !== 200) return null;

    // Extract readable text content — strip HTML + Google Groups chrome
    let text = res.data
      .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
      .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<\/p>/gi, '\n\n')
      .replace(/<\/div>/gi, '\n')
      .replace(/<[^>]+>/g, ' ')
      .replace(/&nbsp;/g, ' ')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .replace(/&#x[0-9A-Fa-f]+;/g, '')
      .replace(/\n{3,}/g, '\n\n')
      .replace(/ {2,}/g, ' ')
      .trim();

    // Strip Google Groups UI boilerplate
    const boilerplate = [
      /Groups\s+Groups\s+Conversations.*?Sign in/gs,
      /Bitcoin Development Mailing List\s+Conversations\s+About/g,
      /Privacy.*?Terms/g,
      /Skip to first unread message/g,
      /Reply to author.*?Sign in to reply to author/g,
      /Forward\s+Sign in to forward/g,
      /Delete\s+You do not have permission.*?this group/g,
      /Copy link\s+Report message\s+Show original message/g,
      /Either email addresses are anonymous.*?original message/g,
      /Sign in to reply.*?to author/g,
      /unread,/g,
    ];
    for (const pat of boilerplate) {
      text = text.replace(pat, '');
    }
    text = text.replace(/\n{3,}/g, '\n\n').replace(/ {2,}/g, ' ').trim();

    // Extract title
    const titleMatch = res.data.match(/<title[^>]*>([^<]+)<\/title>/i);
    const title = titleMatch ? titleMatch[1].replace(' - Google Groups', '').trim() : thread.id;

    // Extract dates mentioned
    const datePatterns = text.match(/(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}(?:,\s*\d{4})?/gi) || [];

    return {
      ...thread,
      title,
      content: text.substring(0, 50000), // Cap content size
      dates: datePatterns,
      fetchedAt: new Date().toISOString()
    };
  } catch (e) {
    console.error(`⚠️ Failed to fetch thread ${thread.id}: ${e.message}`);
    return null;
  }
}

// ── GitHub Commits ──

async function fetchCommits(since) {
  const sinceISO = new Date(since).toISOString();
  const url = `${GITHUB_API}?sha=master&per_page=30&since=${sinceISO}`;
  const res = await fetch(url, {
    'Accept': 'application/vnd.github+json'
  });

  if (res.status !== 200) {
    console.error(`❌ Failed to fetch commits (${res.status})`);
    return [];
  }

  try {
    const commits = JSON.parse(res.data);
    return commits.map(c => ({
      sha: c.sha.substring(0, 8),
      fullSha: c.sha,
      message: c.commit.message,
      summary: c.commit.message.split('\n')[0],
      author: c.commit.author.name,
      date: c.commit.author.date,
      url: c.html_url
    }));
  } catch (e) {
    console.error(`❌ Failed to parse commits: ${e.message}`);
    return [];
  }
}

// ── Archive ──

function archiveData(date, data) {
  const dateStr = formatDate(date);
  const dir = path.join(ARCHIVE_DIR, dateStr);
  ensureDir(dir);

  // Archive mailing list threads
  if (data.threads && data.threads.length > 0) {
    const mlDir = path.join(dir, 'mailing-list');
    ensureDir(mlDir);

    for (const thread of data.threads) {
      if (!thread) continue;
      const filename = `${thread.id}.json`;
      fs.writeFileSync(path.join(mlDir, filename), JSON.stringify(thread, null, 2));
    }

    // Index file
    fs.writeFileSync(path.join(mlDir, '_index.json'), JSON.stringify(
      data.threads.filter(Boolean).map(t => ({
        id: t.id, title: t.title, url: t.url
      })), null, 2
    ));
  }

  // Archive commits
  if (data.commits && data.commits.length > 0) {
    fs.writeFileSync(path.join(dir, 'commits.json'), JSON.stringify(data.commits, null, 2));
  }

  // Archive the summary itself
  if (data.summary) {
    fs.writeFileSync(path.join(dir, 'summary.md'), data.summary);
  }

  console.log(`📁 Archived to ${dir}`);
  return dir;
}

// ── Summary Generation ──

function generateSummary(date, threads, commits) {
  const dateStr = formatDate(date);
  const lines = [];

  lines.push(`# Bitcoin Dev Digest — ${dateStr}`);
  lines.push('');

  // Mailing list section
  lines.push('## 📧 Mailing List Activity');
  lines.push('');

  const validThreads = threads.filter(Boolean);
  if (validThreads.length === 0) {
    lines.push('No new threads detected.');
  } else {
    for (let i = 0; i < validThreads.length; i++) {
      const t = validThreads[i];
      // Clean preview: strip boilerplate, get first meaningful paragraph
      const preview = t.content
        .replace(/\s+/g, ' ')
        .substring(0, 500)
        .trim();
      lines.push(`${i + 1}. **${t.title}** — ${preview}...`);
      lines.push(`   [Thread](${t.url})`);
      lines.push('');
    }
  }

  // Commits section
  lines.push('## 💻 Bitcoin Core Commits (master)');
  lines.push('');

  if (commits.length === 0) {
    lines.push('No new commits.');
  } else {
    for (const c of commits) {
      // Extract PR number for link
      const prMatch = c.summary.match(/#(\d+)/);
      const prLink = prMatch ? `[#${prMatch[1]}](https://github.com/bitcoin/bitcoin/pull/${prMatch[1]})` : '';
      lines.push(`- **${c.sha}** (${c.author}): ${c.summary}${prLink ? ' — ' + prLink : ''}`);
    }
  }

  lines.push('');
  lines.push(`---`);
  lines.push(`_Generated ${new Date().toISOString()}_`);

  return lines.join('\n');
}

// ── Main ──

async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'digest';

  switch (command) {
    case 'digest': {
      // Optional: pass a date like "2026-01-28"
      const targetDate = args[1] ? new Date(args[1] + 'T00:00:00') : getYesterday();
      const dateStr = formatDate(targetDate);

      console.log(`📰 Bitcoin Dev Digest for ${dateStr}`);
      console.log('='.repeat(40));

      // Fetch mailing list threads
      console.log('📧 Fetching mailing list...');
      const threadList = await fetchMailingList();
      console.log(`  Found ${threadList.length} threads on front page`);

      // Fetch each thread's content (limit to top 10 to avoid hammering)
      const threads = [];
      const fetchLimit = Math.min(threadList.length, 10);
      for (let i = 0; i < fetchLimit; i++) {
        process.stdout.write(`  Fetching ${i + 1}/${fetchLimit}...\r`);
        const thread = await fetchThread(threadList[i]);
        if (thread) threads.push(thread);
        // Be polite
        await new Promise(r => setTimeout(r, 500));
      }
      console.log(`  Fetched ${threads.length} threads`);

      // Fetch commits
      console.log('💻 Fetching Bitcoin Core commits...');
      const sinceDate = new Date(targetDate);
      sinceDate.setHours(0, 0, 0, 0);
      const commits = await fetchCommits(sinceDate);
      console.log(`  Found ${commits.length} commits`);

      // Generate summary
      const summary = generateSummary(targetDate, threads, commits);

      // Archive everything
      const archiveDir = archiveData(targetDate, { threads, commits, summary });

      console.log('');
      console.log(summary);

      return { threads, commits, summary, archiveDir };
    }

    case 'archive': {
      // List archived dates
      ensureDir(ARCHIVE_DIR);
      const dates = fs.readdirSync(ARCHIVE_DIR)
        .filter(d => /^\d{4}-\d{2}-\d{2}$/.test(d))
        .sort()
        .reverse();

      console.log(`📁 Archive (${dates.length} days)`);
      console.log('='.repeat(40));
      for (const d of dates) {
        const dir = path.join(ARCHIVE_DIR, d);
        const mlDir = path.join(dir, 'mailing-list');
        const threadCount = fs.existsSync(mlDir)
          ? fs.readdirSync(mlDir).filter(f => f.endsWith('.json') && !f.startsWith('_')).length
          : 0;
        const hasCommits = fs.existsSync(path.join(dir, 'commits.json'));
        console.log(`${d}: ${threadCount} threads${hasCommits ? ' + commits' : ''}`);
      }
      break;
    }

    case 'read': {
      // Read a specific day's summary
      const dateStr = args[1];
      if (!dateStr) {
        console.error('Usage: digest.js read <YYYY-MM-DD>');
        process.exit(1);
      }
      const summaryPath = path.join(ARCHIVE_DIR, dateStr, 'summary.md');
      if (!fs.existsSync(summaryPath)) {
        console.error(`❌ No archive for ${dateStr}`);
        process.exit(1);
      }
      console.log(fs.readFileSync(summaryPath, 'utf8'));
      break;
    }

    default:
      console.log(`
📰 Bitcoin Dev Daily Digest

Commands:
  digest [YYYY-MM-DD]    Fetch & summarize (default: yesterday)
  archive                List archived digests
  read <YYYY-MM-DD>      Read a past summary

Archive: ~/workspace/bitcoin-dev-archive/
`);
  }
}

main().catch(e => {
  console.error(`❌ ${e.message}`);
  process.exit(1);
});
