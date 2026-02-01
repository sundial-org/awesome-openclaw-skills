/**
 * Luma Web Scraper
 * Scrapes event data from lu.ma pages
 */

import * as cheerio from 'cheerio';
import { LumaEvent, Attendee, Location } from './index';
import { fetchWithBackoff, extractJsonScript, findFirstObjectWithKeys } from './utils';

const LUMA_BASE_URL = 'https://lu.ma';
const USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36';

const LUMA_BACKOFF_OPTIONS = {
  minIntervalMs: 1000,
  maxRetries: 4,
  baseDelayMs: 500,
  maxDelayMs: 8000,
  retryOnStatuses: [429, 500, 502, 503, 504],
};

/**
 * Fetch with rate limiting
 */
async function fetchHtml(url: string, cookies?: string, options: RequestInit = {}): Promise<string> {
  const headers: Record<string, string> = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
  };
  
  if (cookies) {
    headers['Cookie'] = cookies;
  }
  
  const response = await fetchWithBackoff(
    url,
    {
      ...options,
      headers: {
        ...headers,
        ...(options.headers || {}),
      },
    },
    LUMA_BACKOFF_OPTIONS
  );
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  
  return response.text();
}

function selectText($: cheerio.CheerioAPI, selectors: string[], label: string): string {
  for (const selector of selectors) {
    const text = $(selector).first().text().trim();
    if (text) {
      return text;
    }
  }
  console.warn(`[luma] Selector failed for ${label}: ${selectors.join(', ')}`);
  return '';
}

function selectAttr(
  $: cheerio.CheerioAPI,
  selectors: string[],
  attr: string,
  label: string,
  warnOnFail: boolean = true
): string | undefined {
  for (const selector of selectors) {
    const value = $(selector).first().attr(attr);
    if (value) {
      return value.trim();
    }
  }
  if (warnOnFail) {
    console.warn(`[luma] Selector failed for ${label}: ${selectors.join(', ')}`);
  }
  return undefined;
}

function getString(value: unknown): string | undefined {
  if (typeof value === 'string') {
    const trimmed = value.trim();
    return trimmed ? trimmed : undefined;
  }
  return undefined;
}

function extractEventFromNextData(nextData: unknown, slug: string): Partial<LumaEvent> | null {
  const candidate = findFirstObjectWithKeys(
    nextData,
    ['slug'],
    (obj) => {
      const slugValue = getString(obj.slug);
      const hasTitle = Boolean(getString(obj.title) || getString(obj.name) || getString(obj.event_name));
      return slugValue === slug && hasTitle;
    }
  );

  if (!candidate) {
    return null;
  }

  const title = getString(candidate.title) || getString(candidate.name) || getString(candidate.event_name);
  const startTime = getString(candidate.start_time)
    || getString(candidate.start_at)
    || getString(candidate.start);
  const endTime = getString(candidate.end_time) || getString(candidate.end_at) || getString(candidate.end);
  const timezone = getString(candidate.timezone) || getString(candidate.tz);
  const hostName = getString(candidate.host_name) || getString(candidate.host) || getString(candidate.organizer_name);
  const description = getString(candidate.description) || getString(candidate.summary) || getString(candidate.about);

  const locationCandidate = (candidate.location || candidate.place || candidate.venue) as Record<string, unknown> | undefined;
  const locationName = locationCandidate ? getString(locationCandidate.name) : undefined;
  const locationAddress = locationCandidate ? getString(locationCandidate.address) : undefined;
  const isVirtual = Boolean(
    candidate.is_virtual
    || candidate.virtual
    || getString(candidate.event_type) === 'virtual'
    || getString(candidate.location_type) === 'virtual'
  );

  return {
    slug,
    title: title || '',
    description: description || '',
    start_time: startTime || '',
    end_time: endTime || '',
    timezone: timezone || 'America/Los_Angeles',
    location: {
      type: isVirtual ? 'virtual' : 'physical',
      name: locationName,
      address: locationAddress,
    },
    host_name: hostName,
  };
}

function findEventList(value: unknown): Array<Record<string, unknown>> | null {
  if (!value || typeof value !== 'object') {
    return null;
  }

  if (Array.isArray(value)) {
    const isEventList = value.length > 0 && value.every(item => {
      return item && typeof item === 'object'
        && ('slug' in item)
        && (typeof (item as Record<string, unknown>).slug === 'string');
    });
    if (isEventList) {
      return value as Array<Record<string, unknown>>;
    }
  }

  const entries = Array.isArray(value)
    ? value
    : Object.values(value as Record<string, unknown>);

  for (const entry of entries) {
    const found = findEventList(entry);
    if (found) {
      return found;
    }
  }

  return null;
}

/**
 * Scrape event details from event page
 */
export async function scrapeEvent(slug: string): Promise<LumaEvent | null> {
  try {
    const url = `${LUMA_BASE_URL}/${slug}`;
    const html = await fetchHtml(url);
    const $ = cheerio.load(html);
    
    // Try multiple selectors (Luma's structure may vary)
    const title = selectText(
      $,
      ['h1', '[data-testid="event-title"]', 'title'],
      'event title'
    ).split('|')[0].trim();
    
    if (!title) {
      console.warn(`[luma] No title found for event ${slug}`);
    }
    
    // Extract date/time from meta tags or page content
    const dateText = selectAttr(
      $,
      ['meta[property="event:start_time"]', 'meta[name="event:start_time"]'],
      'content',
      'event time (meta)'
    ) || selectText($, ['[data-testid="event-time"]', '[class*="event-time"]'], 'event time');
    
    // Extract location
    const locationText = selectText(
      $,
      ['[data-testid="event-location"]', 'address', '[class*="event-location"]'],
      'event location'
    );
    
    const isVirtual = 
      html.includes('virtual') || 
      html.includes('online') ||
      $('[data-testid="virtual-badge"]').length > 0;
    
    // Extract host info
    const hostName = selectText(
      $,
      ['[data-testid="host-name"]', 'a[href*="/u/"]', '[class*="host"]'],
      'host name'
    ) || 'Unknown Host';
    
    // Extract description
    const description = selectText(
      $,
      ['[data-testid="event-description"]', '[class*="event-description"]'],
      'event description'
    ) || selectAttr($, ['meta[name="description"]', 'meta[property="og:description"]'], 'content', 'event description');
    
    // Extract cover image
    const coverImage = selectAttr(
      $,
      ['meta[property="og:image"]'],
      'content',
      'cover image',
      false
    ) || selectAttr(
      $,
      ['img[data-testid="cover-image"]', 'img[class*="cover"]'],
      'src',
      'cover image'
    );

    const nextData = extractJsonScript(html, '__NEXT_DATA__');
    const nextEvent = nextData ? extractEventFromNextData(nextData, slug) : null;

    const resolvedTitle = title || nextEvent?.title || '';
    if (!resolvedTitle) {
      return null;
    }
    
    return {
      slug,
      title: resolvedTitle,
      description: description || nextEvent?.description || '',
      start_time: dateText || nextEvent?.start_time || '',
      end_time: nextEvent?.end_time || '',
      timezone: nextEvent?.timezone || 'America/Los_Angeles',
      location: {
        type: nextEvent?.location?.type || (isVirtual ? 'virtual' : 'physical'),
        name: nextEvent?.location?.name,
        address: locationText || nextEvent?.location?.address,
      },
      cover_image: coverImage || nextEvent?.cover_image,
      status: 'published',
      host_id: '',
      host_name: hostName || nextEvent?.host_name,
      url,
    };
  } catch (error) {
    console.error(`Error scraping event ${slug}:`, error);
    return null;
  }
}

/**
 * Scrape events from discover page
 */
export async function scrapeDiscover(params: {
  lat?: number;
  lng?: number;
  query?: string;
}): Promise<LumaEvent[]> {
  try {
    const url = new URL(`${LUMA_BASE_URL}/discover`);
    
    if (params.lat && params.lng) {
      url.searchParams.set('geo', `${params.lat},${params.lng}`);
    }
    
    if (params.query) {
      url.searchParams.set('q', params.query);
    }
    
    const html = await fetchHtml(url.toString());
    const $ = cheerio.load(html);
    
    const events: LumaEvent[] = [];
    
    // Category slugs and city links to filter out (nav links, not events)
    const categoryPaths = new Set([
      'tech', 'food', 'ai', 'arts', 'climate', 'fitness', 'wellness', 'crypto',
      'music', 'sports', 'gaming', 'fashion', 'health', 'business', 'education',
      'networking', 'social', 'community', 'startup', 'design', 'marketing',
      // Common city/location slugs
      'atlanta', 'austin', 'boston', 'chicago', 'dallas', 'denver', 'houston',
      'los-angeles', 'miami', 'new-york', 'nyc', 'philadelphia', 'phoenix',
      'portland', 'san-diego', 'san-francisco', 'seattle', 'washington-dc',
      'london', 'paris', 'berlin', 'tokyo', 'singapore', 'toronto', 'vancouver',
      'sydney', 'melbourne', 'dubai', 'amsterdam', 'barcelona', 'mumbai',
      'calgary', 'las-vegas', 'mexico-city', 'montreal', 'ottawa', 'san-jose',
      'bay-area', 'silicon-valley', 'brooklyn', 'manhattan', 'la', 'sf',
      'hong-kong', 'shanghai', 'beijing', 'seoul', 'taipei', 'jakarta',
      'bangkok', 'kuala-lumpur', 'ho-chi-minh', 'hanoi', 'manila', 'delhi',
      'bangalore', 'hyderabad', 'chennai', 'pune', 'kolkata', 'tel-aviv',
      'jerusalem', 'cairo', 'johannesburg', 'cape-town', 'lagos', 'nairobi',
      'sao-paulo', 'rio', 'buenos-aires', 'santiago', 'bogota', 'lima', 'medellin',
    ]);

    // Track seen slugs to avoid duplicates
    const seenSlugs = new Set<string>();

    // Try to find event cards
    $('a[href^="/"]').each((i, el) => {
      const href = $(el).attr('href');
      if (!href || href.startsWith('/discover') || href.startsWith('/home')) {
        return;
      }
      
      const slug = href.replace('/', '').split('?')[0]; // Remove query params
      if (slug.includes('/') || slug.length < 3) {
        return;
      }

      // Skip category links and duplicates
      if (categoryPaths.has(slug.toLowerCase()) || seenSlugs.has(slug)) {
        return;
      }
      
      const title = $(el).find('h3, h4, [class*="title"]').first().text().trim();
      if (!title) {
        return;
      }

      // Skip if title matches a category name (additional filter)
      if (categoryPaths.has(title.toLowerCase().replace(/[^a-z]/g, ''))) {
        return;
      }

      seenSlugs.add(slug);
      events.push({
        slug,
        title,
        description: '',
        start_time: '',
        end_time: '',
        timezone: 'America/Los_Angeles',
        location: { type: 'physical' },
        status: 'published',
        host_id: '',
        host_name: '',
        url: `${LUMA_BASE_URL}/${slug}`,
      });
    });

    if (events.length === 0) {
      console.warn('[luma] No events found with primary selectors on discover page. Trying Next.js data...');
      const nextData = extractJsonScript(html, '__NEXT_DATA__');
      const eventList = nextData ? findEventList(nextData) : null;
      if (eventList) {
        for (const item of eventList) {
          const slugValue = getString(item.slug);
          const titleValue = getString(item.title) || getString(item.name) || getString(item.event_name);
          if (!slugValue || !titleValue) continue;
          events.push({
            slug: slugValue,
            title: titleValue,
            description: '',
            start_time: getString(item.start_time) || getString(item.start_at) || '',
            end_time: getString(item.end_time) || getString(item.end_at) || '',
            timezone: getString(item.timezone) || 'America/Los_Angeles',
            location: { type: 'physical' },
            status: 'published',
            host_id: '',
            host_name: getString(item.host_name) || '',
            url: `${LUMA_BASE_URL}/${slugValue}`,
          });
        }
      } else {
        console.warn('[luma] Next.js data did not include discover events list.');
      }
    }

    return events;
  } catch (error) {
    console.error('Error scraping discover page:', error);
    return [];
  }
}

/**
 * Scrape user's RSVP'd events (requires auth)
 */
export async function scrapeMyEvents(cookies: string): Promise<LumaEvent[]> {
  try {
    const html = await fetchHtml(`${LUMA_BASE_URL}/home`, cookies);
    const $ = cheerio.load(html);
    
    const events: LumaEvent[] = [];
    
    // Parse upcoming events section
    $('a[href^="/"]').each((i, el) => {
      const href = $(el).attr('href');
      if (!href) return;
      
      const slug = href.replace('/', '');
      const title = $(el).text().trim();
      
      if (title && slug && !slug.includes('/')) {
        events.push({
          slug,
          title,
          description: '',
          start_time: '',
          end_time: '',
          timezone: 'America/Los_Angeles',
          location: { type: 'physical' },
          status: 'published',
          host_id: '',
          host_name: '',
          url: `${LUMA_BASE_URL}/${slug}`,
        });
      }
    });
    
    if (events.length === 0) {
      console.warn('[luma] No events found with primary selectors on home page. Trying Next.js data...');
      const nextData = extractJsonScript(html, '__NEXT_DATA__');
      const eventList = nextData ? findEventList(nextData) : null;
      if (eventList) {
        for (const item of eventList) {
          const slugValue = getString(item.slug);
          const titleValue = getString(item.title) || getString(item.name) || getString(item.event_name);
          if (!slugValue || !titleValue) continue;
          events.push({
            slug: slugValue,
            title: titleValue,
            description: '',
            start_time: getString(item.start_time) || getString(item.start_at) || '',
            end_time: getString(item.end_time) || getString(item.end_at) || '',
            timezone: getString(item.timezone) || 'America/Los_Angeles',
            location: { type: 'physical' },
            status: 'published',
            host_id: '',
            host_name: getString(item.host_name) || '',
            url: `${LUMA_BASE_URL}/${slugValue}`,
          });
        }
      }
    }

    return events;
  } catch (error) {
    console.error('Error scraping my events:', error);
    return [];
  }
}

/**
 * Scrape hosted events (requires auth)
 */
export async function scrapeHostedEvents(cookies: string): Promise<LumaEvent[]> {
  try {
    const html = await fetchHtml(`${LUMA_BASE_URL}/home/manage`, cookies);
    const $ = cheerio.load(html);
    
    const events: LumaEvent[] = [];
    
    // Similar parsing logic
    $('a[href^="/"]').each((i, el) => {
      const href = $(el).attr('href');
      if (!href) return;
      
      const slug = href.replace('/', '');
      const title = $(el).find('h3, h4').first().text().trim();
      
      if (title && slug && !slug.includes('/')) {
        events.push({
          slug,
          title,
          description: '',
          start_time: '',
          end_time: '',
          timezone: 'America/Los_Angeles',
          location: { type: 'physical' },
          status: 'published',
          host_id: '',
          host_name: '',
          url: `${LUMA_BASE_URL}/${slug}`,
        });
      }
    });
    
    if (events.length === 0) {
      console.warn('[luma] No hosted events found with primary selectors. Trying Next.js data...');
      const nextData = extractJsonScript(html, '__NEXT_DATA__');
      const eventList = nextData ? findEventList(nextData) : null;
      if (eventList) {
        for (const item of eventList) {
          const slugValue = getString(item.slug);
          const titleValue = getString(item.title) || getString(item.name) || getString(item.event_name);
          if (!slugValue || !titleValue) continue;
          events.push({
            slug: slugValue,
            title: titleValue,
            description: '',
            start_time: getString(item.start_time) || getString(item.start_at) || '',
            end_time: getString(item.end_time) || getString(item.end_at) || '',
            timezone: getString(item.timezone) || 'America/Los_Angeles',
            location: { type: 'physical' },
            status: 'published',
            host_id: '',
            host_name: getString(item.host_name) || '',
            url: `${LUMA_BASE_URL}/${slugValue}`,
          });
        }
      }
    }

    return events;
  } catch (error) {
    console.error('Error scraping hosted events:', error);
    return [];
  }
}

/**
 * Scrape guest list (requires auth)
 */
export async function scrapeGuestList(slug: string, cookies: string): Promise<Attendee[]> {
  try {
    const html = await fetchHtml(`${LUMA_BASE_URL}/${slug}/guests`, cookies);
    const $ = cheerio.load(html);
    
    const guests: Attendee[] = [];
    
    // Parse guest entries
    $('[data-testid="guest-row"], [class*="guest"], [data-testid="attendee-row"]').each((i, el) => {
      const name = $(el).find('[class*="name"], [data-testid="guest-name"]').first().text().trim();
      const avatar = $(el).find('img').attr('src');
      
      if (name) {
        guests.push({
          name,
          avatar,
          status: 'going',
        });
      }
    });

    if (guests.length === 0) {
      console.warn(`[luma] Guest list selectors failed for ${slug}.`);
    }

    return guests;
  } catch (error) {
    console.error(`Error scraping guest list for ${slug}:`, error);
    return [];
  }
}

/**
 * Load cookies from pass
 */
export async function loadCookies(): Promise<string | null> {
  try {
    const { exec } = await import('child_process');
    const { promisify } = await import('util');
    const execAsync = promisify(exec);
    
    const { stdout } = await execAsync('pass show luma/cookies 2>/dev/null', {
      encoding: 'utf8',
    });
    
    const cookiesJson = stdout.trim();
    if (!cookiesJson) {
      return null;
    }
    
    // Parse JSON and convert to cookie string
    const cookies = JSON.parse(cookiesJson);
    return Object.entries(cookies)
      .map(([k, v]) => `${k}=${v}`)
      .join('; ');
  } catch (error) {
    return null;
  }
}

/**
 * Check if authenticated
 */
export async function isAuthenticated(): Promise<boolean> {
  const cookies = await loadCookies();
  return cookies !== null;
}
