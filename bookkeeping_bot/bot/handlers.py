"""Telegram Bot 消息处理器"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from bookkeeping_bot.core.agent import BookkeepingAgent
from bookkeeping_bot.bot.formatter import ResponseFormatter
from bookkeeping_bot.utils.exceptions import BookkeepingError

logger = logging.getLogger(__name__)


class TelegramBotHandler:
    """
    Telegram Bot 消息处理器

    处理来自 Telegram 的用户消息，调用 Agent 处理后返回回复。
    """

    def __init__(self, agent: BookkeepingAgent, formatter: ResponseFormatter = None):
        """
        初始化处理器

        Args:
            agent: 记账 Agent 实例
            formatter: 响应格式化器（可选）
        """
        self.agent = agent
        self.formatter = formatter or ResponseFormatter()

        # 简单的对话历史存储（生产环境应使用数据库）
        self._conversation_history: dict[int, list[dict]] = {}

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        处理用户消息

        Args:
            update: Telegram 更新对象
            context: Bot 上下文
        """
        # 确保有消息内容
        if not update.message or not update.message.text:
            return

        user_id = update.effective_user.id
        user_message = update.message.text

        logger.info(f"用户 {user_id} 发送消息: {user_message}")

        try:
            # 获取用户的对话历史
            history = self._conversation_history.get(user_id, [])

            # 调用 Agent 处理消息
            response = await self.agent.process_message(user_message, history)

            # 更新对话历史（保留最近 10 条）
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": response})
            self._conversation_history[user_id] = history[-10:]

            # 发送回复
            await update.message.reply_text(response)

        except BookkeepingError as e:
            # 业务错误，使用格式化器处理
            error_message = self.formatter.format_error(e)
            await update.message.reply_text(error_message)
            logger.warning(f"用户 {user_id} 遇到业务错误: {e}")

        except Exception as e:
            # 未知错误
            logger.error(f"处理用户 {user_id} 消息时出错: {e}", exc_info=True)
            await update.message.reply_text("抱歉，处理您的请求时出现了错误，请稍后再试。")

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        处理 /start 命令

        Args:
            update: Telegram 更新对象
            context: Bot 上下文
        """
        welcome_message = (
            "👋 欢迎使用 AI 记账助手！\n\n"
            "我可以帮助您：\n"
            "• 📝 记录支出：\"花了30块吃午饭\"\n"
            "• 📊 查询账单：\"今天花了多少钱\"\n"
            "• ✏️ 修改记录：\"把午餐改成40块\"\n"
            "• 🗑️ 删除记录：\"删除刚才的记录\"\n\n"
            "直接发送消息即可开始记账！"
        )

        await update.message.reply_text(welcome_message)

    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        处理 /help 命令

        Args:
            update: Telegram 更新对象
            context: Bot 上下文
        """
        help_message = (
            "📖 使用帮助\n\n"
            "支持的命令：\n"
            "/start - 开始使用\n"
            "/help - 查看帮助\n"
            "/clear - 清除对话历史\n\n"
            "记账示例：\n"
            "• \"花了30块吃午饭\" → 记录餐饮支出\n"
            "• \"打车去公司50元\" → 记录交通支出\n"
            "• \"今天花了多少钱\" → 查询今日支出\n"
            "• \"本周的餐饮支出\" → 按分类查询\n"
            "• \"修改午餐为40块\" → 更新记录\n"
            "• \"删除刚才的记录\" → 删除记录"
        )

        await update.message.reply_text(help_message)

    async def handle_clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        处理 /clear 命令，清除对话历史

        Args:
            update: Telegram 更新对象
            context: Bot 上下文
        """
        user_id = update.effective_user.id
        self._conversation_history.pop(user_id, None)
        await update.message.reply_text("🔄 已清除对话历史")

    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        统一错误处理

        Args:
            update: Telegram 更新对象
            context: Bot 上下文
        """
        logger.error(f"Bot error: {context.error}", exc_info=context.error)

        # 尝试向用户发送错误提示
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "抱歉，处理请求时出现了错误。"
                )
            except Exception:
                pass
