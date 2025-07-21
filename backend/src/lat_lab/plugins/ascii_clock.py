# ASCII 时钟字符画插件
# 根据当前时间生成一个漂亮的ASCII数字时钟字符画
# 作者: LAT-LAB开发团队

import datetime
import json

# 获取参数（如果有）
params = globals().get("params", {})
use_24h_format = params.get("use_24h_format", True)
show_seconds = params.get("show_seconds", True)
show_date = params.get("show_date", True)
border_style = params.get("border_style", "double")

# 定义数字的ASCII艺术表示（每个数字为5x3的矩阵）
ASCII_DIGITS = {
    "0": [
        " █████ ", 
        "██   ██", 
        "██   ██",
        "██   ██", 
        " █████ "
    ],
    "1": [
        "   ██  ", 
        "  ███  ", 
        "   ██  ",
        "   ██  ", 
        "████████"
    ],
    "2": [
        " █████ ", 
        "██   ██", 
        "    ██ ",
        " ██    ", 
        "███████"
    ],
    "3": [
        " █████ ", 
        "██   ██", 
        "   ███ ",
        "██   ██", 
        " █████ "
    ],
    "4": [
        "██   ██", 
        "██   ██", 
        "███████",
        "     ██", 
        "     ██"
    ],
    "5": [
        "███████", 
        "██     ", 
        "██████ ",
        "     ██", 
        "██████ "
    ],
    "6": [
        " █████ ", 
        "██     ", 
        "██████ ",
        "██   ██", 
        " █████ "
    ],
    "7": [
        "███████", 
        "    ██ ", 
        "   ██  ",
        "  ██   ", 
        " ██    "
    ],
    "8": [
        " █████ ", 
        "██   ██", 
        " █████ ",
        "██   ██", 
        " █████ "
    ],
    "9": [
        " █████ ", 
        "██   ██", 
        " ██████",
        "     ██", 
        " █████ "
    ],
    ":": [
        "   ", 
        "██ ", 
        "   ",
        "██ ", 
        "   "
    ],
    " ": [
        "  ", 
        "  ", 
        "  ",
        "  ", 
        "  "
    ],
    "-": [
        "     ", 
        "     ", 
        "█████",
        "     ", 
        "     "
    ],
    "/": [
        "    ██", 
        "   ██ ", 
        "  ██  ",
        " ██   ", 
        "██    "
    ],
    "AM": [
        "  █████  ██████  ", 
        " ██   ██ ██   ██ ", 
        "██████████████  ",
        "██     ██   ██ ", 
        "██     ██   ██ "
    ],
    "PM": [
        "███████  ██████  ", 
        "██    ██ ██   ██ ", 
        "███████ ██████  ",
        "██      ██   ██ ", 
        "██      ██   ██ "
    ]
}

# 边框样式
BORDERS = {
    "none": {
        "top_left": "", "top": "", "top_right": "",
        "left": "", "right": "",
        "bottom_left": "", "bottom": "", "bottom_right": ""
    },
    "single": {
        "top_left": "┌", "top": "─", "top_right": "┐",
        "left": "│", "right": "│",
        "bottom_left": "└", "bottom": "─", "bottom_right": "┘"
    },
    "double": {
        "top_left": "╔", "top": "═", "top_right": "╗",
        "left": "║", "right": "║",
        "bottom_left": "╚", "bottom": "═", "bottom_right": "╝"
    },
    "rounded": {
        "top_left": "╭", "top": "─", "top_right": "╮",
        "left": "│", "right": "│",
        "bottom_left": "╰", "bottom": "─", "bottom_right": "╯"
    },
    "bold": {
        "top_left": "┏", "top": "━", "top_right": "┓",
        "left": "┃", "right": "┃",
        "bottom_left": "┗", "bottom": "━", "bottom_right": "┛"
    }
}

# 获取当前时间
now = datetime.datetime.now()

# 格式化时间
if use_24h_format:
    hour_format = "%H"
else:
    hour_format = "%I"
    am_pm = now.strftime("%p")

time_str = now.strftime(f"{hour_format}:%M")
if show_seconds:
    time_str = now.strftime(f"{hour_format}:%M:%S")

# 为ASCII艺术准备时间字符
chars = list(time_str)

# 创建ASCII时钟
ascii_clock = []

# 如果边框不是"none"，添加顶部边框
border = BORDERS.get(border_style, BORDERS["double"])
if border_style != "none":
    width = len(chars) * 8 + 4
    top_border = border["top_left"] + border["top"] * (width - 2) + border["top_right"]
    ascii_clock.append(top_border)
    ascii_clock.append(border["left"] + " " * (width - 2) + border["right"])

# 生成数字时钟的每一行
for row in range(5):  # 每个数字有5行
    line = border["left"] + " " if border_style != "none" else ""
    
    # 添加每个数字的对应行
    for char in chars:
        line += ASCII_DIGITS.get(char, ASCII_DIGITS[" "])[row] + " "
    
    # 如果使用12小时制，添加AM/PM
    if not use_24h_format:
        line += " " + ASCII_DIGITS.get(am_pm, ASCII_DIGITS["AM"])[row]
    
    # 添加右边框
    if border_style != "none":
        line += " " + border["right"]
    
    ascii_clock.append(line)

# 如果显示日期，添加日期行
if show_date:
    date_str = now.strftime("%Y-%m-%d")
    date_display = f" {date_str} "
    
    if border_style != "none":
        width = len(chars) * 8 + 4
        padding = (width - len(date_display)) // 2
        date_line = border["left"] + " " * padding + date_display + " " * (width - padding - len(date_display) - 2) + border["right"]
        ascii_clock.append(date_line)

# 添加底部边框
if border_style != "none":
    width = len(chars) * 8 + 4
    ascii_clock.append(border["left"] + " " * (width - 2) + border["right"])
    bottom_border = border["bottom_left"] + border["bottom"] * (width - 2) + border["bottom_right"]
    ascii_clock.append(bottom_border)

# 将ASCII时钟行连接成单个字符串
ascii_clock_str = "\n".join(ascii_clock)

# 定义参数表单，允许用户自定义时钟
params_form = {
    "title": "ASCII时钟配置",
    "fields": [
        {
            "name": "use_24h_format",
            "label": "使用24小时制",
            "type": "checkbox",
            "default": True,
            "description": "选中则使用24小时制，否则使用12小时制(AM/PM)"
        },
        {
            "name": "show_seconds",
            "label": "显示秒数",
            "type": "checkbox",
            "default": True,
            "description": "是否在时钟中显示秒数"
        },
        {
            "name": "show_date",
            "label": "显示日期",
            "type": "checkbox",
            "default": True,
            "description": "是否在时钟下方显示当前日期"
        },
        {
            "name": "border_style",
            "label": "边框样式",
            "type": "select",
            "options": ["none", "single", "double", "rounded", "bold"],
            "default": "double",
            "description": "时钟边框样式"
        }
    ]
}

# 创建小部件
widget_html = f"""
<div style="font-family: monospace; white-space: pre; text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin: 10px 0;">
<h3 style="margin-bottom: 10px;">ASCII时钟</h3>
<pre style="margin: 0; font-size: 14px; line-height: 1.2;">
{ascii_clock_str}
</pre>
<p style="margin-top: 10px; font-size: 12px; color: #666;">当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
"""

# 定义小部件配置
widget_config = {
    "type": "home-widget",
    "name": "ASCII时钟",
    "position": "sidebar",
    "priority": 50,
    "html": widget_html,
    "refresh_interval": 10  # 每10秒刷新一次
}

# 输出结果
result = f"""
# ASCII时钟

```
{ascii_clock_str}
```

当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}

## 小部件配置

此插件也提供了一个前端小部件，可以在博客侧边栏显示实时ASCII时钟。

```json
{json.dumps(widget_config, ensure_ascii=False, indent=2)}
```
""" 