#!/usr/bin/env python
"""
初始化插件示例目录

这个脚本用于手动初始化插件示例目录。
当插件示例无法正常加载时，可以运行此脚本重新生成示例文件。

用法：
    python init_plugin_examples.py
"""

import os
import sys
import traceback
from pathlib import Path

# 获取当前脚本所在目录
current_dir = Path(__file__).parent

# 获取插件示例目录路径
plugin_examples_dir = os.path.join(current_dir, "app", "plugin_examples")

def main():
    """主函数"""
    print("开始初始化插件示例目录...")
    print(f"插件示例目录路径: {plugin_examples_dir}")
    
    try:
        # 确保目录存在
        os.makedirs(plugin_examples_dir, exist_ok=True)
        
        # 导入init_examples函数
        sys.path.append(str(current_dir))
        from app.init_examples import init_examples
        
        # 运行初始化函数
        init_examples()
        
        # 验证文件是否创建成功
        example_files = os.listdir(plugin_examples_dir)
        print(f"创建的示例文件列表: {', '.join(example_files)}")
        
        # 检查文件编码
        for filename in example_files:
            if filename.endswith('.py') or filename.endswith('.md'):
                file_path = os.path.join(plugin_examples_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 检查文件内容是否有效
                        if len(content) > 0:
                            print(f"✓ 文件 {filename} 验证成功 ({len(content)} 字节)")
                        else:
                            print(f"! 警告: 文件 {filename} 内容为空")
                except UnicodeDecodeError:
                    print(f"! 错误: 文件 {filename} 编码有问题，尝试重写...")
                    # 尝试使用不同编码读取并重写
                    try:
                        with open(file_path, 'r', encoding='latin1') as f:
                            content = f.read()
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"  已修复 {filename} 的编码问题")
                    except Exception as e:
                        print(f"  无法修复 {filename} 的编码: {e}")
        
        print("\n初始化成功！插件示例已准备就绪。")
    except Exception as e:
        print(f"初始化失败: {e}")
        traceback.print_exc()
        sys.exit(1)
    
    print("\n现在可以访问插件管理页面，使用'加载示例插件'功能了。")

if __name__ == "__main__":
    main() 