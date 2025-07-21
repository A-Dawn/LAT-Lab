from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from src.lat_lab.models.plugin import Plugin
from src.lat_lab.schemas.plugin import PluginCreate, PluginUpdate

def get_plugin(db: Session, plugin_id: int):
    return db.query(Plugin).filter(Plugin.id == plugin_id).first()

def get_plugin_by_name(db: Session, name: str):
    return db.query(Plugin).filter(Plugin.name == name).first()

def get_plugins(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False):
    query = db.query(Plugin)
    
    if active_only:
        query = query.filter(Plugin.is_active == True)
    
    return query.offset(skip).limit(limit).all()

def create_plugin(db: Session, plugin: PluginCreate, user_id: int):
    db_plugin = Plugin(
        name=plugin.name,
        description=plugin.description,
        code=plugin.code,
        creator_id=user_id,
        version=plugin.version,
        is_public=plugin.is_public
    )
    db.add(db_plugin)
    db.commit()
    db.refresh(db_plugin)
    return db_plugin

def update_plugin(db: Session, plugin_id: int, plugin: PluginUpdate):
    db_plugin = get_plugin(db, plugin_id)
    if not db_plugin:
        return None
    
    # 更新基础字段
    update_data = plugin.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_plugin, key, value)
    
    db.commit()
    db.refresh(db_plugin)
    return db_plugin

def delete_plugin(db: Session, plugin_id: int):
    db_plugin = get_plugin(db, plugin_id)
    if not db_plugin:
        return False
    
    db.delete(db_plugin)
    db.commit()
    return True

def activate_plugin(db: Session, plugin_id: int, active: bool = True):
    db_plugin = get_plugin(db, plugin_id)
    if not db_plugin:
        return None
    
    db_plugin.is_active = active
    db.commit()
    db.refresh(db_plugin)
    return db_plugin

def get_plugin_detail(db: Session, plugin_id: int):
    return db.query(Plugin).filter(Plugin.id == plugin_id).first() 