# LAT-Lab 插件示例

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
