from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.api import user, auth, article, category, comment, plugin, rss, upload, tag
from app.core.config import settings
from app.models.user import Base
from app.core.database import engine

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 确保上传目录存在
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="个人博客系统API"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 创建一个API子应用
api_app = FastAPI(
    title=settings.PROJECT_NAME + " API",
    version=settings.VERSION,
    description="个人博客系统API"
)

# 注册路由到API子应用
api_app.include_router(auth.router)
api_app.include_router(user.router)
api_app.include_router(article.router)
api_app.include_router(category.router)
api_app.include_router(comment.router)
api_app.include_router(plugin.router)
api_app.include_router(rss.router)
api_app.include_router(upload.router)
api_app.include_router(tag.router)
api_app.include_router(tag.public_router)

# 将API子应用挂载到主应用的/api路径下
app.mount("/api", api_app)

@app.get("/api/health")
def health_check():
    """健康检查接口"""
    return {"status": "ok"}

@app.get("/")
def root():
    """API根路径重定向到文档"""
    return {"message": "Welcome to LAT-Lab API! Visit /docs for API documentation."} 