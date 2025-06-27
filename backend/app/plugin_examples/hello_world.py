# 这是一个简单的Hello World示例插件
# 插件可以执行各种任务，例如数据处理、生成报告等
# 插件将在沙箱环境中执行，有一定的安全限制

# 你可以导入标准库
import datetime

# 获取当前时间
now = datetime.datetime.now()

# 创建一个简单的输出
result = f"""
Hello, LAT-Lab World!
===================

这是一个简单的插件示例，演示如何创建一个基本的插件。
插件可以执行各种操作，并将结果返回给博客系统。

当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}
"""

# 插件必须将结果存储在名为 "result" 的变量中
# result 变量的值将作为插件的输出返回