/**
 * RSVP support via lu.ma scraping + POST
 */

import * as cheerio from 'cheerio';
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

function getString(value: unknown): string | undefined {
  if (typeof value === 'string') {
    const trimmed = value.trim();
    return trimmed ? trimmed : undefined;
  }
  return undefined;
}

function normalizeRsvpResponse(response: string): string {
  const normalized = response.toLowerCase().trim();
  if (['yes', 'going', 'y', 'true'].includes(normalized)) return 'yes';
  if (['no', 'not_going', 'n', 'false'].includes(normalized)) return 'no';
  if (['maybe', 'interested'].includes(normalized)) return 'maybe';
  if (['waitlist', 'waitlisted'].includes(normalized)) return 'waitlist';
  return normalized || 'yes';
}

function findFirstValueByKey(value: unknown, key: string): string | undefined {
  if (!value || typeof value !== 'object') {
    return undefined;
  }

  if (!Array.isArray(value)) {
    const candidate = value as Record<string, unknown>;
    const found = getString(candidate[key]);
    if (found) {
      return found;
    }
  }

  const entries = Array.isArray(value)
    ? value
    : Object.values(value as Record<string, unknown>);

  for (const entry of entries) {
    const found = findFirstValueByKey(entry, key);
    if (found) {
      return found;
    }
  }

  return undefined;
}

async function fetchEventPage(slug: string, cookies: string): Promise<string> {
  const headers: Record<string, string> = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cookie': cookies,
  };

  const response = await fetchWithBackoff(
    `${LUMA_BASE_URL}/${slug}`,
    { headers },
    LUMA_BACKOFF_OPTIONS
  );

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.text();
}

function extractEventId(html: string, slug: string): string | null {
  const $ = cheerio.load(html);

  const attributeKeys = [
    'data-event-id',
    'data-event_id',
    'data-event-uuid',
    'data-event_uuid',
  ];

  for (const key of attributeKeys) {
    const value = $(`[${key}]`).first().attr(key);
    if (value) {
      return value.trim();
    }
  }

  const metaId = $('meta[property="event:id"], meta[name="event:id"]').attr('content');
  if (metaId) {
    return metaId.trim();
  }

  const nextData = extractJsonScript(html, '__NEXT_DATA__');
  if (nextData) {
    const candidate = findFirstObjectWithKeys(
      nextData,
      ['slug'],
      (obj) => getString(obj.slug) === slug && Boolean(obj.id || obj.event_id)
    );

    if (candidate) {
      return getString(candidate.event_id) || getString(candidate.id) || null;
    }

    const fallbackId = findFirstValueByKey(nextData, 'event_id') || findFirstValueByKey(nextData, 'id');
    if (fallbackId) {
      return fallbackId;
    }
  }

  return null;
}

function extractCsrfToken(html: string): string | undefined {
  const $ = cheerio.load(html);
  const token =
    $('meta[name="csrf-token"]').attr('content') ||
    $('meta[name="csrfToken"]').attr('content') ||
    $('meta[name="csrf"]').attr('content') ||
    $('input[name="csrfmiddlewaretoken"]').attr('value');

  if (token) {
    return token.trim();
  }

  const nextData = extractJsonScript(html, '__NEXT_DATA__');
  if (!nextData) {
    return undefined;
  }

  return findFirstValueByKey(nextData, 'csrfToken') || findFirstValueByKey(nextData, 'csrf_token');
}

function buildPayloads(eventId: string, response: string): Array<Record<string, unknown>> {
  const payloads: Array<Record<string, unknown>> = [
    { event_id: eventId, response },
    { event_id: eventId, status: response },
    { event_id: eventId, answer: response },
    { event_id: eventId, rsvp: response },
    { event_id: eventId, value: response },
    { event_id: eventId, event_uuid: eventId, response },
  ];

  if (response === 'yes') {
    payloads.push({ event_id: eventId, going: true });
  }

  if (response === 'no') {
    payloads.push({ event_id: eventId, going: false });
  }

  return payloads;
}

export async function rsvpToEvent(
  slug: string,
  response: string,
  cookies: string
): Promise<{ success: boolean; message: string; details?: string } > {
  const normalized = normalizeRsvpResponse(response);
  const html = await fetchEventPage(slug, cookies);
  const eventId = extractEventId(html, slug);

  if (!eventId) {
    console.warn(`[luma] Unable to find event ID for ${slug}.`);
    return {
      success: false,
      message: 'Unable to find event ID. Luma page structure may have changed.',
    };
  }

  const csrfToken = extractCsrfToken(html);
  if (!csrfToken) {
    console.warn('[luma] CSRF token not found. RSVP may fail.');
  }

  const endpoints = [
    `${LUMA_BASE_URL}/api/v2/event/rsvp`,
    `${LUMA_BASE_URL}/api/v1/event/rsvp`,
    `${LUMA_BASE_URL}/api/event/rsvp`,
    `${LUMA_BASE_URL}/api/v2/event/${eventId}/rsvp`,
    `${LUMA_BASE_URL}/api/v1/event/${eventId}/rsvp`,
    `${LUMA_BASE_URL}/api/rsvp`,
  ];

  const payloads = buildPayloads(eventId, normalized);

  for (const endpoint of endpoints) {
    for (const payload of payloads) {
      const headers: Record<string, string> = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': cookies,
      };

      if (csrfToken) {
        headers['x-csrf-token'] = csrfToken;
        headers['x-csrf'] = csrfToken;
      }

      const responseResult = await fetchWithBackoff(
        endpoint,
        {
          method: 'POST',
          headers,
          body: JSON.stringify(payload),
        },
        LUMA_BACKOFF_OPTIONS
      );

      const text = await responseResult.text();

      if (responseResult.ok) {
        return {
          success: true,
          message: `RSVP submitted (${normalized}).`,
          details: text.trim(),
        };
      }

      if (text.includes('already') || text.includes('duplicate')) {
        return {
          success: true,
          message: 'RSVP already recorded.',
          details: text.trim(),
        };
      }
    }
  }

  return {
    success: false,
    message: 'RSVP failed. Luma may have changed their RSVP endpoint.',
  };
}
