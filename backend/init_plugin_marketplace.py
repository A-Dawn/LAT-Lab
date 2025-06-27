#!/usr/bin/env python3
"""
初始化插件市场的示例数据
"""

import os
import sys
import logging
from sqlalchemy.exc import IntegrityError
from app.core.database import SessionLocal
from app.models.plugin import PluginCategory, PluginTag, Plugin
from app.models.user import User

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_categories(db):
    """初始化插件分类"""
    categories = [
        {"name": "工具", "description": "实用工具类插件"},
        {"name": "增强", "description": "增强博客功能的插件"},
        {"name": "数据分析", "description": "数据处理和分析类插件"},
        {"name": "AI 与机器学习", "description": "人工智能和机器学习相关插件"},
        {"name": "外部集成", "description": "与外部服务集成的插件"},
        {"name": "SEO", "description": "搜索引擎优化相关插件"},
        {"name": "安全", "description": "安全增强类插件"},
        {"name": "内容展示", "description": "改进内容展示的插件"},
        {"name": "其他", "description": "其他类型的插件"},
    ]
    
    count = 0
    for category_data in categories:
        try:
            # 检查分类是否已存在
            existing = db.query(PluginCategory).filter_by(name=category_data["name"]).first()
            if existing:
                logger.info(f"分类 '{category_data['name']}' 已存在，跳过")
                continue
            
            # 创建新分类
            category = PluginCategory(**category_data)
            db.add(category)
            db.commit()
            count += 1
            logger.info(f"创建分类: {category_data['name']}")
        except IntegrityError:
            db.rollback()
            logger.warning(f"分类 '{category_data['name']}' 创建失败，可能已存在")
        except Exception as e:
            db.rollback()
            logger.error(f"创建分类 '{category_data['name']}' 时出错: {e}")
    
    logger.info(f"成功创建 {count} 个分类")
    return count

def init_tags(db):
    """初始化插件标签"""
    tags = [
        "ai", "seo", "数据可视化", "文件管理", "社交媒体",
        "安全", "性能优化", "内容处理", "UI增强", "工具",
        "编辑器", "图像处理", "音频", "视频", "统计",
        "备份", "导入导出", "通知", "评论增强", "搜索"
    ]
    
    count = 0
    for tag_name in tags:
        try:
            # 检查标签是否已存在
            existing = db.query(PluginTag).filter_by(name=tag_name).first()
            if existing:
                logger.info(f"标签 '{tag_name}' 已存在，跳过")
                continue
            
            # 创建新标签
            tag = PluginTag(name=tag_name)
            db.add(tag)
            db.commit()
            count += 1
            logger.info(f"创建标签: {tag_name}")
        except IntegrityError:
            db.rollback()
            logger.warning(f"标签 '{tag_name}' 创建失败，可能已存在")
        except Exception as e:
            db.rollback()
            logger.error(f"创建标签 '{tag_name}' 时出错: {e}")
    
    logger.info(f"成功创建 {count} 个标签")
    return count

def init_featured_plugins(db):
    """初始化精选插件"""
    # 获取管理员用户
    admin = db.query(User).filter_by(role="admin").first()
    if not admin:
        logger.error("未找到管理员用户，无法创建精选插件")
        return 0
    
    # 获取分类
    ai_category = db.query(PluginCategory).filter_by(name="AI 与机器学习").first()
    tools_category = db.query(PluginCategory).filter_by(name="工具").first()
    seo_category = db.query(PluginCategory).filter_by(name="SEO").first()
    content_category = db.query(PluginCategory).filter_by(name="内容展示").first()
    
    if not all([ai_category, tools_category, seo_category, content_category]):
        logger.error("未找到所需的插件分类，请先初始化分类")
        return 0
    
    # 精选插件数据
    plugins = [
        {
            "name": "AI 助手",
            "description": "集成OpenAI API，为博客提供智能写作、内容优化和问答功能。支持自动生成文章摘要、标题建议和关键词提取。",
            "code": "# AI 助手插件\n# 集成OpenAI API，提供智能写作和内容优化\n\nimport openai\nimport os\n\n# 这里是示例代码，实际使用时需要配置API密钥\n# openai.api_key = os.getenv('OPENAI_API_KEY')\n\ndef generate_summary(text):\n    \"\"\"生成文本摘要\"\"\"\n    # 实际实现会调用OpenAI API\n    return f\"这是'{text[:30]}...'的AI生成摘要\"\n\n# 测试函数\nresult = generate_summary(\"这是一篇测试文章，用于演示AI助手插件的功能\")\n",
            "category_id": ai_category.id,
            "creator_id": admin.id,
            "is_active": True,
            "is_public": True,
            "featured": True,
            "version": "1.0.0",
            "rating": 4.8,
            "ratings_count": 24,
            "downloads": 156,
            "tags": ["ai", "内容处理", "编辑器"]
        },
        {
            "name": "SEO 优化助手",
            "description": "自动分析文章内容，提供SEO优化建议。检查关键词密度、标题优化、元描述生成，并提供改进建议以提高搜索引擎排名。",
            "code": "# SEO 优化助手插件\n# 提供SEO分析和优化建议\n\ndef analyze_seo(title, content):\n    \"\"\"分析文章的SEO情况\"\"\"\n    word_count = len(content.split())\n    title_length = len(title)\n    \n    analysis = {\n        \"word_count\": word_count,\n        \"title_length\": title_length,\n        \"recommendations\": []\n    }\n    \n    # 添加建议\n    if word_count < 300:\n        analysis[\"recommendations\"].append(\"文章内容过短，建议扩展到至少300词\")\n    \n    if title_length < 5 or title_length > 60:\n        analysis[\"recommendations\"].append(\"标题长度不理想，建议保持在5-60个字符之间\")\n    \n    return analysis\n\n# 测试函数\nresult = analyze_seo(\"测试标题\", \"这是一篇测试文章的内容\")\n",
            "category_id": seo_category.id,
            "creator_id": admin.id,
            "is_active": True,
            "is_public": True,
            "featured": True,
            "version": "1.2.0",
            "rating": 4.5,
            "ratings_count": 18,
            "downloads": 123,
            "tags": ["seo", "内容处理", "统计"]
        },
        {
            "name": "代码高亮增强",
            "description": "为博客文章中的代码块提供语法高亮和格式化功能。支持多种编程语言，提供多种高亮主题，以及代码复制按钮和行号显示。",
            "code": "# 代码高亮增强插件\n# 为文章中的代码块提供语法高亮和格式化\n\ndef enhance_code_blocks(content):\n    \"\"\"增强文章中的代码块\"\"\"\n    # 这里是示例实现\n    # 实际实现会解析Markdown中的代码块并应用高亮\n    return content.replace('```python', '<div class=\"enhanced-code python\">')\\\n                 .replace('```', '</div>')\n\n# 测试函数\nresult = enhance_code_blocks(\"这是一段代码:\\n```python\\nprint('Hello World')\\n```\")\n",
            "category_id": content_category.id,
            "creator_id": admin.id,
            "is_active": True,
            "is_public": True,
            "featured": True,
            "version": "2.0.1",
            "rating": 4.9,
            "ratings_count": 32,
            "downloads": 245,
            "tags": ["编辑器", "UI增强", "内容处理"]
        },
        {
            "name": "自动备份工具",
            "description": "自动定期备份博客数据，包括文章、评论和用户信息。支持导出到本地文件或云存储服务，并提供恢复功能。",
            "code": "# 自动备份工具插件\n# 定期备份博客数据\n\nimport json\nimport datetime\n\ndef create_backup(data):\n    \"\"\"创建数据备份\"\"\"\n    timestamp = datetime.datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n    backup_name = f\"backup_{timestamp}.json\"\n    \n    # 这里是示例实现\n    # 实际实现会将数据保存到文件或云存储\n    backup_data = {\n        \"timestamp\": timestamp,\n        \"data\": data\n    }\n    \n    return json.dumps(backup_data)\n\n# 测试函数\nresult = create_backup({\"test\": \"数据\"})\n",
            "category_id": tools_category.id,
            "creator_id": admin.id,
            "is_active": True,
            "is_public": True,
            "featured": True,
            "version": "1.1.0",
            "rating": 4.7,
            "ratings_count": 15,
            "downloads": 98,
            "tags": ["备份", "工具", "导入导出"]
        }
    ]
    
    count = 0
    for plugin_data in plugins:
        try:
            # 提取标签
            tags_data = plugin_data.pop("tags", [])
            
            # 检查插件是否已存在
            existing = db.query(Plugin).filter_by(name=plugin_data["name"]).first()
            if existing:
                logger.info(f"插件 '{plugin_data['name']}' 已存在，跳过")
                continue
            
            # 创建新插件
            plugin = Plugin(**plugin_data)
            db.add(plugin)
            db.commit()
            
            # 添加标签关系
            for tag_name in tags_data:
                tag = db.query(PluginTag).filter_by(name=tag_name).first()
                if tag:
                    # 使用SQLAlchemy的关系添加标签
                    plugin.tags.append(tag)
            
            db.commit()
            count += 1
            logger.info(f"创建精选插件: {plugin_data['name']}")
        except IntegrityError:
            db.rollback()
            logger.warning(f"插件 '{plugin_data['name']}' 创建失败，可能已存在")
        except Exception as e:
            db.rollback()
            logger.error(f"创建插件 '{plugin_data['name']}' 时出错: {e}")
    
    logger.info(f"成功创建 {count} 个精选插件")
    return count

def main():
    """主函数"""
    logger.info("开始初始化插件市场数据...")
    
    # 创建数据库会话
    db = SessionLocal()
    try:
        # 初始化分类
        categories_count = init_categories(db)
        
        # 初始化标签
        tags_count = init_tags(db)
        
        # 初始化精选插件
        plugins_count = init_featured_plugins(db)
        
        logger.info(f"插件市场初始化完成！创建了 {categories_count} 个分类、{tags_count} 个标签和 {plugins_count} 个精选插件。")
    except Exception as e:
        logger.error(f"初始化过程中发生错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # 确保在正确的目录中运行
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 运行初始化
    main()
