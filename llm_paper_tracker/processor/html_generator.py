"""HTML简报生成模块"""
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class HTMLGenerator:
    """生成HTML格式的论文简报"""
    
    def __init__(self, title: str = "LLM论文追踪简报"):
        self.title = title
    
    def generate(self, papers: List[Dict], date: Optional[str] = None) -> str:
        """生成HTML简报"""
        if date is None:
            date = datetime.now().strftime("%Y年%m月%d日")
        
        papers_html = self._generate_papers_html(papers)
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title} - {date}</title>
    <style>
        :root {{
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-color: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --tag-bg: #dbeafe;
            --tag-text: #1e40af;
        }}
        
        @media (prefers-color-scheme: dark) {{
            :root {{
                --primary-color: #60a5fa;
                --secondary-color: #3b82f6;
                --bg-color: #0f172a;
                --card-bg: #1e293b;
                --text-color: #f1f5f9;
                --text-secondary: #94a3b8;
                --border-color: #334155;
                --tag-bg: #1e3a5f;
                --tag-text: #60a5fa;
            }}
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--border-color);
        }}
        
        h1 {{
            font-size: 28px;
            color: var(--primary-color);
            margin-bottom: 10px;
        }}
        
        .meta {{
            color: var(--text-secondary);
            font-size: 14px;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: var(--primary-color);
        }}
        
        .stat-label {{
            font-size: 12px;
            color: var(--text-secondary);
        }}
        
        .papers-list {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        
        .paper-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border: 1px solid var(--border-color);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .paper-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        }}
        
        .paper-source {{
            display: inline-block;
            background: var(--primary-color);
            color: white;
            padding: 2px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 10px;
        }}
        
        .paper-title {{
            font-size: 18px;
            font-weight: 600;
            color: var(--text-color);
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        
        .paper-title a {{
            color: inherit;
            text-decoration: none;
        }}
        
        .paper-title a:hover {{
            color: var(--primary-color);
        }}
        
        .paper-meta {{
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 12px;
        }}
        
        .paper-section {{
            margin-bottom: 12px;
        }}
        
        .paper-section-title {{
            font-size: 13px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .paper-section-content {{
            font-size: 14px;
            color: var(--text-color);
        }}
        
        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }}
        
        .tag {{
            display: inline-block;
            background: var(--tag-bg);
            color: var(--tag-text);
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 12px;
        }}
        
        .paper-links {{
            display: flex;
            gap: 12px;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--border-color);
        }}
        
        .paper-link {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            color: var(--primary-color);
            text-decoration: none;
            padding: 6px 12px;
            border-radius: 6px;
            background: var(--tag-bg);
            transition: background 0.2s;
        }}
        
        .paper-link:hover {{
            background: var(--secondary-color);
            color: white;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: var(--text-secondary);
        }}
        
        .empty-state-icon {{
            font-size: 48px;
            margin-bottom: 20px;
        }}
        
        footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
            color: var(--text-secondary);
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 {self.title}</h1>
            <div class="meta">📅 {date}</div>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{len(papers)}</div>
                    <div class="stat-label">论文数量</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{self._count_by_source(papers)}</div>
                    <div class="stat-label">来源数</div>
                </div>
            </div>
        </header>
        
        <div class="papers-list">
            {papers_html if papers else '<div class="empty-state"><div class="empty-state-icon">📭</div><p>暂无新论文</p></div>'}
        </div>
        
        <footer>
            <p>🤖 由 LLM Paper Tracker 自动生成</p>
            <p>专注领域：Education, Benchmark</p>
        </footer>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_papers_html(self, papers: List[Dict]) -> str:
        """生成论文列表HTML"""
        if not papers:
            return ""
        
        papers_html = []
        for i, paper in enumerate(papers):
            paper_html = self._generate_paper_html(paper, i + 1)
            papers_html.append(paper_html)
        
        return '\n'.join(papers_html)
    
    def _generate_paper_html(self, paper: Dict, index: int) -> str:
        """生成单篇论文HTML"""
        title = paper.get('title', '无标题')
        authors = paper.get('authors', [])
        if isinstance(authors, list):
            authors_str = ', '.join(authors[:5]) + ('等' if len(authors) > 5 else '')
        else:
            authors_str = str(authors)
        
        source = paper.get('source', 'arXiv')
        date = paper.get('published', '')
        summary = paper.get('summary', '')[:300] + ('...' if len(paper.get('summary', '')) > 300 else '')
        
        methods = paper.get('methods', '暂无')
        problem = paper.get('problem', '暂无')
        contribution = paper.get('contribution', '暂无')
        related_areas = paper.get('related_areas', '')
        highlights = paper.get('highlights', '')
        
        arxiv_url = paper.get('arxiv_url', paper.get('url', ''))
        pdf_url = paper.get('pdf_url', '')
        
        tags = []
        if related_areas:
            if isinstance(related_areas, str):
                tags = [t.strip() for t in related_areas.split('、') if t.strip()]
            elif isinstance(related_areas, list):
                tags = related_areas
        
        tags_html = ''
        if tags:
            tags_inner = ''.join([f'<span class="tag">{tag}</span>' for tag in tags[:4]])
            tags_html = f'<div class="tags">{tags_inner}</div>'
        
        links_html = []
        if arxiv_url:
            links_html.append(f'<a href="{arxiv_url}" class="paper-link" target="_blank">🔗 arXiv</a>')
        if pdf_url:
            links_html.append(f'<a href="{pdf_url}" class="paper-link" target="_blank">📄 PDF</a>')
        
        links_html_str = '<div class="paper-links">' + ''.join(links_html) + '</div>' if links_html else ''
        
        return f"""
        <div class="paper-card">
            <span class="paper-source">{source}</span>
            <h2 class="paper-title">
                <a href="{arxiv_url}" target="_blank">{index}. {title}</a>
            </h2>
            <div class="paper-meta">
                👥 {authors_str} | 📅 {date}
            </div>
            
            <div class="paper-section">
                <div class="paper-section-title">🎯 解决的问题</div>
                <div class="paper-section-content">{problem}</div>
            </div>
            
            <div class="paper-section">
                <div class="paper-section-title">🔧 运用技术</div>
                <div class="paper-section-content">{methods}</div>
            </div>
            
            <div class="paper-section">
                <div class="paper-section-title">💡 主要贡献</div>
                <div class="paper-section-content">{contribution}</div>
            </div>
            
            {tags_html}
            {links_html_str}
        </div>"""
    
    def _count_by_source(self, papers: List[Dict]) -> int:
        """统计来源数量"""
        sources = set()
        for paper in papers:
            sources.add(paper.get('source', 'Unknown'))
        return len(sources)
    
    def save_html(self, papers: List[Dict], output_path: Optional[str] = None) -> str:
        """保存HTML到文件"""
        html = self.generate(papers)
        
        if output_path is None:
            base_dir = Path(__file__).parent.parent.parent
            date_str = datetime.now().strftime("%Y%m%d")
            output_path = base_dir / "data" / "reports" / f"report_{date_str}.html"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(output_path)
