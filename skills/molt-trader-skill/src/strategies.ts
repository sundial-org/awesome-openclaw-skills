/**
 * Base strategy class for building trading strategies
 */

import { MoltTraderClient } from './client';
import { Position, PortfolioMetrics } from './types';

export abstract class TradingStrategy {
  protected client: MoltTraderClient;
  protected name: string;

  constructor(client: MoltTraderClient, name: string) {
    this.client = client;
    this.name = name;
  }

  /**
   * Main strategy loop - override in subclass
   */
  abstract run(): Promise<void>;

  /**
   * Helper: Get current portfolio
   */
  protected async getPortfolio(): Promise<PortfolioMetrics> {
    return this.client.getPortfolioMetrics();
  }

  /**
   * Helper: Calculate position size based on portfolio
   */
  protected async calculatePositionSize(riskPercent: number = 5): Promise<number> {
    const portfolio = await this.getPortfolio();
    const riskAmount = portfolio.balance * (riskPercent / 100);

    // Assume $30 per share average, round to nearest 100
    const shares = Math.floor((riskAmount / 30) / 100) * 100;
    return Math.max(100, shares); // Minimum 100 shares
  }

  /**
   * Helper: Log strategy activity
   */
  protected log(message: string): void {
    console.log(`[${this.name}] ${new Date().toISOString()} - ${message}`);
  }
}
