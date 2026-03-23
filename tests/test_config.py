"""测试配置管理"""
import os

import pytest

from bookkeeping_bot.config import Config
from bookkeeping_bot.utils.exceptions import ConfigurationError


class TestConfig:
    """测试 Config 类"""

    def test_from_env_missing_required_vars(self):
        """测试缺少必需环境变量"""
        # 清空环境变量
        for key in ["TELEGRAM_BOT_TOKEN", "LLM_API_KEY", "NOTION_TOKEN", "NOTION_DATABASE_ID"]:
            os.environ.pop(key, None)

        with pytest.raises(ConfigurationError):
            Config.from_env()

    def test_from_env_with_all_required_vars(self):
        """测试所有必需环境变量都存在"""
        os.environ["TELEGRAM_BOT_TOKEN"] = "test_telegram_token"
        os.environ["LLM_API_KEY"] = "test_llm_key"
        os.environ["NOTION_TOKEN"] = "test_notion_token"
        os.environ["NOTION_DATABASE_ID"] = "test_database_id"

        config = Config.from_env()

        assert config.telegram_bot_token == "test_telegram_token"
        assert config.llm_api_key == "test_llm_key"
        assert config.notion_token == "test_notion_token"
        assert config.notion_database_id == "test_database_id"

    def test_from_env_with_optional_vars(self):
        """测试可选环境变量"""
        os.environ["TELEGRAM_BOT_TOKEN"] = "test"
        os.environ["LLM_API_KEY"] = "test"
        os.environ["NOTION_TOKEN"] = "test"
        os.environ["NOTION_DATABASE_ID"] = "test"
        os.environ["LLM_BASE_URL"] = "https://custom.api.com/v1"
        os.environ["LLM_MODEL"] = "gpt-4"
        os.environ["MAX_RETRIES"] = "5"
        os.environ["RETRY_BASE_DELAY"] = "2.0"
        os.environ["LOG_LEVEL"] = "DEBUG"

        config = Config.from_env()

        assert config.llm_base_url == "https://custom.api.com/v1"
        assert config.llm_model == "gpt-4"
        assert config.max_retries == 5
        assert config.retry_base_delay == 2.0
        assert config.log_level == "DEBUG"

    def test_from_env_default_values(self):
        """测试默认值"""
        # 清除可能存在的可选环境变量
        for key in ["LLM_BASE_URL", "LLM_MODEL", "MAX_RETRIES", "RETRY_BASE_DELAY", "LOG_LEVEL"]:
            os.environ.pop(key, None)

        os.environ["TELEGRAM_BOT_TOKEN"] = "test"
        os.environ["LLM_API_KEY"] = "test"
        os.environ["NOTION_TOKEN"] = "test"
        os.environ["NOTION_DATABASE_ID"] = "test"

        config = Config.from_env()

        assert config.llm_base_url == "https://api.openai.com/v1"
        assert config.llm_model == "gpt-4o-mini"
        assert config.max_retries == 3
        assert config.retry_base_delay == 1.0
        assert config.log_level == "INFO"
