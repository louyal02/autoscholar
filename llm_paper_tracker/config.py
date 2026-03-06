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
                "max_papers_per_day": 10,
                "days_back": 7
            },
            "arxiv": {
                "categories": ["cs.CL", "cs.LG", "cs.AI"],
                "enabled": True
            },
            "llm": {
                "api_key": "",
                "model": "qwen3.5-plus",
                "enabled": True,
                "timeout": 180
            },
            "email": {
                "enabled": True,
                "smtp_host": "smtp.qq.com",
                "smtp_port": 465,
                "smtp_user": "",
                "smtp_password": "",
                "from_name": "LLM Paper Tracker",
                "to_emails": []
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
