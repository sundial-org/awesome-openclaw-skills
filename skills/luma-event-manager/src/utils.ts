/**
 * Utility functions for Luma skill
 */

import { Location } from './index';

export interface BackoffOptions {
  maxRetries?: number;
  baseDelayMs?: number;
  maxDelayMs?: number;
  minIntervalMs?: number;
  retryOnStatuses?: number[];
}

const DEFAULT_RETRY_STATUSES = [429, 500, 502, 503, 504];
const DEFAULT_MIN_INTERVAL_MS = 1000;
let lastRequestAt = 0;

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function applyRateLimit(minIntervalMs: number): Promise<void> {
  const now = Date.now();
  const waitMs = minIntervalMs - (now - lastRequestAt);
  if (waitMs > 0) {
    await sleep(waitMs);
  }
  lastRequestAt = Date.now();
}

function parseRetryAfter(headerValue: string | null): number | null {
  if (!headerValue) return null;

  const seconds = Number(headerValue);
  if (!Number.isNaN(seconds) && seconds >= 0) {
    return seconds * 1000;
  }

  const dateMs = Date.parse(headerValue);
  if (!Number.isNaN(dateMs)) {
    const delayMs = dateMs - Date.now();
    return delayMs > 0 ? delayMs : 0;
  }

  return null;
}

function computeBackoffDelay(attempt: number, baseDelayMs: number, maxDelayMs: number): number {
  const jitter = 0.2 + Math.random() * 0.3;
  const delay = Math.min(maxDelayMs, baseDelayMs * Math.pow(2, attempt));
  return Math.floor(delay * (1 + jitter));
}

export async function fetchWithBackoff(
  url: string,
  options: RequestInit = {},
  backoffOptions: BackoffOptions = {}
): Promise<Response> {
  const {
    maxRetries = 4,
    baseDelayMs = 500,
    maxDelayMs = 8000,
    minIntervalMs = DEFAULT_MIN_INTERVAL_MS,
    retryOnStatuses = DEFAULT_RETRY_STATUSES,
  } = backoffOptions;

  let lastError: unknown = null;

  for (let attempt = 0; attempt <= maxRetries; attempt += 1) {
    if (minIntervalMs > 0) {
      await applyRateLimit(minIntervalMs);
    }

    try {
      const response = await fetch(url, options);

      if (response.ok || !retryOnStatuses.includes(response.status) || attempt === maxRetries) {
        return response;
      }

      const retryAfterMs = parseRetryAfter(response.headers.get('retry-after'));
      const delayMs = retryAfterMs ?? computeBackoffDelay(attempt, baseDelayMs, maxDelayMs);
      console.warn(`[luma] Request failed (${response.status}). Retrying in ${delayMs}ms...`);
      await sleep(delayMs);
    } catch (error) {
      lastError = error;
      if (attempt === maxRetries) {
        break;
      }
      const delayMs = computeBackoffDelay(attempt, baseDelayMs, maxDelayMs);
      console.warn(`[luma] Request error. Retrying in ${delayMs}ms...`);
      await sleep(delayMs);
    }
  }

  throw lastError instanceof Error
    ? lastError
    : new Error('Request failed after retries');
}

export function extractJsonScript(html: string, scriptId: string): unknown | null {
  const regex = new RegExp(`<script[^>]*id="${scriptId}"[^>]*>([\\s\\S]*?)</script>`, 'i');
  const match = html.match(regex);
  if (!match || !match[1]) {
    return null;
  }

  try {
    return JSON.parse(match[1]);
  } catch {
    return null;
  }
}

export function findFirstObjectWithKeys(
  value: unknown,
  keys: string[],
  predicate?: (candidate: Record<string, unknown>) => boolean
): Record<string, unknown> | null {
  if (!value || typeof value !== 'object') {
    return null;
  }

  if (!Array.isArray(value)) {
    const candidate = value as Record<string, unknown>;
    const hasAllKeys = keys.every(key => key in candidate);
    if (hasAllKeys && (!predicate || predicate(candidate))) {
      return candidate;
    }
  }

  const entries = Array.isArray(value)
    ? value
    : Object.values(value as Record<string, unknown>);

  for (const entry of entries) {
    const found = findFirstObjectWithKeys(entry, keys, predicate);
    if (found) {
      return found;
    }
  }

  return null;
}

/**
 * Geocode a location string to coordinates
 * Uses Nominatim (OpenStreetMap) - free, no API key required
 */
export async function geocodeLocation(location: string): Promise<Location | null> {
  try {
    const encoded = encodeURIComponent(location);
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encoded}&limit=1`;
    
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Luma-Skill/1.0',
      },
    });

    if (!response.ok) {
      throw new Error('Geocoding failed');
    }

    const data = await response.json() as Array<{ lat: string; lon: string }>;
    
    if (data.length === 0) {
      return null;
    }

    return {
      lat: parseFloat(data[0].lat),
      lng: parseFloat(data[0].lon),
    };
  } catch (error) {
    console.error('Geocoding error:', error);
    return null;
  }
}

/**
 * Calculate distance between two coordinates (Haversine formula)
 */
export function calculateDistance(
  loc1: Location,
  loc2: Location,
  unit: 'miles' | 'km' = 'miles'
): number {
  const R = unit === 'miles' ? 3959 : 6371; // Earth's radius in miles or km
  
  const dLat = toRad(loc2.lat - loc1.lat);
  const dLon = toRad(loc2.lng - loc1.lng);
  
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(loc1.lat)) * Math.cos(toRad(loc2.lat)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  
  return R * c;
}

function toRad(deg: number): number {
  return deg * (Math.PI / 180);
}

/**
 * Format date for display
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

/**
 * Parse relative date to ISO string
 */
export function parseRelativeDate(dateStr: string): string {
  const now = new Date();
  
  switch (dateStr.toLowerCase()) {
    case 'today':
      return now.toISOString();
    case 'tomorrow':
      now.setDate(now.getDate() + 1);
      return now.toISOString();
    default:
      // Try to parse as YYYY-MM-DD
      if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
        return new Date(dateStr).toISOString();
      }
      return now.toISOString();
  }
}

/**
 * Format event for display
 */
export function formatEventForDisplay(event: {
  id: string;
  title: string;
  start_time: string;
  location: {
    type: string;
    address?: string;
  };
}): string {
  const date = formatDate(event.start_time);
  const location = event.location.type === 'virtual' 
    ? '🌐 Virtual' 
    : `📍 ${event.location.address || 'See map'}`;
  
  return `**${event.title}**\n${date}\n${location}`;
}

/**
 * Parse Luma event ID from URL or string
 */
export function parseEventId(input: string): string {
  // Handle URLs like https://lu.ma/abc123
  const urlMatch = input.match(/lu\.ma\/([a-zA-Z0-9_-]+)/);
  if (urlMatch) {
    return urlMatch[1];
  }
  
  // Handle already-clean IDs
  return input.trim();
}

/**
 * Check if Luma API key is configured
 */
export async function isConfigured(): Promise<boolean> {
  try {
    const { exec } = await import('child_process');
    const { promisify } = await import('util');
    const execAsync = promisify(exec);

    await execAsync('pass show luma/api_key 2>/dev/null', { encoding: 'utf8' });
    return true;
  } catch {
    return false;
  }
}
