from fastapi import APIRouter

from src.lat_lab.api import user, auth, article, category, comment, plugin, rss, upload, tag, marketplace

api_router = APIRouter()

# 注册所有子路由
api_router.include_router(auth.router, tags=["认证"])
api_router.include_router(user.router, tags=["用户"])
api_router.include_router(article.router, tags=["文章"])
api_router.include_router(category.router, tags=["分类"])
api_router.include_router(comment.router, tags=["评论"])
api_router.include_router(plugin.router, tags=["插件"])
api_router.include_router(rss.router, tags=["RSS"])
api_router.include_router(upload.router, tags=["文件上传"])
api_router.include_router(tag.router, tags=["标签"])
api_router.include_router(tag.public_router, tags=["公共标签"])
api_router.include_router(marketplace.router, tags=["插件市场"]) 