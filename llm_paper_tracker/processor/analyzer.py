"""LLM分析模块"""
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """使用LLM分析论文内容"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None, timeout: int = 180):
        self.api_key = api_key
        self.base_url = base_url or "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        self.model = model or "qwen3.5-plus"
        self.timeout = timeout
        self.client = None
    
    def _get_client(self):
        """获取OpenAI客户端"""
        if self.client is None:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                    timeout=self.timeout
                )
            except ImportError:
                logger.error("OpenAI package not installed")
                return None
        return self.client
    
    def analyze_paper(self, paper: Dict) -> Dict:
        """分析单篇论文"""
        prompt = self._build_analysis_prompt(paper)
        
        try:
            client = self._get_client()
            if not client:
                return self._fallback_analysis(paper)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的AI学术论文分析师，擅长提取论文的核心技术方法和解决的问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_analysis(analysis_text)
            
        except Exception as e:
            logger.warning(f"LLM analysis failed for '{paper.get('title', '')[:50]}': {e}")
            return self._fallback_analysis(paper)
    
    def analyze_batch(self, papers: List[Dict]) -> List[Dict]:
        """批量分析论文"""
        analyzed = []
        for i, paper in enumerate(papers):
            logger.info(f"Analyzing paper {i+1}/{len(papers)}: {paper.get('title', '')[:50]}...")
            analysis = self.analyze_paper(paper)
            analyzed_paper = {**paper, **analysis}
            analyzed.append(analyzed_paper)
        return analyzed
    
    def _build_analysis_prompt(self, paper: Dict) -> str:
        """构建分析提示词"""
        title = paper.get('title', '')
        summary = paper.get('summary', '')[:1500]
        
        prompt = f"""请分析以下学术论文，提取关键信息：

论文标题：{title}

摘要：{summary}

请用JSON格式返回以下信息（只返回JSON，不要其他内容）：
{{
    "methods": "运用技术/方法（用中文，简洁描述）",
    "problem": "解决什么问题/研究目标（用中文）",
    "contribution": "主要贡献（用中文，1-2句话）",
    "related_areas": "相关领域（如：教育、评测、对话系统等，用逗号分隔）",
    "highlights": "亮点/创新点（用中文，简要）"
}}
"""
        return prompt
    
    def _parse_analysis(self, analysis_text: str) -> Dict:
        """解析LLM返回的分析结果"""
        try:
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = analysis_text[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return self._extract_from_text(analysis_text)
    
    def _extract_from_text(self, text: str) -> Dict:
        """从文本中提取分析结果"""
        return {
            "methods": "见摘要",
            "problem": "LLM相关研究",
            "contribution": "详见原文",
            "related_areas": "人工智能",
            "highlights": "需查看原文"
        }
    
    def _fallback_analysis(self, paper: Dict) -> Dict:
        """备用分析方法（不使用LLM）"""
        title = paper.get('title', '').lower()
        summary = paper.get('summary', '').lower()
        
        methods = []
        problems = []
        
        method_keywords = {
            'transformer': 'Transformer架构',
            'bert': 'BERT预训练',
            'gpt': 'GPT生成模型',
            'llm': '大语言模型',
            'rlhf': '强化学习微调',
            'prompt': '提示学习',
            'fine-tun': '微调',
            'attention': '注意力机制',
            'embedding': '嵌入表示',
            'retrieval': '检索增强',
            'rag': '检索增强生成'
        }
        
        problem_keywords = {
            'education': '教育应用',
            'learning': '学习',
            'teaching': '教学',
            'benchmark': '基准测试',
            'evaluation': '评估',
            'assessment': '评测',
            'dialogue': '对话生成',
            'question': '问答',
            'summariz': '摘要',
            'translation': '翻译',
            'reasoning': '推理',
            'code': '代码生成'
        }
        
        for kw, method in method_keywords.items():
            if kw in title or kw in summary:
                methods.append(method)
        
        for kw, problem in problem_keywords.items():
            if kw in title or kw in summary:
                problems.append(problem)
        
        return {
            "methods": '、'.join(methods) if methods else 'LLM相关技术',
            "problem": '、'.join(problems) if problems else 'LLM研究',
            "contribution": "推动LLM在相关领域的发展",
            "related_areas": '、'.join(set(problems + ['人工智能'])),
            "highlights": "基于标题和摘要分析"
        }
