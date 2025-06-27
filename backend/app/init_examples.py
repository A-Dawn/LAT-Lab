#!/usr/bin/env python
"""
初始化插件示例目录

该脚本用于确保插件示例目录存在，并包含所有必要的示例文件。
可以在应用启动时运行，或手动运行以重新初始化示例。
"""

import os
import shutil
import sys
from pathlib import Path

# 获取当前脚本所在目录
current_dir = Path(__file__).parent
app_dir = current_dir

# 插件示例目录
plugin_examples_dir = os.path.join(app_dir, "plugin_examples")

def init_examples():
    """初始化插件示例目录和文件"""
    print(f"初始化插件示例目录: {plugin_examples_dir}")
    
    # 确保插件示例目录存在
    os.makedirs(plugin_examples_dir, exist_ok=True)
    
    # 插件示例内容
    examples = {
        "hello_world.py": '''# 这是一个简单的Hello World示例插件
# 插件可以执行各种任务，例如数据处理、生成报告等
# 插件将在沙箱环境中执行，有一定的安全限制

# 你可以导入标准库
import datetime

# 获取当前时间
now = datetime.datetime.now()

# 创建一个简单的输出
result = f"""
Hello, LAT-LAB World!
===================

这是一个简单的插件示例，演示如何创建一个基本的插件。
插件可以执行各种操作，并将结果返回给博客系统。

当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}
"""

# 插件必须将结果存储在名为 "result" 的变量中
# result 变量的值将作为插件的输出返回''',
        
        "article_stats.py": '''# 文章统计分析插件示例
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
    article_table += f"| {month} | {count} |\\n"

# 格式化评论统计数据
comment_table = ""
for month, count in comment_stats:
    comment_table += f"| {month} | {count} |\\n"

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
"""''',
        
        "simple_counter.py": '''# 简单计数器插件示例
# 此插件演示如何创建和维护一个简单的计数器

import json
import os
import datetime

# 计数器文件路径
counter_file = "counter.json"

# 加载或初始化计数器
def load_counter():
    if os.path.exists(counter_file):
        try:
            with open(counter_file, "r") as f:
                return json.load(f)
        except Exception:
            return {"count": 0, "last_updated": None}
    else:
        return {"count": 0, "last_updated": None}

# 保存计数器
def save_counter(counter_data):
    with open(counter_file, "w") as f:
        json.dump(counter_data, f)

# 更新计数器
counter_data = load_counter()
counter_data["count"] += 1
counter_data["last_updated"] = datetime.datetime.now().isoformat()
save_counter(counter_data)

# 生成小部件配置
widget_config = {
    "type": "home-widget",
    "name": "计数器小部件",
    "position": "sidebar",
    "priority": 200,
    "html": f"""
    <div class="counter-widget">
        <h3>计数器</h3>
        <div class="counter-value">
            <span>此插件已被运行 </span>
            <span class="counter-number">{counter_data["count"]}</span>
            <span> 次</span>
        </div>
        <div class="counter-date">
            最后更新: {counter_data["last_updated"].split("T")[0]}
        </div>
    </div>
    """
}

# 创建结果输出
result = f"""
# 简单计数器插件

此插件演示如何创建一个简单的计数器，每次运行时增加计数。

## 当前计数

插件已运行: **{counter_data["count"]}** 次
最后更新: {counter_data["last_updated"]}

## 小部件配置

此插件将在首页显示一个计数器小部件。

```json
{json.dumps(widget_config, ensure_ascii=False, indent=2)}
```
"""''',

        "openrouter_llm.py": '''# OpenRouter LLM API 调用插件示例
# 此插件演示如何调用外部API（OpenRouter.ai）访问各种大语言模型

import json
import requests
import os

# 这里应该配置你的 OpenRouter API 密钥
# 实际应用中，不应该在代码中硬编码API密钥，应该使用环境变量或安全存储
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# 如果没有找到API密钥，可以使用演示模式
DEMO_MODE = not OPENROUTER_API_KEY

def call_openrouter_api(prompt, model="openai/gpt-3.5-turbo"):
    """调用 OpenRouter API 获取回复"""
    if DEMO_MODE:
        # 演示模式：返回模拟回复
        return f"这是一个演示模式回复。你询问了: '{prompt}'。\n\n要使用真实的API，请配置OPENROUTER_API_KEY环境变量。"
    
    # API端点
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://luminarc.tech",  # 你的网站URL
        "X-Title": "LAT-LAB Plugin"  # 你的应用名称
    }
    
    # 请求体
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是LAT-LAB系统的AI助手，用中文回答用户的问题。"},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, json=data)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"API请求失败: HTTP {response.status_code}\\n{response.text}"
    
    except Exception as e:
        return f"API调用出错: {str(e)}"

# 获取前端传递的参数
# 在实际运行时，前端可以传递参数，如prompt和model
# 这里使用默认值作为备选
prompt = globals().get("prompt", "介绍一下自己")
model = globals().get("model", "openai/gpt-3.5-turbo")

# 调用API获取响应
api_response = call_openrouter_api(prompt, model)

# 构建结果
result = f"""
# OpenRouter LLM API 调用结果

## 请求信息
- 模型: {model}
- 提示词: "{prompt}"
- 演示模式: {"是" if DEMO_MODE else "否"}

## 生成内容
{api_response}

---

## 使用说明
此插件演示如何调用OpenRouter API访问各种大型语言模型。
在实际使用中，你需要:

1. 在环境变量中设置 OPENROUTER_API_KEY
2. 前端传递参数:
   - prompt: 用户提示词
   - model: 模型ID (例如 "openai/gpt-3.5-turbo", "anthropic/claude-3-opus" 等)

## 前端小部件配置

```json
{
  "type": "home-widget",
  "name": "AI助手",
  "position": "sidebar",
  "priority": 50,
  "html": "<div class=\\"ai-widget\\"><h3>AI助手</h3><p>使用OpenRouter API连接各种大语言模型</p><div class=\\"api-status\\">API状态: " + ("演示模式" if DEMO_MODE else "已连接") + "</div></div>"
}
```
"""''',
        
        "image_widget.py": '''# 图片小部件插件示例
# 这个插件演示如何创建一个在前端首页添加带图片的小部件

import datetime
import json
import base64

# 示例：将图片编码为base64
def get_image_base64():
    # 这里使用一个简单的示例图片（1x1像素的蓝色图片）
    # 在实际应用中，你可以读取本地文件或从网络获取图片
    blue_pixel = bytes([0, 0, 255])  # RGB蓝色
    base64_data = base64.b64encode(blue_pixel).decode('utf-8')
    
    # 实际项目中可以使用这种方式读取本地图片
    # with open("path/to/image.jpg", "rb") as image_file:
    #     base64_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    return f"data:image/png;base64,{base64_data}"

# 获取当前时间
now = datetime.datetime.now()

# 创建小部件配置
widget_config = {
    "type": "home-widget",
    "name": "图片示例小部件",
    "position": "sidebar",
    "priority": 50,
    "html": f"""
    <div class="image-widget">
        <h3>图片示例</h3>
        <p>这是一个带图片的小部件示例，当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <!-- 内嵌base64图片 -->
        <div class="sample-image">
            <img src="{get_image_base64()}" alt="示例图片" style="width:100%; height:100px; background-color:blue;" />
        </div>
        
        <!-- 也可以使用外部图片链接 -->
        <div class="external-image">
            <p>外部图片示例:</p>
            <img src="https://picsum.photos/300/200" alt="随机图片" style="width:100%; border-radius:8px; margin-top:10px;" />
        </div>
        
        <div class="widget-footer" style="margin-top:15px; font-size:0.9em; color:#999;">
            由图片小部件插件生成
        </div>
    </div>
    """
}

# 将配置序列化为JSON，并包装在markdown代码块中以便前端识别
result = f"""
插件执行成功! 创建了一个图片小部件，将显示在博客首页侧边栏。

```json
{json.dumps(widget_config, ensure_ascii=False, indent=2)}
```
"""''',

        "README.md": '''# LAT-Lab 插件示例

这个目录包含了一些插件示例，帮助你了解如何为LAT-Lab开发插件。

## 插件列表

1. **hello_world.py** - 基本的Hello World插件示例
2. **article_stats.py** - 展示如何访问数据库生成文章统计报告
3. **simple_counter.py** - 演示如何创建和维护状态的计数器插件
4. **openrouter_llm.py** - 展示如何调用外部API访问大语言模型
5. **image_widget.py** - 展示如何创建带图片的前端小部件

## 如何使用

1. 在管理面板的插件管理页面，点击"加载示例插件"
2. 选择一个示例插件，查看其代码
3. 根据需要修改代码，然后保存为新插件

## 开发插件

开发LAT-Lab插件时，需要注意以下几点：

1. 插件是Python脚本，将在沙箱环境中执行
2. 插件必须将输出结果存储在名为`result`的变量中
3. 可以使用标准库和已安装的第三方库
4. 为了安全起见，某些操作可能受到限制

## 前端小部件

要创建可在博客前端显示的小部件，插件应返回包含以下格式JSON的markdown代码块：

```json
{
  "type": "home-widget",
  "name": "小部件名称",
  "position": "sidebar",
  "priority": 100,
  "html": "<div>小部件HTML内容</div>"
}
```

其中：
- `type`: 固定为"home-widget"
- `name`: 小部件显示名称
- `position`: 显示位置，可选值: "sidebar", "top", "bottom", "left", "right"
- `priority`: 显示优先级(数字越小越靠前)
- `html`: 小部件的HTML内容

## 安全考虑

开发插件时，需要注意安全性：

1. 避免执行危险操作
2. 不要在代码中硬编码敏感信息
3. 使用参数化查询防止SQL注入
4. 验证和清理所有外部输入
'''
    }
    
    # 创建示例文件
    for filename, content in examples.items():
        file_path = os.path.join(plugin_examples_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"创建示例文件: {filename}")
    
    print("插件示例初始化完成！")

if __name__ == "__main__":
    init_examples() 