"""从 Markdown 文件加载 Agent Skills 定义"""
import json
import re
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
