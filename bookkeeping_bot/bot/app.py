"""Telegram Bot 应用创建"""
from telegram.ext import Application

from bookkeeping_bot.bot.handlers import TelegramBotHandler
from bookkeeping_bot.core.agent import BookkeepingAgent


def create_app(bot_token: str, agent: BookkeepingAgent) -> Application:
    """
    创建 Telegram Bot 应用

    Args:
        bot_token: Telegram Bot Token
        agent: BookkeepingAgent 实例

    Returns:
        Application: Telegram Bot 应用实例
    """
    application = Application.builder().token(bot_token).build()

    # 创建消息处理器
    bot_handler = TelegramBotHandler(agent=agent)

    # 注册命令处理器
    application.add_handler("start", bot_handler.handle_start)
    application.add_handler("help", bot_handler.handle_help)
    application.add_handler("clear", bot_handler.handle_clear)

    # 注册消息处理器
    from telegram.ext import MessageHandler, filters
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.handle_message)
    )

    # 注册错误处理器
    application.add_error_handler(bot_handler.handle_error)

    return application
