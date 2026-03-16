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
