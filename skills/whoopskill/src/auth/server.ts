import { createServer, type Server } from 'node:http';
import { URL } from 'node:url';

export interface CallbackResult {
  code: string;
  state: string;
}

export async function findAvailablePort(startPort: number = 3000): Promise<number> {
  return new Promise((resolve) => {
    const server = createServer();
    server.listen(startPort, () => {
      server.close(() => resolve(startPort));
    });
    server.on('error', () => {
      resolve(findAvailablePort(startPort + 1));
    });
  });
}

export function startCallbackServer(port: number): Promise<CallbackResult> {
  return new Promise((resolve, reject) => {
    let server: Server;

    const timeout = setTimeout(() => {
      server?.close();
      reject(new Error('OAuth callback timeout'));
    }, 120000);

    server = createServer((req, res) => {
      const url = new URL(req.url || '/', `http://localhost:${port}`);

      if (url.pathname === '/callback') {
        const code = url.searchParams.get('code');
        const state = url.searchParams.get('state');
        const error = url.searchParams.get('error');

        if (error) {
          res.writeHead(400, { 'Content-Type': 'text/html' });
          res.end('<h1>Authorization Failed</h1><p>You can close this window.</p>');
          clearTimeout(timeout);
          server.close();
          reject(new Error(`OAuth error: ${error}`));
          return;
        }

        if (code && state) {
          res.writeHead(200, { 'Content-Type': 'text/html' });
          res.end('<h1>Authorization Successful</h1><p>You can close this window.</p>');
          clearTimeout(timeout);
          server.close();
          resolve({ code, state });
          return;
        }

        res.writeHead(400, { 'Content-Type': 'text/html' });
        res.end('<h1>Missing Parameters</h1>');
        return;
      }

      res.writeHead(404);
      res.end('Not Found');
    });

    server.listen(port);
  });
}
