"""LLM Paper Tracker 主程序"""
import os
import sys
import time
import ssl
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from llm_paper_tracker.config import Config
from llm_paper_tracker.fetcher.arxiv_fetcher import ArxivFetcher
from llm_paper_tracker.fetcher.conf_fetcher import ConferenceFetcher
from llm_paper_tracker.processor.deduplicator import Deduplicator
from llm_paper_tracker.processor.analyzer import LLMAnalyzer
from llm_paper_tracker.processor.html_generator import HTMLGenerator
from llm_paper_tracker.sender.email_sender import EmailSender
from llm_paper_tracker.scheduler.task_scheduler import TaskScheduler, WindowsTaskScheduler


def setup_logging(config: Config):
    """设置日志"""
    log_level = config.get('logging.level', 'INFO')
    log_file = config.get('logging.file', 'data/logs/tracker.log')
    
    base_dir = Path(__file__).parent.parent
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


def fetch_all_papers(config: Config, days_back: int = 7, max_results: int = 50) -> List[Dict]:
    """获取所有来源的论文"""
    papers = []
    logger = logging.getLogger(__name__)
    
    if config.get('arxiv.enabled', True):
        logger.info(f"Fetching papers from arXiv (days_back={days_back})...")
        
        categories = config.get('arxiv.categories', ['cs.CL', 'cs.LG', 'cs.AI'])
        keywords = config.get('paper.keywords', ['LLM', 'Large Language Model', 'GPT'])
        
        fetcher = ArxivFetcher(categories=categories, keywords=keywords)
        arxiv_papers = fetcher.fetch_papers(max_results=max_results, days_back=days_back)
        papers.extend(arxiv_papers)
        logger.info(f"Fetched {len(arxiv_papers)} papers from arXiv")
    
    if config.get('conferences.enabled', True):
        logger.info("Fetching papers from conferences...")
        
        conferences = config.get('conferences.list', ['NeurIPS', 'AAAI', 'ACL', 'EMNLP'])
        keywords = config.get('paper.keywords', ['LLM', 'Large Language Model', 'GPT'])
        
        fetcher = ConferenceFetcher(conferences=conferences, keywords=keywords)
        conf_papers = fetcher.fetch_papers(max_results_per_conf=10)
        papers.extend(conf_papers)
        logger.info(f"Fetched {len(conf_papers)} papers from conferences")
    
    return papers


def strict_filter_by_focus_areas(papers: List[Dict], config: Config) -> List[Dict]:
    """严格筛选：必须同时包含LLM关键词 AND (教育关键词 OR 基准测试关键词)"""
    llm_keywords = ['llm', 'large language model', 'gpt', 'language model', 'transformer', 'chatgpt']
    
    education_keywords = [
        'education', 'educational', 'learner', 'learning', 'teaching', 'student',
        'teacher', 'school', 'classroom', 'course', 'tutorial', 
        'pedagogy', 'instruction', 'curriculum', 'exam', 'homework', 'assignment',
        '知识图谱', '知识蒸馏', '教育', '教学', '学习'
    ]
    
    benchmark_keywords = [
        'benchmark', 'benchmarks', 'leaderboard', '排行榜',
        '评估基准', '评测基准', '性能基准'
    ]
    
    filtered = []
    for paper in papers:
        title = paper.get('title', '').lower()
        summary = paper.get('summary', '').lower()
        
        has_llm = any(kw in title or kw in summary for kw in llm_keywords)
        has_education = any(kw in title or kw in summary for kw in education_keywords)
        has_benchmark = any(kw in title or kw in summary for kw in benchmark_keywords)
        
        if has_llm and (has_education or has_benchmark):
            filtered.append(paper)
    
    logging.getLogger(__name__).info(f"Strict filtering: {len(papers)} -> {len(filtered)} papers (LLM+Education OR LLM+Benchmark)")
    return filtered


def fallback_filter_llm(papers: List[Dict], config: Config) -> List[Dict]:
    """宽松筛选：只有当所有关键词筛选都失败时才使用，返回所有LLM相关论文"""
    llm_keywords = ['llm', 'large language model', 'gpt', 'language model', 'transformer', 'chatgpt']
    
    filtered = []
    for paper in papers:
        title = paper.get('title', '').lower()
        summary = paper.get('summary', '').lower()
        
        if any(kw in title or kw in summary for kw in llm_keywords):
            filtered.append(paper)
    
    logging.getLogger(__name__).info(f"Fallback LLM filtering: {len(papers)} -> {len(filtered)} papers (LLM only - last resort)")
    return filtered


def collect_papers_with_fallback(config: Config, deduplicator: Deduplicator) -> List[Dict]:
    """收集论文，必要时回溯旧文章"""
    logger = logging.getLogger(__name__)
    
    max_papers = config.get('paper.max_papers_per_day', 20)
    min_papers = 10
    
    fetched_papers = []
    used_fallback = False
    
    days_back_list = [7, 14, 30, 60, 90, 180, 365]
    
    for i, days_back in enumerate(days_back_list):
        logger.info(f"Attempting to fetch papers from last {days_back} days...")
        
        papers = fetch_all_papers(config, days_back=days_back, max_results=100)
        
        if not papers:
            continue
        
        papers = strict_filter_by_focus_areas(papers, config)
        
        new_papers = deduplicator.filter_new_papers(papers)
        fetched_papers.extend(new_papers)
        
        logger.info(f"Found {len(new_papers)} new papers in last {days_back} days")
        
        if len(fetched_papers) >= min_papers:
            break
    
    logger.info(f"Total new papers collected: {len(fetched_papers)}")
    
    if len(fetched_papers) < min_papers and (len(fetched_papers) == 0 or i == len(days_back_list) - 1):
        if len(fetched_papers) == 0:
            logger.info(f"No papers found with strict filtering, trying fallback LLM search...")
        else:
            logger.info(f"Only {len(fetched_papers)} papers found after 1 year, trying fallback LLM search...")
        
        used_fallback = True
        
        for days_back in [7, 14, 30, 60, 90, 180, 365]:
            papers = fetch_all_papers(config, days_back=days_back, max_results=100)
            
            if not papers:
                continue
            
            papers = fallback_filter_llm(papers, config)
            
            new_papers = deduplicator.filter_new_papers(papers)
            
            for p in new_papers:
                if p not in fetched_papers:
                    fetched_papers.append(p)
            
            if len(fetched_papers) >= min_papers:
                break
        
        logger.info(f"After fallback: {len(fetched_papers)} papers")
    
    return fetched_papers[:max_papers]


def analyze_papers(papers: List[Dict], config: Config) -> List[Dict]:
    """使用LLM分析论文"""
    if not config.get('llm.enabled', True):
        return papers
    
    api_key = config.get('llm.api_key', '')
    if not api_key:
        logging.warning("LLM API key not configured, using fallback analysis")
        return papers
    
    base_url = config.get('llm.base_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    model = config.get('llm.model', 'qwen3.5-plus')
    
    analyzer = LLMAnalyzer(
        api_key=api_key,
        base_url=base_url,
        model=model
    )
    
    return analyzer.analyze_batch(papers)


def generate_html_report(papers: List[Dict], config: Config) -> str:
    """生成HTML简报"""
    generator = HTMLGenerator(title="LLM论文追踪简报")
    return generator.generate(papers)


def send_email_report(html_content: str, paper_count: int, config: Config) -> bool:
    """发送邮件报告"""
    if not config.get('email.enabled', True):
        logging.info("Email disabled, skipping...")
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
    
    logger.info("=" * 50)
    logger.info("LLM Paper Tracker started")
    logger.info("=" * 50)
    
    deduplicator = Deduplicator()
    
    papers = collect_papers_with_fallback(config, deduplicator)
    logger.info(f"Total new papers to process: {len(papers)}")
    
    if not papers:
        logger.info("No new papers to send")
        return
    
    analyzed_papers = analyze_papers(papers, config)
    
    html_content = generate_html_report(analyzed_papers, config)
    
    if send_email_report(html_content, len(analyzed_papers), config):
        for paper in analyzed_papers:
            deduplicator.mark_sent(
                title=paper.get('title', ''),
                date=paper.get('published', ''),
                metadata={'source': paper.get('source', '')}
            )
        logger.info(f"Successfully sent report with {len(analyzed_papers)} papers")
    else:
        logger.error("Failed to send email report")
    
    logger.info("LLM Paper Tracker finished")


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LLM Paper Tracker')
    parser.add_argument('--config', '-c', help='Config file path', default=None)
    parser.add_argument('--run-now', '-r', action='store_true', help='Run immediately')
    parser.add_argument('--setup-task', '-s', action='store_true', help='Setup Windows scheduled task')
    parser.add_argument('--test-email', '-t', action='store_true', help='Test email configuration')
    
    args = parser.parse_args()
    
    config = Config(args.config) if args.config else Config()
    
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
        
        test_content = "<h1>Test Email</h1><p>LLM Paper Tracker is working correctly!</p>"
        
        to_emails = config.get('email.to_emails', [])
        if sender.send(to_emails, "LLM Paper Tracker Test", test_content):
            print("Test email sent successfully!")
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
        
        print(f"LLM Paper Tracker started. Press Ctrl+C to stop.")
        print(f"Daily run time: {hour:02d}:{minute:02d}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop()
            print("\nScheduler stopped.")


if __name__ == "__main__":
    main()
