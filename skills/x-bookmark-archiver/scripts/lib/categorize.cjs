/**
 * URL categorization based on domain patterns
 */

const CATEGORIES = {
  tools: ['github.com', 'gitlab.com', 'github.io', 'huggingface.co', 'replicate.com', 'vercel.com', 'vercel.app', 'npmjs.com', 'pypi.org', 'raw.githubusercontent.com'],
  articles: ['medium.com', 'substack.com', 'dev.to', 'hashnode.dev', 'x.com/i/article', 'blog.', 'towardsdatascience.com'],
  videos: ['youtube.com', 'youtu.be', 'vimeo.com', 'twitch.tv'],
  research: ['arxiv.org', 'paperswithcode.com', 'semanticscholar.org', 'researchgate.net', 'dl.acm.org', 'ieee.org'],
  news: ['techcrunch.com', 'theverge.com', 'hn.algolia.com', 'news.ycombinator.com', 'wired.com', 'arstechnica.com']
};

/**
 * Categorize a URL based on its domain
 * @param {string} url - The URL to categorize
 * @returns {string} - Category name or 'bookmarks' as fallback
 */
function categorize(url) {
  const lowerUrl = url.toLowerCase();
  for (const [cat, domains] of Object.entries(CATEGORIES)) {
    if (domains.some(d => lowerUrl.includes(d))) return cat;
  }
  return 'bookmarks'; // fallback
}

/**
 * Get all available categories
 * @returns {string[]} - List of category names
 */
function getCategories() {
  return [...Object.keys(CATEGORIES), 'bookmarks'];
}

module.exports = { categorize, getCategories, CATEGORIES };
