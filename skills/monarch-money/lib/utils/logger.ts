import { Logger } from '../types'

export class ConsoleLogger implements Logger {
  constructor(private level: 'debug' | 'info' | 'warn' | 'error' = 'info') {}

  private shouldLog(level: string): boolean {
    const levels = ['debug', 'info', 'warn', 'error']
    const currentIndex = levels.indexOf(this.level)
    const messageIndex = levels.indexOf(level)
    return messageIndex >= currentIndex
  }

  debug(message: string, ...args: unknown[]): void {
    if (this.shouldLog('debug')) {
      console.error(`[MonarchMoney DEBUG] ${message}`, ...args)
    }
  }

  info(message: string, ...args: unknown[]): void {
    if (this.shouldLog('info')) {
      console.error(`[MonarchMoney INFO] ${message}`, ...args)
    }
  }

  warn(message: string, ...args: unknown[]): void {
    if (this.shouldLog('warn')) {
      console.error(`[MonarchMoney WARN] ${message}`, ...args)
    }
  }

  error(message: string, ...args: unknown[]): void {
    if (this.shouldLog('error')) {
      console.error(`[MonarchMoney ERROR] ${message}`, ...args)
    }
  }
}

export class SilentLogger implements Logger {
  debug(): void {}
  info(): void {}
  warn(): void {}
  error(): void {}
}

export function createLogger(level?: 'debug' | 'info' | 'warn' | 'error' | 'silent'): Logger {
  if (level === 'silent') {
    return new SilentLogger()
  }
  
  return new ConsoleLogger(level)
}

// Default logger instance
export const logger = createLogger(
  (process.env.MONARCH_LOG_LEVEL as 'debug' | 'info' | 'warn' | 'error' | 'silent') || 'info'
)