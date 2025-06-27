# LAT-Lab 插件辅助函数库
# 这个文件提供了插件可能需要的通用功能和工具
# 在沙箱环境中可以安全使用的功能

import json
import base64
import datetime

# 网络请求功能已由安全沙箱提供，使用 requests 直接调用

# 简单的日志功能
def log_info(message):
    """记录信息日志"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[INFO {now}] {message}"

def log_error(message):
    """记录错误日志"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[ERROR {now}] {message}"

# 创建小部件工具函数
def create_widget(name, html_content, position="sidebar", priority=100):
    """创建一个小部件配置对象
    
    参数:
        name (str): 小部件名称
        html_content (str): 小部件HTML内容
        position (str): 小部件位置 (sidebar, top, bottom, left, right)
        priority (int): 显示优先级 (数字越小越优先)
        
    返回:
        dict: 小部件配置对象
    """
    return {
        "type": "home-widget",
        "name": name,
        "position": position,
        "priority": priority,
        "html": html_content
    }

# 生成Markdown输出
def create_markdown_output(content, widget_config=None):
    """生成Markdown格式的插件输出
    
    参数:
        content (str): Markdown格式的内容
        widget_config (dict, optional): 小部件配置对象
        
    返回:
        str: 完整的Markdown格式输出
    """
    output = content
    
    # 如果提供了小部件配置，添加到输出中
    if widget_config:
        output += "\n\n## 前端小部件配置\n\n```json\n"
        output += json.dumps(widget_config, ensure_ascii=False, indent=2)
        output += "\n```"
    
    return output

# Base64图片工具
def encode_image_base64(image_bytes):
    """将图片数据编码为base64
    
    参数:
        image_bytes (bytes): 图片二进制数据
        
    返回:
        str: base64编码的图片数据URI
    """
    base64_data = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:image/png;base64,{base64_data}"

# 创建示例图片
def create_sample_image(width=100, height=100, color=(0, 0, 255)):
    """创建一个简单的纯色示例图片
    
    参数:
        width (int): 图片宽度(像素)
        height (int): 图片高度(像素)
        color (tuple): RGB颜色值
        
    返回:
        str: base64编码的图片数据URI
    """
    try:
        from PIL import Image
        img = Image.new('RGB', (width, height), color)
        import io
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return encode_image_base64(img_bytes.getvalue())
    except ImportError:
        # 如果没有PIL库，创建一个1x1像素的图片
        return encode_image_base64(bytes(color)) 