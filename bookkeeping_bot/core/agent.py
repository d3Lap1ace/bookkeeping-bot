"""记账 Agent 主逻辑"""
import json
from datetime import datetime, timedelta
from typing import Optional

from bookkeeping_bot.core.llm_client import LLMClient
from bookkeeping_bot.core.skill_loader import SkillLoader
from bookkeeping_bot.storage.base import ExpenseStorage
from bookkeeping_bot.storage.models import Expense, QueryFilter
from bookkeeping_bot.utils.exceptions import LLMError


class BookkeepingAgent:
    """
    记账 Agent

    协调 LLM 和 Skill 执行，实现自然语言记账功能。
    工作流程：
        1. 接收用户消息
        2. 调用 LLM 解析意图和参数
        3. 执行对应的 Skill（存储操作）
        4. 将执行结果回传给 LLM 生成自然语言回复
    """

    def __init__(self, llm_client: LLMClient, storage: ExpenseStorage, skill_loader: SkillLoader):
        """
        初始化 Agent

        Args:
            llm_client: LLM 客户端
            storage: 存储适配器
            skill_loader: Skill 加载器
        """
        self.llm = llm_client
        self.storage = storage
        self.skill_loader = skill_loader

        # 加载所有 Skills
        self.skills = skill_loader.load_all()
        self.system_prompt = skill_loader.get_system_prompt()

    async def process_message(self, user_message: str, conversation_history: Optional[list[dict]] = None) -> str:
        """
        处理用户消息的主流程

        Args:
            user_message: 用户输入的消息
            conversation_history: 对话历史（可选）

        Returns:
            Agent 的自然语言回复
        """
        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        # 添加对话历史
        if conversation_history:
            messages.extend(conversation_history)

        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})

        # 调用 LLM
        try:
            response = await self.llm.chat_with_tools(
                messages=messages,
                tools=list(self.skills.values()),
            )
        except LLMError as e:
            return f"抱歉，处理请求时出错：{e}"

        # 处理 LLM 响应
        if response["tool_calls"]:
            # LLM 返回了 tool_calls，执行对应的 Skills
            return await self._execute_tool_calls(messages, response["tool_calls"])
        else:
            # LLM 直接返回了内容
            return response.get("content", "抱歉，我没有理解您的意思。")

    async def _execute_tool_calls(self, messages: list[dict], tool_calls: list[dict]) -> str:
        """
        执行 LLM 返回的 tool_calls

        Args:
            messages: 对话消息列表
            tool_calls: LLM 返回的工具调用列表

        Returns:
            最终的自然语言回复
        """
        # 执行所有 tool_calls
        tool_responses = []

        for tool_call in tool_calls:
            skill_name = tool_call["name"]
            arguments_str = tool_call["arguments"]

            try:
                arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
            except json.JSONDecodeError:
                arguments = {}

            # 执行 Skill
            result = await self._execute_skill(skill_name, arguments)

            tool_responses.append({
                "tool_call_id": tool_call["id"],
                "role": "tool",
                "name": skill_name,
                "content": result,
            })

        fallback_response = self._format_tool_responses(tool_responses)

        # Gemini 的 OpenAI 兼容接口在二次提交 tool 结果时更容易触发 INVALID_ARGUMENT。
        # MVP 场景下直接返回工具执行结果，比额外润色一轮更稳。
        if getattr(self.llm, "is_gemini_compatible", False):
            return fallback_response

        # 将 tool_calls 和响应添加到消息列表
        messages.append({
            "role": "assistant",
            "content": "",
            "tool_calls": tool_calls,
        })
        messages.extend(tool_responses)

        # 再次调用 LLM 生成最终回复
        try:
            final_response = await self.llm.chat_with_tools(
                messages=messages,
                tools=list(self.skills.values()),
            )
        except LLMError:
            return fallback_response

        return final_response.get("content", "操作已完成。")

    @staticmethod
    def _format_tool_responses(tool_responses: list[dict]) -> str:
        """将一个或多个工具结果拼成最终回复。"""
        contents = [response["content"] for response in tool_responses if response.get("content")]
        return "\n".join(contents) if contents else "操作已完成。"

    async def _execute_skill(self, skill_name: str, arguments: dict) -> str:
        """
        执行单个 Skill

        Args:
            skill_name: Skill 名称
            arguments: Skill 参数

        Returns:
            执行结果的字符串描述
        """
        try:
            if skill_name == "record_expense":
                return await self._record_expense(arguments)

            elif skill_name == "query_expenses":
                return await self._query_expenses(arguments)

            elif skill_name == "update_expense":
                return await self._update_expense(arguments)

            elif skill_name == "delete_expense":
                return await self._delete_expense(arguments)

            else:
                return f"未知的 Skill: {skill_name}"

        except Exception as e:
            return f"执行 {skill_name} 时出错：{e}"

    async def _record_expense(self, arguments: dict) -> str:
        """执行记账 Skill"""
        # 解析参数
        amount = float(arguments.get("amount", 0))
        category = arguments.get("category", "其他")
        description = arguments.get("description", "")
        date_str = arguments.get("date", "")

        # 处理日期
        if date_str:
            try:
                date = datetime.fromisoformat(date_str)
            except ValueError:
                # 尝试处理相对日期（如"今天"、"昨天"）
                date = self._parse_relative_date(date_str) or datetime.now()
        else:
            date = datetime.now()

        # 创建 Expense 对象
        expense = Expense(
            amount=amount,
            category=category,
            description=description,
            date=date,
        )

        # 保存到存储
        result = await self.storage.save_expense(expense)

        if result.success:
            notion_url = result.data.get("notion_url", "") if result.data else ""
            url_part = f" [查看详情]({notion_url})" if notion_url else ""
            return f"✅ 已记录：{category} {amount}元 {url_part}"
        else:
            return f"❌ 保存失败：{result.message}"

    async def _query_expenses(self, arguments: dict) -> str:
        """执行查询 Skill"""
        # 解析参数
        start_date_str = arguments.get("start_date", "")
        end_date_str = arguments.get("end_date", "")
        category = arguments.get("category", "")

        # 处理日期
        start_date = self._parse_relative_date(start_date_str) if start_date_str else None
        end_date = self._parse_relative_date(end_date_str) if end_date_str else None

        # 构建查询过滤器
        filters = QueryFilter(
            start_date=start_date,
            end_date=end_date,
            category=category,
            limit=50,
        )

        # 执行查询
        expenses = await self.storage.query_expenses(filters)

        if not expenses:
            return "没有找到符合条件的支出记录。"

        # 构建结果
        lines = ["📊 支出记录：", ""]
        total = 0

        for expense in expenses:
            date_str = expense.date.strftime("%Y-%m-%d")
            lines.append(f"• {date_str} | {expense.category} | {expense.description} | {expense.amount}元")
            total += expense.amount

        lines.append("")
        lines.append(f"总计：{total}元")

        return "\n".join(lines)

    async def _update_expense(self, arguments: dict) -> str:
        """执行更新 Skill"""
        locator = arguments.get("locator", "")

        if not locator:
            return "❌ 需要提供要更新的记录 ID"

        # 先查询原始记录，避免覆盖数据
        original = await self._get_expense_by_notion_id(locator)
        if not original:
            return "❌ 未找到要更新的记录"

        # 解析更新参数（只更新提供的字段，保留原有值）
        if "amount" in arguments:
            amount = float(arguments.get("amount", 0))
        else:
            amount = original.amount

        if "category" in arguments:
            category = arguments.get("category")
        else:
            category = original.category

        if "description" in arguments:
            description = arguments.get("description")
        else:
            description = original.description

        date_str = arguments.get("date")
        if date_str:
            date = self._parse_relative_date(date_str) or original.date
        else:
            date = original.date

        # 创建更新后的 Expense
        expense = Expense(
            amount=amount,
            category=category,
            description=description,
            date=date,
            notion_id=locator,
        )

        # 执行更新
        result = await self.storage.update_expense(locator, expense)

        if result.success:
            return "✅ 已更新支出记录"
        else:
            return f"❌ 更新失败：{result.message}"

    async def _delete_expense(self, arguments: dict) -> str:
        """执行删除 Skill"""
        notion_id = arguments.get("notion_id", "")

        if not notion_id:
            return "❌ 需要提供要删除的记录 ID"

        # 执行删除
        result = await self.storage.delete_expense(notion_id)

        if result.success:
            return "✅ 已删除支出记录"
        else:
            return f"❌ 删除失败：{result.message}"

    def _parse_relative_date(self, date_str: str) -> Optional[datetime]:
        """
        解析相对日期

        Args:
            date_str: 日期字符串，可能是 "今天"、"昨天" 或 ISO 格式

        Returns:
            datetime 对象或 None
        """
        now = datetime.now()

        if date_str in ["今天", "today"]:
            return now

        elif date_str in ["昨天", "yesterday"]:
            return now - timedelta(days=1)

        else:
            try:
                return datetime.fromisoformat(date_str)
            except ValueError:
                return None

    async def _get_expense_by_notion_id(self, notion_id: str) -> Optional[Expense]:
        """
        通过 Notion ID 查询单条支出记录

        Args:
            notion_id: Notion 行 ID

        Returns:
            Expense 对象或 None
        """
        # 查询所有记录（简化实现，生产环境应优化）
        filters = QueryFilter(limit=100)
        expenses = await self.storage.query_expenses(filters)

        # 查找匹配的记录
        for expense in expenses:
            if expense.notion_id == notion_id:
                return expense

        return None
