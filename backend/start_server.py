#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
启动脚本
用于一键启动LAT-Lab博客系统的服务
"""

import subprocess
import os
import time
import sys
import threading
import signal
import platform

def is_windows():
    return platform.system().lower() == 'windows'

# 当前目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 进程列表，用于优雅关闭
processes = []

def run_command(cmd, cwd=None):
    """运行命令，返回进程对象"""
    if is_windows():
        # Windows系统使用shell=True
        process = subprocess.Popen(cmd, shell=True, cwd=cwd)
    else:
        # Linux/Mac系统
        process = subprocess.Popen(cmd, shell=True, cwd=cwd)
    
    processes.append(process)
    return process

def start_backend():
    """启动后端服务"""
    print("\n正在启动后端服务...")
    
    # 配置命令
    cmd = "python -m src.lat_lab.main"
    
    # 执行命令
    process = run_command(cmd, cwd=BASE_DIR)
    
    # 等待服务启动
    print("等待后端服务启动...")
    time.sleep(3)
    
    return process

def cleanup(signum=None, frame=None):
    """清理进程，优雅退出"""
    print("\n正在关闭服务...")
    
    for process in processes:
        if process.poll() is None:  # 如果进程还在运行
            try:
                if is_windows():
                    # Windows下使用taskkill强制结束进程树
                    subprocess.call(f'taskkill /F /T /PID {process.pid}', shell=True)
                else:
                    # Linux/Mac下发送SIGTERM信号
                    process.terminate()
                    process.wait(timeout=5)
            except Exception as e:
                print(f"关闭进程时出错: {e}")
    
    print("所有服务已关闭")
    sys.exit(0)

def main():
    """主函数"""
    print("=" * 60)
    print("LAT-Lab博客系统启动脚本")
    print("=" * 60)
    print(f"当前工作目录: {os.getcwd()}")
    print(f"脚本目录: {BASE_DIR}")
    print("")
    
    # 检查虚拟环境
    if not os.environ.get("VIRTUAL_ENV"):
        print("警告: 未检测到激活的虚拟环境。建议在虚拟环境中运行此脚本。")
        print("您可以使用以下命令激活虚拟环境:")
        if is_windows():
            print("  .venv\\Scripts\\activate")
        else:
            print("  source .venv/bin/activate")
        
        proceed = input("是否继续? (y/n): ")
        if proceed.lower() != 'y':
            print("已取消启动")
            return
    
    # 注册信号处理器，用于优雅退出
    if not is_windows():
        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)
    
    try:
        # 启动后端
        backend_process = start_backend()
        print("后端服务已启动")
        print("API文档: http://localhost:8000/docs")
        
        print("\n服务已启动，按Ctrl+C停止服务")
        
        # 等待进程结束
        while True:
            if backend_process.poll() is not None:
                print("后端服务已停止")
                break
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n接收到关闭信号")
    finally:
        cleanup()

if __name__ == "__main__":
    main() 