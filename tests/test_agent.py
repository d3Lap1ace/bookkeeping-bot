"""测试 Agent 的工具调用回退逻辑"""
import json

import pytest

from bookkeeping_bot.core.agent import BookkeepingAgent
from bookkeeping_bot.utils.exceptions import LLMError
from bookkeeping_bot.storage.models import StorageResult


class FakeSkillLoader:
    """最小 skill loader 桩对象"""

    def load_all(self):
        return {
            "record_expense": {
                "type": "function",
                "function": {
                    "name": "record_expense",
                    "description": "记录支出",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        }

    def get_system_prompt(self):
        return "你是一个记账助手"


class FakeStorage:
    """最小存储桩对象"""

    async def save_expense(self, expense):
        return StorageResult(success=True, message="ok", data={"notion_url": "https://notion.so/test"})

    async def query_expenses(self, filters):
        return ()

    async def update_expense(self, notion_id, expense):
        return StorageResult(success=True, message="ok")

    async def delete_expense(self, notion_id):
        return StorageResult(success=True, message="ok")


class GeminiFirstCallOnlyLLM:
    """Gemini 兼容端点：只做首轮工具选择"""

    is_gemini_compatible = True

    def __init__(self):
        self.calls = 0

    async def chat_with_tools(self, messages, tools):
        self.calls += 1
        return {
            "content": None,
            "tool_calls": [
                {
                    "id": "call-1",
                    "name": "record_expense",
                    "arguments": json.dumps(
                        {
                            "amount": 20,
                            "category": "餐饮",
                            "description": "咖啡",
                            "date": "今天",
                        }
                    ),
                }
            ],
        }


class FailingSecondCallLLM:
    """非 Gemini 端点：第二轮总结失败时应回退到工具结果"""

    is_gemini_compatible = False

    def __init__(self):
        self.calls = 0

    async def chat_with_tools(self, messages, tools):
        self.calls += 1

        if self.calls == 1:
            return {
                "content": None,
                "tool_calls": [
                    {
                        "id": "call-1",
                        "name": "record_expense",
                        "arguments": json.dumps(
                            {
                                "amount": 20,
                                "category": "餐饮",
                                "description": "咖啡",
                                "date": "今天",
                            }
                        ),
                    }
                ],
            }

        raise LLMError("final response failed")


@pytest.mark.asyncio
async def test_agent_returns_tool_result_directly_for_gemini():
    """Gemini 兼容接口应跳过第二轮总结请求"""
    llm = GeminiFirstCallOnlyLLM()
    agent = BookkeepingAgent(llm_client=llm, storage=FakeStorage(), skill_loader=FakeSkillLoader())

    response = await agent.process_message("今天下午买了杯咖啡花了20")

    assert "✅ 已记录：餐饮 20.0元" in response
    assert llm.calls == 1


@pytest.mark.asyncio
async def test_agent_falls_back_to_tool_result_when_second_call_fails():
    """第二轮总结失败时仍应返回工具执行结果"""
    llm = FailingSecondCallLLM()
    agent = BookkeepingAgent(llm_client=llm, storage=FakeStorage(), skill_loader=FakeSkillLoader())

    response = await agent.process_message("今天下午买了杯咖啡花了20")

    assert "✅ 已记录：餐饮 20.0元" in response
    assert llm.calls == 2
