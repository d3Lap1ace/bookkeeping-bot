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
