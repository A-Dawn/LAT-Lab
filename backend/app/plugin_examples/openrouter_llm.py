# OpenRouter LLM API 调用插件
# 此插件提供与OpenRouter API的集成，可访问各种大语言模型

import json
import requests
import sys

# 直接设置API密钥（无需环境变量）
API_KEY = "sk-or-v1-xxxxxxx"

# 没有API密钥时启用演示模式
DEMO_MODE = not API_KEY

# 默认参数
DEFAULT_PROMPT = "介绍一下自己"
DEFAULT_MODEL = "google/gemini-pro"

# 获取前端传递的参数
# 调试语句: 打印全局变量，帮助排查问题
debug_info = f"全局变量: {str(list(globals().keys()))}\n"

# 尝试多种可能的方式获取prompt参数
prompt = None
model = DEFAULT_MODEL

# 1. 直接从全局变量中获取
if 'prompt' in globals():
    prompt = globals().get('prompt')
    debug_info += f"从全局变量获取prompt: '{prompt}'\n"

# 2. 从args参数中获取
try:
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        debug_info += f"从命令行参数获取prompt: '{prompt}'\n"
except:
    debug_info += "尝试获取命令行参数时出错\n"

# 3. 如果仍然没有找到prompt，使用默认值
if not prompt:
    debug_info += f"使用默认prompt: '{DEFAULT_PROMPT}'\n"
    prompt = DEFAULT_PROMPT

# 同样尝试获取model参数
if 'model' in globals():
    model = globals().get('model')
    debug_info += f"获取model参数: '{model}'\n"

# 生成响应
response_text = ""
if DEMO_MODE:
    # 演示模式的固定回复
    response_text = f"这是一个演示模式回复。你询问了: '{prompt}'。请配置API密钥后使用实际功能。"
else:
    try:
        # 请求OpenRouter API
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "HTTP-Referer": "http://localhost:8000"  # 本地开发环境
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "你是LAT-Lab系统的AI助手，请用中文回答问题。"},
                {"role": "user", "content": prompt}
            ]
        }
        
        # 发送请求并处理响应
        response = requests.post(url, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            response_text = result["choices"][0]["message"]["content"]
        else:
            response_text = f"API请求失败: HTTP {response.status_code}\n{response.text}"
            
    except Exception as e:
        response_text = f"发生错误: {str(e)}"

# 构建HTML显示
html_widget = f"""
<div style="font-family: Arial, sans-serif; padding: 15px; border: 1px solid #eee; border-radius: 5px;">
  <h3 style="margin-top: 0; color: #1a73e8;">AI助手</h3>
  
  <div style="margin-bottom: 10px; padding: 8px; background-color: {('#ffebee' if DEMO_MODE else '#e8f5e9')}; 
    border-radius: 4px; font-size: 12px;">
    状态: {('演示模式' if DEMO_MODE else '已连接')}
  </div>
  
  <div style="background-color: #f5f5f5; padding: 12px; border-radius: 4px; 
    white-space: pre-wrap; font-size: 14px;">
    {response_text}
  </div>
</div>
"""

# 最终结果输出
result = f"""
# OpenRouter LLM API 调用结果

## 调试信息
{debug_info}

## 请求信息
- 模型: {model}
- 提示词: "{prompt}"
- 演示模式: {"是" if DEMO_MODE else "否"}
- API密钥: {"未配置" if DEMO_MODE else "已配置"}

## 生成内容
{response_text}

## 使用说明
此插件通过OpenRouter API访问各种大语言模型。

- API密钥已在代码中直接配置
- 支持的参数：prompt (问题), model (模型ID)

## 前端显示预览
```html
{html_widget}
```
"""
