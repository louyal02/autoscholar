"""arXiv论文获取模块"""
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ArxivFetcher:
    """arXiv论文获取器"""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    def __init__(self, categories: List[str] = None, keywords: List[str] = None):
        self.categories = categories or ["cs.CL", "cs.LG", "cs.AI"]
        self.keywords = keywords or ["LLM", "Large Language Model", "GPT", "Transformer"]
    
    def _build_query(self, keywords: List[str], categories: List[str], days_back: int = 7) -> str:
        """构建搜索查询"""
        date_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d%H%M")
        
        keyword_parts = [f"all:{kw}" for kw in keywords]
        keyword_query = " OR ".join(keyword_parts)
        
        cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
        
        full_query = f"({keyword_query}) AND ({cat_query}) AND submittedDate:[{date_from} TO 99991231235959]"
        
        return urllib.parse.quote(full_query)
    
    def fetch_papers(self, max_results: int = 50, days_back: int = 7) -> List[Dict]:
        """获取论文列表"""
        query = self._build_query(self.keywords, self.categories, days_back)
        url = f"{self.BASE_URL}?search_query={query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
        
        logger.info(f"Fetching arXiv papers with URL: {url}")
        
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read().decode('utf-8')
            
            return self._parse_arxiv_response(content)
        except Exception as e:
            logger.error(f"Error fetching arXiv papers: {e}")
            return []
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict]:
        """解析arXiv XML响应"""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', namespace):
                try:
                    paper = {
                        'id': self._get_text(entry, 'atom:id', namespace),
                        'title': self._clean_text(self._get_text(entry, 'atom:title', namespace)),
                        'summary': self._clean_text(self._get_text(entry, 'atom:summary', namespace)),
                        'authors': [author.find('atom:name', namespace).text 
                                   for author in entry.findall('atom:author', namespace)],
                        'published': self._get_text(entry, 'atom:published', namespace)[:10],
                        'updated': self._get_text(entry, 'atom:updated', namespace)[:10],
                        'categories': [cat.attrib.get('term', '') 
                                     for cat in entry.findall('atom:category', namespace)],
                        'pdf_url': self._get_pdf_url(entry, namespace),
                        'arxiv_url': self._get_text(entry, 'atom:id', namespace),
                        'source': 'arXiv'
                    }
                    papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing entry: {e}")
                    continue
                    
        except ET.ParseError as e:
            logger.error(f"Error parsing XML: {e}")
            
        return papers
    
    def _get_text(self, element, path: str, namespace: Dict) -> str:
        """获取元素文本"""
        el = element.find(path, namespace)
        return el.text if el is not None else ""
    
    def _get_pdf_url(self, entry, namespace: Dict) -> str:
        """获取PDF链接"""
        for link in entry.findall('atom:link', namespace):
            if link.attrib.get('title') == 'pdf':
                return link.attrib.get('href', '')
        return ""
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = ' '.join(text.split())
        return text.strip()
