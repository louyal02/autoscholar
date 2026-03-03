# LLM Paper Tracker

每日自动追踪LLM领域最新论文，生成HTML简报并发送到邮箱。

## 功能特性

- 📚 每日自动从 arXiv 获取 LLM 相关论文
- 🎯 严格筛选：LLM+教育 或 LLM+基准测试
- 🤖 使用阿里百炼 qwen3.5-plus 分析论文
- 📰 生成美观的 HTML 简报
- 📧 自动发送到指定邮箱
- 🔄 去重机制，避免重复推送

## 论文来源

- **arXiv**: cs.CL, cs.LG, cs.AI

## 筛选领域

- **Education**: 教育相关（education, learning, teaching, student, course等）
- **Benchmark**: 基准测试相关（benchmark, leaderboard, 排行榜等）

只有同时满足"LLM关键词" AND ("教育关键词" OR "基准测试关键词")的论文才会被推送。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置说明

配置文件：`llm_paper_tracker/config.yaml`

```yaml
llm:
  api_key: "your-api-key"          # 阿里百炼API Key
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  model: "qwen3.5-plus"             # 使用模型

email:
  smtp_host: "smtp.qq.com"
  smtp_port: 465
  smtp_user: "your-email@qq.com"
  smtp_password: "your-auth-code"
  to_emails:
    - "recipient@example.com"

scheduler:
  time: "09:30"                    # 每日运行时间
```

### 3. 运行

```bash
# 立即运行一次
python -m llm_paper_tracker.main --run-now

# 设置Windows定时任务（每天9:30）
schtasks /create /tn "LLMPaperTracker" /tr "python -m llm_paper_tracker.main --run-now" /sc daily /st 09:30 /f

# 测试邮件配置
python -m llm_paper_tracker.main --test-email
```

## 项目结构

```
llm_paper_tracker/
├── config.yaml              # 配置文件
├── main.py                  # 主入口
├── config.py                # 配置管理
├── fetcher/                 # 论文获取
│   ├── arxiv_fetcher.py
│   └── conf_fetcher.py
├── processor/               # 处理模块
│   ├── deduplicator.py      # 去重
│   ├── analyzer.py          # LLM分析
│   └── html_generator.py   # HTML生成
├── sender/
│   └── email_sender.py      # 邮件发送
└── scheduler/
    └── task_scheduler.py    # 定时任务
```

## 配置选项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `paper.max_papers_per_day` | 每日最大推送数 | 10 |
| `paper.days_back` | 回溯天数 | 7 |
| `llm.model` | 分析模型 | qwen3.5-plus |
| `llm.timeout` | API超时(秒) | 180 |
| `scheduler.time` | 运行时间 | 09:30 |

## 使用说明

1. **首次运行**：配置好config.yaml后，运行 `--run-now` 测试
2. **定时任务**：使用Windows任务计划程序设置每日自动运行
3. **去重**：已发送文章保存在 `data/sent_papers.json`

## 依赖

- openai>=1.0.0
- pyyaml>=6.0
- beautifulsoup4>=4.12.0

## 注意事项

- 筛选严格：只推送LLM+教育或LLM+基准测试相关论文
- 如果7天内找不到10篇，会依次回溯到14/30/60/90/180/365天
- 只有一年都找不到10篇时，才会推送纯LLM文章

## 许可证

MIT License
