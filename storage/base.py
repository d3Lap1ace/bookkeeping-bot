"""存储抽象基类，定义账单存储的标准接口"""
from abc import ABC, abstractmethod
from typing import Tuple

from storage.models import Expense, QueryFilter, StorageResult


class ExpenseStorage(ABC):
    """
    存储抽象基类

    所有存储适配器必须实现此接口，确保存储操作的一致性。
    这使得应用可以轻松切换不同的存储后端（如 Notion、Google Sheets 等）。
    """

    @abstractmethod
    async def save_expense(self, expense: Expense) -> StorageResult:
        """
        保存新账单到存储后端

        Args:
            expense: 要保存的账单对象

        Returns:
            StorageResult: 包含成功状态、消息和附加数据（如 notion_url）

        Raises:
            StorageError: 当保存操作失败时
        """
        pass

    @abstractmethod
    async def query_expenses(self, filters: QueryFilter) -> Tuple[Expense, ...]:
        """
        根据条件查询账单列表

        Args:
            filters: 查询条件过滤器

        Returns:
            符合条件的账单元组

        Raises:
            StorageError: 当查询操作失败时
        """
        pass

    @abstractmethod
    async def update_expense(self, notion_id: str, expense: Expense) -> StorageResult:
        """
        更新已有的账单

        Args:
            notion_id: Notion 行 ID，用于定位要更新的账单
            expense: 更新后的账单数据

        Returns:
            StorageResult: 包含成功状态和消息

        Raises:
            StorageError: 当更新操作失败时
        """
        pass

    @abstractmethod
    async def delete_expense(self, notion_id: str) -> StorageResult:
        """
        删除指定的账单

        Args:
            notion_id: Notion 行 ID，用于定位要删除的账单

        Returns:
            StorageResult: 包含成功状态和消息

        Raises:
            StorageError: 当删除操作失败时
        """
        pass
