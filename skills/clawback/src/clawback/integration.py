"""
Integration between congressional data system and E*TRADE trading bot
"""
import json
import logging
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from congress_data.config import CongressConfig
from congress_data.data_collector import CongressDataCollector
from congress_data.alert_manager import AlertManager

# Import trading bot components
try:
    from broker_adapter import get_broker_adapter
    from trade_engine import TradeEngine
    from congress_tracker import CongressTracker
except ImportError:
    print("Warning: Trading bot components not found. Make sure to install dependencies.")
    get_broker_adapter = None
    TradeEngine = None
    CongressTracker = None

logger = logging.getLogger(__name__)

class TradingIntegration:
    """Integrates congressional data with broker trading bot"""

    def __init__(self, congress_config_path=None, broker_config_path=None):
        # Setup logging
        self.setup_logging()

        # Initialize congressional data system
        self.congress_config = CongressConfig(congress_config_path)
        self.data_collector = CongressDataCollector(self.congress_config)
        self.alert_manager = AlertManager(self.congress_config)

        # Initialize trading bot if available
        self.broker = None
        self.trade_engine = None

        if broker_config_path and get_broker_adapter:
            try:
                with open(broker_config_path, 'r') as f:
                    broker_config = json.load(f)

                self.broker = get_broker_adapter(broker_config)
                self.trade_engine = TradeEngine(self.broker, broker_config)

                logger.info(f"Trading bot integration initialized with {self.broker.BROKER_NAME}")
            except Exception as e:
                logger.error(f"Error initializing trading bot: {e}")
        
        # Integration state
        self.processed_trades = []
        self.integration_history = []
        self.history_file = "data/integration_history.json"
        
        # Load history
        self.load_history()
        
        logger.info("Trading integration system initialized")
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "integration.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def load_history(self):
        """Load integration history from file"""
        try:
            with open(self.history_file, 'r') as f:
                self.integration_history = json.load(f)
            logger.info(f"Loaded {len(self.integration_history)} integration records")
        except (FileNotFoundError, json.JSONDecodeError):
            self.integration_history = []
    
    def save_history(self):
        """Save integration history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.integration_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving integration history: {e}")
    
    def filter_trades_for_trading(self, trades):
        """Filter trades suitable for automated trading"""
        filtered_trades = []
        
        for trade in trades:
            try:
                # Check basic requirements
                if not all(key in trade for key in ['ticker', 'transaction_type', 'amount']):
                    continue
                
                ticker = trade['ticker'].strip().upper()
                trade_type = trade['transaction_type'].lower()
                amount = trade.get('amount', 0)
                
                # Skip if ticker is invalid
                if not ticker or len(ticker) > 5:
                    continue
                
                # Skip if trade type is not purchase/sale
                if trade_type not in ['purchase', 'sale']:
                    continue
                
                # Check minimum trade size
                min_trade_size = self.congress_config.get_politician_config().get('minimum_trade_size', 10000)
                if amount < min_trade_size:
                    continue
                
                # Check if we've already processed this trade
                trade_key = self.get_trade_key(trade)
                if trade_key in self.processed_trades:
                    continue
                
                # Additional filtering based on politician
                politician = trade.get('politician', '').lower()
                
                # Prioritize certain politicians
                priority_politicians = ['nancy pelosi', 'mitch mcconnell', 'chuck schumer']
                is_priority = any(p in politician for p in priority_politicians)
                
                filtered_trade = trade.copy()
                filtered_trade['priority'] = is_priority
                filtered_trade['trade_key'] = trade_key
                
                filtered_trades.append(filtered_trade)
                
            except Exception as e:
                logger.debug(f"Error filtering trade: {e}")
                continue
        
        # Sort by priority and amount (largest trades first)
        filtered_trades.sort(key=lambda x: (x['priority'], x['amount']), reverse=True)
        
        logger.info(f"Filtered {len(filtered_trades)} trades for potential trading")
        return filtered_trades
    
    def get_trade_key(self, trade):
        """Create unique key for a trade"""
        key_parts = [
            trade.get('politician', ''),
            trade.get('ticker', ''),
            trade.get('transaction_date', ''),
            trade.get('transaction_type', ''),
            str(round(trade.get('amount', 0), 2))
        ]
        return "_".join(str(p) for p in key_parts)
    
    def analyze_trade_for_execution(self, trade):
        """Analyze if a trade should be executed"""
        analysis = {
            'should_execute': False,
            'reason': '',
            'confidence': 0,
            'recommended_action': None,
            'estimated_quantity': 0,
            'estimated_cost': 0
        }
        
        try:
            if not self.broker or not self.trade_engine:
                analysis['reason'] = 'Trading bot not initialized'
                return analysis
            
            # Check if market is open
            if not self.trade_engine.is_market_open():
                analysis['reason'] = 'Market is closed'
                return analysis
            
            # Get account balance
            balance_info = self.broker.get_account_balance()
            if not balance_info:
                analysis['reason'] = 'Could not get account balance'
                return analysis
            
            account_balance = balance_info['cash_available']
            
            # Calculate scaled trade
            trade_calc = self.trade_engine.calculate_scaled_trade(trade, account_balance)
            if not trade_calc:
                analysis['reason'] = 'Could not calculate scaled trade'
                return analysis
            
            # Check position limits
            symbol = trade_calc['symbol']
            quantity = trade_calc['quantity']
            action = trade_calc['action']
            
            if not self.trade_engine.check_position_limits(symbol, quantity, action, account_balance):
                analysis['reason'] = 'Position limits exceeded'
                return analysis
            
            # Check daily loss limit
            if not self.trade_engine.check_daily_loss_limit():
                analysis['reason'] = 'Daily loss limit exceeded'
                return analysis
            
            # All checks passed
            analysis['should_execute'] = True
            analysis['reason'] = 'All checks passed'
            analysis['confidence'] = self.calculate_confidence(trade)
            analysis['recommended_action'] = action
            analysis['estimated_quantity'] = quantity
            analysis['estimated_cost'] = trade_calc['estimated_cost']
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing trade: {e}")
            analysis['reason'] = f'Analysis error: {str(e)}'
            return analysis
    
    def calculate_confidence(self, trade):
        """Calculate confidence score for a trade"""
        confidence = 50  # Base confidence
        
        try:
            # Factors increasing confidence
            politician = trade.get('politician', '').lower()
            amount = trade.get('amount', 0)
            trade_type = trade.get('transaction_type', '').lower()
            
            # Priority politicians
            priority_politicians = ['nancy pelosi', 'mitch mcconnell', 'chuck schumer']
            if any(p in politician for p in priority_politicians):
                confidence += 20
            
            # Large trade size
            if amount > 1000000:
                confidence += 15
            elif amount > 100000:
                confidence += 10
            elif amount > 50000:
                confidence += 5
            
            # Recent trade (if date available)
            if 'transaction_date' in trade:
                try:
                    if isinstance(trade['transaction_date'], str):
                        # Try to parse date
                        from datetime import datetime
                        trade_date = datetime.fromisoformat(trade['transaction_date'].replace('Z', '+00:00'))
                        days_ago = (datetime.now() - trade_date).days
                        
                        if days_ago <= 7:
                            confidence += 10
                        elif days_ago <= 30:
                            confidence += 5
                    elif isinstance(trade['transaction_date'], datetime):
                        days_ago = (datetime.now() - trade['transaction_date']).days
                        if days_ago <= 7:
                            confidence += 10
                        elif days_ago <= 30:
                            confidence += 5
                except:
                    pass
            
            # Trade type (buys might be more reliable than sells)
            if trade_type == 'purchase':
                confidence += 5
            
            # Cap at 100
            confidence = min(confidence, 100)
            
        except Exception as e:
            logger.debug(f"Error calculating confidence: {e}")
        
        return confidence
    
    def execute_trade(self, trade, analysis):
        """Execute a trade through the trading bot"""
        try:
            if not self.broker:
                logger.error("E*TRADE client not initialized")
                return False
            
            # Prepare order details
            order_details = {
                'symbol': trade['ticker'].upper(),
                'quantity': analysis['estimated_quantity'],
                'action': analysis['recommended_action'],
                'price_type': 'MARKET',
                'order_type': 'EQ'
            }
            
            # Execute order
            success = self.broker.place_order(
                self.broker.account_id,
                order_details
            )
            
            if success:
                # Record execution
                execution_record = {
                    'timestamp': datetime.now().isoformat(),
                    'trade': trade,
                    'analysis': analysis,
                    'order_details': order_details,
                    'status': 'executed'
                }
                
                self.integration_history.append(execution_record)
                self.processed_trades.append(trade.get('trade_key', ''))
                
                # Save history
                self.save_history()
                
                logger.info(f"Trade executed: {order_details['action']} {order_details['quantity']} "
                          f"{order_details['symbol']} (confidence: {analysis['confidence']}%)")
                return True
            else:
                logger.error("Trade execution failed")
                return False
                
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False
    
    def process_trades_automatically(self, max_trades=5):
        """Process trades automatically for execution"""
        try:
            logger.info("Starting automatic trade processing")
            
            # Collect recent trades
            trades = self.data_collector.collect_all_data()
            
            # Filter for trading
            filtered_trades = self.filter_trades_for_trading(trades)
            
            if not filtered_trades:
                logger.info("No suitable trades found for execution")
                return []
            
            # Process trades
            executed_trades = []
            
            for trade in filtered_trades[:max_trades]:  # Limit to max_trades
                # Analyze trade
                analysis = self.analyze_trade_for_execution(trade)
                
                if analysis['should_execute'] and analysis['confidence'] >= 70:
                    # Execute trade
                    success = self.execute_trade(trade, analysis)
                    
                    if success:
                        executed_trades.append({
                            'trade': trade,
                            'analysis': analysis,
                            'executed': True
                        })
                        
                        # Small delay between trades
                        import time
                        time.sleep(2)
                else:
                    logger.info(f"Trade not executed: {trade.get('ticker')} "
                              f"(confidence: {analysis['confidence']}%, reason: {analysis['reason']})")
            
            logger.info(f"Executed {len(executed_trades)} trades automatically")
            return executed_trades
            
        except Exception as e:
            logger.error(f"Error in automatic trade processing: {e}")
            return []
    
    def get_integration_status(self):
        """Get integration system status"""
        status = {
            'congress_system_ready': bool(self.data_collector and self.alert_manager),
            'broker_ready': bool(self.broker and self.trade_engine),
            'broker_name': self.broker.BROKER_NAME if self.broker else None,
            'processed_trades_count': len(self.processed_trades),
            'integration_history_count': len(self.integration_history),
            'last_execution': self.integration_history[-1] if self.integration_history else None
        }
        
        return status
    
    def run_demo_mode(self):
        """Run in demo mode (analysis only, no execution)"""
        print("\n" + "="*60)
        print("Trading Integration - Demo Mode")
        print("="*60)
        print("Analyzing trades without execution...\n")
        
        # Collect recent trades
        trades = self.data_collector.collect_all_data()
        filtered_trades = self.filter_trades_for_trading(trades)
        
        if not filtered_trades:
            print("No suitable trades found.")
            return
        
        print(f"Found {len(filtered_trades)} potential trades:\n")
        
        for i, trade in enumerate(filtered_trades[:10], 1):  # Show first 10
            politician = trade.get('politician', 'Unknown')
            ticker = trade.get('ticker', 'Unknown')
            trade_type = trade.get('transaction_type', '').upper()
            amount = trade.get('amount', 0)
            priority = trade.get('priority', False)
            
            if amount >= 1000000:
                amount_str = f"${amount/1000000:.2f}M"
            else:
                amount_str = f"${amount/1000:.1f}K"
            
            print(f"{i}. {politician}: {trade_type} {ticker} ({amount_str})")
            if priority:
                print("   ⭐ PRIORITY TRADE")
            
            # Analyze trade
            analysis = self.analyze_trade_for_execution(trade)
            
            print(f"   Confidence: {analysis['confidence']}%")
            print(f"   Recommendation: {'EXECUTE' if analysis['should_execute'] else 'SKIP'}")
            print(f"   Reason: {analysis['reason']}")
            
            if analysis['should_execute']:
                print(f"   Estimated: {analysis['estimated_quantity']} shares "
                      f"(${analysis['estimated_cost']:,.2f})")
            
            print()
        
        print("="*60)
        print(f"Total trades analyzed: {len(filtered_trades)}")
        print("Note: Demo mode only analyzes trades. No orders are placed.")

def main():
    """Main entry point for integration system"""
    print("Congressional Trade Data & Broker Trading Integration")
    print("="*60)

    # Configuration paths
    congress_config = "config/congress_config.json"
    broker_config = "config/config.json"

    # Check if config files exist
    if not os.path.exists(congress_config):
        print(f"Warning: Congress config not found at {congress_config}")
        print("Creating default configuration...")
        # Create default config
        config_dir = os.path.dirname(congress_config)
        os.makedirs(config_dir, exist_ok=True)

        default_config = {
            "sources": {
                "senate": {
                    "enabled": True,
                    "check_interval_hours": 24
                },
                "house": {
                    "enabled": True,
                    "check_interval_hours": 24
                }
            },
            "politicians": {
                "track_all": False,
                "specific_politicians": ["Nancy Pelosi", "Dan Crenshaw", "Tommy Tuberville"],
                "minimum_trade_size": 10000
            },
            "alerting": {
                "enabled": False
            }
        }

        with open(congress_config, 'w') as f:
            json.dump(default_config, f, indent=2)

        print(f"Default config created at {congress_config}")
        print("Please edit to add API keys and configure alerts")

    if not os.path.exists(broker_config):
        print(f"Error: Broker config not found at {broker_config}")
        print("Please run the trading bot setup first.")
        return

    # Initialize integration system
    integration = TradingIntegration(congress_config, broker_config)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'demo':
            integration.run_demo_mode()
        elif sys.argv[1] == 'auto':
            max_trades = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            integration.process_trades_automatically(max_trades)
        elif sys.argv[1] == 'status':
            status = integration.get_integration_status()
            print(json.dumps(status, indent=2))
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Available commands: demo, auto [max_trades], status")
    else:
        # Default to demo mode
        integration.run_demo_mode()

if __name__ == "__main__":
    main()