export enum ExitCode {
  SUCCESS = 0,
  GENERAL_ERROR = 1,
  AUTH_ERROR = 2,
  RATE_LIMIT = 3,
  NETWORK_ERROR = 4,
}

export class WhoopError extends Error {
  constructor(
    message: string,
    public code: ExitCode,
    public statusCode?: number
  ) {
    super(message);
    this.name = 'WhoopError';
  }
}

export function handleError(error: unknown): never {
  if (error instanceof WhoopError) {
    const status = error.statusCode ? ` (${error.statusCode})` : '';
    console.error(`Error: ${error.message}${status}`);
    process.exit(error.code);
  }

  if (error instanceof Error) {
    if (error.message.includes('fetch failed') || error.message.includes('ECONNREFUSED')) {
      console.error('Error: Network connection failed');
      process.exit(ExitCode.NETWORK_ERROR);
    }
    console.error(`Error: ${error.message}`);
    process.exit(ExitCode.GENERAL_ERROR);
  }

  console.error('Error: Unknown error occurred');
  process.exit(ExitCode.GENERAL_ERROR);
}
