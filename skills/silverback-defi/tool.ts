/**
 * Silverback DeFi Intelligence Tool for OpenClaw
 *
 * This tool provides DeFi intelligence via the Silverback x402 API.
 * It uses Claude Sonnet as the brain with 11 intelligence tools for
 * real-time market data, technical analysis, yield opportunities, and more.
 *
 * Usage:
 *   User: "What are the top coins?"
 *   Agent calls: silverback_chat({ message: "What are the top coins?" })
 *   Returns: Natural language response with market data
 */

const SILVERBACK_API_URL = 'https://x402.silverbackdefi.app/api/v1/chat';

interface SilverbackChatInput {
  message: string;
  history?: Array<{ role: 'user' | 'assistant'; content: string }>;
}

interface SilverbackChatResponse {
  success: boolean;
  response: string;
  toolsUsed: string[];
  cost: number;
  error?: string;
}

/**
 * Query Silverback DeFi intelligence
 *
 * Available intelligence:
 * - top_coins: Market cap rankings with prices
 * - top_pools: Best yielding liquidity pools
 * - top_protocols: DeFi protocol TVL rankings
 * - swap_quote: Optimal swap routing on Base
 * - technical_analysis: RSI, MACD, trends
 * - defi_yield: Yield opportunities
 * - pool_analysis: LP pool health
 * - token_audit: Security audit
 * - whale_moves: Large transaction tracking
 * - agent_reputation: ERC-8004 reputation
 * - agent_discover: Find trusted agents
 */
export async function silverback_chat(input: SilverbackChatInput): Promise<string> {
  try {
    const response = await fetch(SILVERBACK_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: input.message,
        history: input.history || [],
      }),
    });

    // Handle x402 payment required
    if (response.status === 402) {
      return 'This query requires x402 payment. Please ensure you have USDC on Base chain for micropayments.';
    }

    if (!response.ok) {
      const errorText = await response.text();
      return `Silverback API error: ${response.status} - ${errorText}`;
    }

    const data: SilverbackChatResponse = await response.json();

    if (!data.success) {
      return `Error: ${data.error || 'Unknown error from Silverback API'}`;
    }

    // Format response with tools used
    let result = data.response;

    if (data.toolsUsed && data.toolsUsed.length > 0) {
      const toolNames = data.toolsUsed.map(formatToolName).join(', ');
      result += `\n\n[Intelligence used: ${toolNames}]`;
    }

    return result;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return `Failed to query Silverback: ${errorMessage}`;
  }
}

/**
 * Format tool name for display
 */
function formatToolName(tool: string): string {
  const names: Record<string, string> = {
    swap_quote: 'Swap Quote',
    technical_analysis: 'Technical Analysis',
    defi_yield: 'Yield Finder',
    pool_analysis: 'Pool Analysis',
    top_coins: 'Market Data',
    top_pools: 'Pool Rankings',
    top_protocols: 'Protocol Rankings',
    token_audit: 'Security Audit',
    whale_moves: 'Whale Tracker',
    agent_reputation: 'Agent Reputation',
    agent_discover: 'Agent Discovery',
  };
  return names[tool] || tool.replace(/_/g, ' ');
}

// Tool definition for OpenClaw
export const toolDefinition = {
  name: 'silverback_chat',
  description:
    'Query Silverback DeFi intelligence for market data, swap quotes, technical analysis, ' +
    'yield opportunities, token audits, and whale tracking. Powered by Claude with real-time ' +
    'x402 intelligence tools. Use for any DeFi, trading, or crypto market questions.',
  parameters: {
    type: 'object',
    properties: {
      message: {
        type: 'string',
        description: "The user's question about DeFi, trading, yields, tokens, or market data",
      },
    },
    required: ['message'],
  },
};

export default silverback_chat;
