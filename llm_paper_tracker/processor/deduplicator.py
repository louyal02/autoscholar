"""文章去重管理器"""
import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class Deduplicator:
    """文章去重管理器"""
    
    def __init__(self, data_file: Optional[str] = None):
        if data_file is None:
            base_dir = Path(__file__).parent.parent.parent
            data_file = base_dir / "data" / "sent_papers.json"
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.sent_papers = self._load_sent_papers()
    
    def _load_sent_papers(self) -> Dict:
        """加载已发送文章列表"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"papers": [], "last_updated": ""}
        return {"papers": [], "last_updated": ""}
    
    def _save_sent_papers(self):
        """保存已发送文章列表"""
        self.sent_papers["last_updated"] = datetime.now().isoformat()
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.sent_papers, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self, title: str, date: Optional[str] = None) -> str:
        """生成唯一ID"""
        if date is None:
            date = datetime.now().strftime("%Y-%m")
        content = f"{title}_{date}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def is_sent(self, title: str, date: Optional[str] = None) -> bool:
        """检查文章是否已发送"""
        paper_id = self._generate_id(title, date)
        return any(p['id'] == paper_id for p in self.sent_papers.get('papers', []))
    
    def mark_sent(self, title: str, date: Optional[str] = None, metadata: Optional[Dict] = None):
        """标记文章为已发送"""
        paper_id = self._generate_id(title, date)
        paper_info = {
            "id": paper_id,
            "title": title,
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "sent_at": datetime.now().isoformat()
        }
        if metadata:
            paper_info.update(metadata)
        
        self.sent_papers.setdefault('papers', []).append(paper_info)
        self._save_sent_papers()
    
    def filter_new_papers(self, papers: List[Dict]) -> List[Dict]:
        """过滤出未发送的新文章"""
        new_papers = []
        for paper in papers:
            if not self.is_sent(paper.get('title', ''), paper.get('date')):
                new_papers.append(paper)
        return new_papers
    
    def get_sent_count(self) -> int:
        """获取已发送文章数量"""
        return len(self.sent_papers.get('papers', []))
