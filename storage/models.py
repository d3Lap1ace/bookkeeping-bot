"""存储层数据模型定义"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Expense:
    """
    账单实体

    Attributes:
        amount: 金额（正数）
        category: 分类（如"餐饮"、"交通"）
        description: 描述（如"午餐"、"地铁"）
        date: 日期时间
        notion_id: Notion 行 ID（用于更新/删除操作）
    """

    amount: float
    category: str
    description: str
    date: datetime
    notion_id: Optional[str] = None

    def __post_init__(self):
        """验证数据"""
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        if not self.category:
            raise ValueError("Category cannot be empty")


@dataclass
class QueryFilter:
    """
    查询条件

    Attributes:
        start_date: 起始日期（可选）
        end_date: 结束日期（可选）
        category: 分类筛选（可选）
        limit: 返回结果数量限制
    """

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[str] = None
    limit: int = 50


@dataclass
class StorageResult:
    """
    存储操作结果

    Attributes:
        success: 操作是否成功
        message: 结果消息
        data: 附加数据（如 notion_url、row_id 等）
    """

    success: bool
    message: str
    data: Optional[dict] = None
