"""智能重试装饰器，使用指数退避策略"""
import asyncio
import functools
import logging
from typing import Callable, TypeVar

try:
    from typing import ParamSpec
except ImportError:
    from typing_extensions import ParamSpec

from bookkeeping_bot.utils.exceptions import RateLimitError

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
