"""OpenAI 兼容的 LLM 客户端"""
from openai import AsyncOpenAI

from bookkeeping_bot.utils.exceptions import LLMError, RateLimitError
from bookkeeping_bot.utils.retry import retry_with_backoff


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
        self.base_url = base_url.rstrip("/")
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.base_url,
        )
        self.model = model

    @property
    def is_gemini_compatible(self) -> bool:
        """标识当前是否走 Gemini 的 OpenAI 兼容端点。"""
        return "generativelanguage.googleapis.com" in self.base_url

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
                tool_choice="auto",
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
