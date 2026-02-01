#!/usr/bin/env node
/**
 * Process pending bookmarks into markdown files
 * - Expands t.co links
 * - Categorizes URLs
 * - Generates AI summary
 * - Writes to X-knowledge/{category}/{slug}.md
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const os = require('os');
const { loadPending, clearPending, markProcessed } = require('./lib/state.cjs');
const { categorize } = require('./lib/categorize.cjs');

// Resolve OpenClaw workspace directory
// Priority: env var > ~/clawd (legacy) > ~/.openclaw/workspace (new default)
function resolveOpenClawWorkspace() {
  // Explicit override
  if (process.env.OPENCLAW_WORKSPACE) {
    return process.env.OPENCLAW_WORKSPACE;
  }
  
  const home = os.homedir();
  
  // Legacy: ~/clawd (old name, no dot)
  const legacyWorkspace = path.join(home, 'clawd');
  if (fs.existsSync(legacyWorkspace)) {
    return legacyWorkspace;
  }
  
  // New default: ~/.openclaw/workspace (or workspace-<profile>)
  const profile = process.env.OPENCLAW_PROFILE?.trim();
  const workspaceName = profile && profile.toLowerCase() !== 'default' 
    ? `workspace-${profile}` 
    : 'workspace';
  return path.join(home, '.openclaw', workspaceName);
}

const WORKSPACE_DIR = resolveOpenClawWorkspace();
const KNOWLEDGE_DIR = path.join(WORKSPACE_DIR, 'X-knowledge');

/**
 * Expand a t.co shortened URL
 * @param {string} url - The URL to expand
 * @returns {Promise<string>} - The expanded URL
 */
function expandUrl(url) {
  return new Promise((resolve) => {
    if (!url.includes('t.co/')) {
      resolve(url);
      return;
    }
    
    const req = https.get(url, { method: 'HEAD' }, (res) => {
      resolve(res.headers.location || url);
    });
    
    req.on('error', () => resolve(url));
    req.setTimeout(10000, () => {
      req.destroy();
      resolve(url);
    });
  });
}

/**
 * Generate slug from URL or title
 * @param {string} url - The URL
 * @param {string} title - The bookmark title
 * @returns {string} - Safe filename slug
 */
function generateSlug(url, title) {
  if (title) {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')
      .slice(0, 50);
  }
  
  try {
    const urlObj = new URL(url);
    const pathSlug = urlObj.pathname
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')
      .slice(0, 40);
    return pathSlug || urlObj.hostname.replace(/\./g, '-');
  } catch {
    return 'bookmark-' + Date.now();
  }
}

/**
 * Generate title, summary, and tags using AI (OpenAI-compatible API)
 * @param {string} url - The URL to analyze
 * @param {string} originalText - Original tweet text
 * @returns {Promise<Object>} - { title, summary, tags }
 */
async function generateMetadata(url, originalText) {
  // Check for OpenAI API key
  const apiKey = process.env.OPENAI_API_KEY;
  
  // Extract description from text (remove URL if it's the whole text)
  const description = originalText?.startsWith('http') 
    ? 'Bookmark from X'
    : (originalText || 'Bookmark from X');
  
  if (!apiKey) {
    // Fallback: use URL hostname as title
    try {
      const urlObj = new URL(url);
      return {
        title: urlObj.hostname,
        summary: description,
        tags: []
      };
    } catch {
      return {
        title: 'Untitled Bookmark',
        summary: description,
        tags: []
      };
    }
  }
  
  const prompt = `Analyze this URL and the tweet that shared it. Generate a concise title (max 60 chars), a 2-3 sentence summary, and 3-5 relevant tags.

URL: ${url}
Tweet: ${originalText || 'N/A'}

Respond in JSON format:
{
  "title": "...",
  "summary": "...",
  "tags": ["tag1", "tag2", "tag3"]
}`;

  try {
    const result = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [{ role: 'user', content: prompt }],
        response_format: { type: 'json_object' }
      })
    });
    
    const data = await result.json();
    const content = JSON.parse(data.choices[0].message.content);
    
    return {
      title: content.title || 'Untitled',
      summary: content.summary || '',
      tags: content.tags || []
    };
  } catch (e) {
    console.warn('AI generation failed:', e.message);
    return {
      title: 'Untitled Bookmark',
      summary: originalText || `Bookmarked link: ${url}`,
      tags: []
    };
  }
}

/**
 * Write markdown file for a bookmark
 * @param {Object} bookmark - The bookmark object
 * @param {string} category - The category
 * @param {Object} metadata - { title, summary, tags }
 */
function writeMarkdown(bookmark, category, metadata) {
  const categoryDir = path.join(KNOWLEDGE_DIR, category);
  fs.mkdirSync(categoryDir, { recursive: true });
  
  const slug = generateSlug(bookmark.url, metadata.title);
  const filename = path.join(categoryDir, `${slug}.md`);
  
  const dateStr = new Date().toISOString().split('T')[0];
  
  const frontmatter = `---
title: "${metadata.title.replace(/"/g, '\\"')}"
type: ${category}
date_archived: ${dateStr}
source_tweet: https://x.com/i/web/status/${bookmark.id}
link: ${bookmark.url}
tags: [${metadata.tags.map(t => `"${t}"`).join(', ')}]
---

${metadata.summary}
`;
  
  // Handle duplicates by adding number suffix
  let finalFilename = filename;
  let counter = 1;
  while (fs.existsSync(finalFilename)) {
    const ext = path.extname(filename);
    const base = filename.slice(0, -ext.length);
    finalFilename = `${base}-${counter}${ext}`;
    counter++;
  }
  
  fs.writeFileSync(finalFilename, frontmatter);
  return finalFilename;
}

/**
 * Extract URL from bookmark (bird CLI uses 'text' field for URL)
 * @param {Object} bookmark - The bookmark object
 * @returns {string} - The URL
 */
function extractUrl(bookmark) {
  // bird CLI returns URL in 'text' field
  if (bookmark.url) return bookmark.url;
  if (bookmark.text && bookmark.text.startsWith('http')) return bookmark.text;
  // Try to extract URL from text
  const urlMatch = bookmark.text?.match(/(https?:\/\/[^\s]+)/);
  return urlMatch ? urlMatch[1] : '';
}

/**
 * Main processing function
 */
async function main() {
  console.log('📦 Processing bookmarks...\n');
  
  const pending = loadPending();
  if (pending.length === 0) {
    console.log('No pending bookmarks to process.');
    return;
  }
  
  const stats = {
    total: pending.length,
    processed: 0,
    byCategory: {}
  };
  
  const processedIds = [];
  
  for (const bookmark of pending) {
    try {
      // Extract URL from bookmark (bird uses 'text' field)
      const rawUrl = extractUrl(bookmark);
      if (!rawUrl) {
        console.error(`  ✗ No URL found in bookmark ${bookmark.id}`);
        continue;
      }
      
      // Expand t.co links
      const expandedUrl = await expandUrl(rawUrl);
      bookmark.url = expandedUrl;
      
      // Categorize
      const category = categorize(expandedUrl);
      stats.byCategory[category] = (stats.byCategory[category] || 0) + 1;
      
      // Generate metadata with AI
      const metadata = await generateMetadata(expandedUrl, bookmark.text);
      
      // Write markdown
      const filepath = writeMarkdown(bookmark, category, metadata);
      console.log(`  ✓ [${category}] ${metadata.title}`);
      console.log(`    → ${filepath}`);
      
      processedIds.push(bookmark.id);
      stats.processed++;
    } catch (e) {
      console.error(`  ✗ Failed to process bookmark ${bookmark.id}:`, e.message);
    }
  }
  
  // Update state
  markProcessed(processedIds);
  clearPending();
  
  // Output summary
  console.log(`\n✓ Archived ${stats.processed}/${stats.total} bookmarks`);
  
  const categoryBreakdown = Object.entries(stats.byCategory)
    .map(([cat, count]) => `${count} ${cat}`)
    .join(', ');
  
  if (categoryBreakdown) {
    console.log(`  → ${categoryBreakdown}`);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { processBookmarks: main, expandUrl, generateMetadata, writeMarkdown };
