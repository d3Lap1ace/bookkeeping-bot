"""命令行入口"""
import asyncio
import sys
from pathlib import Path

from bookkeeping_bot.config import Config
from bookkeeping_bot.bot.handlers import TelegramBotHandler
from bookkeeping_bot.bot.app import create_app
from bookkeeping_bot.core.agent import BookkeepingAgent
from bookkeeping_bot.core.llm_client import LLMClient
from bookkeeping_bot.core.skill_loader import SkillLoader
from bookkeeping_bot.storage.notion import NotionStorage
from bookkeeping_bot.utils.exceptions import ConfigurationError
from bookkeeping_bot.utils.logger import setup_logger, logger


def print_banner():
    """打印启动横幅"""
    print("""
╔═══════════════════════════════════════════════════════╗
║         📖 AI 记账 Bot - Bookkeeping Bot              ║
╚═══════════════════════════════════════════════════════╝
    """)


def print_example_config():
    """打印示例配置"""
    example = Config.get_example_config()
    print("请创建配置文件: ~/.bookkeeping/config.json")
    print("\n示例配置内容:")
    print("-" * 50)

    import json
    print(json.dumps(example, indent=2, ensure_ascii=False))

    print("\n" + "-" * 50)
    print("\n配置说明:")
    print("  telegram_bot_token: 从 @BotFather 获取")
    print("  llm_api_key: OpenAI API Key 或兼容服务的 Key")
    print("  notion_token: Notion Integration Token")
    print("  notion_database_id: Notion Database ID")


async def main():
    """应用主入口"""
    print_banner()

    try:
        # 1. 加载配置
        logger.info("正在加载配置...")
        config = Config.from_file()
        logger.info("✓ 配置加载成功")

        # 2. 初始化日志
        logger = setup_logger(level=config.log_level)

        # 3. 初始化存储层
        logger.info("正在初始化 Notion 存储适配器...")
        storage = NotionStorage(
            token=config.notion_token,
            database_id=config.notion_database_id,
            max_retries=config.max_retries,
        )
        logger.info("✓ Notion 存储适配器已初始化")

        # 4. 初始化 LLM 客户端
        logger.info(f"正在初始化 LLM 客户端: {config.llm_base_url}")
        llm_client = LLMClient(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            model=config.llm_model,
        )
        logger.info(f"✓ LLM 客户端已初始化 (模型: {config.llm_model})")

        # 5. 加载 Skills
        logger.info("正在加载 Agent Skills...")
        skill_loader = SkillLoader(skills_dir=Path(__file__).parent / "skills")
        logger.info("✓ Skills 已加载")

        # 6. 初始化 Agent
        logger.info("正在初始化记账 Agent...")
        agent = BookkeepingAgent(
            llm_client=llm_client,
            storage=storage,
            skill_loader=skill_loader,
        )
        logger.info("✓ Agent 已初始化")

        # 7. 创建并启动 Telegram Bot
        logger.info("正在启动 Telegram Bot...")
        application = create_app(config.telegram_bot_token, agent)

        logger.info("")
        logger.info("═══════════════════════════════════════════════════")
        logger.info("✓ Bot 已启动，等待消息...")
        logger.info("按 Ctrl+C 停止")
        logger.info("═══════════════════════════════════════════════════")
        logger.info("")

        await application.initialize()
        await application.start()
        await application.run_polling()

    except ConfigurationError as e:
        logger.error(f"配置错误: {e}")
        print("\n")
        print_example_config()
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n收到停止信号，正在关闭...")
        sys.exit(0)

    except Exception as e:
        logger.error(f"启动失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
