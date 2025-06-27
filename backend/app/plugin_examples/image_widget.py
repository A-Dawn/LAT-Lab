# 图片小部件插件示例
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
"""