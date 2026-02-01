import type { ToolDef } from '../../../src/types';
import { z } from 'zod';

const ZOOMIN_API = 'https://servicenow-be-prod.servicenow.com/search';
const DEV_SEARCH_API = 'https://developer.servicenow.com/api/now/uxf/databroker/exec';
const DEV_SUGGEST_API = 'https://developer.servicenow.com/api/now/graphql';
const DEV_GUIDES_API = 'https://developer.servicenow.com/api/snc/v1/guides';
const DEV_SEARCH_DEFINITION_SYSID = '0cac8b3073ad101052c7d5fdbdf6a78a';
const DEV_SEARCH_CONTEXT_CONFIG_ID = '25aaf50afbd9b21043e2fe638eefdc19';
const DEFAULT_RELEASE = 'zurich';

// Convert Zoomin API URL to public docs.servicenow.com URL
function toPublicUrl(zoominUrl: string): string {
  return zoominUrl.replace('servicenow-be-prod.servicenow.com', 'docs.servicenow.com');
}

function cleanHtml(html: string): string {
  if (!html) return '';
  return html
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function extractUrl(value: unknown, depth: number = 0): string | null {
  if (depth > 4 || value == null) return null;
  if (typeof value === 'string') {
    if (value.startsWith('http')) return value;
    return null;
  }
  if (Array.isArray(value)) {
    for (const item of value) {
      const url = extractUrl(item, depth + 1);
      if (url) return url;
    }
    return null;
  }
  if (typeof value === 'object') {
    for (const [key, entry] of Object.entries(value)) {
      if (['url', 'link', 'href', 'targetUrl', 'recordUrl', 'record_url'].includes(key)) {
        const url = extractUrl(entry, depth + 1);
        if (url) return url;
      }
      const nested = extractUrl(entry, depth + 1);
      if (nested) return nested;
    }
  }
  return null;
}

function pickString(obj: Record<string, unknown>, keys: string[], fallback: string = ''): string {
  for (const key of keys) {
    const value = obj[key];
    if (typeof value === 'string' && value.trim()) {
      return value;
    }
  }
  return fallback;
}

interface SearchResult {
  title: string;
  link: string;
  snippet: string;
  publicationTitle: string;
  updatedOn: string;
  shortlabels?: {
    Products?: string;
    Versions?: string;
  };
}

interface SearchResponse {
  SearchResults: SearchResult[];
}

// Format a single search result
function formatResult(result: SearchResult, index: number): string {
  const date = new Date(result.updatedOn).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });

  let output = `${index + 1}. **${result.title}**\n`;
  output += `   ${result.snippet}\n`;
  output += `   📄 ${result.publicationTitle}`;
  if (result.shortlabels?.Versions) {
    output += ` (${result.shortlabels.Versions})`;
  }
  output += `\n   🔗 ${toPublicUrl(result.link)}\n`;
  output += `   📅 Updated: ${date}\n`;

  return output;
}

// Search ServiceNow documentation
async function searchDocs(query: string, limit: number = 10, version?: string): Promise<string> {
  try {
    let url = `${ZOOMIN_API}?q=${encodeURIComponent(query)}&publication=latest`;

    if (version) {
      url += `&version=${encodeURIComponent(version)}`;
    }

    const response = await fetch(url);
    if (!response.ok) {
      return `Error: Search failed with status ${response.status}`;
    }

    const data: SearchResponse = await response.json();
    const results = data.SearchResults?.slice(0, limit) || [];

    if (results.length === 0) {
      return `No results found for "${query}". Try different search terms.`;
    }

    let output = `🔍 **Search Results for "${query}"**\n`;
    output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;

    results.forEach((result, index) => {
      output += formatResult(result, index);
    });

    output += `\n*${results.length} result(s) found*`;

    return output;
  } catch (error) {
    console.error('ServiceNow docs search error:', error);
    return 'Error: Failed to search ServiceNow documentation';
  }
}

async function suggestDevDocs(term: string): Promise<string> {
  try {
    const payload = {
      operationName: 'snCxSearchInputDesktop',
      query:
        'query snCxSearchInputDesktop($searchContextConfigId:String!$term:String!){GlideSearch_Query{suggestions(searchContextConfigId:$searchContextConfigId searchTerm:$term){term data{name records{type columns{label fieldName value displayValue}}}}}}',
      variables: {
        searchContextConfigId: DEV_SEARCH_CONTEXT_CONFIG_ID,
        term,
      },
      nowUxInteraction: null,
      nowUiInteraction: 'ytiyoatnchw-2548',
      cacheable: false,
      extensions: {},
      queryContext: null,
    };

    const response = await fetch(DEV_SUGGEST_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      return `Error: Suggest failed with status ${response.status}`;
    }

    const data = await response.json();
    const suggestions = data?.data?.GlideSearch_Query?.suggestions?.data || [];
    const nameRecords = suggestions[1]?.records || [];

    const results: string[] = [];
    for (const record of nameRecords) {
      const columns = record?.columns || [];
      for (const col of columns) {
        if (col?.fieldName === 'name' && col?.displayValue) {
          const label = String(col.displayValue).replace(/<[^>]+>/g, '').trim();
          if (label && !results.includes(label)) {
            results.push(label);
          }
        }
      }
    }

    if (results.length === 0) {
      return `No suggestions found for "${term}".`;
    }

    let output = `🔎 **Developer Docs Suggestions for "${term}"**\n`;
    output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
    results.slice(0, 10).forEach((item, index) => {
      output += `${index + 1}. ${item}\n`;
    });
    return output;
  } catch (error) {
    console.error('ServiceNow dev docs suggest error:', error);
    return 'Error: Failed to fetch developer doc suggestions';
  }
}

async function getDevGuide(path: string, release: string = DEFAULT_RELEASE): Promise<string> {
  try {
    // Clean up path - remove leading/trailing slashes
    const cleanPath = path.replace(/^\/+|\/+$/g, '');
    const url = `${DEV_GUIDES_API}/${release}/${cleanPath}`;

    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0',
      },
    });

    if (!response.ok) {
      return `Error: Guide not found (status ${response.status})`;
    }

    const data = await response.json();
    const result = data?.result;

    if (!result || result.status === 'error') {
      return `Guide not found: ${path}`;
    }

    const title = result.title || 'Guide';
    const description = result.description || '';
    const kbText = result.kb_text || '';
    
    // Clean HTML from kb_text
    const content = kbText ? cleanHtml(kbText) : description;
    const guideUrl = `https://developer.servicenow.com/dev.do#!/guides/${release}/${cleanPath}`;

    let output = `📚 **${title}**\n`;
    output += `🔗 ${guideUrl}\n\n`;
    if (content) {
      output += content.slice(0, 4000);
    }
    return output;
  } catch (error) {
    console.error('ServiceNow dev guide error:', error);
    return 'Error: Failed to fetch developer guide';
  }
}

async function searchDevDocsWithUrls(query: string, limit: number = 10): Promise<string> {
  try {
    const payload = [
      {
        definitionSysId: DEV_SEARCH_DEFINITION_SYSID,
        type: 'GRAPHQL',
        inputValues: {
          searchContextConfigId: { type: 'JSON_LITERAL', value: DEV_SEARCH_CONTEXT_CONFIG_ID },
          searchTerm: { type: 'JSON_LITERAL', value: query },
        },
      },
    ];

    const response = await fetch(DEV_SEARCH_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      return `Error: Search failed with status ${response.status}`;
    }

    const data = await response.json();
    const items =
      (data?.result?.[0]?.executionResult?.searchMetadata?.searchResultMetadata?.searchAnalyticsPayload?.searchResults ||
        []) as Array<Record<string, unknown>>;

    if (!items.length) {
      return `No results found for "${query}". Try different search terms.`;
    }

    const results = items
      .map((item) => {
        const recordId = item.recordId as string || '';
        const tableName = item.tableName as string || '';
        let url = '';
        
        if (tableName === 'dev_reference_content' && recordId) {
          url = `https://developer.servicenow.com/dev.do#!/reference/api/${recordId}`;
        } else if (recordId) {
          url = `https://developer.servicenow.com/dev.do#!/search?query=${encodeURIComponent(query)}`;
        }
        
        const title = pickString(item, ['title', 'name', 'label']) || recordId;
        const snippet = pickString(item, ['snippet', 'summary']);
        return { title, url, snippet, tableName };
      })
      .slice(0, limit);

    let output = `🔍 **Developer Docs Results for "${query}"**\n`;
    output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;

    results.forEach((result, index) => {
      output += `${index + 1}. **${result.title}**\n`;
      if (result.snippet) output += `   ${result.snippet}\n`;
      if (result.tableName) output += `   📁 ${result.tableName}\n`;
      if (result.url) output += `   🔗 ${result.url}\n`;
      output += '\n';
    });

    output += `*${results.length} result(s) found*\n`;
    output += `\n_Note: API Reference pages require browser access. Use the URLs above._`;

    return output;
  } catch (error) {
    console.error('ServiceNow dev docs search error:', error);
    return 'Error: Failed to search ServiceNow developer documentation';
  }
}

// Fetch full article content (simplified - returns metadata and attempts to extract main content)
async function getArticle(url: string): Promise<string> {
  try {
    // Fetch from Zoomin API with proper headers to get JSON with full HTML
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json',
      },
      redirect: 'follow',
    });

    if (!response.ok) {
      return `Error: Failed to fetch article (status ${response.status})`;
    }

    const data = await response.json();

    // Extract content from the JSON response
    const html = data.html || data.content || '';
    const title = data.title || 'ServiceNow Documentation';

    if (!html) {
      return `Error: No content found in article`;
    }

    // Parse the HTML article content
    const articleMatch = html.match(/<article[^>]*class="[^"]*dita[^"]*"[^>]*>([\s\S]*?)<\/article>/i) ||
                        html.match(/<div[^>]*class="[^"]*content[^"]*"[^>]*>([\s\S]*?)<\/div>/i) ||
                        html.match(/<main[^>]*>([\s\S]*?)<\/main>/i);

    let content = '';
    if (articleMatch) {
      content = articleMatch[1].replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
                               .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
                               .replace(/<[^>]+>/g, ' ')
                               .replace(/\s+/g, ' ')
                               .replace(/&nbsp;/g, ' ')
                               .replace(/&amp;/g, '&')
                               .replace(/&lt;/g, '<')
                               .replace(/&gt;/g, '>')
                               .trim();
    }

    // Limit content length
    if (content.length > 3000) {
      content = content.substring(0, 3000) + '...';
    }

    let output = `📄 **${title}**\n`;
    output += `🔗 ${toPublicUrl(url)}\n\n`;

    if (content) {
      output += `${content}`;
    } else {
      output += `_Could not extract article content_`;
    }

    return output;
  } catch (error) {
    console.error('ServiceNow article fetch error:', error);
    return 'Error: Failed to fetch article';
  }
}

// List available documentation versions
async function listVersions(): Promise<string> {
  // ServiceNow versions (ordered by release date, newest first)
  const versions = [
    { name: 'Zurich', code: 'zurich', status: 'Latest' },
    { name: 'Yokohama', code: 'yokohama', status: 'Previous' },
    { name: 'Washington DC', code: 'washingtondc', status: 'Older' },
    { name: 'Xanadu', code: 'xanadu', status: 'Legacy' },
  ];

  let output = `📚 **ServiceNow Documentation Versions**\n`;
  output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;

  versions.forEach((v) => {
    const icon = v.status === 'Latest' ? '✅' : v.status === 'Previous' ? '📗' : '📙';
    output += `${icon} ${v.name} (${v.code})\n`;
  });

  output += `\n_Search results default to latest version unless specified._`;

  return output;
}

// Get the latest release notes (searches all versions and returns most recent)
async function getLatestReleaseNotes(): Promise<string> {
  const versions = ['zurich', 'yokohama', 'washingtondc'];
  const versionNames: Record<string, string> = {
    'zurich': 'Zurich',
    'yokohama': 'Yokohama',
    'washingtondc': 'Washington DC'
  };

  let latestResult: SearchResult | null = null;
  let latestVersion = '';

  // Search release notes for each version
  for (const version of versions) {
    try {
      const url = `${ZOOMIN_API}?q=release%20notes%20${version}&limit=3`;
      const response = await fetch(url);
      if (!response.ok) continue;

      const data: SearchResponse = await response.json();
      const results = data.SearchResults || [];

      for (const result of results) {
        const resultDate = new Date(result.updatedOn);
        if (!latestResult || resultDate > new Date(latestResult.updatedOn)) {
          latestResult = result;
          latestVersion = versionNames[version];
        }
      }
    } catch (error) {
      console.error(`Error checking ${version}:`, error);
    }
  }

  if (!latestResult) {
    return 'Error: Could not find release notes for any version';
  }

  const date = new Date(latestResult.updatedOn).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  let output = `📦 **Latest ServiceNow Release Notes**\n`;
  output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
  output += `🎯 **${latestVersion}** (Latest Release)\n\n`;
  output += `📄 ${latestResult.title}\n`;
  output += `${latestResult.snippet}\n\n`;
  output += `🔗 ${toPublicUrl(latestResult.link)}\n`;
  output += `📅 Updated: ${date}`;

  return output;
}

// Tool definitions
export const servicenow_search: ToolDef = {
  name: 'servicenow_search',
  description: 'Search ServiceNow documentation for API references, scripting guides, and platform features',
  schema: z.object({
    query: z.string().describe('Search terms (e.g., GlideRecord, business rule)'),
    limit: z.number().default(10).describe('Maximum results to return'),
    version: z.string().optional().describe('Filter by version (e.g., Washington DC, Zurich)'),
  }),
  execute: async (args: unknown) => {
    const { query, limit, version } = args as { query: string; limit?: number; version?: string };
    return searchDocs(query, limit, version);
  },
};

export const servicenow_get_article: ToolDef = {
  name: 'servicenow_get_article',
  description: 'Fetch the full content of a ServiceNow documentation article',
  schema: z.object({
    url: z.string().describe('The article URL from search results'),
  }),
  execute: async (args: unknown) => {
    const { url } = args as { url: string };
    return getArticle(url);
  },
};

export const servicenow_list_versions: ToolDef = {
  name: 'servicenow_list_versions',
  description: 'List available ServiceNow documentation versions',
  schema: z.object({}),
  execute: async () => listVersions(),
};

export const servicenow_latest_release: ToolDef = {
  name: 'servicenow_latest_release',
  description: 'Get release notes for the latest ServiceNow version (automatically finds Zurich, Yokohama, or Washington DC)',
  schema: z.object({}),
  execute: async () => getLatestReleaseNotes(),
};

export const servicenow_dev_suggest: ToolDef = {
  name: 'servicenow_dev_suggest',
  description: 'Get autocomplete suggestions from ServiceNow Developer Documentation',
  schema: z.object({
    term: z.string().describe('Partial search term (e.g., Glide, openFrame, spContext)')
  }),
  execute: async (args: unknown) => {
    const { term } = args as { term: string };
    return suggestDevDocs(term);
  },
};

export const servicenow_dev_search: ToolDef = {
  name: 'servicenow_dev_search',
  description: 'Search ServiceNow Developer Documentation (APIs, guides, references). Returns URLs to reference pages.',
  schema: z.object({
    query: z.string().describe('Search terms (e.g., openFrameAPI, ScriptLoader, spContextManager)'),
    limit: z.number().default(10).describe('Maximum results to return'),
  }),
  execute: async (args: unknown) => {
    const { query, limit } = args as { query: string; limit?: number };
    return searchDevDocsWithUrls(query, limit);
  },
};

export const servicenow_dev_guide: ToolDef = {
  name: 'servicenow_dev_guide',
  description: 'Fetch a ServiceNow Developer Guide by path. Works for PDI guides, developer program docs, etc.',
  schema: z.object({
    path: z.string().describe('Guide path (e.g., developer-program/getting-instance-assistance, pdi-guide/requesting-an-instance)'),
    release: z.string().default(DEFAULT_RELEASE).describe('Release version (default: zurich)'),
  }),
  execute: async (args: unknown) => {
    const { path, release } = args as { path: string; release?: string };
    return getDevGuide(path, release);
  },
};

export const tools = [
  servicenow_search,
  servicenow_get_article,
  servicenow_list_versions,
  servicenow_latest_release,
  servicenow_dev_suggest,
  servicenow_dev_search,
  servicenow_dev_guide,
];
