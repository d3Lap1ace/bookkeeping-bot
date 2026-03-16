"""配置管理模块，从环境变量加载应用配置"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """应用配置类，从环境变量加载所有配置项"""

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
    def from_env(cls) -> "Config":
        """
        从环境变量加载配置

        Returns:
            Config: 加载完成的配置对象

        Raises:
            ValueError: 当必需的环境变量未设置时
        """
        # 必需配置项
        telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")

        llm_api_key = os.getenv("LLM_API_KEY")
        if not llm_api_key:
            raise ValueError("LLM_API_KEY is required")

        notion_token = os.getenv("NOTION_TOKEN")
        if not notion_token:
            raise ValueError("NOTION_TOKEN is required")

        notion_database_id = os.getenv("NOTION_DATABASE_ID")
        if not notion_database_id:
            raise ValueError("NOTION_DATABASE_ID is required")

        # 可选配置项（带默认值）
        llm_base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        max_retries = int(os.getenv("MAX_RETRIES", "3"))
        retry_base_delay = float(os.getenv("RETRY_BASE_DELAY", "1.0"))
        log_level = os.getenv("LOG_LEVEL", "INFO")

        return cls(
            telegram_bot_token=telegram_bot_token,
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
            llm_model=llm_model,
            notion_token=notion_token,
            notion_database_id=notion_database_id,
            max_retries=max_retries,
            retry_base_delay=retry_base_delay,
            log_level=log_level,
        )
