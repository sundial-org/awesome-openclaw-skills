"""
Cron job scheduler for congressional trade data collection
"""
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timedelta
import schedule
import threading

logger = logging.getLogger(__name__)

class CongressCronScheduler:
    """Schedules and manages cron jobs for congressional data collection"""
    
    def __init__(self, config, data_collector, alert_manager):
        self.config = config
        self.data_collector = data_collector
        self.alert_manager = alert_manager
        self.cron_config = config.get_cron_config()
        
        # Scheduler state
        self.scheduler = schedule.Scheduler()
        self.running = False
        self.thread = None
        
        # Statistics
        self.stats = {
            "runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "last_run": None,
            "last_success": None,
            "total_trades_collected": 0,
            "total_alerts_sent": 0,
            "start_time": datetime.now()
        }
        
        logger.info("Congressional cron scheduler initialized")
    
    def setup_schedule(self):
        """Set up the scheduled job based on configuration"""
        cron_schedule = self.cron_config.get("schedule", "0 9 * * 1-5")
        timezone = self.cron_config.get("timezone", "America/New_York")
        
        # Parse cron schedule
        # schedule library doesn't support cron syntax directly, so we'll use a simpler approach
        # For now, we'll use schedule.every().day.at() for simplicity
        # In production, you might want to use a proper cron parser
        
        # Default: Run at 9 AM on weekdays
        if cron_schedule == "0 9 * * 1-5":
            # Weekdays at 9 AM
            self.scheduler.every().monday.at("09:00").do(self.run_collection_job)
            self.scheduler.every().tuesday.at("09:00").do(self.run_collection_job)
            self.scheduler.every().wednesday.at("09:00").do(self.run_collection_job)
            self.scheduler.every().thursday.at("09:00").do(self.run_collection_job)
            self.scheduler.every().friday.at("09:00").do(self.run_collection_job)
            logger.info("Scheduled job: Weekdays at 9:00 AM")
        else:
            # Fallback: Run every day at 9 AM
            self.scheduler.every().day.at("09:00").do(self.run_collection_job)
            logger.info("Scheduled job: Daily at 9:00 AM (fallback)")
        
        # Run on startup if configured
        if self.cron_config.get("run_on_startup", True):
            logger.info("Running collection job on startup")
            self.run_collection_job()
    
    def run_collection_job(self):
        """Run the data collection job"""
        logger.info("Starting congressional data collection job")
        
        run_start = datetime.now()
        self.stats["runs"] += 1
        self.stats["last_run"] = run_start.isoformat()
        
        try:
            # Collect data from all sources
            trades = self.data_collector.collect_all_data()
            
            # Process alerts
            alerts_sent = self.alert_manager.process_trades_for_alerts(trades)
            
            # Update statistics
            self.stats["successful_runs"] += 1
            self.stats["last_success"] = datetime.now().isoformat()
            self.stats["total_trades_collected"] += len(trades)
            self.stats["total_alerts_sent"] += len(alerts_sent)
            
            # Get collection stats
            collection_stats = self.data_collector.get_collection_stats()
            
            # Log results
            run_duration = (datetime.now() - run_start).total_seconds()
            logger.info(f"Collection job completed in {run_duration:.2f} seconds")
            logger.info(f"Collected {len(trades)} trades, sent {len(alerts_sent)} alerts")
            
            # Save run log
            self.save_run_log({
                "timestamp": run_start.isoformat(),
                "duration_seconds": run_duration,
                "trades_collected": len(trades),
                "alerts_sent": len(alerts_sent),
                "collection_stats": collection_stats,
                "success": True
            })
            
            return {
                "success": True,
                "trades_collected": len(trades),
                "alerts_sent": len(alerts_sent),
                "duration_seconds": run_duration,
                "collection_stats": collection_stats
            }
            
        except Exception as e:
            logger.error(f"Collection job failed: {e}")
            self.stats["failed_runs"] += 1
            
            # Save error log
            self.save_run_log({
                "timestamp": run_start.isoformat(),
                "duration_seconds": (datetime.now() - run_start).total_seconds(),
                "error": str(e),
                "success": False
            })
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_run_log(self, log_data):
        """Save run log to file"""
        try:
            data_dir = self.config.get_storage_config().get("data_directory", "data/congress_trades")
            logs_dir = os.path.join(data_dir, "logs")
            os.makedirs(logs_dir, exist_ok=True)
            
            # Daily log file
            date_str = datetime.now().strftime("%Y%m%d")
            log_file = os.path.join(logs_dir, f"runs_{date_str}.json")
            
            # Load existing logs or create new list
            logs = []
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
            
            # Add new log
            logs.append(log_data)
            
            # Keep only last 100 logs per day
            if len(logs) > 100:
                logs = logs[-100:]
            
            # Save
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            logger.debug(f"Run log saved to {log_file}")
            
        except Exception as e:
            logger.error(f"Error saving run log: {e}")
    
    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        logger.info("Starting congressional cron scheduler")
        self.running = True
        
        try:
            while self.running:
                self.scheduler.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
        finally:
            self.running = False
            logger.info("Congressional cron scheduler stopped")
    
    def start(self):
        """Start the cron scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return False
        
        # Set up schedule
        self.setup_schedule()
        
        # Start scheduler in background thread
        self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info("Congressional cron scheduler started")
        return True
    
    def stop(self):
        """Stop the cron scheduler"""
        logger.info("Stopping congressional cron scheduler")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=10)
        
        logger.info("Congressional cron scheduler stopped")
        return True
    
    def run_once(self):
        """Run collection job once (manual trigger)"""
        logger.info("Manual collection job triggered")
        return self.run_collection_job()
    
    def get_scheduler_stats(self):
        """Get scheduler statistics"""
        stats = self.stats.copy()
        
        # Add uptime
        if stats["start_time"]:
            uptime = datetime.now() - stats["start_time"]
            stats["uptime_seconds"] = uptime.total_seconds()
            stats["uptime_human"] = str(uptime).split('.')[0]
        
        # Add success rate
        if stats["runs"] > 0:
            stats["success_rate"] = (stats["successful_runs"] / stats["runs"]) * 100
        else:
            stats["success_rate"] = 0
        
        # Add next run time
        if self.scheduler.get_jobs():
            next_run = self.scheduler.next_run
            if next_run:
                stats["next_scheduled_run"] = next_run.isoformat()
                stats["seconds_until_next_run"] = (next_run - datetime.now()).total_seconds()
        
        return stats
    
    def save_stats(self):
        """Save statistics to file"""
        try:
            data_dir = self.config.get_storage_config().get("data_directory", "data/congress_trades")
            stats_file = os.path.join(data_dir, "scheduler_stats.json")
            
            stats = self.get_scheduler_stats()
            
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            logger.debug(f"Scheduler stats saved to {stats_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving scheduler stats: {e}")
            return False
    
    def cleanup_old_data(self):
        """Clean up old data files based on retention policy"""
        try:
            data_dir = self.config.get_storage_config().get("data_directory", "data/congress_trades")
            max_days = self.config.get_storage_config().get("max_days_to_keep", 90)
            
            if not os.path.exists(data_dir):
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=max_days)
            files_deleted = 0
            
            # Walk through data directory
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if file.endswith('.json'):
                        filepath = os.path.join(root, file)
                        
                        # Check file modification time
                        try:
                            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                            if file_mtime < cutoff_date:
                                os.remove(filepath)
                                files_deleted += 1
                                logger.debug(f"Deleted old file: {filepath}")
                        except (OSError, FileNotFoundError):
                            continue
            
            logger.info(f"Cleaned up {files_deleted} old data files (older than {max_days} days)")
            return files_deleted
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0