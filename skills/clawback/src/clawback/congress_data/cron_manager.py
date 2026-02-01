"""
Cron job manager for congressional trade data collection
"""
import json
import logging
import os
import schedule
import time
from datetime import datetime, timedelta
import threading
import sys

logger = logging.getLogger(__name__)

class CronManager:
    """Manages scheduled congressional trade data collection"""
    
    def __init__(self, data_collector, alert_manager, config):
        self.data_collector = data_collector
        self.alert_manager = alert_manager
        self.config = config
        self.cron_config = config.get_cron_config()
        
        # Scheduler state
        self.scheduler = schedule.Scheduler()
        self.is_running = False
        self.thread = None
        
        # Execution tracking
        self.execution_history = []
        self.history_file = "data/cron_history.json"
        
        # Load execution history
        self.load_history()
        
        logger.info("Cron manager initialized")
    
    def load_history(self):
        """Load execution history from file"""
        try:
            with open(self.history_file, 'r') as f:
                self.execution_history = json.load(f)
            logger.info(f"Loaded {len(self.execution_history)} previous executions")
        except (FileNotFoundError, json.JSONDecodeError):
            self.execution_history = []
    
    def save_history(self):
        """Save execution history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.execution_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving execution history: {e}")
    
    def job_function(self):
        """Main job function to collect data and send alerts"""
        try:
            start_time = datetime.now()
            logger.info("Starting scheduled congressional data collection")
            
            # Record start
            execution_record = {
                "start_time": start_time.isoformat(),
                "status": "running",
                "trades_collected": 0,
                "alerts_sent": 0,
                "errors": []
            }
            
            try:
                # Collect data from all sources
                trades = self.data_collector.collect_all_data()
                execution_record["trades_collected"] = len(trades)
                
                # Process alerts for significant trades
                alerted_trades = self.alert_manager.process_trades_for_alerts(trades)
                execution_record["alerts_sent"] = len(alerted_trades)
                
                # Get collection stats
                stats = self.data_collector.get_collection_stats()
                execution_record["collection_stats"] = stats
                
                # Get alert stats
                alert_stats = self.alert_manager.get_alert_stats(days=1)
                execution_record["alert_stats"] = alert_stats
                
                execution_record["status"] = "completed"
                execution_record["end_time"] = datetime.now().isoformat()
                
                logger.info(f"Job completed: collected {len(trades)} trades, sent {len(alerted_trades)} alerts")
                
            except Exception as e:
                execution_record["status"] = "failed"
                execution_record["error"] = str(e)
                execution_record["end_time"] = datetime.now().isoformat()
                logger.error(f"Job failed: {e}")
            
            # Save execution record
            self.execution_history.append(execution_record)
            
            # Keep only recent history (last 100 executions)
            if len(self.execution_history) > 100:
                self.execution_history = self.execution_history[-100:]
            
            self.save_history()
            
        except Exception as e:
            logger.error(f"Error in job function: {e}")
    
    def setup_schedule(self):
        """Setup the scheduled job based on configuration"""
        try:
            cron_schedule = self.cron_config.get("schedule", "0 9 * * 1-5")
            timezone = self.cron_config.get("timezone", "America/New_York")
            
            # Parse cron schedule
            # Format: "minute hour day month day_of_week"
            parts = cron_schedule.split()
            if len(parts) != 5:
                logger.warning(f"Invalid cron schedule: {cron_schedule}, using default")
                cron_schedule = "0 9 * * 1-5"
                parts = cron_schedule.split()
            
            minute, hour, day, month, day_of_week = parts
            
            # Clear existing jobs
            self.scheduler.clear()
            
            # Add job based on schedule
            if day_of_week == "*":
                # Daily job
                self.scheduler.every().day.at(f"{hour}:{minute}").do(self.job_function)
                logger.info(f"Scheduled daily job at {hour}:{minute}")
            elif "-" in day_of_week:
                # Weekday range (e.g., 1-5 for Monday-Friday)
                start_day, end_day = map(int, day_of_week.split("-"))
                for day_num in range(start_day, end_day + 1):
                    # Convert to schedule day name
                    day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                    if 0 <= day_num <= 6:
                        day_name = day_names[day_num]
                        getattr(self.scheduler.every(), day_name).at(f"{hour}:{minute}").do(self.job_function)
                logger.info(f"Scheduled weekday job at {hour}:{minute} (days {day_of_week})")
            else:
                # Specific day(s)
                day_nums = list(map(int, day_of_week.split(",")))
                day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                for day_num in day_nums:
                    if 0 <= day_num <= 6:
                        day_name = day_names[day_num]
                        getattr(self.scheduler.every(), day_name).at(f"{hour}:{minute}").do(self.job_function)
                logger.info(f"Scheduled job at {hour}:{minute} on days {day_of_week}")
            
            # Run on startup if configured
            if self.cron_config.get("run_on_startup", True):
                logger.info("Running job on startup")
                self.job_function()
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up schedule: {e}")
            return False
    
    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        try:
            logger.info("Starting cron scheduler")
            self.is_running = True
            
            while self.is_running:
                self.scheduler.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user")
            self.is_running = False
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            self.is_running = False
    
    def start(self):
        """Start the cron scheduler"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return False
        
        # Setup schedule
        if not self.setup_schedule():
            return False
        
        # Start scheduler in background thread
        self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info("Cron scheduler started")
        return True
    
    def stop(self):
        """Stop the cron scheduler"""
        logger.info("Stopping cron scheduler")
        self.is_running = False
        
        if self.thread:
            self.thread.join(timeout=10)
        
        logger.info("Cron scheduler stopped")
        return True
    
    def run_once(self):
        """Run the job once immediately"""
        logger.info("Running job once immediately")
        self.job_function()
        return True
    
    def get_status(self):
        """Get current scheduler status"""
        status = {
            "is_running": self.is_running,
            "schedule": self.cron_config.get("schedule", ""),
            "next_run": None,
            "last_executions": self.execution_history[-5:] if self.execution_history else [],
            "total_executions": len(self.execution_history),
            "successful_executions": sum(1 for e in self.execution_history if e.get("status") == "completed"),
            "failed_executions": sum(1 for e in self.execution_history if e.get("status") == "failed")
        }
        
        # Get next run time if scheduler is running
        if self.is_running and hasattr(self.scheduler, 'next_run'):
            try:
                next_run = self.scheduler.next_run
                if next_run:
                    status["next_run"] = next_run.isoformat()
            except:
                pass
        
        return status
    
    def update_schedule(self, new_schedule):
        """Update the cron schedule"""
        try:
            self.cron_config["schedule"] = new_schedule
            self.config.update_config({"cron": {"schedule": new_schedule}})
            
            # Restart scheduler with new schedule
            if self.is_running:
                self.stop()
                time.sleep(1)
                self.start()
            
            logger.info(f"Schedule updated to: {new_schedule}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating schedule: {e}")
            return False
    
    def get_execution_history(self, limit=50):
        """Get execution history"""
        return self.execution_history[-limit:] if self.execution_history else []
    
    def cleanup_old_data(self, days_to_keep=30):
        """Clean up old data files"""
        try:
            data_dir = self.data_collector.storage_config.get("data_directory", "data/congress_trades")
            backup_dir = self.data_collector.storage_config.get("backup_directory", "data/backups")
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            files_removed = 0
            
            # Clean data directory
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if file.endswith('.json'):
                        filepath = os.path.join(root, file)
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                        
                        if file_mtime < cutoff_date:
                            os.remove(filepath)
                            files_removed += 1
            
            # Clean backup directory
            if os.path.exists(backup_dir):
                for root, dirs, files in os.walk(backup_dir):
                    for file in files:
                        if file.endswith('.json'):
                            filepath = os.path.join(root, file)
                            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                            
                            if file_mtime < cutoff_date:
                                os.remove(filepath)
                                files_removed += 1
            
            logger.info(f"Cleaned up {files_removed} old data files")
            return files_removed
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0