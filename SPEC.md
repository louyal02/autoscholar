# LLM Paper Tracker - 项目规格说明

## 1. 项目概述

**项目名称**: LLM Paper Tracker  
**项目类型**: Python自动化工具  
**核心功能**: 每日自动从arXiv和CCF高质量会议获取LLM相关论文，生成HTML简报并发送到邮箱  
**目标用户**: 从事LLM研究的教育/benchmark领域研究人员

---

## 2. 功能规格

### 2.1 论文来源
- **arXiv**: cs.CL, cs.LG, cs.AI分类下的LLM相关论文
- **CCF会议**: NeurIPS, AAAI, ACL, EMNLP, ICLR, KDD, CHI
- **搜索关键词**: LLM, Large Language Model, GPT, Language Model, Transformer

### 2.2 筛选领域
- Education (教育)
- Benchmark (基准测试)
- 侧重：教育应用、评测基准相关论文

### 2.3 论文获取方式
- arXiv API (优先，无反爬)
- 会议官网/DBLP (备选)
- 支持MCP/Agent作为备选方案处理反爬

### 2.4 去重机制
- 使用文章标题+日期生成唯一ID
- 本地JSON文件存储已推送文章列表
- 每次获取前检查，避免重复推送

### 2.5 LLM分析模块
- 使用用户提供的API Key调用大模型
- 分析内容：
  - 运用技术 (Methods/Techniques)
  - 解决问题 (Problem Addressed)
  - 主要贡献 (Key Contributions)
  - 相关领域 (Related Areas)
- 支持模型：OpenAI API兼容格式

### 2.6 HTML简报生成
- 响应式设计，美观易读
- 包含：标题、作者、摘要、技术要点、问题描述、链接
- 支持深色/浅色主题

### 2.7 邮件发送
- SMTP协议发送
- 支持HTML格式邮件
- 可配置发件人/收件人

### 2.8 定时任务
- 每日9:30自动执行
- Windows任务计划程序集成
- 支持手动触发

---

## 3. 技术架构

```
llm_paper_tracker/
├── config/
│   └── config.yaml          # 配置文件
├── src/
│   ├── __init__.py
│   ├── fetcher/
│   │   ├── __init__.py
│   │   ├── arxiv_fetcher.py    # arXiv获取
│   │   ├── conf_fetcher.py     # 会议论文获取
│   │   └── base.py             # 基类
│   ├── processor/
│   │   ├── __init__.py
│   │   ├── deduplicator.py     # 去重
│   │   ├── analyzer.py          # LLM分析
│   │   └── html_generator.py   # HTML生成
│   ├── sender/
│   │   ├── __init__.py
│   │   └── email_sender.py     # 邮件发送
│   └── scheduler/
│       ├── __init__.py
│       └── task_scheduler.py   # 定时任务
├── data/
│   ├── sent_papers.json    # 已发送文章列表
│   └── logs/               # 日志目录
├── main.py                 # 主入口
├── requirements.txt        # 依赖
└── README.md               # 说明文档
```

---

## 4. 验收标准

1. ✅ 能从arXiv获取最新LLM论文
2. ✅ 能从CCF会议获取论文信息
3. ✅ 去重列表正常工作，不重复推送
4. ✅ LLM分析生成技术要点和问题描述
5. ✅ HTML简报格式美观，内容完整
6. ✅ 邮件成功发送到指定邮箱
7. ✅ 定时任务每日9:30自动运行
8. ✅ 配置文件可自定义所有参数
9. ✅ 支持手动运行和调试模式
