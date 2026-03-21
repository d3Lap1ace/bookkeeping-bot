"""配置管理模块，从 JSON 文件加载应用配置"""
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bookkeeping_bot.utils.exceptions import ConfigurationError


@dataclass
class Config:
    """应用配置类，从 JSON 文件加载所有配置项"""

    # Telegram Bot 配置
    telegram_bot_token: str

    # LLM 配置
    llm_api_key: str
    llm_base_url: str
    llm_model: str

    # Notion 配置
    notion_token: str
    notion_database_id: str

    # 重试配置
    max_retries: int
    retry_base_delay: float

    # 日志配置
    log_level: str

    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> "Config":
        """
        从 JSON 文件加载配置

        Args:
            config_path: 配置文件路径，默认为 ~/.bookkeeping/config.json

        Returns:
            Config: 加载完成的配置对象

        Raises:
            ConfigurationError: 当配置文件不存在或格式错误时
        """
        config_path = config_path or cls._get_default_config_path()

        if not config_path.exists():
            raise ConfigurationError(
                f"配置文件不存在: {config_path}\n"
                f"请创建配置文件，参考示例: https://github.com/d3lap1ace/bookeeping-skills#配置"
            )

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"配置文件格式错误: {e}")

        # 验证必需配置项
        required_keys = [
            "telegram_bot_token",
            "llm_api_key",
            "notion_token",
            "notion_database_id",
        ]

        missing_keys = [key for key in required_keys if key not in config_data or not config_data[key]]
        if missing_keys:
            raise ConfigurationError(f"配置文件缺少必需的配置项: {', '.join(missing_keys)}")

        # 可选配置项（带默认值）
        return cls(
            telegram_bot_token=config_data["telegram_bot_token"],
            llm_api_key=config_data["llm_api_key"],
            llm_base_url=config_data.get("llm_base_url", "https://api.openai.com/v1"),
            llm_model=config_data.get("llm_model", "gpt-4o-mini"),
            notion_token=config_data["notion_token"],
            notion_database_id=config_data["notion_database_id"],
            max_retries=config_data.get("max_retries", 3),
            retry_base_delay=config_data.get("retry_base_delay", 1.0),
            log_level=config_data.get("log_level", "INFO"),
        )

    @classmethod
    def from_env(cls) -> "Config":
        """
        从环境变量加载配置（兼容旧版本）

        Returns:
            Config: 加载完成的配置对象

        Raises:
            ConfigurationError: 当必需的环境变量未设置时
        """
        # 必需配置项
        telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_bot_token:
            raise ConfigurationError("TELEGRAM_BOT_TOKEN is required")

        llm_api_key = os.getenv("LLM_API_KEY")
        if not llm_api_key:
            raise ConfigurationError("LLM_API_KEY is required")

        notion_token = os.getenv("NOTION_TOKEN")
        if not notion_token:
            raise ConfigurationError("NOTION_TOKEN is required")

        notion_database_id = os.getenv("NOTION_DATABASE_ID")
        if not notion_database_id:
            raise ConfigurationError("NOTION_DATABASE_ID is required")

        # 可选配置项（带默认值）
        return cls(
            telegram_bot_token=telegram_bot_token,
            llm_api_key=llm_api_key,
            llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            notion_token=notion_token,
            notion_database_id=notion_database_id,
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            retry_base_delay=float(os.getenv("RETRY_BASE_DELAY", "1.0")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    @staticmethod
    def _get_default_config_path() -> Path:
        """
        获取默认配置文件路径

        优先级：
        1. 环境变量 BOOKKEEPING_CONFIG_PATH
        2. ~/.bookkeeping/config.json
        3. ./bookkeeping.config.json

        Returns:
            Path: 配置文件路径
        """
        # 1. 环境变量
        env_path = os.getenv("BOOKKEEPING_CONFIG_PATH")
        if env_path:
            return Path(env_path).expanduser()

        # 2. ~/.bookkeeping/config.json
        home_config = Path("~/.bookkeeping/config.json").expanduser()
        if home_config.exists():
            return home_config

        # 3. ./bookkeeping.config.json
        local_config = Path("bookkeeping.config.json")
        if local_config.exists():
            return local_config

        # 默认返回 ~/.bookkeeping/config.json
        return home_config

    @staticmethod
    def get_example_config() -> dict:
        """
        获取示例配置

        Returns:
            dict: 示例配置字典
        """
        return {
            "telegram_bot_token": "你的 Telegram Bot Token (从 @BotFather 获取)",
            "llm_api_key": "你的 LLM API Key (OpenAI 或兼容服务)",
            "llm_base_url": "https://api.openai.com/v1",
            "llm_model": "gpt-4o-mini",
            "notion_token": "你的 Notion Integration Token",
            "notion_database_id": "你的 Notion Database ID",
            "max_retries": 3,
            "retry_base_delay": 1.0,
            "log_level": "INFO",
        }
