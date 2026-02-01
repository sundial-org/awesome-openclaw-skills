#!/usr/bin/env python3
"""
Basic OpenSoul Logger Example

This example demonstrates the simplest use case:
1. Initialize logger with BSV private key
2. Log some actions
3. Flush to blockchain

Prerequisites:
- BSV private key set in environment: export BSV_PRIV_WIF="your_key_here"
- BSV wallet funded with at least 0.001 BSV
"""

from Scripts.AuditLogger import AuditLogger
import os
import asyncio
from datetime import datetime


async def main():
    print("🧠 OpenSoul Basic Logger Example\n")
    
    # Check for private key
    priv_wif = os.getenv("BSV_PRIV_WIF")
    if not priv_wif:
        print("❌ Error: BSV_PRIV_WIF environment variable not set")
        print("   Run: export BSV_PRIV_WIF='your_private_key_here'")
        return
    
    # Initialize logger
    print("Initializing logger...")
    logger = AuditLogger(
        priv_wif=priv_wif,
        config={
            "agent_id": "basic-example-agent",
            "session_id": f"example-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        }
    )
    print(f"✓ Logger initialized for agent: basic-example-agent\n")
    
    # Log some actions
    print("Logging actions...")
    
    # Action 1: Agent startup
    logger.log({
        "action": "startup",
        "tokens_in": 10,
        "tokens_out": 20,
        "details": {
            "version": "1.0",
            "timestamp": datetime.now().isoformat()
        },
        "status": "success"
    })
    print("  ✓ Logged: startup")
    
    # Action 2: Simulated web search
    logger.log({
        "action": "web_search",
        "tokens_in": 50,
        "tokens_out": 100,
        "details": {
            "query": "What is Bitcoin SV?",
            "results_count": 10
        },
        "status": "success"
    })
    print("  ✓ Logged: web_search")
    
    # Action 3: Data processing
    logger.log({
        "action": "data_processing",
        "tokens_in": 200,
        "tokens_out": 150,
        "details": {
            "operation": "analyze",
            "dataset": "sample.csv",
            "rows_processed": 1000
        },
        "status": "success"
    })
    print("  ✓ Logged: data_processing")
    
    # Flush logs to blockchain
    print("\nFlushing logs to BSV blockchain...")
    try:
        tx_id = await logger.flush()
        print(f"✓ Logs successfully written to blockchain!")
        print(f"\n📍 Transaction ID: {tx_id}")
        print(f"🔗 View at: https://whatsonchain.com/tx/{tx_id}")
    except Exception as e:
        print(f"❌ Error flushing logs: {e}")
        print("   Tip: Check your BSV balance and network connectivity")
    
    print("\n✅ Example complete!")


if __name__ == "__main__":
    asyncio.run(main())
