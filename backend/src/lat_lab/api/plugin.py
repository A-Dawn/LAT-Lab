from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import subprocess
import tempfile
import os
import importlib.util
import sys
from src.lat_lab.schemas.plugin import (
    Plugin, PluginCreate, PluginUpdate, PluginDetail
)
from src.lat_lab.crud.plugin import (
    get_plugin, get_plugin_by_name, get_plugins, get_plugin_detail,
    create_plugin, update_plugin, delete_plugin, activate_plugin
)
from src.lat_lab.core.deps import get_db, get_current_admin_user, get_current_user
from src.lat_lab.core.rate_limiter import create_rate_limit_dependency
from src.lat_lab.models.user import User
from src.lat_lab.core.config import settings
from src.lat_lab.utils.security import secure_filename
from datetime import datetime

router = APIRouter(prefix="/plugins", tags=["plugins"])

# 插件运行速率限制依赖
plugin_run_rate_limit = create_rate_limit_dependency(
    "plugin_run", 
    settings.RATE_LIMIT_PLUGIN_REQUESTS, 
    settings.RATE_LIMIT_PLUGIN_WINDOW
)

# 示例插件相关路由应该放在具体ID路由之前
@router.get("/examples", response_model=List[Dict[str, str]])
def list_example_plugins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """列出所有示例插件（仅管理员）"""
    # 检查插件示例目录是否存在
    if not os.path.exists(settings.PLUGIN_EXAMPLES_DIR):
        # 尝试创建目录
        try:
            os.makedirs(settings.PLUGIN_EXAMPLES_DIR, exist_ok=True)
            # 尝试初始化示例
            try:
                init_examples_path = os.path.join(os.path.dirname(settings.PLUGIN_EXAMPLES_DIR), "init_examples.py")
                if os.path.exists(init_examples_path):
                    spec = importlib.util.spec_from_file_location("init_examples", init_examples_path)
                    if spec and spec.loader:
                        init_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(init_module)
                        if hasattr(init_module, "init_examples"):
                            init_module.init_examples()
            except Exception as e:
                print(f"初始化插件示例失败: {e}")
        except Exception:
            return []
        
        # 如果目录仍然不存在，返回空列表
        if not os.path.exists(settings.PLUGIN_EXAMPLES_DIR):
            return []
    
    examples = []
    
    # 遍历目录获取所有.py文件
    for filename in os.listdir(settings.PLUGIN_EXAMPLES_DIR):
        if filename.endswith('.py'):
            example_name = filename[:-3]  # 去掉.py后缀
            # 使用安全的文件名
            safe_example_name = secure_filename(example_name)
            example_path = os.path.join(settings.PLUGIN_EXAMPLES_DIR, filename)
            
            # 读取文件前几行获取描述
            description = ""
            try:
                with open(example_path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        if i >= 10:  # 只读取前10行
                            break
                        if line.startswith('#'):
                            if description:
                                description += " "
                            description += line[1:].strip()
                        elif line.strip() and not line.startswith('#'):
                            break
            except UnicodeDecodeError:
                # 尝试使用不同编码
                try:
                    with open(example_path, 'r', encoding='latin1') as f:
                        content = f.read()
                        # 将内容重新写入文件，确保UTF-8编码
                        with open(example_path, 'w', encoding='utf-8') as fw:
                            fw.write(content)
                        
                        # 重新提取描述
                        for i, line in enumerate(content.split('\n')):
                            if i >= 10:  # 只读取前10行
                                break
                            if line.startswith('#'):
                                if description:
                                    description += " "
                                description += line[1:].strip()
                            elif line.strip() and not line.startswith('#'):
                                break
                except Exception:
                    description = "无法读取描述"
            except Exception:
                description = "无法读取描述"
            
            examples.append({
                "name": safe_example_name,
                "description": description
            })
    
    # 添加README
    readme_path = os.path.join(settings.PLUGIN_EXAMPLES_DIR, "README.md")
    if os.path.exists(readme_path):
        examples.append({
            "name": "README",
            "description": "插件系统使用和开发说明"
        })
    
    return examples

@router.get("/examples/{example_name}", response_model=Dict[str, Any])
def get_example_plugin(
    example_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取示例插件（仅管理员）"""
    # 检查插件示例目录是否存在
    if not os.path.exists(settings.PLUGIN_EXAMPLES_DIR):
        # 尝试创建目录
        try:
            os.makedirs(settings.PLUGIN_EXAMPLES_DIR, exist_ok=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail="无法创建插件示例目录")
        raise HTTPException(status_code=404, detail="插件示例目录不存在")
    
    # 构建示例文件路径
    # 移除可能存在的.py后缀
    example_name = example_name.replace('.py', '')
    # 应用安全验证
    safe_example_name = secure_filename(example_name)
    example_path = os.path.join(settings.PLUGIN_EXAMPLES_DIR, f"{safe_example_name}.py")
    
    # 检查示例文件是否存在
    if not os.path.exists(example_path):
        # 如果找不到指定的示例，返回README
        if safe_example_name.lower() == "readme":
            readme_path = os.path.join(settings.PLUGIN_EXAMPLES_DIR, "README.md")
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return {
                        "name": "插件开发指南",
                        "description": "插件系统使用和开发说明",
                        "code": content
                    }
                except UnicodeDecodeError:
                    # 尝试使用不同编码
                    try:
                        with open(readme_path, 'r', encoding='latin1') as f:
                            content = f.read()
                            # 将内容重新写入文件，确保UTF-8编码
                            with open(readme_path, 'w', encoding='utf-8') as fw:
                                fw.write(content)
                        return {
                            "name": "插件开发指南",
                            "description": "插件系统使用和开发说明",
                            "code": content
                        }
                    except Exception as e:
                        raise HTTPException(status_code=500, detail="读取README文件失败")
        
        # 显示可用的示例插件列表
        available_examples = []
        try:
            for filename in os.listdir(settings.PLUGIN_EXAMPLES_DIR):
                if filename.endswith('.py'):
                    available_examples.append(filename[:-3])  # 去掉.py后缀
        except Exception:
            available_examples = []
        
        examples_str = ", ".join(available_examples) if available_examples else "无"
        raise HTTPException(
            status_code=404, 
            detail=f"插件示例 '{example_name}' 不存在。可用示例: {examples_str}"
        )
    
    # 读取示例文件内容
    try:
        with open(example_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except UnicodeDecodeError:
        # 尝试使用不同编码
        try:
            with open(example_path, 'r', encoding='latin1') as f:
                code = f.read()
                # 将内容重新写入文件，确保UTF-8编码
                with open(example_path, 'w', encoding='utf-8') as fw:
                    fw.write(code)
        except Exception as e:
            raise HTTPException(status_code=500, detail="读取插件文件失败")
    
    # 解析插件描述（从注释中提取）
    description = ""
    lines = code.split('\n')
    for line in lines[:10]:  # 只查看前10行
        if line.startswith('#'):
            if description:
                description += " "
            description += line[1:].strip()
        elif line.strip() and not line.startswith('#'):
            break
    
    return {
        "name": f"示例插件 - {example_name}",
        "description": description,
        "code": code
    }

@router.get("/", response_model=List[Plugin])
async def read_plugins(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有插件（仅管理员）或获取激活的插件（所有用户）"""
    # 如果不是请求激活的插件，检查用户是否为管理员
    if not active_only and current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以查看所有插件"
        )
    
    return get_plugins(db, skip=skip, limit=limit, active_only=active_only)

@router.get("/{plugin_id}", response_model=Plugin)
def read_plugin(
    plugin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取插件详情（激活的插件所有用户可见，未激活插件仅管理员可见）"""
    db_plugin = get_plugin(db, plugin_id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="插件不存在")
    
    # 如果插件未激活且用户不是管理员，则返回403
    if not db_plugin.is_active and current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以查看未激活的插件"
        )
    
    return db_plugin

@router.post("/", response_model=Plugin)
def create_new_plugin(
    plugin: PluginCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建插件（仅管理员）"""
    # 检查插件名是否已存在
    if get_plugin_by_name(db, plugin.name):
        raise HTTPException(status_code=400, detail="插件名已存在")
    
    return create_plugin(db, plugin, current_user.id)

@router.put("/{plugin_id}", response_model=Plugin)
def update_plugin_by_id(
    plugin_id: int,
    plugin_update: PluginUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新插件（仅管理员）"""
    db_plugin = get_plugin(db, plugin_id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="插件不存在")
    
    return update_plugin(db, plugin_id, plugin_update)

@router.delete("/{plugin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plugin_by_id(
    plugin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除插件（仅管理员）"""
    db_plugin = get_plugin(db, plugin_id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="插件不存在")
    
    delete_plugin(db, plugin_id)
    return None

@router.post("/{plugin_id}/activate", response_model=Plugin)
def activate_plugin_by_id(
    plugin_id: int,
    activate: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """激活/停用插件（仅管理员）"""
    db_plugin = get_plugin(db, plugin_id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="插件不存在")
    
    return activate_plugin(db, plugin_id, activate)

@router.post("/{plugin_id}/run", response_model=Dict[str, Any])
async def run_plugin(
    plugin_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    params: Dict[str, Any] = {},
    _rate_limit: bool = Depends(plugin_run_rate_limit)
):
    """运行插件（所有用户可运行激活的插件，未激活插件仅管理员可运行）"""
    # 避免可变默认值造成的副作用
    params = params or {}
    db_plugin = get_plugin(db, plugin_id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="插件不存在")
    
    # 如果插件未激活，检查用户权限
    if not db_plugin.is_active and current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以运行未激活的插件"
        )
    
    # 已由权限检查控制未激活插件的运行权限
    if False and not db_plugin.is_active:
        raise HTTPException(status_code=400, detail="插件未激活，无法运行")
    
    # 创建临时文件
    temp_path = ""
    wrapper_path = ""
    
    try:
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as temp:
            temp_path = temp.name
            
            # 如果有参数，将参数添加到代码中
            plugin_code = db_plugin.code
            if params:
                param_lines = []
                for key, value in params.items():
                        param_lines.append(f"{key} = {repr(value)}")
                
                # 将参数添加到代码顶部
                param_code = "\n".join(param_lines)
                plugin_code = param_code + "\n\n" + plugin_code
                
                # 打印调试信息
                print(f"插件参数: {params}")
            
            temp.write(plugin_code)
        
        # 在沙箱中运行插件
        if settings.PLUGIN_SANDBOX_ENABLED:
            # 创建一个包装脚本，安全地执行插件并捕获结果
            wrapper_code = """# -*- coding: utf-8 -*-
import os
import sys
import json
import traceback
import types

# 确保使用UTF-8编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加当前目录到路径以便导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 首先打印出参数和环境信息，用于调试（写入stderr，避免污染插件输出）
print("Python版本:", sys.version, file=sys.stderr)
print("参数:", sys.argv, file=sys.stderr)
print("当前目录:", os.getcwd(), file=sys.stderr)
print("文件目录:", os.path.dirname(os.path.abspath(__file__)), file=sys.stderr)
print("模块路径:", sys.path, file=sys.stderr)

# 从环境变量中安全获取prompt参数
plugin_prompt = os.environ.get('PLUGIN_PROMPT', '')

# 定义安全的标准库白名单（仅限安全子集）
SAFE_MODULES = [
    'datetime', 'json', 'base64', 'hashlib', 'math', 
    'random', 're', 'time', 'uuid',
    'collections', 'io', 'string'
]

# 创建安全的执行环境
safe_globals = dict()

# 定义受限的内置函数集合
safe_builtins = {}

# 添加安全的内置函数
for name in ['abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytes', 'chr', 
            'complex', 'dict', 'dir', 'divmod', 'enumerate', 'filter', 
            'float', 'format', 'frozenset', 'hash', 'hex', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'map', 'max', 'min', 'next',
            'object', 'oct', 'ord', 'pow', 'print', 'range', 'repr', 'reversed',
            'round', 'set', 'slice', 'sorted', 'str', 'sum', 'tuple', 'type', 'zip']:
    try:
        if isinstance(__builtins__, dict):
            if name in __builtins__:
                safe_builtins[name] = __builtins__[name]
        else:
            if hasattr(__builtins__, name):
                safe_builtins[name] = getattr(__builtins__, name)
    except (AttributeError, KeyError):
        pass

# 实现受限导入：仅允许白名单模块和伪 requests
_allowed_modules = set([m.split('.')[0] for m in SAFE_MODULES])
_allowed_modules.add('requests')

class SafeRequests:
    def __init__(self):
        try:
            import requests as real_requests
            self._requests = real_requests
        except Exception:
            self._requests = None
    def get(self, url, **kwargs):
        if not self._requests:
            return {"error": "requests模块不可用"}
        try:
            allowed_domains = ['api.openweathermap.org', 'api.openrouter.ai', 'picsum.photos']
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            if not any(allowed_domain in domain for allowed_domain in allowed_domains):
                return {"error": "不允许访问域名: " + domain}
            if 'timeout' not in kwargs:
                kwargs['timeout'] = 3
            response = self._requests.get(url, **kwargs)
            return response
        except Exception as e:
            return {"error": str(e)}
    def post(self, url, **kwargs):
        if not self._requests:
            return {"error": "requests模块不可用"}
        try:
            allowed_domains = ['api.openrouter.ai']
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            if not any(allowed_domain in domain for allowed_domain in allowed_domains):
                return {"error": "不允许访问域名: " + domain}
            if 'timeout' not in kwargs:
                kwargs['timeout'] = 3
            response = self._requests.post(url, **kwargs)
            return response
        except Exception as e:
            return {"error": str(e)}

_safe_requests = SafeRequests()
SafeRequestsModule = types.SimpleNamespace(get=_safe_requests.get, post=_safe_requests.post)

def _restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    root = name.split('.')[0]
    if root == 'requests':
        return SafeRequestsModule
    if root not in _allowed_modules:
        raise ImportError("模块不允许导入: " + root)
    return __import__(name, globals, locals, fromlist, level)

# 将受限导入注入内置
safe_builtins['__import__'] = _restricted_import

# 将安全内置注入执行环境
safe_globals['__builtins__'] = safe_builtins

# 预加载安全模块到全局（便于直接使用）
for module_name in SAFE_MODULES:
    try:
        if '.' in module_name:
            package, submodule = module_name.split('.', 1)
            module = __import__(package, fromlist=[submodule])
            safe_module = getattr(module, submodule)
        else:
            safe_module = __import__(module_name)
        safe_globals[module_name.split('.')[-1]] = safe_module
    except ImportError:
        pass

# 也提供一个 requests 变量（非必需，import 更常见）
safe_globals['requests'] = _safe_requests

# 将prompt参数安全地传递给插件
safe_globals['prompt'] = plugin_prompt

# 执行插件代码
try:
    local_vars = {}
    
    # 读取原始代码文件
    plugin_path = "TEMP_PATH_PLACEHOLDER"
    with open(plugin_path, "r", encoding="utf-8") as code_file:
        plugin_code = code_file.read()
    
    # 执行插件代码
    exec(plugin_code, safe_globals, local_vars)
    
    # 获取结果
    if 'result' in local_vars:
        print(local_vars['result'])
    else:
        print("错误: 插件未定义'result'变量")
except Exception as e:
    # 只输出安全的错误信息，不包含堆栈跟踪
    error_msg = "插件执行错误: " + str(type(e).__name__)
    print(error_msg)
    sys.exit(1)
"""
            
            # 替换临时文件路径，避免使用format和特殊字符
            wrapper_code = wrapper_code.replace("TEMP_PATH_PLACEHOLDER", temp_path.replace("\\", "\\\\"))
            
            # 创建包装器脚本文件
            wrapper_path = temp_path + "_wrapper.py"
            with open(wrapper_path, 'w', encoding='utf-8') as f:
                f.write(wrapper_code)
            
            # 准备运行参数 - 移除不安全的命令行参数传递
            run_args = [sys.executable, wrapper_path]
            
            # 通过环境变量安全传递prompt参数，避免命令行注入
            env = os.environ.copy()
            if 'prompt' in params:
                # 将prompt参数通过环境变量传递，避免命令行注入风险
                env['PLUGIN_PROMPT'] = str(params['prompt'])
            else:
                # 确保环境变量存在，即使没有prompt参数
                env['PLUGIN_PROMPT'] = ''
            
            # 运行包装器脚本
            result = subprocess.run(
                run_args,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=settings.PLUGIN_TIMEOUT_SECONDS,
                env=env
            )
            
            # 删除包装器脚本
            try:
                if os.path.exists(wrapper_path):
                    os.unlink(wrapper_path)
            except:
                pass
            
            if result.returncode != 0:
                # 错误处理
                from src.lat_lab.utils.security import SecurityError
                SecurityError.log_error_safe(
                    Exception(f"插件运行失败，返回码: {result.returncode}"),
                    "plugin_subprocess_execution",
                    {
                        "plugin_id": plugin_id,
                        "return_code": result.returncode,
                        "stderr_length": len(result.stderr) if result.stderr else 0
                    }
                )
                
                raise HTTPException(
                    status_code=500,
                    detail="插件运行失败"
                )
            
            output = result.stdout
            
            # 如果没有输出，记录错误
            if not output.strip():
                output = "警告: 插件没有生成任何输出"
                
        else:
            # 不安全的执行方式，仅用于开发环境
            with open(temp_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # 警告：在生产环境中，永远不要直接执行用户提供的代码
            # 这里仅作为示例，实际应该使用更安全的沙箱机制
            safe_builtins = {}
            
            # 获取安全内置函数
            for name in ['abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytes', 'chr', 
                        'complex', 'dict', 'dir', 'divmod', 'enumerate', 'filter', 
                        'float', 'format', 'frozenset', 'hash', 'hex', 'int', 'isinstance',
                        'issubclass', 'iter', 'len', 'list', 'map', 'max', 'min', 'next',
                        'object', 'oct', 'ord', 'pow', 'print', 'range', 'repr', 'reversed',
                        'round', 'set', 'slice', 'sorted', 'str', 'sum', 'tuple', 'type', 'zip']:
                if isinstance(__builtins__, dict):
                    if name in __builtins__:
                        safe_builtins[name] = __builtins__[name]
                else:
                    if hasattr(__builtins__, name):
                        safe_builtins[name] = getattr(__builtins__, name)
            
            local_vars = {}
            # 允许访问部分安全模块
            global_vars = {'__builtins__': safe_builtins}
            
            # 允许导入一些安全的模块
            for module_name in ['datetime', 'json', 'base64', 'math', 'random', 're']:
                try:
                    module = __import__(module_name)
                    global_vars[module_name] = module
                except ImportError:
                    pass
            
            # 添加prompt参数支持（从环境变量获取）
            if 'prompt' in params:
                global_vars['prompt'] = params['prompt']
            
            # 执行代码
            exec(code, global_vars, local_vars)
            
            if 'result' in local_vars:
                output = str(local_vars.get('result'))
            else:
                output = "警告: 插件没有定义'result'变量"
                
                # 调试信息
                var_names = list(local_vars.keys())
                if var_names:
                    output += "\n\n可用变量: " + ', '.join(var_names)
        
        # 返回结果
        return {"success": True, "output": output}
    
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=500,
            detail="插件执行超时（" + str(settings.PLUGIN_TIMEOUT_SECONDS) + "秒）"
        )
    except Exception as e:
        # 错误处理
        from src.lat_lab.utils.security import SecurityError
        SecurityError.log_and_raise_safe_error(
            error=e,
            user_message="插件执行失败",
            status_code=500,
            context={
                "plugin_id": plugin_id,
                "params_keys": list(params.keys()) if params else [],
                "operation": "plugin_execution"
            }
        )
    finally:
        # 清理临时文件
        for path in [temp_path, wrapper_path]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except:
                    pass

@router.get("/{plugin_id}/detail", response_model=PluginDetail)
def get_plugin_detail_route(
    plugin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取插件详情，包括分类、标签和评论（认证用户）"""
    db_plugin = get_plugin_detail(db, plugin_id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="插件不存在")
    
    # 如果插件未激活且用户不是管理员，则返回403
    if not db_plugin.is_active and current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以查看未激活的插件"
        )
    
    # 如果插件不公开且用户不是管理员或创建者，则返回403
    if not db_plugin.is_public and current_user.role != 'admin' and db_plugin.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您无权查看此插件"
        )
    
    return db_plugin

# 插件市场相关路由
@router.get("/marketplace/info", response_model=Dict[str, Any])
def get_marketplace_info(
    db: Session = Depends(get_db)
):
    """获取插件市场基本信息"""
    try:
        from src.lat_lab.services.marketplace import marketplace_service
        return marketplace_service.get_marketplace_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取插件市场信息失败")

@router.get("/marketplace/categories", response_model=List[Dict[str, Any]])
def get_marketplace_categories(
    db: Session = Depends(get_db)
):
    """获取插件市场分类列表"""
    try:
        from src.lat_lab.services.marketplace import marketplace_service
        return marketplace_service.get_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取插件市场分类失败")

@router.get("/marketplace/tags", response_model=List[str])
def get_marketplace_tags(
    db: Session = Depends(get_db)
):
    """获取插件市场标签列表"""
    try:
        from src.lat_lab.services.marketplace import marketplace_service
        return marketplace_service.get_tags()
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取插件市场标签失败")

@router.get("/marketplace/plugins", response_model=List[Dict[str, Any]])
def get_marketplace_plugins(
    db: Session = Depends(get_db),
    category_id: Optional[int] = None,
    tags: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取插件市场插件列表（支持筛选）"""
    try:
        from src.lat_lab.services.marketplace import marketplace_service
        
        # 处理标签字符串
        tag_list = tags.split(",") if tags else None
        
        # 获取插件列表
        plugins = marketplace_service.get_plugins(
            category_id=category_id,
            tags=tag_list,
            search_term=search,
            featured=featured
        )
        
        # 分页
        total = len(plugins)
        plugins = plugins[skip:min(skip+limit, total)]
        
        return plugins
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取插件市场插件列表失败")

@router.get("/marketplace/plugins/{plugin_id}", response_model=Dict[str, Any])
def get_marketplace_plugin(
    plugin_id: str,
    db: Session = Depends(get_db)
):
    """获取插件市场插件详情"""
    try:
        from src.lat_lab.services.marketplace import marketplace_service
        plugin = marketplace_service.get_plugin_by_id(plugin_id)
        
        if not plugin:
            raise HTTPException(status_code=404, detail=f"插件ID '{plugin_id}' 不存在")
        
        return plugin
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取插件市场插件详情失败")

@router.post("/marketplace/plugins/{plugin_id}/download", response_model=Dict[str, Any])
def download_marketplace_plugin(
    plugin_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """下载/安装插件市场插件（仅管理员）"""
    try:
        from src.lat_lab.services.marketplace import marketplace_service
        plugin = marketplace_service.get_plugin_by_id(plugin_id)
        
        if not plugin:
            raise HTTPException(status_code=404, detail=f"插件ID '{plugin_id}' 不存在")
        
        # 检查插件是否已存在
        existing_plugin = get_plugin_by_name(db, plugin["name"])
        if existing_plugin:
            raise HTTPException(status_code=400, detail=f"插件 '{plugin['name']}' 已存在，请先删除或重命名")
        
        # 获取插件代码（从readme或配置中提取示例代码）
        plugin_code = plugin.get("readme", "# " + plugin["name"] + "\n" + plugin["description"])
        
        # 创建插件
        new_plugin = {
            "name": plugin["name"],
            "description": plugin["description"],
            "code": plugin_code,
            "version": plugin.get("version", "1.0.0"),
            "is_public": True
        }
        
        from src.lat_lab.schemas.plugin import PluginCreate
        plugin_create = PluginCreate(**new_plugin)
        
        # 创建插件实例
        created_plugin = create_plugin(db, plugin_create, current_user.id)
        
        return {
            "success": True,
            "message": f"插件 '{plugin['name']}' 已安装成功",
            "plugin_id": created_plugin.id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="下载/安装插件失败") 

@router.get("/marketplace/source", response_model=Dict[str, Any])
def get_marketplace_source(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取插件市场数据源设置（仅管理员）"""
    try:
        return {
            "source": settings.PLUGIN_MARKETPLACE_SOURCE,
            "local_path": str(settings.PLUGIN_MARKETPLACE_LOCAL_PATH),
            "git_repo": settings.PLUGIN_MARKETPLACE_GIT_REPO,
            "git_branch": settings.PLUGIN_MARKETPLACE_GIT_BRANCH
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取数据源信息失败")

@router.post("/marketplace/source", response_model=Dict[str, Any])
def update_marketplace_source(
    source_settings: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新插件市场数据源设置（仅管理员）"""
    try:
        # 获取设置参数
        source = source_settings.get("source")
        git_repo = source_settings.get("git_repo")
        git_branch = source_settings.get("git_branch", "main")
        
        if source not in ["local", "git"]:
            raise HTTPException(status_code=400, detail="无效的数据源类型，支持的类型: local, git")
        
        # 更新设置
        settings.PLUGIN_MARKETPLACE_SOURCE = source
        
        if source == "git" and not git_repo:
            raise HTTPException(status_code=400, detail="使用Git数据源时必须提供仓库地址")
        
        settings.PLUGIN_MARKETPLACE_GIT_REPO = git_repo or ""
        settings.PLUGIN_MARKETPLACE_GIT_BRANCH = git_branch
        
        # 返回更新后的设置
        return {
            "success": True,
            "message": "数据源设置已更新",
            "source": source,
            "git_repo": git_repo,
            "git_branch": git_branch
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="更新数据源设置失败")

@router.post("/marketplace/refresh", response_model=Dict[str, Any])
def refresh_marketplace(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """刷新插件市场数据（仅管理员）"""
    try:
        import json
        import os
        
        # 读取JSON配置文件
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "marketplace_config.json")
        
        if not os.path.exists(config_path):
            raise HTTPException(status_code=404, detail="插件市场配置文件不存在")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 更新时间戳
        if "marketplace_info" in config:
            config["marketplace_info"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            
            # 保存更新后的配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        return {
            "success": True,
            "message": "插件市场数据已刷新",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="刷新插件市场数据失败") 