# AI 记账 Agent 实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：** 从零构建一个支持自然语言记账的 AI Agent，通过 Telegram Bot 交互，数据存储到 Notion

**架构：** 经典三层架构（Bot 交互层 → Agent 核心层 → 存储抽象层），支持 OpenAI 兼容的 LLM 接口，采用智能重试策略

**技术栈：** Python 3.9, python-telegram-bot, OpenAI API (兼容), Notion API, python-dotenv

**开发者：** d3Lap1ace

---

## 文件结构

创建以下文件结构：

```
bookkeeping-skills/
├── bot/
│   ├── __init__.py
│   ├── handlers.py          # Telegram 消息处理器
│   └── formatter.py         # 响应格式化器
├── core/
│   ├── __init__.py
│   ├── agent.py             # Agent 主逻辑
│   ├── skill_loader.py      # Skill 加载器（从 md 文件）
│   └── llm_client.py        # OpenAI 兼容 LLM 客户端
├── storage/
│   ├── __init__.py
│   ├── base.py              # ExpenseStorage 抽象基类
│   ├── models.py            # 数据模型（Expense, QueryFilter, StorageResult）
│   └── notion.py            # Notion 适配器实现
├── utils/
│   ├── __init__.py
│   ├── retry.py             # 智能重试装饰器
│   ├── exceptions.py        # 自定义异常
│   └── logger.py            # 日志配置
├── skills/
│   ├── record_expense.md
│   ├── query_expenses.md
│   ├── update_expense.md
│   └── delete_expense.md
├── config.py                # 配置管理
├── main.py                  # 应用入口
├── requirements.txt         # 依赖列表
├── .env.example             # 环境变量模板
├── .gitignore
└── README.md                # 项目文档
```

---

## Chunk 1: 基础设施与配置

### Task 1: 创建项目基础文件

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`

- [ ] **Step 1: 创建 requirements.txt**

```txt
# Telegram Bot
python-telegram-bot==20.7

# LLM
openai>=1.0.0

# Notion
notion-client>=2.2.1

# 工具库
python-dotenv==1.0.0
pydantic>=2.0.0

# 测试
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-cov==4.1.0
```

- [ ] **Step 2: 创建 .env.example**

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# LLM 配置（支持 OpenAI 兼容接口）
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# Notion 配置
NOTION_TOKEN=your_notion_token_here
NOTION_DATABASE_ID=your_database_id_here

# 重试配置（可选）
MAX_RETRIES=3
RETRY_BASE_DELAY=1.0

# 日志级别（可选）
LOG_LEVEL=INFO
```

- [ ] **Step 3: 创建 .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# 虚拟环境
.venv/
venv/

# 环境变量
.env

# IDE
.idea/
.vscode/
*.swp
*.swo

# 日志
*.log

# 测试覆盖率
.coverage
htmlcov/
.pytest_cache/

# MacOS
.DS_Store
```

- [ ] **Step 4: 提交基础文件**

```bash
git add requirements.txt .env.example .gitignore
git commit -m "chore: add project infrastructure files"
```

---

### Task 2: 创建配置管理模块

**Files:**
- Create: `config.py`

- [ ] **Step 1: 创建 config.py - 配置数据类**

```python
"""配置管理模块，从环境变量加载应用配置"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """应用配置类，从环境变量加载所有配置项"""

    # Telegram Bot 配置
    telegram_bot_token: str

    # LLM 配置
    llm_api_key: str
    llm_base_url: str
    llm_model: str

    # Notion 配置
    notion_token: str
    notion_database_id: str

    # 重试配置
    max_retries: int
    retry_base_delay: float

    # 日志配置
    log_level: str

    @classmethod
    def from_env(cls) -> "Config":
        """
        从环境变量加载配置

        Returns:
            Config: 加载完成的配置对象

        Raises:
            ValueError: 当必需的环境变量未设置时
        """
        # 必需配置项
        telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")

        llm_api_key = os.getenv("LLM_API_KEY")
        if not llm_api_key:
            raise ValueError("LLM_API_KEY is required")

        notion_token = os.getenv("NOTION_TOKEN")
        if not notion_token:
            raise ValueError("NOTION_TOKEN is required")

        notion_database_id = os.getenv("NOTION_DATABASE_ID")
        if not notion_database_id:
            raise ValueError("NOTION_DATABASE_ID is required")

        # 可选配置项（带默认值）
        llm_base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        max_retries = int(os.getenv("MAX_RETRIES", "3"))
        retry_base_delay = float(os.getenv("RETRY_BASE_DELAY", "1.0"))
        log_level = os.getenv("LOG_LEVEL", "INFO")

        return cls(
            telegram_bot_token=telegram_bot_token,
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
            llm_model=llm_model,
            notion_token=notion_token,
            notion_database_id=notion_database_id,
            max_retries=max_retries,
            retry_base_delay=retry_base_delay,
            log_level=log_level,
        )
```

- [ ] **Step 2: 提交配置模块**

```bash
git add config.py
git commit -m "feat: add configuration management module"
```

---

### Task 3: 创建工具层 - 异常定义

**Files:**
- Create: `utils/__init__.py`
- Create: `utils/exceptions.py`

- [ ] **Step 1: 创建 utils/__init__.py**

```python
"""工具包模块"""
```

- [ ] **Step 2: 创建 utils/exceptions.py - 自定义异常类**

```python
"""自定义异常类定义"""


class BookkeepingError(Exception):
    """基础异常类，所有自定义异常的父类"""

    pass


class ConfigurationError(BookkeepingError):
    """配置错误（如缺失环境变量、配置格式错误等）"""

    pass


class StorageError(BookkeepingError):
    """存储层操作错误（如 API 调用失败、数据格式错误等）"""

    pass


class LLMError(BookkeepingError):
    """LLM 调用错误（如 API 调用失败、响应格式错误等）"""

    pass


class RateLimitError(BookkeepingError):
    """API 限流错误（触发速率限制时抛出）"""

    pass


class ValidationError(BookkeepingError):
    """数据验证错误（如参数不符合要求时抛出）"""

    pass
```

- [ ] **Step 3: 提交异常定义**

```bash
git add utils/exceptions.py utils/__init__.py
git commit -m "feat: add custom exception classes"
```

---

### Task 4: 创建工具层 - 智能重试装饰器

**Files:**
- Create: `utils/retry.py`

- [ ] **Step 1: 创建 utils/retry.py - 智能重试装饰器**

```python
"""智能重试装饰器，使用指数退避策略"""
import asyncio
import functools
import logging
from typing import Callable, ParamSpec, TypeVar, tuple

from utils.exceptions import RateLimitError

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: tuple = (ConnectionError, TimeoutError, RateLimitError),
):
    """
    智能重试装饰器，使用指数退避策略

    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟时间（秒）
        max_delay: 最大延迟时间（秒）
        retryable_exceptions: 可重试的异常类型元组

    Returns:
        装饰器函数

    重试逻辑：
        - 首次失败后等待 base_delay 秒
        - 每次重试延迟翻倍（2^n * base_delay），不超过 max_delay
        - 仅对 retryable_exceptions 重试
        - 其他异常直接抛出
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        # 最后一次尝试失败，不再重试
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise

                    # 计算延迟时间（指数退避）
                    delay = min(base_delay * (2**attempt), max_delay)
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}), "
                        f"retrying in {delay:.1f}s: {e}"
                    )
                    await asyncio.sleep(delay)

            # 理论上不会到达这里，但为了类型检查
            raise last_exception  # type: ignore

        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise

                    delay = min(base_delay * (2**attempt), max_delay)
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}), "
                        f"retrying in {delay:.1f}s: {e}"
                    )
                    import time

                    time.sleep(delay)

            raise last_exception  # type: ignore

        # 根据函数类型返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore

    return decorator
```

- [ ] **Step 2: 提交重试装饰器**

```bash
git add utils/retry.py
git commit -m "feat: add intelligent retry decorator with exponential backoff"
```

---

### Task 5: 创建工具层 - 日志配置

**Files:**
- Create: `utils/logger.py`

- [ ] **Step 1: 创建 utils/logger.py - 日志配置**

```python
"""日志配置模块"""
import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "bookkeeping",
    level: str = "INFO",
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    配置结构化日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 可选的日志文件路径，如果提供则同时输出到文件

    Returns:
        配置好的 Logger 实例

    日志格式:
        [时间] [级别] [模块名] 消息内容
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 创建格式化器
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（可选）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
```

- [ ] **Step 2: 提交日志配置**

```bash
git add utils/logger.py
git commit -m "feat: add logging configuration module"
```

---

## Chunk 2: 存储层实现

### Task 6: 创建存储层数据模型

**Files:**
- Create: `storage/__init__.py`
- Create: `storage/models.py`

- [ ] **Step 1: 创建 storage/__init__.py**

```python
"""存储层模块"""
```

- [ ] **Step 2: 创建 storage/models.py - 数据模型**

```python
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
```

- [ ] **Step 3: 提交数据模型**

```bash
git add storage/models.py storage/__init__.py
git commit -m "feat: add storage data models (Expense, QueryFilter, StorageResult)"
```

---

### Task 7: 创建存储抽象基类

**Files:**
- Create: `storage/base.py`

- [ ] **Step 1: 创建 storage/base.py - 抽象基类**

```python
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
```

- [ ] **Step 2: 提交抽象基类**

```bash
git add storage/base.py
git commit -m "feat: add ExpenseStorage abstract base class"
```

---

### Task 8: 实现 Notion 适配器

**Files:**
- Create: `storage/notion.py`

- [ ] **Step 1: 创建 storage/notion.py - Notion 适配器**

```python
"""Notion 存储适配器实现"""
from datetime import datetime
from typing import Optional, Tuple

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
                except Exception as e:
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
```

- [ ] **Step 2: 提交 Notion 适配器**

```bash
git add storage/notion.py
git commit -m "feat: add Notion storage adapter implementation"
```

---

## Chunk 3: Agent 核心层实现

### Task 9: 创建 LLM 客户端

**Files:**
- Create: `core/__init__.py`
- Create: `core/llm_client.py`

- [ ] **Step 1: 创建 core/__init__.py**

```python
"""Agent 核心层模块"""
```

- [ ] **Step 2: 创建 core/llm_client.py - LLM 客户端**

```python
"""OpenAI 兼容的 LLM 客户端"""
from openai import AsyncOpenAI

from utils.exceptions import LLMError, RateLimitError
from utils.retry import retry_with_backoff


class LLMClient:
    """
    OpenAI 兼容的 LLM 客户端

    支持标准 OpenAI API 以及兼容 OpenAI 格式的本地模型（如 Ollama、LM Studio 等）。
    通过配置 base_url 可以切换不同的 API 端点。
    """

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", model: str = "gpt-4o-mini"):
        """
        初始化 LLM 客户端

        Args:
            api_key: API 密钥
            base_url: API 基础 URL（默认为 OpenAI 官方地址）
            model: 使用的模型名称
        """
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = model

    @retry_with_backoff(retryable_exceptions=(RateLimitError,))
    async def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> dict:
        """
        调用 LLM 进行对话，支持 Function Calling

        Args:
            messages: 对话历史消息列表
            tools: 可用的工具（Function Calling）定义列表

        Returns:
            LLM 响应，可能包含 tool_calls 字段

        Raises:
            LLMError: 当 API 调用失败时
            RateLimitError: 当触发速率限制时
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
            )

            # 解析响应
            message = response.choices[0].message

            result = {
                "content": message.content,
                "tool_calls": [],
            }

            # 解析 tool_calls
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    result["tool_calls"].append({
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    })

            return result

        except Exception as e:
            error_msg = str(e).lower()

            # 判断是否为限流错误
            if "rate_limit" in error_msg or "429" in error_msg:
                raise RateLimitError(f"LLM API rate limit exceeded: {e}")

            raise LLMError(f"LLM API error: {e}")
```

- [ ] **Step 3: 提交 LLM 客户端**

```bash
git add core/llm_client.py core/__init__.py
git commit -m "feat: add OpenAI-compatible LLM client"
```

---

### Task 10: 创建 Skills 定义文件

**Files:**
- Create: `skills/record_expense.md`
- Create: `skills/query_expenses.md`
- Create: `skills/update_expense.md`
- Create: `skills/delete_expense.md`

- [ ] **Step 1: 创建 skills/record_expense.md**

```markdown
---
description: 记录一笔新支出
---

当用户想要记录支出时调用此技能。

**参数说明：**
- `amount` (number, 必需): 支出金额，必须为正数
- `category` (string, 必需): 支出分类，建议使用：餐饮、交通、购物、娱乐、医疗、教育、居住、其他
- `description` (string, 可选): 支出描述，如"午餐"、"地铁"、"超市购物"
- `date` (string, 可选): 支出日期，格式 YYYY-MM-DD，默认为今天

**使用场景：**
- "花了30块吃午饭" → amount=30, category="餐饮", description="午饭"
- "打车去公司花了50" → amount=50, category="交通", description="打车去公司"
- "昨天买了本书80元" → amount=80, category="教育", description="买书", date="昨天"

**注意事项：**
- 金额必须为正数
- 如果用户没有明确说明日期，使用当前日期
- 分类应该尽量准确，不确定时使用"其他"
```

- [ ] **Step 2: 创建 skills/query_expenses.md**

```markdown
---
description: 查询支出记录，支持按日期范围、分类筛选
---

当用户想要查看、查询、统计历史支出时调用此技能。

**参数说明：**
- `start_date` (string, 可选): 起始日期，格式 YYYY-MM-DD
- `end_date` (string, 可选): 结束日期，格式 YYYY-MM-DD
- `category` (string, 可选): 分类筛选，如"餐饮"、"交通"

**使用场景：**
- "今天花了多少钱" → start_date="今天", end_date="今天"
- "本周的餐饮支出" → category="餐饮", start_date="本周一", end_date="今天"
- "上个月所有的账单" → start_date="上月1号", end_date="上月最后一天"

**注意事项：**
- 日期范围应该合理，避免查询过长时间范围
- 如果用户只说"最近"，默认查询最近7天
- 返回结果应该包含总金额统计
```

- [ ] **Step 3: 创建 skills/update_expense.md**

```markdown
---
description: 更新已有的支出记录
---

当用户想要修改、更正已有的支出记录时调用此技能。

**参数说明：**
- `locator` (string, 必需): 定位信息，可以是 notion_id 或账单描述
- `amount` (number, 可选): 新的金额
- `category` (string, 可选): 新的分类
- `description` (string, 可选): 新的描述
- `date` (string, 可选): 新的日期，格式 YYYY-MM-DD

**使用场景：**
- "把那条打车记录改成60块" → locator="打车", amount=60
- "修改午餐的分类为商务宴请" → locator="午餐", category="商务宴请"

**注意事项：**
- 至少需要提供一个要修改的字段（amount/category/description/date）
- 如果 locator 是描述而不是 notion_id，可能需要先查询找到对应的记录
- 修改前应该确认用户的意图
```

- [ ] **Step 4: 创建 skills/delete_expense.md**

```markdown
---
description: 删除一笔支出记录
---

当用户明确要求删除某笔支出记录时调用此技能。

**参数说明：**
- `notion_id` (string, 必需): Notion 行 ID，用于定位要删除的记录

**使用场景：**
- "删除刚才那条记录" → 需要先从上下文中获取 notion_id
- "删除 id 为 xxx 的记录" → notion_id="xxx"

**注意事项：**
- 删除是永久性操作，无法恢复
- 如果用户没有提供明确的 notion_id，应该先查询让用户确认
- 删除前应该向用户确认，避免误删
```

- [ ] **Step 5: 提交 Skills 定义文件**

```bash
git add skills/
git commit -m "feat: add agent skills definition files"
```

---

### Task 11: 创建 Skill 加载器

**Files:**
- Create: `core/skill_loader.py`

- [ ] **Step 1: 创建 core/skill_loader.py - Skill 加载器**

```python
"""从 Markdown 文件加载 Agent Skills 定义"""
import json
import os
from pathlib import Path
from typing import Optional


class SkillLoader:
    """
    Skill 加载器

    从 skills/ 目录下的 Markdown 文件加载 Skills 定义，
    解析 YAML frontmatter 和内容，生成 LLM Function Calling 所需的格式。
    """

    def __init__(self, skills_dir: str = "skills"):
        """
        初始化 Skill 加载器

        Args:
            skills_dir: Skills 文件所在目录
        """
        self.skills_dir = Path(skills_dir)
        self._skills_cache: Optional[dict] = None

    def load_all(self) -> dict[str, dict]:
        """
        扫描 skills 目录，解析所有 .md 文件

        Returns:
            Skills 定义字典，格式适合 LLM Function Calling
            {
                "skill_name": {
                    "type": "function",
                    "function": {
                        "name": "skill_name",
                        "description": "...",
                        "parameters": {...}
                    }
                },
                ...
            }
        """
        if self._skills_cache is not None:
            return self._skills_cache

        skills = {}

        if not self.skills_dir.exists():
            raise FileNotFoundError(f"Skills directory not found: {self.skills_dir}")

        for md_file in self.skills_dir.glob("*.md"):
            skill_name = md_file.stem
            skill_definition = self._parse_skill_file(md_file)

            # 转换为 OpenAI Function Calling 格式
            skills[skill_name] = {
                "type": "function",
                "function": {
                    "name": skill_name,
                    "description": skill_definition["description"],
                    "parameters": self._build_parameters_schema(skill_definition),
                }
            }

        self._skills_cache = skills
        return skills

    def _parse_skill_file(self, file_path: Path) -> dict:
        """
        解析单个 Skill 文件

        Args:
            file_path: Skill 文件路径

        Returns:
            包含 description 和 parameters 的字典
        """
        content = file_path.read_text(encoding="utf-8")

        # 分离 frontmatter 和正文
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1].strip()
                # 简单解析 YAML frontmatter
                frontmatter = {}
                for line in frontmatter_text.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        frontmatter[key.strip()] = value.strip()

                return {
                    "description": frontmatter.get("description", ""),
                    "parameters": self._extract_parameters_from_content(parts[2]),
                }

        # 如果没有 frontmatter，尝试从内容中提取
        return {
            "description": f"Skill: {file_path.stem}",
            "parameters": self._extract_parameters_from_content(content),
        }

    def _extract_parameters_from_content(self, content: str) -> dict:
        """
        从 Markdown 内容中提取参数定义

        Args:
            content: Markdown 正文内容

        Returns:
            参数定义字典
        """
        parameters = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        in_param_section = False
        for line in content.split("\n"):
            line = line.strip()

            if "**参数说明：**" in line or "参数说明:" in line:
                in_param_section = True
                continue

            if in_param_section and line.startswith("- `"):
                # 解析参数行，例如：- `amount` (number, 必需): 支出金额
                try:
                    param_info = self._parse_param_line(line)
                    if param_info:
                        param_name, param_type, param_required, param_desc = param_info
                        parameters["properties"][param_name] = {
                            "type": param_type,
                            "description": param_desc,
                        }
                        if param_required:
                            parameters["required"].append(param_name)
                except Exception:
                    pass

        return parameters

    def _parse_param_line(self, line: str) -> Optional[tuple]:
        """
        解析参数定义行

        Args:
            line: 参数行文本

        Returns:
            (name, type, required, description) 或 None
        """
        import re

        # 匹配 - `name` (type, required): description
        pattern = r"- `(\w+)`\s*\((\w+),\s*(\w+)\):\s*(.+)"
        match = re.match(pattern, line)

        if match:
            name, param_type, required, description = match.groups()
            return (name, param_type, required == "必需", description)

        return None

    def _build_parameters_schema(self, skill_definition: dict) -> dict:
        """
        构建 Parameters JSON Schema

        Args:
            skill_definition: Skill 定义

        Returns:
            Parameters JSON Schema
        """
        return skill_definition.get("parameters", {
            "type": "object",
            "properties": {},
            "required": [],
        })

    def get_skill_prompt(self, skill_name: str) -> str:
        """
        获取 Skill 的详细说明，用于构建 System Prompt

        Args:
            skill_name: Skill 名称

        Returns:
            Skill 的详细说明文本
        """
        skill_file = self.skills_dir / f"{skill_name}.md"

        if not skill_file.exists():
            return f"Skill: {skill_name}"

        content = skill_file.read_text(encoding="utf-8")

        # 移除 frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()

        return content

    def get_system_prompt(self) -> str:
        """
        构建包含所有 Skills 说明的 System Prompt

        Returns:
            System Prompt 文本
        """
        skills = self.load_all()
        prompt_parts = [
            "你是一个智能记账助手，可以帮助用户记录、查询、修改和删除支出。",
            "你可以使用以下工具：",
            "",
        ]

        for skill_name, skill_def in skills.items():
            skill_desc = skill_def["function"]["description"]
            prompt_parts.append(f"- {skill_name}: {skill_desc}")

        prompt_parts.append("")
        prompt_parts.append("请根据用户的需求调用合适的工具，并用自然语言回复用户。")

        return "\n".join(prompt_parts)
```

- [ ] **Step 2: 提交 Skill 加载器**

```bash
git add core/skill_loader.py
git commit -m "feat: add skill loader for parsing markdown skill definitions"
```

---

### Task 12: 创建 Agent 主逻辑

**Files:**
- Create: `core/agent.py`

- [ ] **Step 1: 创建 core/agent.py - Agent 主逻辑**

```python
"""记账 Agent 主逻辑"""
import json
from datetime import datetime
from typing import Optional

from core.llm_client import LLMClient
from core.skill_loader import SkillLoader
from storage.base import ExpenseStorage
from storage.models import Expense, QueryFilter
from utils.exceptions import LLMError


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
        except LLMError as e:
            return f"操作完成，但生成回复时出错：{e}"

        return final_response.get("content", "操作已完成。")

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

        # 这里需要先找到对应的记录
        # 简化实现：假设 locator 就是 notion_id
        # 实际项目中可能需要先查询

        # 解析更新参数
        amount = float(arguments.get("amount", 0)) if "amount" in arguments else None
        category = arguments.get("category")
        description = arguments.get("description")
        date_str = arguments.get("date")

        # 获取原始记录（这里简化处理）
        # 实际应该先查询再更新

        date = self._parse_relative_date(date_str) if date_str else None

        # 创建更新后的 Expense
        expense = Expense(
            amount=amount or 0,
            category=category or "",
            description=description or "",
            date=date or datetime.now(),
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
            from datetime import timedelta
            return now - timedelta(days=1)

        else:
            try:
                return datetime.fromisoformat(date_str)
            except ValueError:
                return None
```

- [ ] **Step 2: 提交 Agent 主逻辑**

```bash
git add core/agent.py
git commit -m "feat: add bookkeeping agent main logic"
```

---

## Chunk 4: Bot 交互层实现

### Task 13: 创建响应格式化器

**Files:**
- Create: `bot/__init__.py`
- Create: `bot/formatter.py`

- [ ] **Step 1: 创建 bot/__init__.py**

```python
"""Bot 交互层模块"""
```

- [ ] **Step 2: 创建 bot/formatter.py - 响应格式化器**

```python
"""响应格式化器，将操作结果转化为友好的自然语言回复"""
from datetime import datetime

from storage.models import Expense, StorageResult


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
```

- [ ] **Step 3: 提交响应格式化器**

```bash
git add bot/formatter.py bot/__init__.py
git commit -m "feat: add response formatter for bot interactions"
```

---

### Task 14: 创建 Telegram Bot 消息处理器

**Files:**
- Create: `bot/handlers.py`

- [ ] **Step 1: 创建 bot/handlers.py - 消息处理器**

```python
"""Telegram Bot 消息处理器"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from core.agent import BookkeepingAgent
from bot.formatter import ResponseFormatter
from utils.exceptions import BookkeepingError

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
            "/help - 查看帮助\n\n"
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
```

- [ ] **Step 2: 提交消息处理器**

```bash
git add bot/handlers.py
git commit -m "feat: add Telegram bot message handlers"
```

---

## Chunk 5: 应用入口与文档

### Task 15: 创建应用入口文件

**Files:**
- Modify: `main.py`

- [ ] **Step 1: 替换 main.py 为应用入口**

```python
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
```

- [ ] **Step 2: 提交应用入口**

```bash
git add main.py
git commit -m "feat: add main application entry point"
```

---

### Task 16: 创建项目文档

**Files:**
- Create: `README.md`

- [ ] **Step 1: 创建 README.md**

```markdown
# AI 记账 Agent

> 一个基于 LLM 的智能记账助手，支持自然语言记录、查询、修改和删除支出，数据存储到 Notion。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

## ✨ 特性

- 🗣️ **自然语言交互** - 用日常语言记录支出，无需记忆复杂命令
- 📊 **完整 CRUD** - 支持记录、查询、修改、删除支出记录
- 🔗 **Notion 存储** - 数据存储在你的 Notion 数据库中，完全可控
- 🤖 **LLM 驱动** - 基于 OpenAI 兼容 API，支持本地模型（如 Ollama）
- 💬 **Telegram Bot** - 随时随地通过 Telegram 记账
- 🔄 **智能重试** - 自动处理网络波动和 API 限流

## 🏗️ 架构设计

```
┌─────────────┐
│  Telegram   │
│     Bot     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   Agent Core        │
│  (LLM + Skills)     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Storage Layer      │
│  (抽象接口)          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Notion Adapter    │
└─────────────────────┘
```

## 🚀 快速开始

### 1. 准备工作

#### 创建 Notion 数据库

1. 在 Notion 中创建一个新的数据库
2. 添加以下列：

| 列名 | 类型 | 说明 |
|------|------|------|
| Description | Title | 支出描述 |
| Amount | Number | 金额 |
| Category | Select | 分类 |
| Date | Date | 日期 |

3. 获取 Database ID（URL 中的一段 32 位字符）

#### 获取 API Token

- **Notion Token**: [创建集成](https://www.notion.so/my-integrations) 获取 Token
- **Telegram Bot Token**: 通过 [@BotFather](https://t.me/botfather) 创建 Bot 获取
- **LLM API Key**: [OpenAI API Key](https://platform.openai.com/api-keys) 或兼容服务

### 2. 安装

```bash
# 克隆仓库
git clone https://github.com/d3Lap1ace/Bookkeeping-skills.git
cd Bookkeeping-skills

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
```

`.env` 配置示例：

```bash
TELEGRAM_BOT_TOKEN=你的_bot_token
LLM_API_KEY=你的_api_key
NOTION_TOKEN=你的_notion_token
NOTION_DATABASE_ID=你的_database_id
```

### 4. 运行

```bash
python main.py
```

Bot 启动后，在 Telegram 中发送 `/start` 开始使用！

## 📖 使用示例

```
你: 花了30块吃午饭
Bot: ✅ 已记录支出
     💰 金额：30.0 元
     📂 分类：餐饮
     📝 描述：午饭

你: 今天花了多少钱
Bot: 📊 支出记录
     ──────────────────────
     📅 2026-03-10
       • 餐饮 | 午饭 | ¥30.00
       当日小计：¥30.00
     ──────────────────────
     💵 总计：¥30.00

你: 把午餐改成40块
Bot: ✅ 已更新支出记录
```

## 🛠️ 开发

### 项目结构

```
bookkeeping-skills/
├── bot/              # Telegram Bot 交互层
├── core/             # Agent 核心逻辑
├── storage/          # 存储抽象层
├── utils/            # 工具模块
├── skills/           # Agent Skills 定义（Markdown）
├── config.py         # 配置管理
├── main.py           # 应用入口
└── requirements.txt  # 依赖列表
```

### 运行测试

```bash
pytest tests/ -v
```

## 🔌 扩展

### 添加新的存储后端

继承 `ExpenseStorage` 抽象基类：

```python
from storage.base import ExpenseStorage

class MyStorage(ExpenseStorage):
    async def save_expense(self, expense):
        # 实现保存逻辑
        pass
    # ... 实现其他方法
```

### 添加新的 Skill

在 `skills/` 目录下创建新的 `.md` 文件，定义参数和行为。

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 👤 作者

**d3Lap1ace** - [GitHub](https://github.com/d3Lap1ace)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🙏 致谢

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Notion API](https://developers.notion.com/)
- [OpenAI API](https://platform.openai.com/)
```

- [ ] **Step 2: 创建 Notion 模板文档**

```bash
mkdir -p docs
```

- [ ] **Step 3: 创建 docs/notion-template.md**

```markdown
# Notion 数据库配置指南

## 数据库结构

创建一个新的 Notion 数据库，包含以下列：

### 必需列

| 列名 | 类型 | 配置 |
|------|------|------|
| **Description** | Title | - |
| **Amount** | Number | Format: Number, 默认为 0 |
| **Category** | Select | 预设选项：餐饮、交通、购物、娱乐、医疗、教育、居住、其他 |
| **Date** | Date | 包含时间：可选 |

### 可选列

| 列名 | 类型 | 说明 |
|------|------|------|
| **Tags** | Multi-select | 标签 |
| **Notes** | Text | 备注 |

## 获取 Database ID

1. 打开你的 Notion 数据库
2. 复制 URL
3. Database ID 是 URL 中的一段 32 位字符

例如：
```
https://www.notion.so/username/[database_id]?v=...
                    ↑ 就是这段
```

## 集成配置

1. 访问 [Notion My Integrations](https://www.notion.so/my-integrations)
2. 创建新集成，选择权限（需要读取和插入数据库的权限）
3. 复制 Integration Token

4. 在数据库页面：
   - 点击右上角 `...` → `Add connections`
   - 选择你创建的集成

## 预览

完成配置后，你的数据库应该类似这样：

| Description | Amount | Category | Date |
|-------------|--------|----------|------|
| 午餐 | 30.00 | 餐饮 | 2026-03-10 |
| 地铁 | 5.00 | 交通 | 2026-03-10 |
| 超市购物 | 158.50 | 购物 | 2026-03-09 |
```

- [ ] **Step 4: 提交文档**

```bash
git add README.md docs/
git commit -m "docs: add project documentation and Notion setup guide"
```

---

### Task 17: 创建 LICENSE 文件

**Files:**
- Create: `LICENSE`

- [ ] **Step 1: 创建 MIT LICENSE**

```text
MIT License

Copyright (c) 2026 d3Lap1ace

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: 提交 LICENSE**

```bash
git add LICENSE
git commit -m "chore: add MIT license"
```

---

## 完成检查清单

- [x] 基础设施文件（requirements.txt, .env.example, .gitignore）
- [x] 配置管理模块
- [x] 工具层（异常、重试、日志）
- [x] 存储层（抽象基类、Notion 适配器）
- [x] Agent 核心（LLM 客户端、Skills、Agent 逻辑）
- [x] Bot 交互层（处理器、格式化器）
- [x] 应用入口和文档

---

计划已完成并保存到 `docs/superpowers/plans/2026-03-10-ai-bookkeeping-agent.md`。
