/**
 * Momentum Trading Strategy
 * 
 * Trades stocks that moved >20% during pre-market or mid-day sessions.
 * Shorts extreme gainers (mean reversion bias).
 */

import { MoltTraderClient } from '../client';
import { TradingStrategy } from '../strategies';

export class MomentumTrader extends TradingStrategy {
  private maxPositions: number = 5;
  private targetMovePercent: number = 20;
  private profitTarget: number = 5; // Exit when up 5%

  constructor(client: MoltTraderClient) {
    super(client, 'MomentumTrader');
  }

  async run(): Promise<void> {
    this.log('Starting momentum trading strategy');

    setInterval(async () => {
      try {
        // Get current positions
        const positions = await this.client.getPositions();

        if (positions.length >= this.maxPositions) {
          this.log(`At max positions (${this.maxPositions}), skipping new entries`);
          return;
        }

        // In a real implementation, you'd fetch market data here
        // For now, this is a template
        this.log(`Current positions: ${positions.length}/${this.maxPositions}`);

        // Close winning positions
        for (const position of positions) {
          if (position.profitPercent && position.profitPercent >= this.profitTarget) {
            try {
              await this.client.closePosition(position.id);
              this.log(`✓ Closed ${position.symbol} for ${position.profitPercent.toFixed(2)}% gain`);
            } catch (error) {
              this.log(`✗ Failed to close ${position.id}: ${error}`);
            }
          }
        }

        // Log portfolio status
        const portfolio = await this.client.getPortfolioMetrics();
        this.log(`Portfolio: $${portfolio.balance.toFixed(0)} | ROI: ${portfolio.roi.toFixed(2)}%`);
      } catch (error) {
        this.log(`Error in trading loop: ${error}`);
      }
    }, 30000); // Check every 30 seconds
  }
}

// Usage example
async function main() {
  const client = new MoltTraderClient({
    apiKey: process.env.MOLT_TRADER_API_KEY || '',
    baseUrl: process.env.MOLT_TRADER_BASE_URL || 'http://localhost:3000',
  });

  const trader = new MomentumTrader(client);
  await trader.run();

  // Keep the process alive
  console.log('Strategy running... Press Ctrl+C to stop');
}

main().catch(console.error);
