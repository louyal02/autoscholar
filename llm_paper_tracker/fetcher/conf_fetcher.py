"""会议论文获取模块"""
import urllib.request
import urllib.parse
import json
import ssl
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConferenceFetcher:
    """CCF会议论文获取器"""
    
    DBLP_BASE_URL = "https://dblp.org/search/publ/api"
    
    CONFERENCE_aliases = {
        "NeurIPS": "neural information processing systems",
        "AAAI": "aaai",
        "ACL": "annual meeting of the association for computational linguistics",
        "EMNLP": "empirical methods in natural language processing",
        "ICLR": "international conference on learning representations",
        "KDD": "knowledge discovery and data mining",
        "CHI": "human factors in computing systems"
    }
    
    def __init__(self, conferences: List[str] = None, keywords: List[str] = None):
        self.conferences = conferences or ["NeurIPS", "AAAI", "ACL", "EMNLP", "ICLR", "KDD", "CHI"]
        self.keywords = keywords or ["LLM", "Large Language Model", "GPT", "Transformer"]
        self._create_ssl_context()
    
    def _create_ssl_context(self):
        """创建SSL上下文，跳过证书验证"""
        try:
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        except Exception:
            self.ssl_context = None
    
    def _create_request(self, url: str) -> urllib.request.Request:
        """创建请求对象"""
        return urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
        )
    
    def fetch_papers(self, max_results_per_conf: int = 20) -> List[Dict]:
        """获取各会议的论文"""
        all_papers = []
        
        for conf in self.conferences:
            try:
                papers = self._fetch_conference_papers(conf, max_results_per_conf)
                all_papers.extend(papers)
                logger.info(f"Fetched {len(papers)} papers from {conf}")
            except Exception as e:
                logger.error(f"Error fetching papers from {conf}: {e}")
        
        return all_papers
    
    def _fetch_conference_papers(self, conference: str, max_results: int) -> List[Dict]:
        """从DBLP获取单个会议的论文"""
        query = self._build_query(conference)
        params = urllib.parse.urlencode({
            'q': query,
            'h': max_results,
            'format': 'json'
        })
        
        url = f"{self.DBLP_BASE_URL}?{params}"
        
        try:
            request = self._create_request(url)
            
            if self.ssl_context:
                with urllib.request.urlopen(request, context=self.ssl_context, timeout=30) as response:
                    data = json.loads(response.read().decode('utf-8'))
            else:
                with urllib.request.urlopen(request, timeout=30) as response:
                    data = json.loads(response.read().decode('utf-8'))
            
            return self._parse_dblp_response(data, conference)
        except Exception as e:
            logger.warning(f"DBLP fetch failed for {conference}: {e}")
            return []
    
    def _build_query(self, conference: str) -> str:
        """构建DBLP查询"""
        conf_key = self.CONFERENCE_aliases.get(conference, conference.lower())
        keyword_query = " OR ".join([f"{kw}" for kw in self.keywords])
        return f"venue:{conf_key} AND ({keyword_query})"
    
    def _parse_dblp_response(self, data: Dict, conference: str) -> List[Dict]:
        """解析DBLP响应"""
        papers = []
        
        hits = data.get('result', {}).get('hits', {}).get('hit', [])
        if not isinstance(hits, list):
            hits = [hits]
        
        for hit in hits:
            info = hit.get('info', {})
            
            authors = info.get('authors', {}).get('author', [])
            if isinstance(authors, dict):
                authors = [authors.get('text', '')]
            elif isinstance(authors, list):
                authors = [a.get('text', '') if isinstance(a, dict) else str(a) for a in authors]
            
            paper = {
                'id': f"dblp:{info.get('key', '')}",
                'title': info.get('title', ''),
                'summary': info.get('abstract', ''),
                'authors': authors,
                'year': info.get('year', datetime.now().year),
                'venue': info.get('venue', conference),
                'url': info.get('url', ''),
                'pdf_url': self._extract_pdf_url(info),
                'source': conference,
                'published': f"{info.get('year', datetime.now().year)}-01-01"
            }
            papers.append(paper)
        
        return papers
    
    def _extract_pdf_url(self, info: Dict) -> str:
        """提取PDF链接"""
        return info.get('pdf', '')
    
    def fetch_latest_conference_papers(self, conference: str, year: int = None) -> List[Dict]:
        """获取特定会议的最新论文"""
        if year is None:
            year = datetime.now().year
        
        self.conferences = [conference]
        return self._fetch_conference_papers(conference, 50)
