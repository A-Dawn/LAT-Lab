# 简单计数器插件示例
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
"""