"""AI 记账 Bot - Bookkeeping Bot

一个基于 Telegram 的 AI 记账助手，支持自然语言记账、查询、修改和删除支出。
数据存储在 Notion 中，每个用户独立部署。

使用方法:
    1. pip install bookkeeping-bot
    2. 创建 ~/.bookkeeping/config.json 配置文件
    3. 运行 bookkeeping-bot
"""

__version__ = "0.1.0"
__author__ = "d3lap1ace"

# 延迟导入，避免在包初始化时加载所有依赖
def get_config():
    """获取配置"""
    from bookkeeping_bot.config import Config
    return Config

def get_agent():
    """获取 Agent"""
    from bookkeeping_bot.core.agent import BookkeepingAgent
    return BookkeepingAgent

__all__ = ["__version__", "get_config", "get_agent"]
