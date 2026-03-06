"""LLM Paper Tracker 主程序"""
import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from fetcher.arxiv_fetcher import ArxivFetcher
from processor.deduplicator import Deduplicator
from processor.analyzer import LLMAnalyzer
from processor.html_generator import HTMLGenerator
from sender.email_sender import EmailSender
from scheduler.task_scheduler import TaskScheduler, WindowsTaskScheduler


def setup_logging(config: Config):
    """设置日志"""
    log_level = config.get('logging.level', 'INFO')
    log_file = config.get('logging.file', 'data/logs/tracker.log')
    
    base_dir = Path(__file__).parent
    log_file_path = base_dir / log_file
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def fetch_papers(config: Config, days_back: int = 7, max_results: int = 100) -> List[Dict]:
    """从arXiv获取论文"""
    logger = logging.getLogger(__name__)
    
    categories = config.get('arxiv.categories', ['cs.CL', 'cs.LG', 'cs.AI'])
    fetcher = ArxivFetcher(categories=categories)
    papers = fetcher.fetch_papers(max_results=max_results, days_back=days_back)
    
    logger.info(f"Fetched {len(papers)} papers from arXiv")
    return papers


def collect_papers(config: Config, deduplicator: Deduplicator) -> List[Dict]:
    """收集论文，必要时回溯"""
    logger = logging.getLogger(__name__)
    
    max_papers = config.get('paper.max_papers_per_day', 10)
    min_papers = 10
    
    fetched_papers = []
    days_back_list = [7, 14, 30, 60, 90, 180, 365]
    
    for i, days_back in enumerate(days_back_list):
        logger.info(f"Fetching papers from last {days_back} days...")
        
        papers = fetch_papers(config, days_back=days_back)
        
        if not papers:
            continue
        
        new_papers = deduplicator.filter_new_papers(papers)
        fetched_papers.extend(new_papers)
        
        logger.info(f"Found {len(new_papers)} new papers in last {days_back} days")
        
        if len(fetched_papers) >= min_papers:
            break
    
    logger.info(f"Total new papers collected: {len(fetched_papers)}")
    
    if len(fetched_papers) == 0:
        logger.info("No new papers found")
    
    return fetched_papers[:max_papers]


def analyze_papers(papers: List[Dict], config: Config) -> List[Dict]:
    """使用LLM分析论文"""
    if not config.get('llm.enabled', True):
        return papers
    
    api_key = config.get('llm.api_key', '')
    if not api_key:
        logging.warning("LLM API key not configured")
        return papers
    
    model = config.get('llm.model', 'qwen3.5-plus')
    
    analyzer = LLMAnalyzer(api_key=api_key, model=model)
    return analyzer.analyze_batch(papers)


def generate_html_report(papers: List[Dict]) -> str:
    """生成HTML简报"""
    generator = HTMLGenerator(title="LLM论文追踪简报")
    return generator.generate(papers)


def send_email_report(html_content: str, paper_count: int, config: Config) -> bool:
    """发送邮件报告"""
    if not config.get('email.enabled', True):
        logging.info("Email disabled")
        return False
    
    to_emails = config.get('email.to_emails', [])
    if not to_emails:
        logging.warning("No recipient emails configured")
        return False
    
    sender = EmailSender(
        smtp_host=config.get('email.smtp_host', 'smtp.qq.com'),
        smtp_port=config.get('email.smtp_port', 465),
        smtp_user=config.get('email.smtp_user', ''),
        smtp_password=config.get('email.smtp_password', ''),
        from_name=config.get('email.from_name', 'LLM Paper Tracker')
    )
    
    return sender.send_paper_report(to_emails, html_content, paper_count)


def run_tracker(config: Config = None):
    """运行论文追踪主流程"""
    if config is None:
        config = Config()
    
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    logger.info("LLM Paper Tracker started")
    
    deduplicator = Deduplicator()
    papers = collect_papers(config, deduplicator)
    
    if not papers:
        logger.info("No new papers to send")
        return
    
    analyzed_papers = analyze_papers(papers, config)
    html_content = generate_html_report(analyzed_papers)
    
    if send_email_report(html_content, len(analyzed_papers), config):
        for paper in analyzed_papers:
            deduplicator.mark_sent(
                title=paper.get('title', ''),
                date=paper.get('published', ''),
                metadata={'source': paper.get('source', '')}
            )
        logger.info(f"Sent report with {len(analyzed_papers)} papers")
    else:
        logger.error("Failed to send email report")
    
    logger.info("LLM Paper Tracker finished")


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LLM Paper Tracker')
    parser.add_argument('--run-now', '-r', action='store_true', help='Run immediately')
    parser.add_argument('--setup-task', '-s', action='store_true', help='Setup Windows scheduled task')
    parser.add_argument('--test-email', '-t', action='store_true', help='Test email')
    
    args = parser.parse_args()
    config = Config()
    
    if args.setup_task:
        script_path = os.path.abspath(__file__)
        WindowsTaskScheduler.create_scheduled_task(script_path)
        return
    
    if args.test_email:
        sender = EmailSender(
            smtp_host=config.get('email.smtp_host'),
            smtp_port=config.get('email.smtp_port'),
            smtp_user=config.get('email.smtp_user'),
            smtp_password=config.get('email.smtp_password')
        )
        to_emails = config.get('email.to_emails', [])
        if sender.send(to_emails, "Test", "<h1>Test</h1>"):
            print("Test email sent!")
        else:
            print("Failed to send test email")
        return
    
    if args.run_now:
        run_tracker(config)
    else:
        scheduler_time = config.get('scheduler.time', '09:30')
        hour, minute = map(int, scheduler_time.split(':'))
        
        scheduler = TaskScheduler(hour=hour, minute=minute)
        scheduler.start(lambda: run_tracker(config))
        
        print(f"LLM Paper Tracker running. Daily at {hour:02d}:{minute:02d}. Press Ctrl+C to stop.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop()
            print("\nStopped.")


if __name__ == "__main__":
    main()
