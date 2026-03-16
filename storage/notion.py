"""Notion 存储适配器实现"""
from datetime import datetime
from typing import Tuple

from notion_client import Client as NotionClient
from notion_client.errors import APIResponseError

from storage.base import ExpenseStorage
from storage.models import Expense, QueryFilter, StorageResult
from utils.exceptions import RateLimitError, StorageError
from utils.retry import retry_with_backoff


class NotionStorage(ExpenseStorage):
    """
    Notion 存储适配器

    通过 Notion API 操作用户配置的数据库，实现账单的增删改查功能。
    需要配置 NOTION_TOKEN 和 NOTION_DATABASE_ID 环境变量。

    Notion 数据库预期结构:
        - Amount (Number): 金额
        - Category (Select): 分类
        - Description (Title): 描述
        - Date (Date): 日期
    """

    def __init__(self, token: str, database_id: str, max_retries: int = 3):
        """
        初始化 Notion 存储适配器

        Args:
            token: Notion API Token
            database_id: Notion Database ID
            max_retries: 最大重试次数
        """
        self.client = NotionClient(auth=token)
        self.database_id = database_id
        self.max_retries = max_retries

    @retry_with_backoff(retryable_exceptions=(RateLimitError,))
    async def save_expense(self, expense: Expense) -> StorageResult:
        """
        保存新账单到 Notion

        Args:
            expense: 要保存的账单对象

        Returns:
            StorageResult: 包含成功状态和 Notion 行 URL
        """
        try:
            # 构建 Notion API 所需的数据格式
            page_data = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Amount": {"number": expense.amount},
                    "Category": {"select": {"name": expense.category}},
                    "Description": {
                        "title": [
                            {"text": {"content": expense.description or ""}}
                        ]
                    },
                    "Date": {
                        "date": {"start": expense.date.isoformat()}
                    },
                },
            }

            # 调用 Notion API 创建页面
            response = self.client.pages.create(**page_data)

            # 提取页面 URL
            notion_url = response.get("url", "")
            notion_id = response.get("id", "")

            return StorageResult(
                success=True,
                message=f"已保存到 Notion",
                data={"notion_url": notion_url, "notion_id": notion_id},
            )

        except APIResponseError as e:
            # 处理 Notion API 错误
            if e.status == 429:
                raise RateLimitError("Notion API rate limit exceeded")

            raise StorageError(f"Notion API error: {e.message}")

        except Exception as e:
            raise StorageError(f"Failed to save expense: {str(e)}")

    @retry_with_backoff(retryable_exceptions=(RateLimitError,))
    async def query_expenses(self, filters: QueryFilter) -> Tuple[Expense, ...]:
        """
        从 Notion 查询账单列表

        Args:
            filters: 查询条件

        Returns:
            符合条件的账单元组
        """
        try:
            # 构建 Notion 查询参数
            query_params: dict = {}

            # 添加过滤条件
            conditions = []

            if filters.start_date:
                conditions.append({
                    "property": "Date",
                    "date": {"on_or_after": filters.start_date.isoformat()}
                })

            if filters.end_date:
                conditions.append({
                    "property": "Date",
                    "date": {"on_or_before": filters.end_date.isoformat()}
                })

            if filters.category:
                conditions.append({
                    "property": "Category",
                    "select": {"equals": filters.category}
                })

            if len(conditions) == 1:
                query_params["filter"] = conditions[0]
            elif len(conditions) > 1:
                query_params["filter"] = {
                    "and": conditions
                }

            # 添加结果数量限制
            query_params["page_size"] = min(filters.limit, 100)

            # 执行查询
            response = self.client.databases.query(
                database_id=self.database_id,
                **query_params
            )

            # 解析结果为 Expense 对象
            expenses = []
            for page in response.get("results", []):
                try:
                    expense = self._parse_notion_page(page)
                    expenses.append(expense)
                except Exception:
                    # 跳过解析失败的行，继续处理其他数据
                    continue

            return tuple(expenses)

        except APIResponseError as e:
            if e.status == 429:
                raise RateLimitError("Notion API rate limit exceeded")
            raise StorageError(f"Notion API error: {e.message}")

        except Exception as e:
            raise StorageError(f"Failed to query expenses: {str(e)}")

    @retry_with_backoff(retryable_exceptions=(RateLimitError,))
    async def update_expense(self, notion_id: str, expense: Expense) -> StorageResult:
        """
        更新 Notion 中的已有账单

        Args:
            notion_id: Notion 行 ID
            expense: 更新后的账单数据

        Returns:
            StorageResult: 包含成功状态和消息
        """
        try:
            page_data = {
                "properties": {
                    "Amount": {"number": expense.amount},
                    "Category": {"select": {"name": expense.category}},
                    "Description": {
                        "title": [
                            {"text": {"content": expense.description or ""}}
                        ]
                    },
                    "Date": {"date": {"start": expense.date.isoformat()}},
                },
            }

            response = self.client.pages.update(page_id=notion_id, **page_data)

            notion_url = response.get("url", "")

            return StorageResult(
                success=True,
                message="已更新账单",
                data={"notion_url": notion_url},
            )

        except APIResponseError as e:
            if e.status == 429:
                raise RateLimitError("Notion API rate limit exceeded")
            raise StorageError(f"Notion API error: {e.message}")

        except Exception as e:
            raise StorageError(f"Failed to update expense: {str(e)}")

    @retry_with_backoff(retryable_exceptions=(RateLimitError,))
    async def delete_expense(self, notion_id: str) -> StorageResult:
        """
        从 Notion 删除账单

        Args:
            notion_id: Notion 行 ID

        Returns:
            StorageResult: 包含成功状态和消息
        """
        try:
            # Notion API 的删除是设置页面为 archived 状态
            self.client.pages.update(page_id=notion_id, archived=True)

            return StorageResult(
                success=True,
                message="已删除账单",
            )

        except APIResponseError as e:
            if e.status == 429:
                raise RateLimitError("Notion API rate limit exceeded")
            raise StorageError(f"Notion API error: {e.message}")

        except Exception as e:
            raise StorageError(f"Failed to delete expense: {str(e)}")

    def _parse_notion_page(self, page: dict) -> Expense:
        """
        将 Notion 页面数据解析为 Expense 对象

        Args:
            page: Notion API 返回的页面数据

        Returns:
            Expense: 解析后的账单对象

        Raises:
            ValueError: 当页面数据格式不符合预期时
        """
        props = page.get("properties", {})

        # 解析 Amount
        amount = props.get("Amount", {}).get("number", 0)

        # 解析 Category
        category = props.get("Category", {}).get("select", {}).get("name", "未分类")

        # 解析 Description
        title_array = props.get("Description", {}).get("title", [])
        description = title_array[0].get("text", {}).get("content", "") if title_array else ""

        # 解析 Date
        date_obj = props.get("Date", {}).get("date", {})
        date_str = date_obj.get("start") if date_obj else None
        if date_str:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            date = datetime.now()

        # 获取页面 ID
        notion_id = page.get("id", "")

        return Expense(
            amount=amount,
            category=category,
            description=description,
            date=date,
            notion_id=notion_id,
        )
