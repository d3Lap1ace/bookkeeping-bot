# Notion 数据库配置指南

## 数据库结构

创建一个新的 Notion 数据库，包含以下列：

### 必需列

| 列名 | 类型 | 配置 |
|------|------|------|
| **Description** | Title | - |
| **Amount** | Number | Format: Number, 默认为 0 |
| **Category** | Select | 预设选项：餐饮、交通、购物、娱乐、医疗、教育、居住、其他 |
| **Date** | Date | 包含时间：可选 |

### 可选列

| 列名 | 类型 | 说明 |
|------|------|------|
| **Tags** | Multi-select | 标签 |
| **Notes** | Text | 备注 |

## 获取 Database ID

1. 打开你的 Notion 数据库
2. 复制 URL
3. Database ID 是 URL 中的一段 32 位字符

例如：
```
https://www.notion.so/username/[database_id]?v=...
                    ↑ 就是这段
```

## 集成配置

1. 访问 [Notion My Integrations](https://www.notion.so/my-integrations)
2. 创建新集成，选择权限（需要读取和插入数据库的权限）
3. 复制 Integration Token

4. 在数据库页面：
   - 点击右上角 `...` → `Add connections`
   - 选择你创建的集成

## 预览

完成配置后，你的数据库应该类似这样：

| Description | Amount | Category | Date |
|-------------|--------|----------|------|
| 午餐 | 30.00 | 餐饮 | 2026-03-10 |
| 地铁 | 5.00 | 交通 | 2026-03-10 |
| 超市购物 | 158.50 | 购物 | 2026-03-09 |
