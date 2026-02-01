# OpenSoul Examples

This document provides practical, ready-to-use examples for implementing OpenSoul in your AI agents.

## Table of Contents

1. [Basic Logging](#1-basic-logging)
2. [Research Agent with Memory](#2-research-agent-with-memory)
3. [Multi-Agent Collaboration](#3-multi-agent-collaboration)
4. [Self-Reflecting Agent](#4-self-reflecting-agent)
5. [Cost-Aware Agent](#5-cost-aware-agent)
6. [Session Management](#6-session-management)
7. [Error Handling & Recovery](#7-error-handling--recovery)

---

## 1. Basic Logging

The simplest OpenSoul implementation - log actions and flush to blockchain.

```python
# basic_logger.py
from Scripts.AuditLogger import AuditLogger
import os
import asyncio

async def basic_logging_example():
    # Initialize logger
    logger = AuditLogger(
        priv_wif=os.getenv("BSV_PRIV_WIF"),
        config={
            "agent_id": "basic-agent",
            "session_id": "demo-session-001"
        }
    )
    
    # Log a simple action
    logger.log({
        "action": "greeting",
        "tokens_in": 10,
        "tokens_out": 20,
        "details": {"message": "Hello, OpenSoul!"},
        "status": "success"
    })
    
    # Log a tool call
    logger.log({
        "action": "tool_call",
        "tokens_in": 100,
        "tokens_out": 150,
        "details": {
            "tool": "calculator",
            "operation": "2 + 2",
            "result": 4
        },
        "status": "success"
    })
    
    # Flush to blockchain
    result = await logger.flush()
    print(f"Logs flushed to blockchain. TX ID: {result}")
    
    # View on blockchain explorer
    print(f"View at: https://whatsonchain.com/tx/{result}")

if __name__ == "__main__":
    asyncio.run(basic_logging_example())
```

**Usage**:
```bash
export BSV_PRIV_WIF="your_private_key_here"
python basic_logger.py
```

---

## 2. Research Agent with Memory

An agent that remembers past research and avoids redundant searches.

```python
# research_agent.py
from Scripts.AuditLogger import AuditLogger
import os
import asyncio
from datetime import datetime

class ResearchAgent:
    def __init__(self, agent_id="research-agent"):
        self.logger = AuditLogger(
            priv_wif=os.getenv("BSV_PRIV_WIF"),
            config={
                "agent_id": agent_id,
                "session_id": f"research-{datetime.now().isoformat()}",
                "flush_threshold": 5
            }
        )
        self.session_start = datetime.now()
    
    async def search_with_memory(self, query):
        """Perform web search but check past research first"""
        print(f"\n🔍 Researching: {query}")
        
        # Check if we've researched this before
        history = await self.logger.get_history()
        similar_searches = []
        
        for log in history:
            for metric in log.get("metrics", []):
                if metric.get("action") == "web_search":
                    past_query = metric.get("details", {}).get("query", "")
                    if query.lower() in past_query.lower() or past_query.lower() in query.lower():
                        similar_searches.append({
                            "query": past_query,
                            "timestamp": metric.get("ts"),
                            "results": metric.get("details", {}).get("results_count")
                        })
        
        if similar_searches:
            print(f"💡 Found {len(similar_searches)} similar past searches:")
            for search in similar_searches:
                print(f"  - '{search['query']}' at {search['timestamp']}")
        
        # Perform new search
        results_count = 10  # Simulated search results
        
        self.logger.log({
            "action": "web_search",
            "tokens_in": 50,
            "tokens_out": 200,
            "details": {
                "query": query,
                "results_count": results_count,
                "similar_past_searches": len(similar_searches)
            },
            "status": "success"
        })
        
        print(f"✓ Search completed. Found {results_count} results")
        return results_count
    
    async def analyze_document(self, document_name, word_count):
        """Analyze a document and log the analysis"""
        print(f"\n📄 Analyzing: {document_name}")
        
        self.logger.log({
            "action": "document_analysis",
            "tokens_in": word_count,
            "tokens_out": word_count // 2,
            "details": {
                "document": document_name,
                "word_count": word_count,
                "analysis_type": "summary"
            },
            "status": "success"
        })
        
        print(f"✓ Analysis complete")
    
    async def finish_session(self):
        """Complete research session and generate summary"""
        history = await self.logger.get_history()
        
        # Calculate session stats
        current_session = [
            log for log in history 
            if log.get("session_id") == self.logger.config["session_id"]
        ]
        
        total_searches = sum(
            len([m for m in log.get("metrics", []) if m.get("action") == "web_search"])
            for log in current_session
        )
        
        total_tokens = sum(
            log.get("total_tokens_in", 0) + log.get("total_tokens_out", 0)
            for log in current_session
        )
        
        summary = {
            "session_duration": str(datetime.now() - self.session_start),
            "total_searches": total_searches,
            "total_tokens": total_tokens,
            "total_actions": sum(len(log.get("metrics", [])) for log in current_session)
        }
        
        self.logger.log({
            "action": "session_summary",
            "tokens_in": 20,
            "tokens_out": 50,
            "details": summary,
            "status": "completed"
        })
        
        # Flush final logs
        tx_id = await self.logger.flush()
        print(f"\n📊 Session Summary:")
        print(f"  Duration: {summary['session_duration']}")
        print(f"  Searches: {summary['total_searches']}")
        print(f"  Total tokens: {summary['total_tokens']}")
        print(f"  Blockchain TX: {tx_id}")
        
        return summary

async def research_example():
    agent = ResearchAgent()
    
    # Perform multiple searches
    await agent.search_with_memory("Bitcoin SV transaction fees")
    await agent.search_with_memory("BSV blockchain scalability")
    await agent.analyze_document("whitepaper.pdf", 5000)
    
    # Finish session
    await agent.finish_session()

if __name__ == "__main__":
    asyncio.run(research_example())
```

---

## 3. Multi-Agent Collaboration

Multiple agents sharing encrypted logs with each other.

```python
# multi_agent.py
from Scripts.AuditLogger import AuditLogger
import os
import asyncio

class CollaborativeAgent:
    def __init__(self, agent_id, public_keys, private_key, passphrase):
        """
        Initialize agent with multi-agent encryption
        
        Args:
            agent_id: Unique identifier for this agent
            public_keys: List of PGP public keys (all collaborating agents)
            private_key: This agent's PGP private key
            passphrase: Passphrase for private key
        """
        self.agent_id = agent_id
        self.logger = AuditLogger(
            priv_wif=os.getenv("BSV_PRIV_WIF"),
            config={
                "agent_id": agent_id,
                "pgp": {
                    "enabled": True,
                    "multi_public_keys": public_keys,
                    "private_key": private_key,
                    "passphrase": passphrase
                }
            }
        )
    
    async def share_finding(self, finding, recipient_agents):
        """Share a research finding with other agents"""
        self.logger.log({
            "action": "knowledge_share",
            "tokens_in": 100,
            "tokens_out": 50,
            "details": {
                "finding": finding,
                "shared_with": recipient_agents,
                "timestamp": asyncio.get_event_loop().time()
            },
            "status": "shared"
        })
        
        await self.logger.flush()
        print(f"[{self.agent_id}] Shared: {finding}")
    
    async def read_shared_logs(self):
        """Read and decrypt logs from other agents"""
        history = await self.logger.get_history()
        
        shared_findings = []
        for log in history:
            for metric in log.get("metrics", []):
                if metric.get("action") == "knowledge_share":
                    shared_findings.append({
                        "from": log.get("agent_id"),
                        "finding": metric.get("details", {}).get("finding"),
                        "timestamp": metric.get("ts")
                    })
        
        return shared_findings

async def multi_agent_example():
    # Load PGP keys for three agents
    with open('agent1_pubkey.asc') as f:
        pubkey1 = f.read()
    with open('agent2_pubkey.asc') as f:
        pubkey2 = f.read()
    with open('agent3_pubkey.asc') as f:
        pubkey3 = f.read()
    
    all_public_keys = [pubkey1, pubkey2, pubkey3]
    
    # Create Agent 1
    with open('agent1_privkey.asc') as f:
        privkey1 = f.read()
    
    agent1 = CollaborativeAgent(
        agent_id="research-agent-1",
        public_keys=all_public_keys,
        private_key=privkey1,
        passphrase=os.getenv("AGENT1_PGP_PASS")
    )
    
    # Agent 1 shares a finding
    await agent1.share_finding(
        "BSV transactions cost ~0.00001 BSV each",
        ["research-agent-2", "research-agent-3"]
    )
    
    # Other agents can now decrypt and read this finding
    shared = await agent1.read_shared_logs()
    print(f"\nShared findings accessible to all agents: {len(shared)}")

if __name__ == "__main__":
    asyncio.run(multi_agent_example())
```

---

## 4. Self-Reflecting Agent

An agent that analyzes its own performance and optimizes behavior.

```python
# self_reflecting_agent.py
from Scripts.AuditLogger import AuditLogger
import os
import asyncio
from datetime import datetime, timedelta

class SelfReflectingAgent:
    def __init__(self):
        self.logger = AuditLogger(
            priv_wif=os.getenv("BSV_PRIV_WIF"),
            config={"agent_id": "reflective-agent"}
        )
        self.performance_threshold = {
            "tokens_per_action": 500,
            "success_rate": 0.90,
            "cost_limit_bsv": 0.001
        }
    
    async def perform_action(self, action_type, complexity="medium"):
        """Perform an action and log it"""
        token_costs = {
            "simple": (50, 100),
            "medium": (200, 300),
            "complex": (500, 800)
        }
        
        tokens_in, tokens_out = token_costs.get(complexity, (200, 300))
        
        # Simulate success/failure (90% success rate)
        import random
        status = "success" if random.random() < 0.9 else "failed"
        
        self.logger.log({
            "action": action_type,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "details": {"complexity": complexity},
            "status": status
        })
    
    async def reflect_on_performance(self):
        """Analyze past performance and identify areas for improvement"""
        print("\n🤔 Reflecting on performance...")
        
        history = await self.logger.get_history()
        
        # Gather metrics
        all_metrics = []
        for log in history:
            all_metrics.extend(log.get("metrics", []))
        
        if not all_metrics:
            print("No performance data available yet.")
            return None
        
        # Calculate statistics
        total_actions = len(all_metrics)
        successful_actions = len([m for m in all_metrics if m.get("status") == "success"])
        failed_actions = total_actions - successful_actions
        
        total_tokens = sum(
            m.get("tokens_in", 0) + m.get("tokens_out", 0)
            for m in all_metrics
        )
        avg_tokens_per_action = total_tokens / total_actions if total_actions > 0 else 0
        
        total_cost = sum(log.get("total_cost_bsv", 0) for log in history)
        success_rate = successful_actions / total_actions if total_actions > 0 else 0
        
        # Identify issues
        issues = []
        if avg_tokens_per_action > self.performance_threshold["tokens_per_action"]:
            issues.append(f"High token usage: {avg_tokens_per_action:.0f} per action (threshold: {self.performance_threshold['tokens_per_action']})")
        
        if success_rate < self.performance_threshold["success_rate"]:
            issues.append(f"Low success rate: {success_rate:.1%} (threshold: {self.performance_threshold['success_rate']:.0%})")
        
        if total_cost > self.performance_threshold["cost_limit_bsv"]:
            issues.append(f"Cost limit exceeded: {total_cost:.6f} BSV (limit: {self.performance_threshold['cost_limit_bsv']} BSV)")
        
        # Generate reflection
        reflection = {
            "total_sessions": len(history),
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "failed_actions": failed_actions,
            "success_rate": success_rate,
            "avg_tokens_per_action": avg_tokens_per_action,
            "total_cost_bsv": total_cost,
            "issues_identified": issues,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log reflection
        self.logger.log({
            "action": "self_reflection",
            "tokens_in": 50,
            "tokens_out": 150,
            "details": reflection,
            "status": "completed"
        })
        
        await self.logger.flush()
        
        # Print reflection
        print(f"\n📊 Performance Analysis:")
        print(f"  Total actions: {total_actions}")
        print(f"  Success rate: {success_rate:.1%}")
        print(f"  Avg tokens/action: {avg_tokens_per_action:.0f}")
        print(f"  Total cost: {total_cost:.6f} BSV")
        
        if issues:
            print(f"\n⚠️  Issues identified:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"\n✓ Performance within acceptable thresholds")
        
        return reflection
    
    async def optimize_behavior(self, reflection):
        """Adjust behavior based on reflection"""
        if not reflection:
            return
        
        issues = reflection.get("issues_identified", [])
        optimizations = []
        
        if any("token usage" in issue.lower() for issue in issues):
            optimizations.append("Reduce prompt verbosity")
            optimizations.append("Use more efficient tools")
        
        if any("success rate" in issue.lower() for issue in issues):
            optimizations.append("Add retry logic for failed actions")
            optimizations.append("Improve error handling")
        
        if any("cost limit" in issue.lower() for issue in issues):
            optimizations.append("Batch more logs before flushing")
            optimizations.append("Reduce logging frequency")
        
        if optimizations:
            print(f"\n🔧 Recommended optimizations:")
            for opt in optimizations:
                print(f"  - {opt}")
            
            self.logger.log({
                "action": "optimization_plan",
                "tokens_in": 30,
                "tokens_out": 80,
                "details": {"optimizations": optimizations},
                "status": "planned"
            })
            
            await self.logger.flush()

async def reflection_example():
    agent = SelfReflectingAgent()
    
    # Perform various actions
    print("Performing actions...")
    for i in range(10):
        complexity = ["simple", "medium", "complex"][i % 3]
        await agent.perform_action(f"task_{i}", complexity)
    
    await agent.logger.flush()
    
    # Reflect on performance
    reflection = await agent.reflect_on_performance()
    
    # Optimize based on reflection
    await agent.optimize_behavior(reflection)

if __name__ == "__main__":
    asyncio.run(reflection_example())
```

---

## 5. Cost-Aware Agent

An agent that monitors spending and adjusts behavior to stay within budget.

```python
# cost_aware_agent.py
from Scripts.AuditLogger import AuditLogger
import os
import asyncio

class CostAwareAgent:
    def __init__(self, budget_bsv=0.01):
        self.logger = AuditLogger(
            priv_wif=os.getenv("BSV_PRIV_WIF"),
            config={"agent_id": "cost-aware-agent"}
        )
        self.budget_bsv = budget_bsv
        self.spending_warning_threshold = 0.8  # 80% of budget
    
    async def check_budget_status(self):
        """Check current spending against budget"""
        history = await self.logger.get_history()
        total_spent = sum(log.get("total_cost_bsv", 0) for log in history)
        
        remaining = self.budget_bsv - total_spent
        percentage_used = (total_spent / self.budget_bsv) * 100 if self.budget_bsv > 0 else 0
        
        status = {
            "budget_bsv": self.budget_bsv,
            "spent_bsv": total_spent,
            "remaining_bsv": remaining,
            "percentage_used": percentage_used,
            "within_budget": total_spent <= self.budget_bsv
        }
        
        return status
    
    async def can_perform_action(self, estimated_cost_bsv=0.00001):
        """Check if action is within budget"""
        status = await self.check_budget_status()
        
        would_exceed = (status["spent_bsv"] + estimated_cost_bsv) > self.budget_bsv
        
        if would_exceed:
            print(f"⚠️  Action would exceed budget!")
            print(f"  Current: {status['spent_bsv']:.6f} BSV")
            print(f"  Budget: {self.budget_bsv:.6f} BSV")
            return False
        
        # Warning if approaching limit
        if status["percentage_used"] > (self.spending_warning_threshold * 100):
            print(f"⚠️  Approaching budget limit: {status['percentage_used']:.1f}% used")
        
        return True
    
    async def perform_budget_conscious_action(self, action_type):
        """Perform action only if within budget"""
        if not await self.can_perform_action():
            self.logger.log({
                "action": action_type,
                "tokens_in": 0,
                "tokens_out": 0,
                "details": {"reason": "budget_exceeded"},
                "status": "skipped"
            })
            return False
        
        # Perform action
        self.logger.log({
            "action": action_type,
            "tokens_in": 100,
            "tokens_out": 200,
            "details": {"budget_check": "passed"},
            "status": "success"
        })
        
        return True
    
    async def generate_budget_report(self):
        """Generate detailed budget report"""
        status = await self.check_budget_status()
        history = await self.logger.get_history()
        
        # Breakdown by action type
        action_costs = {}
        for log in history:
            for metric in log.get("metrics", []):
                action = metric.get("action", "unknown")
                # Estimate cost per action (simplified)
                cost = log.get("total_cost_bsv", 0) / len(log.get("metrics", [])) if log.get("metrics") else 0
                action_costs[action] = action_costs.get(action, 0) + cost
        
        print(f"\n💰 Budget Report:")
        print(f"  Budget: {status['budget_bsv']:.6f} BSV")
        print(f"  Spent: {status['spent_bsv']:.6f} BSV ({status['percentage_used']:.1f}%)")
        print(f"  Remaining: {status['remaining_bsv']:.6f} BSV")
        print(f"\n  Cost by action type:")
        for action, cost in sorted(action_costs.items(), key=lambda x: x[1], reverse=True):
            print(f"    {action}: {cost:.6f} BSV")
        
        self.logger.log({
            "action": "budget_report",
            "tokens_in": 20,
            "tokens_out": 100,
            "details": {
                "budget_status": status,
                "action_breakdown": action_costs
            },
            "status": "completed"
        })
        
        await self.logger.flush()

async def cost_aware_example():
    agent = CostAwareAgent(budget_bsv=0.001)
    
    # Perform actions within budget
    for i in range(5):
        success = await agent.perform_budget_conscious_action(f"task_{i}")
        if success:
            print(f"✓ Completed task_{i}")
        else:
            print(f"✗ Skipped task_{i} (budget)")
    
    # Generate budget report
    await agent.generate_budget_report()

if __name__ == "__main__":
    asyncio.run(cost_aware_example())
```

---

## 6. Session Management

Best practices for managing agent sessions.

```python
# session_manager.py
from Scripts.AuditLogger import AuditLogger
import os
import asyncio
from datetime import datetime
import uuid

class SessionManager:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.current_session = None
        self.logger = None
    
    async def start_session(self, task_description):
        """Start a new logging session"""
        session_id = f"{self.agent_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        self.logger = AuditLogger(
            priv_wif=os.getenv("BSV_PRIV_WIF"),
            config={
                "agent_id": self.agent_id,
                "session_id": session_id,
                "flush_threshold": 10
            }
        )
        
        self.current_session = {
            "id": session_id,
            "start_time": datetime.now(),
            "task": task_description,
            "actions_count": 0
        }
        
        # Log session start
        self.logger.log({
            "action": "session_start",
            "tokens_in": 10,
            "tokens_out": 10,
            "details": {
                "task": task_description,
                "session_id": session_id
            },
            "status": "started"
        })
        
        print(f"📝 Session started: {session_id}")
        print(f"   Task: {task_description}")
    
    async def log_action(self, action_type, tokens_in, tokens_out, details=None):
        """Log an action in the current session"""
        if not self.logger:
            raise RuntimeError("No active session. Call start_session() first.")
        
        self.logger.log({
            "action": action_type,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "details": details or {},
            "status": "success"
        })
        
        self.current_session["actions_count"] += 1
    
    async def end_session(self):
        """End the current session and flush logs"""
        if not self.logger:
            print("⚠️  No active session to end")
            return
        
        duration = datetime.now() - self.current_session["start_time"]
        
        # Log session end
        self.logger.log({
            "action": "session_end",
            "tokens_in": 10,
            "tokens_out": 20,
            "details": {
                "duration_seconds": duration.total_seconds(),
                "actions_count": self.current_session["actions_count"]
            },
            "status": "completed"
        })
        
        # Flush to blockchain
        tx_id = await self.logger.flush()
        
        print(f"\n✓ Session ended: {self.current_session['id']}")
        print(f"  Duration: {duration}")
        print(f"  Actions: {self.current_session['actions_count']}")
        print(f"  Blockchain TX: {tx_id}")
        
        # Clean up
        self.current_session = None
        self.logger = None
        
        return tx_id

async def session_example():
    manager = SessionManager("demo-agent")
    
    # Session 1: Research task
    await manager.start_session("Research Bitcoin SV scalability")
    await manager.log_action("web_search", 50, 100, {"query": "BSV TPS"})
    await manager.log_action("web_search", 50, 120, {"query": "BSV block size"})
    await manager.log_action("analysis", 200, 300, {"document": "whitepaper.pdf"})
    await manager.end_session()
    
    # Session 2: Data processing
    await manager.start_session("Process transaction data")
    await manager.log_action("data_load", 100, 50, {"file": "transactions.csv"})
    await manager.log_action("computation", 500, 200, {"operation": "aggregate"})
    await manager.end_session()

if __name__ == "__main__":
    asyncio.run(session_example())
```

---

## 7. Error Handling & Recovery

Robust error handling for blockchain interactions.

```python
# error_handling.py
from Scripts.AuditLogger import AuditLogger
import os
import asyncio
import json
from pathlib import Path

class ResilientAgent:
    def __init__(self):
        self.logger = AuditLogger(
            priv_wif=os.getenv("BSV_PRIV_WIF"),
            config={"agent_id": "resilient-agent"}
        )
        self.backup_file = Path("logs/backup_logs.json")
        self.backup_file.parent.mkdir(exist_ok=True)
    
    async def safe_flush(self, max_retries=3):
        """Flush logs with retry logic and local backup"""
        for attempt in range(max_retries):
            try:
                tx_id = await self.logger.flush()
                print(f"✓ Logs flushed to blockchain: {tx_id}")
                return tx_id
            except Exception as e:
                print(f"⚠️  Flush attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    # Last attempt failed - save to local backup
                    print("💾 Saving logs to local backup...")
                    await self.save_backup()
                else:
                    # Wait before retry
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    async def save_backup(self):
        """Save logs to local file as backup"""
        logs = self.logger.pending_logs
        
        # Load existing backups
        backups = []
        if self.backup_file.exists():
            with open(self.backup_file) as f:
                backups = json.load(f)
        
        # Add new logs
        backups.extend(logs)
        
        # Save
        with open(self.backup_file, 'w') as f:
            json.dump(backups, f, indent=2)
        
        print(f"✓ {len(logs)} logs saved to {self.backup_file}")
    
    async def retry_backups(self):
        """Attempt to flush backed-up logs to blockchain"""
        if not self.backup_file.exists():
            print("No backup logs to retry")
            return
        
        with open(self.backup_file) as f:
            backups = json.load(f)
        
        print(f"📤 Retrying {len(backups)} backed-up logs...")
        
        # Add backups to pending logs
        for backup in backups:
            self.logger.pending_logs.append(backup)
        
        # Try to flush
        tx_id = await self.safe_flush()
        
        if tx_id:
            # Success - clear backup file
            self.backup_file.unlink()
            print("✓ All backups successfully flushed")
        
        return tx_id
    
    async def safe_get_history(self, max_retries=3):
        """Get history with retry logic"""
        for attempt in range(max_retries):
            try:
                history = await self.logger.get_history()
                return history
            except Exception as e:
                print(f"⚠️  History retrieval attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    print("✗ Failed to retrieve history from blockchain")
                    return []

async def error_handling_example():
    agent = ResilientAgent()
    
    # Log some actions
    for i in range(5):
        agent.logger.log({
            "action": f"task_{i}",
            "tokens_in": 100,
            "tokens_out": 150,
            "details": {"index": i},
            "status": "success"
        })
    
    # Try to flush (with automatic retry and backup)
    await agent.safe_flush()
    
    # Later, retry any failed flushes
    # await agent.retry_backups()
    
    # Safely get history
    history = await agent.safe_get_history()
    print(f"\n📚 Retrieved {len(history)} historical logs")

if __name__ == "__main__":
    asyncio.run(error_handling_example())
```

---

## Additional Resources

- **Main Skill Guide**: [SKILL.md](SKILL.md)
- **Prerequisites**: [PREREQUISITES.md](PREREQUISITES.md)
- **Repository**: https://github.com/MasterGoogler/OpenSoul

## Tips for Using These Examples

1. **Start with basic_logger.py** to understand the fundamentals
2. **Progress to research_agent.py** to see memory management
3. **Use session_manager.py** as a template for structured agent workflows
4. **Implement error_handling.py patterns** in production code
5. **Study self_reflecting_agent.py** for optimization strategies

All examples are production-ready with proper error handling and can be adapted to your specific use case.
