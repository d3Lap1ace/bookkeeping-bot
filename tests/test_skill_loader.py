"""测试 Skill 加载器"""
import pytest
from pathlib import Path

from bookkeeping_bot.core.skill_loader import SkillLoader


class TestSkillLoader:
    """测试 SkillLoader 类"""

    def test_load_all(self):
        """测试加载所有 Skills"""
        loader = SkillLoader(skills_dir=Path("bookkeeping_bot/skills"))
        skills = loader.load_all()

        # 验证所有 Skills 都被加载
        assert "record_expense" in skills
        assert "query_expenses" in skills
        assert "update_expense" in skills
        assert "delete_expense" in skills

        # 验证 Skills 格式
        for skill_name, skill_def in skills.items():
            assert skill_def["type"] == "function"
            assert "function" in skill_def
            assert "name" in skill_def["function"]
            assert skill_def["function"]["name"] == skill_name

    def test_skill_has_description(self):
        """测试 Skill 有描述"""
        loader = SkillLoader(skills_dir=Path("bookkeeping_bot/skills"))
        skills = loader.load_all()

        for skill_name, skill_def in skills.items():
            description = skill_def["function"]["description"]
            assert description
            assert len(description) > 0

    def test_skill_has_parameters(self):
        """测试 Skill 有参数定义"""
        loader = SkillLoader(skills_dir=Path("bookkeeping_bot/skills"))
        skills = loader.load_all()

        for skill_name, skill_def in skills.items():
            parameters = skill_def["function"]["parameters"]
            assert "type" in parameters
            assert parameters["type"] == "object"
            assert "properties" in parameters

    def test_record_expense_skill_parameters(self):
        """测试 record_expense Skill 的参数"""
        loader = SkillLoader(skills_dir=Path("bookkeeping_bot/skills"))
        skills = loader.load_all()

        record_skill = skills["record_expense"]
        params = record_skill["function"]["parameters"]

        # 验证必需参数
        assert "amount" in params["properties"]
        assert "category" in params["properties"]

        # 验证参数类型
        assert params["properties"]["amount"]["type"] == "number"
        assert params["properties"]["category"]["type"] == "string"

    def test_get_system_prompt(self):
        """测试获取 System Prompt"""
        loader = SkillLoader(skills_dir=Path("bookkeeping_bot/skills"))
        prompt = loader.get_system_prompt()

        assert "智能记账助手" in prompt
        assert "record_expense" in prompt
        assert "query_expenses" in prompt

    def test_cache_works(self):
        """测试缓存机制"""
        loader = SkillLoader(skills_dir=Path("bookkeeping_bot/skills"))

        # 第一次调用
        skills1 = loader.load_all()
        # 第二次调用应该使用缓存
        skills2 = loader.load_all()

        assert skills1 is skills2
