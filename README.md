# LLM Paper Tracker

每日自动追踪LLM领域最新论文，生成HTML简报并发送到邮箱。

## 功能特性

- 📚 每日自动从 arXiv 获取 LLM 相关论文
- 🎯 精确筛选：(LLM同义词) AND (教育同义词 OR 基准测试同义词)
- 🤖 使用阿里百炼 qwen3.5-plus 分析论文
- 📰 生成美观的 HTML 简报
- 📧 自动发送到指定邮箱
- 🔄 去重机制，避免重复推送

## 论文来源

- **arXiv**: cs.CL, cs.LG, cs.AI

## 筛选逻辑

使用精确的arXiv搜索语句：
```
(LLM OR "Large Language Model" OR GPT OR Language Model OR Transformer OR ChatGPT) 
AND 
(education OR educational OR learning OR teaching OR student OR benchmark OR leaderboard)
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

改名 `config.yaml.example` 为 `config.yaml`，填入配置：

```yaml
llm:
  api_key: "your-api-key"
  model: "your-model-name"

email:
  smtp_host: "smtp.qq.com"
  smtp_user: "your-email@qq.com"
  smtp_password: "your-auth-code"
  to_emails:
    - "recipient@example.com"
```

### 3. 运行

```bash
# 立即运行一次
python llm_paper_tracker/main.py --run-now

# 设置每日定时运行（每天9:30）
python llm_paper_tracker/main.py --setup-task

# 测试邮件配置
python llm_paper_tracker/main.py --test-email
```

## 定时任务

已设置 Windows 任务计划程序：
- 任务名：`LLMPaperTracker`
- 运行时间：每天 09:30

查看/删除定时任务：
```cmd
schtasks /query /tn "LLMPaperTracker"
schtasks /delete /tn "LLMPaperTracker"
```

## 配置选项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `paper.max_papers_per_day` | 每日最大推送数 | 10 |
| `llm.model` | 分析模型 | qwen3.5-plus |
| `scheduler.time` | 运行时间 | 09:30 |

## 项目结构

```
llm_paper_tracker/
├── main.py              # 主程序
├── config.yaml          # 配置文件
├── config.yaml.example  # 配置示例
├── fetcher/
│   └── arxiv_fetcher.py   # arXiv论文获取
├── processor/
│   ├── analyzer.py         # LLM分析
│   ├── deduplicator.py    # 去重
│   └── html_generator.py  # HTML生成
├── sender/
│   └── email_sender.py    # 邮件发送
└── scheduler/
    └── task_scheduler.py   # 定时任务
```

## 依赖

- openai>=1.0.0
- pyyaml>=6.0
- beautifulsoup4>=4.12.0

## 许可证

MIT License
