import sys
import os
import uvicorn

# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将backend目录添加到Python路径
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True) 