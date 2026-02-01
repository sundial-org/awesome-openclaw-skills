#!/usr/bin/env python3
"""
Research Agent with Memory Example

This example demonstrates:
1. Checking past research history before performing searches
2. Avoiding redundant work
3. Building on previous knowledge
4. Generating session summaries

Prerequisites:
- BSV private key set in environment
- Run basic_logger.py first to create some history
"""

from Scripts.AuditLogger import AuditLogger
import os
import asyncio
from datetime import datetime


class ResearchAgent:
    def __init__(self, agent_id="research-agent"):
        self.agent_id = agent_id
        self.logger = AuditLogger(
            priv_wif=os.getenv("BSV_PRIV_WIF"),
            config={
                "agent_id": agent_id,
                "session_id": f"research-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "flush_threshold": 5  # Auto-flush after 5 logs
            }
        )
        self.session_start = datetime.now()
    
    async def search_with_memory(self, query):
        """Perform search but check if we've researched this before"""
        print(f"\n🔍 Researching: '{query}'")
        
        # Retrieve all past logs
        print("   Checking past research...")
        history = await self.logger.get_history()
        
        # Find similar past searches
        similar_searches = []
        for log in history:
            for metric in log.get("metrics", []):
                if metric.get("action") == "web_search":
                    past_query = metric.get("details", {}).get("query", "")
                    # Simple similarity check (case-insensitive substring match)
                    if (query.lower() in past_query.lower() or 
                        past_query.lower() in query.lower()):
                        similar_searches.append({
                            "query": past_query,
                            "timestamp": metric.get("ts", "unknown"),
                            "session": log.get("session_id", "unknown")
                        })
        
        # Report findings
        if similar_searches:
            print(f"   💡 Found {len(similar_searches)} similar past search(es):")
            for search in similar_searches[:3]:  # Show first 3
                print(f"      - '{search['query']}' ({search['timestamp']})")
            if len(similar_searches) > 3:
                print(f"      ... and {len(similar_searches) - 3} more")
        else:
            print("   ℹ️  No similar past searches found")
        
        # Simulate new search
        results_count = 10
        
        # Log the search
        self.logger.log({
            "action": "web_search",
            "tokens_in": 50,
            "tokens_out": 200,
            "details": {
                "query": query,
                "results_count": results_count,
                "similar_past_searches": len(similar_searches),
                "leveraged_past_research": len(similar_searches) > 0
            },
            "status": "success"
        })
        
        print(f"   ✓ Search completed ({results_count} results)")
        return results_count
    
    async def analyze_trends(self):
        """Analyze research patterns from history"""
        print("\n📊 Analyzing research trends...")
        
        history = await self.logger.get_history()
        
        # Count searches by topic
        search_topics = {}
        for log in history:
            for metric in log.get("metrics", []):
                if metric.get("action") == "web_search":
                    query = metric.get("details", {}).get("query", "")
                    # Extract topic (simplified - first word)
                    topic = query.split()[0].lower() if query else "unknown"
                    search_topics[topic] = search_topics.get(topic, 0) + 1
        
        if search_topics:
            print("   Most researched topics:")
            for topic, count in sorted(search_topics.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"      {topic}: {count} searches")
        
        # Log analysis
        self.logger.log({
            "action": "trend_analysis",
            "tokens_in": 100,
            "tokens_out": 150,
            "details": {
                "topics": search_topics,
                "most_common_topic": max(search_topics, key=search_topics.get) if search_topics else None
            },
            "status": "success"
        })
        
        return search_topics
    
    async def generate_summary(self):
        """Generate session summary"""
        print("\n📝 Generating session summary...")
        
        history = await self.logger.get_history()
        
        # Filter for current session
        current_session_logs = [
            log for log in history 
            if log.get("session_id") == self.logger.config["session_id"]
        ]
        
        # Calculate metrics
        total_searches = sum(
            len([m for m in log.get("metrics", []) if m.get("action") == "web_search"])
            for log in current_session_logs
        )
        
        total_tokens = sum(
            log.get("total_tokens_in", 0) + log.get("total_tokens_out", 0)
            for log in current_session_logs
        )
        
        duration = datetime.now() - self.session_start
        
        summary = {
            "session_id": self.logger.config["session_id"],
            "duration_seconds": duration.total_seconds(),
            "total_searches": total_searches,
            "total_tokens": total_tokens,
            "searches_per_minute": total_searches / (duration.total_seconds() / 60) if duration.total_seconds() > 0 else 0
        }
        
        print(f"   Duration: {duration}")
        print(f"   Searches: {total_searches}")
        print(f"   Tokens: {total_tokens}")
        
        # Log summary
        self.logger.log({
            "action": "session_summary",
            "tokens_in": 20,
            "tokens_out": 50,
            "details": summary,
            "status": "completed"
        })
        
        return summary
    
    async def finish(self):
        """Complete session and flush logs"""
        await self.generate_summary()
        
        print("\n💾 Flushing logs to blockchain...")
        try:
            tx_id = await self.logger.flush()
            print(f"✓ Session archived to blockchain")
            print(f"🔗 Transaction: https://whatsonchain.com/tx/{tx_id}")
            return tx_id
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


async def main():
    print("🧠 OpenSoul Research Agent Example\n")
    
    # Check prerequisites
    if not os.getenv("BSV_PRIV_WIF"):
        print("❌ Error: BSV_PRIV_WIF not set")
        return
    
    # Create agent
    agent = ResearchAgent()
    
    # Perform research
    await agent.search_with_memory("Bitcoin SV scalability")
    await agent.search_with_memory("BSV transaction fees")
    await agent.search_with_memory("Bitcoin SV use cases")
    
    # Analyze trends
    await agent.analyze_trends()
    
    # Finish session
    await agent.finish()
    
    print("\n✅ Research session complete!")


if __name__ == "__main__":
    asyncio.run(main())
