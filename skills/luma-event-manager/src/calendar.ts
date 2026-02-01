/**
 * Google Calendar sync via gog CLI
 */

import { execFile } from 'child_process';
import { promisify } from 'util';
import { LumaEvent } from './index';

const execFileAsync = promisify(execFile);

interface CalendarSyncOptions {
  account?: string;
  calendarId?: string;
}

interface GogAccount {
  email: string;
}

function toRfc3339(input: string): string | null {
  if (!input) return null;
  const parsed = new Date(input);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  return parsed.toISOString();
}

function buildDescription(event: LumaEvent): string {
  const parts: string[] = [];
  if (event.description) {
    parts.push(event.description.trim());
  }
  parts.push(`Luma: ${event.url}`);
  return parts.join('\n\n');
}

function resolveLocation(event: LumaEvent): string {
  if (event.location.type === 'virtual') {
    return event.location.virtual_link || 'Virtual event';
  }
  return event.location.address || event.location.name || 'See event page';
}

async function runGogCommand(args: string[]): Promise<{ stdout: string; stderr: string }> {
  try {
    const result = await execFileAsync('gog', args, { encoding: 'utf8' });
    return { stdout: result.stdout, stderr: result.stderr ?? '' };
  } catch (error: any) {
    const stderr = error?.stderr || '';
    const stdout = error?.stdout || '';
    const message = error?.message || 'gog command failed';
    throw new Error(`${message}\n${stderr || stdout}`.trim());
  }
}

async function listGogAccounts(): Promise<GogAccount[]> {
  try {
    const { stdout } = await runGogCommand(['auth', 'list', '--json']);
    const parsed = JSON.parse(stdout) as GogAccount[];
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    console.warn('[luma] Unable to list gog accounts:', error instanceof Error ? error.message : error);
    return [];
  }
}

async function resolveAccount(explicitAccount?: string): Promise<string | null> {
  if (explicitAccount) {
    return explicitAccount;
  }

  const envAccount = process.env.GOG_ACCOUNT;
  if (envAccount) {
    return envAccount;
  }

  const accounts = await listGogAccounts();
  if (accounts.length === 1) {
    return accounts[0].email;
  }

  return null;
}

export async function syncEventToGoogleCalendar(
  event: LumaEvent,
  options: CalendarSyncOptions = {}
): Promise<{
  success: boolean;
  message: string;
  event_id?: string;
  calendar_id?: string;
  account?: string;
}> {
  const account = await resolveAccount(options.account);
  if (!account) {
    return {
      success: false,
      message: 'Multiple or zero Google accounts found. Provide an account email or set GOG_ACCOUNT.',
    };
  }

  const calendarId = options.calendarId || 'primary';
  const start = toRfc3339(event.start_time);
  if (!start) {
    return {
      success: false,
      message: 'Event start time is missing or invalid. Cannot create calendar entry.',
      account,
      calendar_id: calendarId,
    };
  }

  const end = toRfc3339(event.end_time) || new Date(new Date(start).getTime() + 60 * 60 * 1000).toISOString();
  const description = buildDescription(event);
  const location = resolveLocation(event);

  const args = [
    'calendar',
    'create',
    calendarId,
    '--summary',
    event.title,
    '--from',
    start,
    '--to',
    end,
    '--description',
    description,
    '--location',
    location,
    '--source-url',
    event.url,
    '--source-title',
    'Luma',
    '--send-updates',
    'none',
    '--account',
    account,
    '--json',
  ];

  try {
    const { stdout } = await runGogCommand(args);
    const payload = stdout ? JSON.parse(stdout) as { id?: string } : {};
    return {
      success: true,
      message: `Added to Google Calendar (${calendarId}).`,
      event_id: payload.id,
      calendar_id: calendarId,
      account,
    };
  } catch (error) {
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Failed to create calendar entry.',
      account,
      calendar_id: calendarId,
    };
  }
}
