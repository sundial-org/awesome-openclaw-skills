"""
OpenSoul Agent Base Template

This template provides a robust foundation for building agents with OpenSoul.
It includes:
- Proper initialization and cleanup
- Session management
- Error handling and recovery
- Performance monitoring
- Budget awareness

Usage:
1. Copy this file to your project
2. Inherit from OpenSoulAgent
3. Implement your agent's specific logic
"""

from Scripts.AuditLogger import AuditLogger
import os
import asyncio
from datetime import datetime
from pathlib import Path
import json


class OpenSoulAgent:
    """
    Base class for agents using OpenSoul for persistent memory and audit logs
    """
    
    def __init__(self, agent_id, config=None):
        """
        Initialize OpenSoul agent
        
        Args:
            agent_id (str): Unique identifier for this agent
            config (dict, optional): Configuration dictionary
        """
        self.agent_id = agent_id
        self.config = config or {}
        
        # Initialize logger (will be set in start_session)
        self.logger = None
        self.current_session = None
        
        # Performance tracking
        self.session_start_time = None
        self.action_count = 0
        
        # Budget management
        self.budget_bsv = self.config.get("budget_bsv", 0.01)
        self.budget_warning_threshold = self.config.get("budget_warning_threshold", 0.8)
        
        # Error handling
        self.max_retries = self.config.get("max_retries", 3)
        self.backup_enabled = self.config.get("enable_backup", True)
        self.backup_dir = Path(self.config.get("backup_dir", "logs/backups"))
        
        # Ensure backup directory exists
        if self.backup_enabled:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    async def start_session(self, task_description=None):
        """
        Start a new logging session
        
        Args:
            task_description (str, optional): Description of task for this session
        """
        # Generate session ID
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        session_id = f"{self.agent_id}-{timestamp}"
        
        # Initialize logger
        opensoul_config = {
            "agent_id": self.agent_id,
            "session_id": session_id,
            "flush_threshold": self.config.get("flush_threshold", 10)
        }
        
        # Add PGP config if available
        if "pgp" in self.config:
            opensoul_config["pgp"] = self.config["pgp"]
        
        self.logger = AuditLogger(
            priv_wif=os.getenv("BSV_PRIV_WIF"),
            config=opensoul_config
        )
        
        # Track session
        self.current_session = {
            "id": session_id,
            "start_time": datetime.now(),
            "task": task_description,
            "action_count": 0
        }
        self.session_start_time = datetime.now()
        self.action_count = 0
        
        # Log session start
        await self._log_action(
            action_type="session_start",
            tokens_in=10,
            tokens_out=10,
            details={
                "task": task_description,
                "session_id": session_id
            },
            status="started"
        )
        
        print(f"🧠 Session started: {session_id}")
        if task_description:
            print(f"   Task: {task_description}")
    
    async def _log_action(self, action_type, tokens_in, tokens_out, details=None, status="success"):
        """
        Internal method to log an action with error handling
        
        Args:
            action_type (str): Type of action
            tokens_in (int): Input tokens
            tokens_out (int): Output tokens
            details (dict, optional): Additional details
            status (str): Action status
        """
        if not self.logger:
            raise RuntimeError("No active session. Call start_session() first.")
        
        self.logger.log({
            "action": action_type,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "details": details or {},
            "status": status,
            "ts": datetime.now().isoformat()
        })
        
        self.action_count += 1
        if self.current_session:
            self.current_session["action_count"] += 1
    
    async def log_action(self, action_type, tokens_in=0, tokens_out=0, details=None):
        """
        Public method to log an action (for use by subclasses)
        
        Args:
            action_type (str): Type of action
            tokens_in (int): Input tokens used
            tokens_out (int): Output tokens generated
            details (dict, optional): Additional action details
        """
        await self._log_action(action_type, tokens_in, tokens_out, details, "success")
    
    async def check_budget(self):
        """
        Check current spending against budget
        
        Returns:
            dict: Budget status information
        """
        try:
            history = await self.logger.get_history()
            total_spent = sum(log.get("total_cost_bsv", 0) for log in history)
            
            remaining = self.budget_bsv - total_spent
            percentage_used = (total_spent / self.budget_bsv * 100) if self.budget_bsv > 0 else 0
            
            status = {
                "budget_bsv": self.budget_bsv,
                "spent_bsv": total_spent,
                "remaining_bsv": remaining,
                "percentage_used": percentage_used,
                "within_budget": total_spent <= self.budget_bsv,
                "warning": percentage_used >= (self.budget_warning_threshold * 100)
            }
            
            # Log warning if approaching limit
            if status["warning"]:
                print(f"⚠️  Budget warning: {percentage_used:.1f}% used")
            
            return status
        except Exception as e:
            print(f"⚠️  Could not check budget: {e}")
            return None
    
    async def safe_flush(self):
        """
        Flush logs to blockchain with retry logic and backup
        
        Returns:
            str: Transaction ID if successful, None otherwise
        """
        for attempt in range(self.max_retries):
            try:
                tx_id = await self.logger.flush()
                print(f"✓ Logs flushed to blockchain: {tx_id}")
                return tx_id
            except Exception as e:
                print(f"⚠️  Flush attempt {attempt + 1} failed: {e}")
                
                if attempt == self.max_retries - 1:
                    # Last attempt failed - save backup
                    if self.backup_enabled:
                        await self._save_backup()
                else:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)
        
        return None
    
    async def _save_backup(self):
        """Save logs to local backup file"""
        if not self.logger or not self.logger.pending_logs:
            return
        
        backup_file = self.backup_dir / f"backup_{self.current_session['id']}.json"
        
        with open(backup_file, 'w') as f:
            json.dump(self.logger.pending_logs, f, indent=2)
        
        print(f"💾 Logs backed up to: {backup_file}")
    
    async def reflect_on_performance(self):
        """
        Analyze agent's performance and identify areas for improvement
        
        Returns:
            dict: Performance analysis
        """
        try:
            history = await self.logger.get_history()
            
            # Gather metrics
            all_metrics = []
            for log in history:
                all_metrics.extend(log.get("metrics", []))
            
            if not all_metrics:
                print("ℹ️  No performance data available yet")
                return None
            
            # Calculate statistics
            total_actions = len(all_metrics)
            successful = len([m for m in all_metrics if m.get("status") == "success"])
            failed = total_actions - successful
            
            total_tokens = sum(
                m.get("tokens_in", 0) + m.get("tokens_out", 0)
                for m in all_metrics
            )
            avg_tokens = total_tokens / total_actions if total_actions > 0 else 0
            
            total_cost = sum(log.get("total_cost_bsv", 0) for log in history)
            success_rate = successful / total_actions if total_actions > 0 else 0
            
            reflection = {
                "total_sessions": len(history),
                "total_actions": total_actions,
                "successful_actions": successful,
                "failed_actions": failed,
                "success_rate": success_rate,
                "avg_tokens_per_action": avg_tokens,
                "total_cost_bsv": total_cost,
                "timestamp": datetime.now().isoformat()
            }
            
            # Log reflection
            await self._log_action(
                action_type="self_reflection",
                tokens_in=50,
                tokens_out=150,
                details=reflection,
                status="completed"
            )
            
            return reflection
        except Exception as e:
            print(f"⚠️  Reflection failed: {e}")
            return None
    
    async def end_session(self):
        """
        End current session and flush logs to blockchain
        
        Returns:
            str: Transaction ID if successful
        """
        if not self.current_session:
            print("⚠️  No active session to end")
            return None
        
        duration = datetime.now() - self.session_start_time
        
        # Log session summary
        await self._log_action(
            action_type="session_end",
            tokens_in=10,
            tokens_out=20,
            details={
                "duration_seconds": duration.total_seconds(),
                "action_count": self.action_count,
                "session_id": self.current_session["id"]
            },
            status="completed"
        )
        
        # Flush to blockchain
        tx_id = await self.safe_flush()
        
        # Print summary
        print(f"\n✓ Session ended: {self.current_session['id']}")
        print(f"  Duration: {duration}")
        print(f"  Actions: {self.action_count}")
        if tx_id:
            print(f"  Blockchain TX: {tx_id}")
        
        # Cleanup
        self.current_session = None
        self.logger = None
        
        return tx_id


# ==============================================================================
# EXAMPLE SUBCLASS
# ==============================================================================

class MyCustomAgent(OpenSoulAgent):
    """
    Example: Custom agent that inherits from OpenSoulAgent
    """
    
    def __init__(self, config=None):
        super().__init__(agent_id="my-custom-agent", config=config)
    
    async def perform_research(self, query):
        """Example custom method"""
        print(f"🔍 Researching: {query}")
        
        # Log the action
        await self.log_action(
            action_type="research",
            tokens_in=50,
            tokens_out=200,
            details={"query": query}
        )
        
        # Your research logic here...
        results = f"Research results for: {query}"
        
        return results
    
    async def analyze_data(self, dataset_name):
        """Example custom method"""
        print(f"📊 Analyzing: {dataset_name}")
        
        # Log the action
        await self.log_action(
            action_type="data_analysis",
            tokens_in=200,
            tokens_out=300,
            details={"dataset": dataset_name}
        )
        
        # Your analysis logic here...
        analysis = f"Analysis of {dataset_name} complete"
        
        return analysis


# ==============================================================================
# USAGE EXAMPLE
# ==============================================================================

async def example_usage():
    """Example of how to use the agent template"""
    
    # Configuration
    config = {
        "budget_bsv": 0.01,
        "flush_threshold": 5,
        "enable_backup": True,
        "backup_dir": "logs/backups"
    }
    
    # Create agent
    agent = MyCustomAgent(config=config)
    
    # Start session
    await agent.start_session("Example research and analysis task")
    
    # Perform work
    await agent.perform_research("Bitcoin SV scalability")
    await agent.analyze_data("transactions.csv")
    
    # Check budget
    budget_status = await agent.check_budget()
    if budget_status:
        print(f"\n💰 Budget: {budget_status['percentage_used']:.1f}% used")
    
    # Reflect on performance
    reflection = await agent.reflect_on_performance()
    if reflection:
        print(f"\n📊 Success rate: {reflection['success_rate']:.1%}")
    
    # End session
    await agent.end_session()


if __name__ == "__main__":
    asyncio.run(example_usage())
