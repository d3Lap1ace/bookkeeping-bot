# AI Bookkeeping Agent

> An intelligent bookkeeping assistant based on LLM, supporting natural language recording, querying, modifying, and deleting expenses, with data stored in Notion.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

## Features

- **Natural Language Interaction** - Record expenses using everyday language, no need to memorize complex commands
- **Complete CRUD** - Support recording, querying, modifying, and deleting expense records
- **Notion Storage** - Data stored in your Notion database, fully under your control
- **LLM Powered** - Based on OpenAI-compatible API, supports local models (e.g., Ollama)
- **Telegram Bot** - Track expenses anytime, anywhere through Telegram
- **Smart Retry** - Automatically handles network fluctuations and API rate limiting

## Architecture Design

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
          │  (Abstract Interface)│
          └──────┬──────────────┘
                    │
                    ▼
          ┌─────────────────────┐
          │   Notion Adapter    │
          └─────────────────────┘
```

## Quick Start

### 1. Prerequisites

#### Create Notion Database

1. Create a new database in Notion
2. Add the following columns:

| Column Name | Type | Description |
|-------------|------|-------------|
| Description | Title | Expense description |
| Amount | Number | Amount |
| Category | Select | Category |
| Date | Date | Date |

3. Get the Database ID (a 32-character string in the URL)

#### Get API Tokens

- **Notion Token**: Create an [integration](https://www.notion.so/my-integrations) to get the Token
- **Telegram Bot Token**: Create a Bot via [@BotFather](https://t.me/botfather) to get it
- **LLM API Key**: [OpenAI API Key](https://platform.openai.com/api-keys) or compatible service

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/d3Lap1ace/Bookkeeping-skills.git
cd Bookkeeping-skills

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment variable template
cp .env.example .env

# Edit .env file and fill in your configuration
```

`.env` configuration example:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
LLM_API_KEY=your_api_key
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_database_id
```

### 4. Run

```bash
python main.py
```

After the Bot starts, send `/start` in Telegram to start using it!

## Usage Examples

```
You: 花了30块吃午饭
Bot: ✅ Expense recorded
     💰 Amount: 30.0 CNY
     📂 Category: 餐饮
     📝 Description: 午饭

You: 今天花了多少钱
Bot: 📊 Expense Records
     ──────────────────────
     📅 2026-03-10
       • 餐饮 | 午饭 | ¥30.00
       Daily subtotal: ¥30.00
     ──────────────────────
     💵 Total: ¥30.00

You: 把午餐改成40块
Bot: ✅ Expense record updated
```

## Development

### Project Structure

```
bookkeeping-skills/
├── bot/              # Telegram Bot interaction layer
├── core/             # Agent core logic
├── storage/          # Storage abstraction layer
├── utils/            # Utility modules
├── skills/           # Agent Skills definitions (Markdown)
├── config.py         # Configuration management
├── main.py           # Application entry point
└── requirements.txt  # Dependency list
```

### Running Tests

```bash
pytest tests/ -v
```

## Extension

### Adding New Storage Backend

Inherit from `ExpenseStorage` abstract base class:

```python
from storage.base import ExpenseStorage

class MyStorage(ExpenseStorage):
    async def save_expense(self, expense):
        # Implement save logic
        pass
    # ... implement other methods
```

### Adding New Skills

Create new `.md` files in the `skills/` directory to define parameters and behaviors.

## License

MIT License - See [LICENSE](LICENSE) for details

## Author

**d3Lap1ace** - [GitHub](https://github.com/d3Lap1ace)

## Contributing

Issues and Pull Requests are welcome!

## Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Notion API](https://developers.notion.com/)
- [OpenAI API](https://platform.openai.com/)
