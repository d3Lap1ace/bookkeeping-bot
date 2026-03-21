"""测试已发布包的最小运行链路"""
import importlib
import json

from telegram.ext import Application, CommandHandler, MessageHandler

from bookkeeping_bot.bot.app import create_app
from bookkeeping_bot.cli import main as cli_main
from bookkeeping_bot.config import Config


class DummyAgent:
    """最小 Agent 桩对象"""

    async def process_message(self, *args, **kwargs):
        return "ok"


class DummyLogger:
    """避免测试期间产生真实日志输出"""

    def info(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


def test_package_config_from_file(tmp_path):
    """包内 Config 可以从 JSON 文件加载"""
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "telegram_bot_token": "bot-token",
                "llm_api_key": "llm-key",
                "notion_token": "notion-token",
                "notion_database_id": "db-id",
                "llm_model": "gpt-4o-mini",
            }
        ),
        encoding="utf-8",
    )

    config = Config.from_file(config_path)

    assert config.telegram_bot_token == "bot-token"
    assert config.llm_api_key == "llm-key"
    assert config.notion_token == "notion-token"
    assert config.notion_database_id == "db-id"
    assert config.llm_base_url == "https://api.openai.com/v1"


def test_create_app_registers_expected_handlers():
    """应用应注册命令和文本消息处理器"""
    application = create_app("123:ABC", DummyAgent())

    assert isinstance(application, Application)
    assert sum(isinstance(handler, CommandHandler) for handler in application.handlers[0]) == 3
    assert sum(isinstance(handler, MessageHandler) for handler in application.handlers[0]) == 1


def test_cli_main_runs_polling(monkeypatch):
    """CLI 主入口应构建应用并启动 polling"""
    run_state = {"called": False}

    class DummyApplication:
        def run_polling(self):
            run_state["called"] = True

    dummy_config = Config(
        telegram_bot_token="bot-token",
        llm_api_key="llm-key",
        llm_base_url="https://api.openai.com/v1",
        llm_model="gpt-4o-mini",
        notion_token="notion-token",
        notion_database_id="db-id",
        max_retries=3,
        retry_base_delay=1.0,
        log_level="INFO",
    )

    monkeypatch.setattr("bookkeeping_bot.cli.print_banner", lambda: None)
    monkeypatch.setattr("bookkeeping_bot.cli.setup_logger", lambda level="INFO": DummyLogger())
    monkeypatch.setattr("bookkeeping_bot.cli.Config.from_file", lambda: dummy_config)
    monkeypatch.setattr("bookkeeping_bot.cli.NotionStorage", lambda **kwargs: object())
    monkeypatch.setattr("bookkeeping_bot.cli.LLMClient", lambda **kwargs: object())
    monkeypatch.setattr("bookkeeping_bot.cli.SkillLoader", lambda **kwargs: object())
    monkeypatch.setattr("bookkeeping_bot.cli.BookkeepingAgent", lambda **kwargs: object())
    monkeypatch.setattr("bookkeeping_bot.cli.create_app", lambda token, agent: DummyApplication())

    cli_main()

    assert run_state["called"] is True


def test_legacy_main_delegates_to_package_cli():
    """根目录 main.py 应复用包版 CLI 入口"""
    legacy_main = importlib.import_module("main")

    assert legacy_main.main is cli_main
