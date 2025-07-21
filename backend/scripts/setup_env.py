#!/usr/bin/env python3
"""
LAT-LAB 项目环境设置脚本
- 创建虚拟环境
- 安装UV包管理工具
- 安装项目依赖
"""
import os
import subprocess
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
VENV_DIR = PROJECT_ROOT / ".venv"


def run_command(command, check=True):
    """运行shell命令"""
    print(f"执行: {' '.join(command)}")
    return subprocess.run(command, check=check)


def create_venv():
    """创建虚拟环境"""
    if VENV_DIR.exists():
        print(f"虚拟环境已存在: {VENV_DIR}")
        return
    
    print(f"创建虚拟环境: {VENV_DIR}")
    run_command([sys.executable, "-m", "venv", str(VENV_DIR)])


def install_uv():
    """安装UV包管理工具"""
    # 获取虚拟环境中的pip路径
    if os.name == "nt":  # Windows
        pip_path = VENV_DIR / "Scripts" / "pip"
    else:  # Unix/Linux/MacOS
        pip_path = VENV_DIR / "bin" / "pip"
    
    # 安装uv
    print("安装UV包管理工具...")
    run_command([str(pip_path), "install", "uv"])
    
    # 获取UV路径
    if os.name == "nt":  # Windows
        uv_path = VENV_DIR / "Scripts" / "uv"
    else:  # Unix/Linux/MacOS
        uv_path = VENV_DIR / "bin" / "uv"
    
    return uv_path


def install_dependencies(uv_path):
    """使用UV安装项目依赖"""
    print("安装项目依赖...")
    run_command([str(uv_path), "pip", "install", "-e", "."])
    run_command([str(uv_path), "pip", "install", "-e", ".[dev]"])


def main():
    """主函数"""
    print("=== LAT-LAB 环境设置 ===")
    
    # 创建虚拟环境
    create_venv()
    
    # 安装UV
    uv_path = install_uv()
    
    # 安装依赖
    install_dependencies(uv_path)
    
    print("\n=== 环境设置完成! ===")
    print(f"虚拟环境位置: {VENV_DIR}")
    
    # 输出激活命令提示
    if os.name == "nt":  # Windows
        activate_cmd = f"{VENV_DIR}\\Scripts\\activate"
    else:  # Unix/Linux/MacOS
        activate_cmd = f"source {VENV_DIR}/bin/activate"
    
    print(f"\n要激活虚拟环境，请运行:\n{activate_cmd}")


if __name__ == "__main__":
    main()