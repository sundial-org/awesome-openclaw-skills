import { randomBytes } from 'node:crypto';
import { createInterface } from 'node:readline';
import open from 'open';
import { saveTokens, clearTokens, getTokenStatus, getValidTokens, isTokenExpired, loadTokens } from './tokens.js';
import { WhoopError, ExitCode } from '../utils/errors.js';
import type { OAuthTokenResponse } from '../types/whoop.js';

const WHOOP_AUTH_URL = 'https://api.prod.whoop.com/oauth/oauth2/auth';
const WHOOP_TOKEN_URL = 'https://api.prod.whoop.com/oauth/oauth2/token';
const SCOPES = 'read:profile read:body_measurement read:workout read:recovery read:sleep read:cycles offline';

function getCredentials(): { clientId: string; clientSecret: string; redirectUri: string } {
  const clientId = process.env.WHOOP_CLIENT_ID;
  const clientSecret = process.env.WHOOP_CLIENT_SECRET;
  const redirectUri = process.env.WHOOP_REDIRECT_URI;

  if (!clientId || !clientSecret || !redirectUri) {
    throw new WhoopError(
      'Missing WHOOP_CLIENT_ID, WHOOP_CLIENT_SECRET, or WHOOP_REDIRECT_URI in environment',
      ExitCode.AUTH_ERROR
    );
  }

  return { clientId, clientSecret, redirectUri };
}

function prompt(question: string): Promise<string> {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

export async function login(): Promise<void> {
  const { clientId, clientSecret, redirectUri } = getCredentials();
  const state = randomBytes(16).toString('hex');

  const authUrl = new URL(WHOOP_AUTH_URL);
  authUrl.searchParams.set('client_id', clientId);
  authUrl.searchParams.set('redirect_uri', redirectUri);
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('scope', SCOPES);
  authUrl.searchParams.set('state', state);

  console.log('Opening browser for authorization...');
  console.log('\nIf browser does not open, visit this URL:\n');
  console.log(authUrl.toString());
  console.log('');

  await open(authUrl.toString()).catch(() => {});

  const callbackUrl = await prompt('Paste the callback URL here: ');

  const url = new URL(callbackUrl);
  const code = url.searchParams.get('code');
  const returnedState = url.searchParams.get('state');

  if (!code) {
    throw new WhoopError('No authorization code in callback URL', ExitCode.AUTH_ERROR);
  }

  if (returnedState !== state) {
    throw new WhoopError('OAuth state mismatch', ExitCode.AUTH_ERROR);
  }

  const tokenResponse = await fetch(WHOOP_TOKEN_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      redirect_uri: redirectUri,
      client_id: clientId,
      client_secret: clientSecret,
    }),
  });

  if (!tokenResponse.ok) {
    const text = await tokenResponse.text();
    throw new WhoopError(`Token exchange failed: ${text}`, ExitCode.AUTH_ERROR, tokenResponse.status);
  }

  const tokens = (await tokenResponse.json()) as OAuthTokenResponse;
  saveTokens(tokens);
  console.log('Authentication successful');
}

export function logout(): void {
  clearTokens();
  console.log('Logged out');
}

export function status(): void {
  const tokenStatus = getTokenStatus();
  const tokens = loadTokens();
  
  if (!tokenStatus.authenticated) {
    console.log(JSON.stringify({ authenticated: false, message: 'Not logged in. Run: whoopskill auth login' }, null, 2));
    return;
  }

  const now = Math.floor(Date.now() / 1000);
  const expiresIn = tokenStatus.expires_at! - now;
  const needsRefresh = isTokenExpired(tokens!);
  
  console.log(JSON.stringify({
    authenticated: true,
    expires_at: tokenStatus.expires_at,
    expires_in_seconds: expiresIn,
    expires_in_human: expiresIn > 0 ? `${Math.floor(expiresIn / 60)} minutes` : 'EXPIRED',
    needs_refresh: needsRefresh,
  }, null, 2));
}

/**
 * Proactively refresh the access token.
 * Use this in cron jobs to keep tokens fresh.
 */
export async function refresh(): Promise<void> {
  const tokens = loadTokens();
  
  if (!tokens) {
    throw new WhoopError('Not authenticated. Run: whoopskill auth login', ExitCode.AUTH_ERROR);
  }

  try {
    const newTokens = await getValidTokens();
    
    const now = Math.floor(Date.now() / 1000);
    const expiresIn = newTokens.expires_at - now;
    
    console.log(JSON.stringify({
      success: true,
      message: 'Token refreshed successfully',
      expires_at: newTokens.expires_at,
      expires_in_seconds: expiresIn,
      expires_in_human: `${Math.floor(expiresIn / 60)} minutes`,
    }, null, 2));
  } catch (error) {
    if (error instanceof WhoopError && error.message.includes('refresh')) {
      throw new WhoopError(
        'Refresh token expired. Please re-authenticate with: whoopskill auth login',
        ExitCode.AUTH_ERROR
      );
    }
    throw error;
  }
}
