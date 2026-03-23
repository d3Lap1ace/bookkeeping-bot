# 📖 AI 记账 Bot - Bookkeeping Bot

> 一个基于 Telegram 的 AI 记账助手，支持自然语言记账、查询、修改和删除支出。数据存储在 Notion 中，每个用户独立部署。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

## ✨ 特性

- 🤖 **AI 驱动** - 使用 LLM 理解自然语言，无需记忆复杂命令
- 💬 **Telegram 集成** - 在 Telegram 中直接对话，无需额外 APP
- 📊 **Notion 存储** - 数据存储在个人 Notion 数据库，安全可控
- 🔍 **智能查询** - 支持自然语言查询，如"今天花了多少钱"
- ✏️ **灵活修改** - 支持修改和删除已记录的支出
- 🔄 **智能重试** - 自动处理网络波动和 API 限流

## 🏗️ 架构设计

```
┌─────────────┐
│  Telegram   │
│     Bot     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   Agent Core        │
│  (LLM + Skills)     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Storage Layer      │
│  (抽象接口)          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Notion Adapter    │
└─────────────────────┘
```

## 🚀 快速开始

### 1. 安装

推荐使用 `pipx` 安装 CLI 工具：

```bash
pipx install bookkeeping-bot
```

如果还没有安装 `pipx`：

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

本地源码安装：

```bash
python -m pip install .
```

开发模式安装：

```bash
python -m pip install -e ".[dev]"
```

安装完成后会生成命令：

```bash
bookkeeping-bot
```

### 2. 准备 Notion 数据库

1. 在 Notion 中创建一个新数据库
2. 添加以下列：

| 列名 | 类型 | 说明 |
|------|------|------|
| Description | Title | 支出描述 |
| Amount | Number | 金额 |
| Category | Select | 分类 |
| Date | Date | 日期 |

3. 获取 Database ID（从 URL 中复制）

### 3. 获取 API Token

**Telegram Bot Token:**
1. 在 Telegram 中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 复制获得的 Token

**Notion Token:**
1. 访问 [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. 创建新的 Integration
3. 复制 Internal Integration Token
4. 在数据库设置中添加该 Integration 连接

**LLM API Key:**
- OpenAI API Key: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- 或兼容服务的 API Key（如 Ollama、LM Studio 等）

### 4. 配置

创建配置文件 `~/.bookkeeping/config.json`：

```bash
mkdir -p ~/.bookkeeping
cat > ~/.bookkeeping/config.json << 'EOF'
{
  "telegram_bot_token": "你的 Telegram Bot Token",
  "llm_api_key": "你的 LLM API Key",
  "llm_base_url": "https://api.openai.com/v1",
  "llm_model": "gpt-4o-mini",
  "notion_token": "你的 Notion Token",
  "notion_database_id": "你的 Notion Database ID"
}
EOF
```

或参考 [config.example.json](config.example.json)

### 5. 启动

```bash
bookkeeping-bot
```

看到以下提示表示启动成功：

```
╔═══════════════════════════════════════════════════════╗
║         📖 AI 记账 Bot - Bookkeeping Bot              ║
╚═══════════════════════════════════════════════════════╝

✓ Bot 已启动，等待消息...
```

Bot 启动后，在 Telegram 中发送 `/start` 开始使用！

## 📝 使用方法

在 Telegram 中找到你的机器人，开始对话：

### 记录支出
```
你: 花了30块吃午饭
Bot: ✅ 已记录：餐饮 30.0元

你: 打车去公司50元
Bot: ✅ 已记录：交通 50.0元
```

### 查询支出
```
你: 今天花了多少钱
Bot: 📊 支出记录：
    • 2026-03-17 | 餐饮 | 午饭 | 30.0元
    • 2026-03-17 | 交通 | 打车去公司 | 50.0元
    总计：80.0元
```

### 修改记录
```
你: 把午餐改成40块
Bot: ✅ 已更新支出记录
```

### 删除记录
```
你: 删除刚才的记录
Bot: ✅ 已删除支出记录
```

### 支持的命令
- `/start` - 开始使用
- `/help` - 查看帮助
- `/clear` - 清除对话历史

## ⚙️ 配置选项

| 配置项 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `telegram_bot_token` | ✅ | - | Telegram Bot Token |
| `llm_api_key` | ✅ | - | LLM API Key |
| `llm_base_url` | ❌ | `https://api.openai.com/v1` | LLM API 地址 |
| `llm_model` | ❌ | `gpt-4o-mini` | 使用的模型名称 |
| `notion_token` | ✅ | - | Notion Integration Token |
| `notion_database_id` | ✅ | - | Notion Database ID |
| `max_retries` | ❌ | `3` | API 调用最大重试次数 |
| `retry_base_delay` | ❌ | `1.0` | 重试基础延迟（秒） |
| `log_level` | ❌ | `INFO` | 日志级别 |

### 配置文件路径优先级

1. 环境变量 `BOOKKEEPING_CONFIG_PATH`
2. `~/.bookkeeping/config.json`
3. `./bookkeeping.config.json`

## 🔧 开发

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/d3lap1ace/bookeeping-skills.git
cd bookeeping-skills

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
python -m pip install -e ".[dev]"

# 运行测试
pytest
```

### 构建安装包

```bash
python -m build
```

构建完成后产物在 `dist/` 目录下。也可以直接安装本地构建结果：

```bash
python -m pip install dist/bookkeeping_bot-0.1.0-py3-none-any.whl
```

如果你想先本地验证 `pipx` 安装体验，也可以直接安装构建后的 wheel：

```bash
pipx install dist/bookkeeping_bot-0.1.0-py3-none-any.whl
```

### 发布到 PyPI

自动发布流程和 Trusted Publishing 配置说明见 [docs/pypi-release.md](docs/pypi-release.md)。

### 项目结构

```
bookkeeping_bot/
├── __init__.py
├── cli.py              # 命令行入口
├── config.py           # 配置管理
├── bot/                # Telegram Bot 模块
│   ├── app.py          # 应用创建
│   ├── handlers.py     # 消息处理器
│   └── formatter.py    # 响应格式化
├── core/               # 核心逻辑
│   ├── agent.py        # 记账 Agent
│   ├── llm_client.py   # LLM 客户端
│   └── skill_loader.py # Skill 加载器
├── storage/            # 存储层
│   ├── base.py         # 抽象基类
│   ├── models.py       # 数据模型
│   └── notion.py       # Notion 适配器
├── utils/              # 工具模块
│   ├── exceptions.py   # 异常定义
│   ├── retry.py        # 重试装饰器
│   └── logger.py       # 日志配置
└── skills/             # Skill 定义
    ├── record_expense.md
    ├── query_expenses.md
    ├── update_expense.md
    └── delete_expense.md
```

### 运行测试

```bash
pytest tests/ -v
```

## 🔌 扩展

### 添加新的存储后端

继承 `ExpenseStorage` 抽象基类：

```python
from storage.base import ExpenseStorage

class MyStorage(ExpenseStorage):
    async def save_expense(self, expense):
        # 实现保存逻辑
        pass
    # ... 实现其他方法
```

### 添加新的 Skill

在 `skills/` 目录下创建新的 `.md` 文件，定义参数和行为。

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系

- GitHub: [d3lap1ace](https://github.com/d3lap1ace)
- Issues: [https://github.com/d3lap1ace/bookeeping-skills/issues](https://github.com/d3lap1ace/bookeeping-skills/issues)
