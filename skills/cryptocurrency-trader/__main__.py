#!/usr/bin/env python3
"""
AI Trading Skill - Module Entry Point

Allows the skill to be invoked as a module:
    python -m cryptocurrency_trader_skill analyze BTC/USDT --balance 10000
"""

from skill import main

if __name__ == '__main__':
    main()
