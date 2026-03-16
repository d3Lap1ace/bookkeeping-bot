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
