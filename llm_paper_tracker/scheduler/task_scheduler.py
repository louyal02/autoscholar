"""定时任务调度模块"""
import time
import logging
import subprocess
from datetime import datetime, timedelta
from threading import Thread
from typing import Callable, Optional
import os

logger = logging.getLogger(__name__)


class TaskScheduler:
    """每日定时任务调度器"""
    
    def __init__(self, hour: int = 9, minute: int = 30):
        self.hour = hour
        self.minute = minute
        self.running = False
        self.thread: Optional[Thread] = None
    
    def _get_next_run_time(self) -> datetime:
        """计算下次运行时间"""
        now = datetime.now()
        next_run = now.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
        
        if next_run <= now:
            next_run += timedelta(days=1)
        
        return next_run
    
    def _wait_until_next_run(self):
        """等待到下次运行时间"""
        while self.running:
            next_run = self._get_next_run_time()
            wait_seconds = (next_run - datetime.now()).total_seconds()
            
            if wait_seconds > 0:
                logger.info(f"Next run scheduled at {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(wait_seconds)
            
            if self.running:
                yield datetime.now()
    
    def _run_loop(self, task_func: Callable):
        """运行任务循环"""
        while self.running:
            try:
                logger.info("Running scheduled task...")
                task_func()
                logger.info("Task completed successfully")
            except Exception as e:
                logger.error(f"Task failed: {e}")
            
            time.sleep(60)
    
    def start(self, task_func: Callable):
        """启动调度器"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.thread = Thread(target=self._run_loop, args=(task_func,), daemon=True)
        self.thread.start()
        logger.info(f"Scheduler started - will run daily at {self.hour:02d}:{self.minute:02d}")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler stopped")
    
    def is_running(self) -> bool:
        """检查调度器是否运行中"""
        return self.running
    
    def run_once(self, task_func: Callable):
        """立即运行一次任务"""
        logger.info("Running task immediately...")
        try:
            task_func()
            logger.info("Task completed successfully")
            return True
        except Exception as e:
            logger.error(f"Task failed: {e}")
            return False


class WindowsTaskScheduler:
    """Windows任务计划程序集成"""
    
    @staticmethod
    def create_scheduled_task(script_path: str, task_name: str = "LLMPaperTracker"):
        """创建Windows定时任务"""
        exe_path = os.sys.executable
        
        command = f'schtasks /create /tn "{task_name}" /tr "\\"{exe_path}\\" \\"{script_path}\\"" /sc daily /st 09:30 /f'
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Windows scheduled task '{task_name}' created successfully")
                return True
            else:
                logger.error(f"Failed to create task: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating scheduled task: {e}")
            return False
    
    @staticmethod
    def delete_scheduled_task(task_name: str = "LLMPaperTracker"):
        """删除Windows定时任务"""
        command = f'schtasks /delete /tn "{task_name}" /f'
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Windows scheduled task '{task_name}' deleted")
                return True
            else:
                logger.warning(f"Failed to delete task: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting scheduled task: {e}")
            return False
    
    @staticmethod
    def list_tasks():
        """列出相关任务"""
        command = 'schtasks /query /fo csv'
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                tasks = [line for line in result.stdout.split('\n') 
                        if 'LLM' in line or 'Paper' in line or 'Tracker' in line]
                return tasks
            return []
                
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return []
