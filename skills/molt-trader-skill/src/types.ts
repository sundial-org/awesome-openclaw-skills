/**
 * Type definitions for Molt Trader SDK
 */

export type PositionType = 'long' | 'short';
export type OrderType = 'market' | 'limit';
export type LeaderboardPeriod = 'weekly' | 'monthly' | 'quarterly' | 'ytd' | 'alltime';

/**
 * Configuration for MoltTraderClient
 */
export interface MoltTraderConfig {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
  retryAttempts?: number;
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
}

/**
 * Position data
 */
export interface Position {
  id: string;
  userId: string;
  symbol: string;
  type: PositionType;
  shares: number;
  entryPrice: number;
  exitPrice?: number;
  profit?: number;
  profitPercent?: number;
  openedAt: Date | string;
  closedAt?: Date | string;
  status: 'open' | 'closed';
}

/**
 * Config to open a position
 */
export interface OpenPositionConfig {
  symbol: string;
  type: PositionType;
  shares: number;
  orderType?: OrderType;
  limitPrice?: number;
}

/**
 * Locate request (for shorting)
 */
export interface LocateRequest {
  symbol: string;
  shares: number;
  percentChange: number;
}

export interface LocateResult {
  symbol: string;
  shares: number;
  feePaid: number;
  expiresAt: Date | string;
}

/**
 * Leaderboard ranking
 */
export interface LeaderboardRanking {
  rank: number;
  userId: string;
  displayName: string;
  roi: number;
  totalProfit: number;
  totalTrades: number;
  winRate: number;
}

export interface LeaderboardResponse {
  period: LeaderboardPeriod;
  rankings: LeaderboardRanking[];
}

/**
 * Portfolio metrics
 */
export interface PortfolioMetrics {
  userId: string;
  balance: number;
  totalValue: number;
  roi: number;
  winRate: number;
  totalTrades: number;
  openPositions: number;
  bestTrade?: number;
  worstTrade?: number;
  lastUpdateTime: Date | string;
}

/**
 * Trading history for analysis
 */
export interface TradeHistory {
  positionId: string;
  symbol: string;
  type: PositionType;
  shares: number;
  entryPrice: number;
  exitPrice: number;
  profit: number;
  profitPercent: number;
  openedAt: Date | string;
  closedAt: Date | string;
  holdDays: number;
}
