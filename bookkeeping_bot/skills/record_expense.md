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
