# 文章统计分析插件示例
# 此插件展示如何使用数据库交互，并生成一个简单的统计报告

# 导入标准库
import datetime
import sqlite3
import json

# 连接数据库
# 注意：实际生产环境中，应该使用后端提供的安全数据库连接方式
# 此处为示例，直接连接SQLite数据库
conn = sqlite3.connect("blog.db")
cursor = conn.cursor()

# 查询文章数据
cursor.execute("""
SELECT
    strftime('%Y-%m', created_at) as month,
    COUNT(*) as article_count
FROM
    articles
GROUP BY
    strftime('%Y-%m', created_at)
ORDER BY
    month
""")
article_stats = cursor.fetchall()

# 查询评论数据
cursor.execute("""
SELECT
    strftime('%Y-%m', created_at) as month,
    COUNT(*) as comment_count
FROM
    comments
GROUP BY
    strftime('%Y-%m', created_at)
ORDER BY
    month
""")
comment_stats = cursor.fetchall()

# 关闭连接
conn.close()

# 格式化文章统计数据
article_table = ""
for month, count in article_stats:
    article_table += f"| {month} | {count} |\n"

# 格式化评论统计数据
comment_table = ""
for month, count in comment_stats:
    comment_table += f"| {month} | {count} |\n"

# 生成小部件配置
widget_config = {
    "type": "home-widget",
    "name": "文章统计小部件",
    "position": "sidebar",
    "priority": 100,
    "html": f"""
    <div class="stats-widget">
        <h3>博客统计</h3>
        <div class="stats-item">
            <span class="stats-label">总文章数:</span>
            <span class="stats-value">{sum([count for _, count in article_stats])}</span>
        </div>
        <div class="stats-item">
            <span class="stats-label">总评论数:</span>
            <span class="stats-value">{sum([count for _, count in comment_stats])}</span>
        </div>
        <div class="stats-item">
            <span class="stats-label">最近更新:</span>
            <span class="stats-value">{datetime.datetime.now().strftime('%Y-%m-%d')}</span>
        </div>
    </div>
    """
}

# 生成结果报告
result = f"""
# 博客统计报告

生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 文章发布统计

| 月份 | 文章数 |
|------|--------|
{article_table}

## 评论统计

| 月份 | 评论数 |
|------|--------|
{comment_table}

## 小部件配置

此插件可以在首页显示博客统计小部件。

```json
{json.dumps(widget_config, ensure_ascii=False, indent=2)}
```
"""