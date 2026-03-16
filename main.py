"""AI 记账 Agent 应用入口"""
import asyncio
import logging

from telegram.ext import Application

from config import Config
from core.agent import BookkeepingAgent
from core.llm_client import LLMClient
from core.skill_loader import SkillLoader
from storage.notion import NotionStorage
from bot.handlers import TelegramBotHandler
from utils.logger import setup_logger
from utils.exceptions import ConfigurationError


async def main():
    """
    应用启动流程：

    1. 加载配置
    2. 初始化日志
    3. 初始化存储层（Notion）
    4. 初始化 LLM 客户端
    5. 加载 Skills
    6. 初始化 Agent
    7. 启动 Telegram Bot
    """
    try:
        # 1. 加载配置
        config = Config.from_env()
        logger = setup_logger(level=config.log_level)
        logger.info("AI 记账 Agent 启动中...")

        # 2. 初始化存储层
        logger.info("初始化 Notion 存储适配器...")
        storage = NotionStorage(
            token=config.notion_token,
            database_id=config.notion_database_id,
            max_retries=config.max_retries,
        )

        # 3. 初始化 LLM 客户端
        logger.info(f"初始化 LLM 客户端: {config.llm_base_url}")
        llm_client = LLMClient(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            model=config.llm_model,
        )

        # 4. 加载 Skills
        logger.info("加载 Agent Skills...")
        skill_loader = SkillLoader(skills_dir="skills")

        # 5. 初始化 Agent
        logger.info("初始化记账 Agent...")
        agent = BookkeepingAgent(
            llm_client=llm_client,
            storage=storage,
            skill_loader=skill_loader,
        )

        # 6. 初始化 Telegram Bot
        logger.info("初始化 Telegram Bot...")
        application = Application.builder().token(config.telegram_bot_token).build()

        # 创建消息处理器
        bot_handler = TelegramBotHandler(agent=agent)

        # 注册命令处理器
        application.add_handler(CommandHandler("start", bot_handler.handle_start))
        application.add_handler(CommandHandler("help", bot_handler.handle_help))
        application.add_handler(CommandHandler("clear", bot_handler.handle_clear))

        # 注册消息处理器
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.handle_message))

        # 注册错误处理器
        application.add_error_handler(bot_handler.handle_error)

        # 7. 启动 Bot
        logger.info("Bot 已启动，等待消息...")
        logger.info("按 Ctrl+C 停止")

        await application.initialize()
        await application.start()
        await application.run_polling()

    except ConfigurationError as e:
        logger.error(f"配置错误: {e}")
        logger.error("请检查 .env 文件中的环境变量配置")

    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭...")

    except Exception as e:
        logger.error(f"启动失败: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
