# AI 记账 Agent

> 一个基于 LLM 的智能记账助手，支持自然语言记录、查询、修改和删除支出，数据存储到 Notion。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

## ✨ 特性

- 🗣️ **自然语言交互** - 用日常语言记录支出，无需记忆复杂命令
- 📊 **完整 CRUD** - 支持记录、查询、修改、删除支出记录
- 🔗 **Notion 存储** - 数据存储在你的 Notion 数据库中，完全可控
- 🤖 **LLM 驱动** - 基于 OpenAI 兼容 API，支持本地模型（如 Ollama）
- 💬 **Telegram Bot** - 随时随地通过 Telegram 记账
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

### 1. 准备工作

#### 创建 Notion 数据库

1. 在 Notion 中创建一个新的数据库
2. 添加以下列：

| 列名 | 类型 | 说明 |
|------|------|------|
| Description | Title | 支出描述 |
| Amount | Number | 金额 |
| Category | Select | 分类 |
| Date | Date | 日期 |

3. 获取 Database ID（URL 中的一段 32 位字符）

#### 获取 API Token

- **Notion Token**: [创建集成](https://www.notion.so/my-integrations) 获取 Token
- **Telegram Bot Token**: 通过 [@BotFather](https://t.me/botfather) 创建 Bot 获取
- **LLM API Key**: [OpenAI API Key](https://platform.openai.com/api-keys) 或兼容服务

### 2. 安装

```bash
# 克隆仓库
git clone https://github.com/d3Lap1ace/Bookkeeping-skills.git
cd Bookkeeping-skills

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
```

`.env` 配置示例：

```bash
TELEGRAM_BOT_TOKEN=你的_bot_token
LLM_API_KEY=你的_api_key
NOTION_TOKEN=你的_notion_token
NOTION_DATABASE_ID=你的_database_id
```

### 4. 运行

```bash
python main.py
```

Bot 启动后，在 Telegram 中发送 `/start` 开始使用！

## 📖 使用示例

```
你: 花了30块吃午饭
Bot: ✅ 已记录支出
     💰 金额：30.0 元
     📂 分类：餐饮
     📝 描述：午饭

你: 今天花了多少钱
Bot: 📊 支出记录
     ──────────────────────
     📅 2026-03-10
       • 餐饮 | 午饭 | ¥30.00
       当日小计：¥30.00
     ──────────────────────
     💵 总计：¥30.00

你: 把午餐改成40块
Bot: ✅ 已更新支出记录
```

## 🛠️ 开发

### 项目结构

```
bookkeeping-skills/
├── bot/              # Telegram Bot 交互层
├── core/             # Agent 核心逻辑
├── storage/          # 存储抽象层
├── utils/            # 工具模块
├── skills/           # Agent Skills 定义（Markdown）
├── config.py         # 配置管理
├── main.py           # 应用入口
└── requirements.txt  # 依赖列表
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

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 👤 作者

**d3Lap1ace** - [GitHub](https://github.com/d3Lap1ace)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🙏 致谢

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Notion API](https://developers.notion.com/)
- [OpenAI API](https://platform.openai.com/)
