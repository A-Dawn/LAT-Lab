# Markdown增强工具插件
# 此插件提供多种Markdown增强功能，如语法高亮、目录生成等
# 作者: LAT-LAB开发团队

import re
import json
import datetime

# 获取参数
params = globals().get("params", {})
markdown_text = params.get("markdown_text", "")
generate_toc = params.get("generate_toc", True)
highlight_code = params.get("highlight_code", True)
add_footnotes = params.get("add_footnotes", False)
add_table_styles = params.get("add_table_styles", True)

# 定义默认示例Markdown文本
if not markdown_text:
    markdown_text = """# Markdown示例文档

这是一个示例Markdown文档，演示Markdown增强工具的功能。

## 目录

## 代码示例

```python
def hello_world():
    print("Hello, LAT-LAB!")
    
# 这是一个简单的Python函数
for i in range(5):
    hello_world()
```

## 表格示例

| 姓名 | 年龄 | 职业 |
|-----|-----|------|
| 张三 | 28 | 工程师 |
| 李四 | 32 | 设计师 |
| 王五 | 45 | 经理 |

## 脚注示例

这里是一段带有脚注的文本[^1]。

[^1]: 这是脚注的内容。
"""

# 生成目录函数
def generate_table_of_contents(markdown):
    # 匹配标题行 (# 标题)，捕获标题级别和标题文本
    headers = re.findall(r'^(#{1,6})\s+(.+?)$', markdown, re.MULTILINE)
    
    if not headers:
        return ""
    
    toc = ["## 目录\n"]
    
    for header in headers:
        # 跳过"目录"标题本身
        if header[1].strip().lower() == "目录":
            continue
            
        level = len(header[0]) - 1  # 减去1，因为h1对应0缩进
        indent = "  " * level
        
        # 创建锚点ID (将标题转为小写，替换空格为连字符)
        anchor = header[1].lower().replace(" ", "-").replace(".", "").replace(",", "")
        # 移除其他不适合作为ID的特殊字符
        anchor = re.sub(r'[^\w\-]', '', anchor)
        
        # 添加到目录
        toc.append(f"{indent}- [{header[1]}](#{anchor})")
    
    return "\n".join(toc) + "\n\n"

# 语法高亮函数（在实际中，前端会处理语法高亮，这里只添加类名）
def highlight_code_blocks(markdown):
    def code_replace(match):
        language = match.group(1) or ""
        code = match.group(2)
        return f'```{language} class="language-{language} hljs"\n{code}\n```'
    
    # 匹配代码块并添加类名
    highlighted = re.sub(r'```(\w*)\n(.*?)\n```', code_replace, markdown, flags=re.DOTALL)
    return highlighted

# 处理表格样式
def enhance_tables(markdown):
    def table_replace(match):
        table = match.group(0)
        # 在表格前后添加div包装器
        return f'<div class="markdown-table-wrapper" markdown="1">\n\n{table}\n\n</div>'
    
    # 匹配整个表格（表头和表体）并添加包装器
    enhanced = re.sub(r'(\|.+\|\n\|[-:| ]+\|\n(?:\|.+\|\n)+)', table_replace, markdown)
    return enhanced

# 处理脚注
def process_footnotes(markdown):
    # 已经是标准Markdown语法，无需特殊处理
    # 但可以添加一个脚注部分的标题
    if "[^" in markdown and not re.search(r'^## 脚注', markdown, re.MULTILINE):
        markdown += "\n\n## 脚注\n"
    return markdown

# 处理Markdown文本
processed_markdown = markdown_text

# 1. 生成目录
if generate_toc and "## 目录" in processed_markdown:
    # 找到目录标记并替换
    toc_content = generate_table_of_contents(processed_markdown)
    processed_markdown = re.sub(r'## 目录\s*\n', toc_content, processed_markdown)

# 2. 高亮代码块
if highlight_code:
    processed_markdown = highlight_code_blocks(processed_markdown)

# 3. 添加表格样式
if add_table_styles:
    processed_markdown = enhance_tables(processed_markdown)

# 4. 处理脚注
if add_footnotes:
    processed_markdown = process_footnotes(processed_markdown)

# 创建说明文档
explanation = """
# Markdown增强工具

此工具可以增强你的Markdown文档，添加以下功能：

1. **目录生成**：自动从文档标题生成目录
2. **代码高亮**：为代码块添加语法高亮支持
3. **表格增强**：改进表格的显示样式
4. **脚注处理**：支持脚注语法并自动添加脚注标题

## 使用方法

1. 在文档中添加`## 目录`标记来放置目录
2. 使用标准的Markdown语法编写文档
3. 使用此工具处理文档，得到增强版本

## 示例

输入Markdown文本，并选择需要的增强功能。
"""

# 定义参数表单
params_form = {
    "title": "Markdown增强工具",
    "fields": [
        {
            "name": "markdown_text",
            "label": "Markdown文本",
            "type": "textarea",
            "default": markdown_text,
            "required": True,
            "rows": 10,
            "description": "输入需要处理的Markdown文本"
        },
        {
            "name": "generate_toc",
            "label": "生成目录",
            "type": "checkbox",
            "default": True,
            "description": "自动生成目录（需在文档中添加'## 目录'标记）"
        },
        {
            "name": "highlight_code",
            "label": "代码高亮",
            "type": "checkbox",
            "default": True,
            "description": "为代码块添加语法高亮支持"
        },
        {
            "name": "add_table_styles",
            "label": "表格样式增强",
            "type": "checkbox",
            "default": True,
            "description": "改进表格的显示样式"
        },
        {
            "name": "add_footnotes",
            "label": "处理脚注",
            "type": "checkbox",
            "default": False,
            "description": "支持脚注语法并自动添加脚注标题"
        }
    ]
}

# 创建小部件
widget_html = f"""
<div style="font-family: Arial, sans-serif; background: #f8f9fa; padding: 15px; border-radius: 5px; border: 1px solid #ddd;">
    <h3 style="margin-top: 0;">Markdown增强工具</h3>
    <p>此小部件可以增强你的Markdown文档，添加目录、代码高亮等功能。</p>
    <div style="display: flex; gap: 10px; margin-top: 10px;">
        <a href="/admin/plugins/markdown-tools" style="display: inline-block; padding: 8px 15px; background: #3498db; color: white; text-decoration: none; border-radius: 4px;">使用工具</a>
        <a href="/admin/plugins" style="display: inline-block; padding: 8px 15px; background: #f1f1f1; color: #333; text-decoration: none; border-radius: 4px;">查看所有插件</a>
    </div>
</div>
"""

# 定义小部件配置
widget_config = {
    "type": "home-widget",
    "name": "Markdown增强工具",
    "position": "sidebar",
    "priority": 80,
    "html": widget_html
}

# 为了展示，创建输出结果
demo_result = f"""
# Markdown增强工具结果

## 原始文本

```markdown
{markdown_text}
```

## 处理后的文本

```markdown
{processed_markdown}
```

## 更多信息

- **处理时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **启用的功能**: 
  - 目录生成: {"是" if generate_toc else "否"}
  - 代码高亮: {"是" if highlight_code else "否"}
  - 表格样式增强: {"是" if add_table_styles else "否"}
  - 脚注处理: {"是" if add_footnotes else "否"}
"""

# 输出结果
result = f"""
{explanation}

## 处理结果

```markdown
{processed_markdown}
```

## 小部件配置

此插件提供了一个前端小部件，用于快速访问Markdown增强工具。

```json
{json.dumps(widget_config, ensure_ascii=False, indent=2)}
```

> 注意：实际使用时，前端需要支持相应的CSS和JavaScript来正确显示增强的Markdown内容。
""" 