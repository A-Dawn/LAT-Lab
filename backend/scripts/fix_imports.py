#!/usr/bin/env python3
"""
修复导入路径脚本
用于将项目中的所有Python文件中的导入路径从'app.'替换为'src.lat_lab.'，从'lat_lab.'替换为'src.lat_lab.'
"""
import os
import re
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SRC_DIR = PROJECT_ROOT / "src"

def fix_imports(file_path):
    """修复文件中的导入路径"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换导入路径
    modified_content = re.sub(r'from\s+app\.', 'from src.lat_lab.', content)
    modified_content = re.sub(r'import\s+app\.', 'import src.lat_lab.', modified_content)
    
    # 替换lat_lab导入路径（但不替换已经是src.lat_lab的路径）
    modified_content = re.sub(r'from\s+lat_lab\.', 'from src.lat_lab.', modified_content)
    modified_content = re.sub(r'import\s+lat_lab\.', 'import src.lat_lab.', modified_content)
    
    # 避免重复替换
    modified_content = modified_content.replace('from src.src.lat_lab.', 'from src.lat_lab.')
    modified_content = modified_content.replace('import src.src.lat_lab.', 'import src.lat_lab.')
    
    # 如果内容有变化，写回文件
    if content != modified_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        return True
    return False

def process_directory(directory):
    """处理目录中的所有Python文件"""
    modified_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_imports(file_path):
                    modified_files.append(os.path.relpath(file_path, PROJECT_ROOT))
    
    return modified_files

def main():
    """主函数"""
    print("开始修复导入路径...")
    
    modified_files = process_directory(SRC_DIR)
    
    print(f"修复完成，共修改了 {len(modified_files)} 个文件:")
    for file in modified_files:
        print(f"  - {file}")

if __name__ == "__main__":
    main() 