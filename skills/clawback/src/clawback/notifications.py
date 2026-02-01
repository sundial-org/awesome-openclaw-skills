"""
Notification system for Congressional Trade Bot
Supports Telegram notifications for trade alerts
"""
import json
import logging
import requests
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications via Telegram bot"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.enabled = bool(bot_token and chat_id)

        if self.enabled:
            logger.info("Telegram notifications enabled")
        else:
            logger.warning("Telegram notifications disabled (missing token or chat_id)")

    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send a message to Telegram"""
        if not self.enabled:
            return False

        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def notify_new_trade(self, trade: dict) -> bool:
        """Notify about a new congressional trade discovered"""
        ticker = trade.get('ticker', 'N/A')
        tx_type = trade.get('transaction_type', 'N/A').upper()
        rep = trade.get('representative', 'Unknown')
        amount = trade.get('amount_range', trade.get('amount', 'N/A'))
        date = trade.get('disclosure_date', 'N/A')

        emoji = "🟢" if tx_type == "PURCHASE" else "🔴"

        message = f"""
{emoji} *New Congressional Trade*

*{rep}*
{tx_type} *{ticker}*
Amount: {amount}
Disclosed: {date}

_Processing for execution..._
"""
        return self.send_message(message)

    def notify_trade_executed(self, trade: dict) -> bool:
        """Notify about a trade we executed"""
        symbol = trade.get('symbol', 'N/A')
        action = trade.get('action', 'N/A')
        qty = trade.get('quantity', 0)
        price = trade.get('estimated_price', 0)
        cost = trade.get('estimated_cost', 0)

        emoji = "✅" if action == "BUY" else "💰"

        message = f"""
{emoji} *Trade Executed*

{action} *{qty}* shares of *{symbol}*
Price: ${price:.2f}
Total: ${cost:.2f}

_Position tracking enabled_
"""
        return self.send_message(message)

    def notify_stop_loss(self, stop_info: dict) -> bool:
        """Notify about a stop-loss execution"""
        symbol = stop_info.get('symbol', 'N/A')
        qty = stop_info.get('quantity', 0)
        current = stop_info.get('current_price', 0)
        stop = stop_info.get('stop_price', 0)
        entry = stop_info.get('entry_price', 0)
        pnl = stop_info.get('pnl_percent', 0)

        emoji = "🛑" if pnl < 0 else "🎯"

        message = f"""
{emoji} *Stop-Loss Triggered*

SOLD *{qty}* shares of *{symbol}*
Entry: ${entry:.2f}
Stop: ${stop:.2f}
Exit: ${current:.2f}
P/L: *{pnl:+.1f}%*
"""
        return self.send_message(message)

    def notify_risk_alert(self, risk_info: dict) -> bool:
        """Notify about risk management alerts"""
        status = risk_info.get('status', 'unknown')
        warnings = risk_info.get('warnings', [])

        if not warnings:
            return True  # No alerts

        message = "⚠️ *Risk Alert*\n\n"
        for w in warnings:
            message += f"• {w}\n"

        if status == 'halt':
            message += "\n🛑 *Trading halted*"

        return self.send_message(message)

    def notify_daily_summary(self, summary: dict) -> bool:
        """Send daily trading summary"""
        trades = summary.get('total_trades', 0)
        pnl = summary.get('daily_pnl', 0)
        positions = summary.get('open_positions', 0)
        new_disclosures = summary.get('new_disclosures', 0)

        emoji = "📈" if pnl >= 0 else "📉"

        message = f"""
{emoji} *Daily Summary*

New Disclosures: {new_disclosures}
Trades Executed: {trades}
Open Positions: {positions}
Daily P/L: ${pnl:+,.2f}
"""
        return self.send_message(message)


class NotificationManager:
    """Manage all notification channels"""

    def __init__(self, config: dict):
        self.config = config
        self.notifiers = []

        # Initialize Telegram if configured
        telegram_config = config.get('notifications', {}).get('telegram', {})
        if telegram_config.get('enabled', False):
            self.notifiers.append(TelegramNotifier(
                bot_token=telegram_config.get('botToken', ''),
                chat_id=telegram_config.get('chatId', '')
            ))

    def notify_new_trade(self, trade: dict):
        """Notify all channels about new trade"""
        for notifier in self.notifiers:
            notifier.notify_new_trade(trade)

    def notify_trade_executed(self, trade: dict):
        """Notify all channels about executed trade"""
        for notifier in self.notifiers:
            notifier.notify_trade_executed(trade)

    def notify_stop_loss(self, stop_info: dict):
        """Notify all channels about stop-loss"""
        for notifier in self.notifiers:
            notifier.notify_stop_loss(stop_info)

    def notify_risk_alert(self, risk_info: dict):
        """Notify all channels about risk alerts"""
        for notifier in self.notifiers:
            notifier.notify_risk_alert(risk_info)

    def notify_daily_summary(self, summary: dict):
        """Notify all channels with daily summary"""
        for notifier in self.notifiers:
            notifier.notify_daily_summary(summary)
