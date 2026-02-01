#!/usr/bin/env python3
"""
LLM-Powered AI Trading Assistant

Conversational interface for cryptocurrency trading analysis powered by LLMs.
Supports OpenAI GPT-4 and Anthropic Claude APIs.

This is Version 1: Standalone LLM-Powered Tool
"""

import sys
import os
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

# Add scripts directory to path
SCRIPT_DIR = os.path.join(os.path.dirname(__file__), 'scripts')
sys.path.insert(0, SCRIPT_DIR)

# Import trading agent
from trading_agent_v2 import TradingAgentV2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMTradingAssistant:
    """
    LLM-powered conversational trading assistant

    Features:
    - Natural language interaction
    - Educational explanations
    - Personalized recommendations
    - Context-aware responses
    - Multi-turn conversations

    Supports:
    - OpenAI GPT-4 (via openai library)
    - Anthropic Claude (via anthropic library)
    """

    SYSTEM_PROMPT = """You are an expert cryptocurrency trading assistant powered by advanced AI trading algorithms.

Your capabilities:
- Analyze cryptocurrencies using 12-stage analysis pipeline
- Provide probabilistic trading recommendations with confidence scores
- Explain complex trading concepts in simple terms
- Educate users about risks and best practices
- Never guarantee profits or make unrealistic promises

Available commands you can execute:
1. analyze <symbol> - Comprehensive trading analysis
2. scan - Find best trading opportunities
3. explain - Explain analysis results
4. compare <symbol1> <symbol2> - Compare two cryptocurrencies
5. risk_assessment - Detailed risk analysis
6. market_context - Current market conditions

When users ask about trading, interpret their intent and:
1. Determine what analysis they need
2. Execute appropriate commands
3. Explain results in educational, accessible language
4. Provide context about risks and limitations
5. Suggest next steps if appropriate

Always emphasize:
- Trading involves significant risk
- Past performance doesn't guarantee future results
- Only invest what you can afford to lose
- This is analysis, not financial advice
- Users should do their own research

Respond conversationally, educationally, and professionally."""

    def __init__(
        self,
        balance: float = 10000,
        llm_provider: str = 'openai',  # 'openai' or 'anthropic'
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize LLM trading assistant

        Args:
            balance: Trading account balance
            llm_provider: LLM provider ('openai' or 'anthropic')
            api_key: API key for LLM provider (or from env)
            model: Specific model to use (default: gpt-4 or claude-3-opus)
        """
        self.balance = balance
        self.llm_provider = llm_provider
        self.model = model
        self.conversation_history = []

        # Initialize trading agent
        self.trading_agent = TradingAgentV2(
            balance=balance,
            enable_health_monitoring=True,
            enable_adaptive_learning=True
        )

        # Initialize LLM client
        self.llm_client = self._initialize_llm(llm_provider, api_key, model)

        logger.info(f"Initialized LLM Trading Assistant (provider: {llm_provider}, balance: ${balance})")

    def _initialize_llm(self, provider: str, api_key: Optional[str], model: Optional[str]):
        """Initialize LLM client"""
        if provider == 'openai':
            try:
                import openai
                if api_key:
                    openai.api_key = api_key
                else:
                    openai.api_key = os.getenv('OPENAI_API_KEY')

                if not openai.api_key:
                    raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

                self.model = model or 'gpt-4'
                logger.info(f"✓ OpenAI client initialized (model: {self.model})")
                return openai

            except ImportError:
                raise ImportError("OpenAI library not installed. Run: pip install openai")

        elif provider == 'anthropic':
            try:
                import anthropic
                if api_key:
                    client = anthropic.Anthropic(api_key=api_key)
                else:
                    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

                self.model = model or 'claude-3-opus-20240229'
                logger.info(f"✓ Anthropic client initialized (model: {self.model})")
                return client

            except ImportError:
                raise ImportError("Anthropic library not installed. Run: pip install anthropic")

        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def chat(self, user_message: str) -> str:
        """
        Send message and get conversational response

        Args:
            user_message: User's message

        Returns:
            Assistant's response
        """
        logger.info(f"User: {user_message}")

        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })

        # Detect if user wants to execute trading analysis
        intent = self._detect_intent(user_message)

        # Execute trading commands if needed
        if intent['requires_analysis']:
            analysis_results = self._execute_analysis(intent)
            # Inject analysis results into context
            analysis_summary = self._summarize_analysis(analysis_results)
            system_context = f"\n\nCurrent Analysis Results:\n{analysis_summary}"
        else:
            system_context = ""

        # Get LLM response
        response = self._get_llm_response(system_context)

        # Add to conversation history
        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })

        logger.info(f"Assistant: {response[:100]}...")

        return response

    def _detect_intent(self, message: str) -> Dict:
        """Detect user intent from message"""
        message_lower = message.lower()

        intent = {
            'requires_analysis': False,
            'action': None,
            'symbol': None,
            'params': {}
        }

        # Detect symbols
        common_symbols = ['btc', 'eth', 'bnb', 'sol', 'xrp', 'ada', 'doge', 'matic', 'avax', 'dot']
        for symbol in common_symbols:
            if symbol in message_lower:
                intent['symbol'] = f"{symbol.upper()}/USDT"
                break

        # Detect actions
        if any(word in message_lower for word in ['analyze', 'analysis', 'look at', 'check', 'review']):
            if intent['symbol']:
                intent['requires_analysis'] = True
                intent['action'] = 'analyze'

        elif any(word in message_lower for word in ['scan', 'find', 'opportunities', 'best', 'top']):
            intent['requires_analysis'] = True
            intent['action'] = 'scan'

        elif any(word in message_lower for word in ['risk', 'risky', 'safe', 'dangerous']):
            if intent['symbol']:
                intent['requires_analysis'] = True
                intent['action'] = 'risk_assessment'

        elif any(word in message_lower for word in ['market', 'conditions', 'sentiment', 'trend']):
            intent['requires_analysis'] = True
            intent['action'] = 'market_context'

        return intent

    def _execute_analysis(self, intent: Dict) -> Dict:
        """Execute trading analysis based on intent"""
        action = intent['action']
        symbol = intent['symbol']

        try:
            if action == 'analyze' and symbol:
                logger.info(f"Executing analysis for {symbol}")
                return self.trading_agent.comprehensive_analysis(symbol)

            elif action == 'scan':
                logger.info("Executing market scan")
                # Use market scanner
                if hasattr(self.trading_agent, 'market_scanner'):
                    return self.trading_agent.market_scanner.scan_market(top_n=5)
                else:
                    return {'error': 'Market scanner not available'}

            elif action == 'risk_assessment' and symbol:
                logger.info(f"Executing risk assessment for {symbol}")
                analysis = self.trading_agent.comprehensive_analysis(symbol)
                return analysis.get('stage_8_risk', {})

            elif action == 'market_context':
                logger.info("Analyzing market context")
                analysis = self.trading_agent.comprehensive_analysis('BTC/USDT')
                return analysis.get('stage_1_market_context', {})

            else:
                return {'error': 'Unknown action or missing parameters'}

        except Exception as e:
            logger.error(f"Analysis execution failed: {e}")
            return {'error': str(e)}

    def _summarize_analysis(self, analysis: Dict) -> str:
        """Create concise summary of analysis results for LLM context"""
        if 'error' in analysis:
            return f"Analysis Error: {analysis['error']}"

        summary_parts = []

        # Symbol and recommendation
        symbol = analysis.get('symbol', 'Unknown')
        recommendation = analysis.get('final_recommendation', {})
        action = recommendation.get('action', 'HOLD')
        confidence = recommendation.get('confidence', 0)

        summary_parts.append(f"Symbol: {symbol}")
        summary_parts.append(f"Recommendation: {action} ({confidence:.1%} confidence)")

        # Key metrics
        if 'entry_price' in recommendation:
            summary_parts.append(f"Entry: ${recommendation['entry_price']:,.2f}")
        if 'stop_loss' in recommendation:
            summary_parts.append(f"Stop Loss: ${recommendation['stop_loss']:,.2f}")
        if 'take_profit' in recommendation:
            summary_parts.append(f"Take Profit: ${recommendation['take_profit']:,.2f}")

        # Risk metrics
        risk = analysis.get('stage_8_risk', {})
        if 'var' in risk:
            summary_parts.append(f"VaR (95%): ${risk['var']:.2f}")
        if 'metrics' in risk and 'sharpe_ratio' in risk['metrics']:
            summary_parts.append(f"Sharpe Ratio: {risk['metrics']['sharpe_ratio']:.2f}")

        # Market context
        context = analysis.get('stage_1_market_context', {})
        if context.get('enabled') and context.get('context'):
            regime = context['context'].get('market_regime', 'unknown')
            summary_parts.append(f"Market Regime: {regime}")

        # Execution ready
        exec_ready = analysis.get('execution_ready', False)
        summary_parts.append(f"Execution Ready: {'✓ Yes' if exec_ready else '✗ No'}")

        if not exec_ready:
            validation = analysis.get('stage_11_validation', {})
            if 'reason' in validation:
                summary_parts.append(f"Reason: {validation['reason']}")

        return "\n".join(summary_parts)

    def _get_llm_response(self, system_context: str = "") -> str:
        """Get response from LLM"""
        messages = [
            {'role': 'system', 'content': self.SYSTEM_PROMPT + system_context}
        ] + self.conversation_history

        try:
            if self.llm_provider == 'openai':
                response = self.llm_client.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.choices[0].message.content

            elif self.llm_provider == 'anthropic':
                # Anthropic API format
                response = self.llm_client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    system=self.SYSTEM_PROMPT + system_context,
                    messages=self.conversation_history
                )
                return response.content[0].text

        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return f"I apologize, but I encountered an error communicating with the AI service: {e}"

    def interactive_session(self):
        """Run interactive chat session"""
        print("\n" + "="*80)
        print("AI TRADING ASSISTANT - Interactive Mode")
        print("="*80)
        print("\nWelcome! I'm your AI trading assistant powered by advanced algorithms.")
        print("I can analyze cryptocurrencies, find opportunities, and explain trading concepts.")
        print("\nType 'quit' or 'exit' to end the session.\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nThank you for using the AI Trading Assistant. Trade safely!")
                    break

                response = self.chat(user_input)
                print(f"\nAssistant: {response}\n")

            except KeyboardInterrupt:
                print("\n\nSession ended by user.")
                break
            except Exception as e:
                print(f"\nError: {e}\n")
                logger.error(f"Interactive session error: {e}", exc_info=True)

    def analyze_with_explanation(self, symbol: str) -> str:
        """
        Analyze and get educational explanation

        Args:
            symbol: Trading pair to analyze

        Returns:
            Educational explanation of analysis
        """
        # Run analysis
        analysis = self.trading_agent.comprehensive_analysis(symbol)

        # Create detailed explanation via LLM
        analysis_json = json.dumps(analysis, default=str, indent=2)

        explanation_prompt = f"""I just completed a comprehensive 12-stage analysis of {symbol}.

Here are the key results:
{self._summarize_analysis(analysis)}

Please provide a clear, educational explanation that:
1. Explains what the recommendation means
2. Breaks down the key metrics (VaR, Sharpe ratio, etc.)
3. Discusses the risks involved
4. Provides context about market conditions
5. Suggests what a beginner should consider

Keep it conversational and educational."""

        self.conversation_history.append({
            'role': 'user',
            'content': explanation_prompt
        })

        response = self._get_llm_response()

        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })

        return response


def main():
    """Main entry point for LLM trading assistant"""
    import argparse

    parser = argparse.ArgumentParser(
        description='LLM-Powered AI Trading Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode with OpenAI
  python llm_trading_assistant.py --interactive --provider openai

  # Interactive mode with Anthropic Claude
  python llm_trading_assistant.py --interactive --provider anthropic

  # Analyze with explanation
  python llm_trading_assistant.py --analyze BTC/USDT --provider openai

  # Custom balance
  python llm_trading_assistant.py --interactive --balance 50000

Environment Variables:
  OPENAI_API_KEY - OpenAI API key
  ANTHROPIC_API_KEY - Anthropic API key
        """
    )

    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Start interactive chat session')
    parser.add_argument('--analyze', '-a', type=str,
                       help='Analyze specific symbol with explanation')
    parser.add_argument('--provider', '-p', type=str, choices=['openai', 'anthropic'],
                       default='openai', help='LLM provider (default: openai)')
    parser.add_argument('--model', '-m', type=str,
                       help='Specific model to use')
    parser.add_argument('--balance', '-b', type=float, default=10000,
                       help='Trading account balance (default: 10000)')
    parser.add_argument('--api-key', type=str,
                       help='API key for LLM provider')

    args = parser.parse_args()

    # Initialize assistant
    try:
        assistant = LLMTradingAssistant(
            balance=args.balance,
            llm_provider=args.provider,
            api_key=args.api_key,
            model=args.model
        )

        if args.interactive:
            assistant.interactive_session()
        elif args.analyze:
            print(f"\nAnalyzing {args.analyze}...\n")
            explanation = assistant.analyze_with_explanation(args.analyze)
            print(f"\n{explanation}\n")
        else:
            parser.print_help()

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
