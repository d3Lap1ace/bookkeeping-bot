"""响应格式化器，将操作结果转化为友好的自然语言回复"""
from datetime import datetime

from bookkeeping_bot.storage.models import Expense, StorageResult


class ResponseFormatter:
    """响应格式化器类"""

    @staticmethod
    def format_save_result(result: StorageResult, expense: Expense) -> str:
        """
        格式化保存结果

        Args:
            result: 存储操作结果
            expense: 保存的账单对象

        Returns:
            格式化的友好回复
        """
        if result.success:
            notion_url = result.data.get("notion_url", "") if result.data else ""
            url_part = f" [查看详情]({notion_url})" if notion_url else ""

            return (
                f"✅ 已记录支出\n"
                f"💰 金额：{expense.amount} 元\n"
                f"📂 分类：{expense.category}\n"
                f"📝 描述：{expense.description or '无'}\n"
                f"📅 日期：{expense.date.strftime('%Y-%m-%d')}{url_part}"
            )
        else:
            return f"❌ 保存失败：{result.message}"

    @staticmethod
    def format_query_result(expenses: tuple[Expense, ...]) -> str:
        """
        格式化查询结果

        Args:
            expenses: 查询到的账单元组

        Returns:
            格式化的列表展示
        """
        if not expenses:
            return "📭 没有找到符合条件的支出记录。"

        lines = ["📊 支出记录", "─" * 30, ""]

        # 按日期分组
        grouped = {}
        total = 0

        for expense in expenses:
            date_str = expense.date.strftime("%Y-%m-%d")
            if date_str not in grouped:
                grouped[date_str] = []
            grouped[date_str].append(expense)
            total += expense.amount

        # 按日期展示
        for date_str in sorted(grouped.keys(), reverse=True):
            day_expenses = grouped[date_str]
            day_total = sum(e.amount for e in day_expenses)

            lines.append(f"📅 {date_str}")
            for expense in day_expenses:
                lines.append(
                    f"  • {expense.category} | {expense.description or '-'} | ¥{expense.amount:.2f}"
                )
            lines.append(f"  当日小计：¥{day_total:.2f}")
            lines.append("")

        lines.append("─" * 30)
        lines.append(f"💵 总计：¥{total:.2f}")

        return "\n".join(lines)

    @staticmethod
    def format_update_result(result: StorageResult) -> str:
        """
        格式化更新结果

        Args:
            result: 存储操作结果

        Returns:
            格式化的友好回复
        """
        if result.success:
            notion_url = result.data.get("notion_url", "") if result.data else ""
            url_part = f"\n[查看详情]({notion_url})" if notion_url else ""
            return f"✅ 已更新支出记录{url_part}"
        else:
            return f"❌ 更新失败：{result.message}"

    @staticmethod
    def format_delete_result(result: StorageResult) -> str:
        """
        格式化删除结果

        Args:
            result: 存储操作结果

        Returns:
            格式化的友好回复
        """
        if result.success:
            return "✅ 已删除支出记录"
        else:
            return f"❌ 删除失败：{result.message}"

    @staticmethod
    def format_error(error: Exception) -> str:
        """
        格式化错误信息

        Args:
            error: 异常对象

        Returns:
            用户友好的错误描述
        """
        error_type = type(error).__name__
        error_msg = str(error)

        # 根据错误类型返回不同提示
        if "rate limit" in error_msg.lower():
            return "⏳ API 调用过于频繁，请稍后再试。"

        if "notion" in error_msg.lower():
            return "🔗 Notion 连接出现问题，请检查配置。"

        if "validation" in error_type.lower():
            return "⚠️ 输入信息有误，请检查后重试。"

        return f"❌ 发生错误：{error_msg}"
