import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: Optional[str] = None):
        if config_file is None:
            base_dir = Path(__file__).parent
            config_file = base_dir / "config.yaml"
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_file.exists():
            return self._default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config if config else {}
        except (yaml.YAMLError, IOError):
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "paper": {
                "keywords": ["LLM", "Large Language Model", "GPT", "Language Model", "Transformer", "ChatGPT"],
                "focus_areas": ["Education", "Benchmark", "evaluation", "assessment", "learning"],
                "max_papers_per_day": 10,
                "days_back": 7
            },
            "arxiv": {
                "categories": ["cs.CL", "cs.LG", "cs.AI"],
                "enabled": True
            },
            "conferences": {
                "enabled": False,
                "list": ["NeurIPS", "AAAI", "ACL", "EMNLP", "ICLR", "KDD", "CHI"]
            },
            "llm": {
                "api_key": os.environ.get("DASHSCOPE_API_KEY", ""),
                "base_url": os.environ.get("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                "model": os.environ.get("DASHSCOPE_MODEL", "qwen3.5-plus"),
                "enabled": True,
                "timeout": 180
            },
            "email": {
                "enabled": True,
                "smtp_host": os.environ.get("SMTP_HOST", "smtp.qq.com"),
                "smtp_port": int(os.environ.get("SMTP_PORT", "465")),
                "smtp_user": os.environ.get("SMTP_USER", ""),
                "smtp_password": os.environ.get("SMTP_PASSWORD", ""),
                "from_name": "LLM Paper Tracker",
                "to_emails": [os.environ.get("TO_EMAIL", "")]
            },
            "scheduler": {
                "time": "09:30",
                "enabled": True
            },
            "logging": {
                "level": "INFO",
                "file": "data/logs/tracker.log"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """设置配置项"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
    
    def save(self):
        """保存配置到文件"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config
