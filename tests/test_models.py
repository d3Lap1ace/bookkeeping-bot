"""测试数据模型"""
from datetime import datetime

import pytest

from bookkeeping_bot.storage.models import Expense, QueryFilter, StorageResult


class TestExpense:
    """测试 Expense 模型"""

    def test_create_expense(self):
        """测试创建账单"""
        expense = Expense(
            amount=100.0,
            category="餐饮",
            description="午餐",
            date=datetime.now(),
        )
        assert expense.amount == 100.0
        assert expense.category == "餐饮"
        assert expense.description == "午餐"
        assert expense.notion_id is None

    def test_expense_validation_negative_amount(self):
        """测试负金额验证"""
        with pytest.raises(ValueError, match="Amount must be positive"):
            Expense(
                amount=-10.0,
                category="餐饮",
                description="午餐",
                date=datetime.now(),
            )

    def test_expense_validation_empty_category(self):
        """测试空分类验证"""
        with pytest.raises(ValueError, match="Category cannot be empty"):
            Expense(
                amount=100.0,
                category="",
                description="午餐",
                date=datetime.now(),
            )

    def test_expense_with_notion_id(self):
        """测试带 notion_id 的账单"""
        expense = Expense(
            amount=50.0,
            category="交通",
            description="地铁",
            date=datetime.now(),
            notion_id="abc123",
        )
        assert expense.notion_id == "abc123"


class TestQueryFilter:
    """测试 QueryFilter 模型"""

    def test_default_filter(self):
        """测试默认查询条件"""
        filters = QueryFilter()
        assert filters.start_date is None
        assert filters.end_date is None
        assert filters.category is None
        assert filters.limit == 50

    def test_filter_with_category(self):
        """测试带分类的查询条件"""
        filters = QueryFilter(category="餐饮")
        assert filters.category == "餐饮"

    def test_filter_with_custom_limit(self):
        """测试自定义数量限制"""
        filters = QueryFilter(limit=100)
        assert filters.limit == 100


class TestStorageResult:
    """测试 StorageResult 模型"""

    def test_success_result(self):
        """测试成功结果"""
        result = StorageResult(
            success=True,
            message="保存成功",
            data={"notion_url": "https://notion.so/abc123"},
        )
        assert result.success is True
        assert result.message == "保存成功"
        assert result.data["notion_url"] == "https://notion.so/abc123"

    def test_failure_result(self):
        """测试失败结果"""
        result = StorageResult(
            success=False,
            message="保存失败",
        )
        assert result.success is False
        assert result.data is None
