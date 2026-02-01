/**
 * Main MoltTraderClient - Entry point for trading
 */

import {
  MoltTraderConfig,
  Position,
  OpenPositionConfig,
  LocateRequest,
  LocateResult,
  LeaderboardResponse,
  LeaderboardPeriod,
  PortfolioMetrics,
  TradeHistory,
} from './types';

import {
  MoltTraderError,
  AuthenticationError,
  InsufficientFundsError,
  NetworkError,
} from './errors';

export class MoltTraderClient {
  private apiKey: string;
  private baseUrl: string;
  private timeout: number;
  private retryAttempts: number;
  private logLevel: 'debug' | 'info' | 'warn' | 'error';

  constructor(config: MoltTraderConfig) {
    this.apiKey = config.apiKey;
    this.baseUrl = config.baseUrl || 'https://api.moltrader.ai';
    this.timeout = config.timeout || 10000;
    this.retryAttempts = config.retryAttempts || 3;
    this.logLevel = config.logLevel || 'info';

    if (!this.apiKey) {
      throw new AuthenticationError('API key is required');
    }

    this.log('info', `MoltTraderClient initialized (${this.baseUrl})`);
  }

  /**
   * Open a new trading position
   */
  async openPosition(config: OpenPositionConfig): Promise<Position> {
    this.log('debug', `Opening ${config.type} position: ${config.symbol} x${config.shares}`);

    try {
      const response = await this.request('POST', '/api/simulator/positions', {
        symbol: config.symbol,
        type: config.type,
        shares: config.shares,
        orderType: config.orderType || 'market',
        limitPrice: config.limitPrice,
      });

      this.log('info', `Position opened: ${response.id}`);
      return response;
    } catch (error) {
      if (error instanceof MoltTraderError) throw error;
      throw new NetworkError(`Failed to open position: ${error}`);
    }
  }

  /**
   * Close an open position
   */
  async closePosition(positionId: string): Promise<Position> {
    this.log('debug', `Closing position: ${positionId}`);

    try {
      const response = await this.request('POST', `/api/simulator/positions/${positionId}/close`);

      this.log('info', `Position closed: profit $${response.profit}`);
      return response;
    } catch (error) {
      if (error instanceof MoltTraderError) throw error;
      throw new NetworkError(`Failed to close position: ${error}`);
    }
  }

  /**
   * Get all open positions
   */
  async getPositions(): Promise<Position[]> {
    this.log('debug', 'Fetching positions');

    try {
      const response = await this.request('GET', '/api/simulator/positions');
      this.log('info', `Retrieved ${response.length} positions`);
      return response;
    } catch (error) {
      if (error instanceof MoltTraderError) throw error;
      throw new NetworkError(`Failed to fetch positions: ${error}`);
    }
  }

  /**
   * Get a specific position by ID
   */
  async getPosition(positionId: string): Promise<Position> {
    this.log('debug', `Fetching position: ${positionId}`);

    try {
      return await this.request('GET', `/api/simulator/positions/${positionId}`);
    } catch (error) {
      if (error instanceof MoltTraderError) throw error;
      throw new NetworkError(`Failed to fetch position: ${error}`);
    }
  }

  /**
   * Request to locate shares for shorting
   */
  async requestLocate(config: LocateRequest): Promise<LocateResult> {
    this.log('debug', `Requesting locate: ${config.symbol} x${config.shares}`);

    try {
      return await this.request('POST', '/api/simulator/locate', config);
    } catch (error) {
      if (error instanceof MoltTraderError) throw error;
      throw new NetworkError(`Failed to request locate: ${error}`);
    }
  }

  /**
   * Get global leaderboard
   */
  async getLeaderboard(period: LeaderboardPeriod, tier?: string): Promise<LeaderboardResponse> {
    this.log('debug', `Fetching leaderboard: ${period}${tier ? ` (${tier})` : ''}`);

    try {
      const params = new URLSearchParams({ period });
      if (tier) params.append('tier', tier);

      const response = await this.request('GET', `/api/leaderboard/global?${params}`);
      this.log('info', `Retrieved leaderboard with ${response.rankings.length} entries`);
      return response;
    } catch (error) {
      if (error instanceof MoltTraderError) throw error;
      throw new NetworkError(`Failed to fetch leaderboard: ${error}`);
    }
  }

  /**
   * Get your portfolio metrics
   */
  async getPortfolioMetrics(): Promise<PortfolioMetrics> {
    this.log('debug', 'Fetching portfolio metrics');

    try {
      return await this.request('GET', '/api/simulator/portfolio');
    } catch (error) {
      if (error instanceof MoltTraderError) throw error;
      throw new NetworkError(`Failed to fetch portfolio metrics: ${error}`);
    }
  }

  /**
   * Get trade history
   */
  async getTradeHistory(limit: number = 50): Promise<TradeHistory[]> {
    this.log('debug', `Fetching trade history (limit: ${limit})`);

    try {
      const params = new URLSearchParams({ limit: limit.toString() });
      return await this.request('GET', `/api/simulator/history?${params}`);
    } catch (error) {
      if (error instanceof MoltTraderError) throw error;
      throw new NetworkError(`Failed to fetch trade history: ${error}`);
    }
  }

  /**
   * Internal HTTP request method with retry logic
   */
  private async request(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    endpoint: string,
    data?: unknown
  ): Promise<any> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < this.retryAttempts; attempt++) {
      try {
        const url = `${this.baseUrl}${endpoint}`;
        const options: RequestInit = {
          method,
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.apiKey}`,
          },
          body: data ? JSON.stringify(data) : undefined,
        };

        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), this.timeout);

        try {
          const response = await fetch(url, {
            ...options,
            signal: controller.signal,
          });

          clearTimeout(timeout);

          if (!response.ok) {
            const error = await response.json().catch(() => ({})) as { message?: string; code?: string };
            throw new MoltTraderError(
              error.message || `HTTP ${response.status}`,
              error.code,
              response.status
            );
          }

          return await response.json();
        } finally {
          clearTimeout(timeout);
        }
      } catch (error) {
        lastError = error as Error;

        if (error instanceof MoltTraderError) {
          // Don't retry auth errors
          if (error.statusCode === 401) {
            throw new AuthenticationError(error.message);
          }
          // Don't retry validation errors
          if (error.statusCode === 400) {
            throw error;
          }
        }

        // Exponential backoff
        if (attempt < this.retryAttempts - 1) {
          const delay = Math.pow(2, attempt) * 1000;
          this.log('warn', `Attempt ${attempt + 1} failed, retrying in ${delay}ms...`);
          await new Promise((resolve) => setTimeout(resolve, delay));
        }
      }
    }

    throw lastError || new NetworkError('All retry attempts failed');
  }

  /**
   * Internal logging
   */
  private log(level: string, message: string): void {
    const levels = { debug: 0, info: 1, warn: 2, error: 3 };
    if (levels[level as keyof typeof levels] >= levels[this.logLevel]) {
      console.log(`[Molt Trader] ${level.toUpperCase()}: ${message}`);
    }
  }
}
