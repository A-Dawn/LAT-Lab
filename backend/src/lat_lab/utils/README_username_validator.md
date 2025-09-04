# 用户名验证工具

## 概述

用户名验证工具用于验证用户名是否符合规范，并阻止使用保留词汇。该工具在用户注册、修改用户名等操作中被使用。

## 功能特性

### 1. 基本格式验证
- 用户名长度必须在3-32个字符之间
- 只能包含字母、数字和下划线
- 不能以数字开头
- 不能以下划线开头或结尾
- 不能包含连续的下划线

### 2. 保留词汇检查
系统禁止使用以下类型的用户名：

#### 管理类词汇
- admin, administrator, root, superuser, super, master, owner, manager
- moderator, mod, operator, op, staff, support, help, service

#### 系统保留词汇
- system, sys, server, host, localhost, local, test, testing, demo
- guest, anonymous, unknown, null, undefined, none, nobody
- api, app, web, www, site, website, portal, platform

#### 技术性词汇
- user, users, account, accounts, login, logout, register, signup
- signin, auth, authentication, authorization, session, token
- password, passwd, pwd, secret, private, public, secure
- database, db, data, config, configuration, settings, preferences
- profile, avatar, image, file, upload, download, media

#### 常见功能词汇
- home, index, main, default, start, welcome, about, contact
- help, faq, support, feedback, report, bug, error, 404, 500
- search, find, browse, view, edit, create, delete, remove
- add, new, old, current, previous, next, back, forward

#### 严重不雅词汇
包含中文和英文的严重不雅词汇，如：
- 傻逼, 狗屎, 混蛋, 王八蛋, 贱人, 婊子, 妓女, 嫖客, 强奸, 轮奸
- fuck, shit, bitch, whore, slut, cunt, dick, cock, pussy
- asshole, bastard, motherfucker, nigger, faggot, dyke, queer

## 使用方式

### 在API中使用

```python
from src.lat_lab.utils.username_validator import validate_username

# 验证用户名
is_valid, error_message = validate_username("new_username")
if not is_valid:
    raise HTTPException(status_code=400, detail=error_message)
```

### 检查是否为保留词汇

```python
from src.lat_lab.utils.username_validator import is_username_reserved

# 检查用户名是否为保留词汇
if is_username_reserved("admin"):
    print("该用户名已被保留")
```

### 获取保留用户名列表

```python
from src.lat_lab.utils.username_validator import get_reserved_usernames

# 获取所有保留用户名
reserved_names = get_reserved_usernames()
```

## 验证规则

1. **完全匹配检查**：只检查用户名是否完全匹配保留词汇，不检查包含关系
2. **大小写不敏感**：验证时会将用户名转换为小写进行比较
3. **统一错误提示**：对于保留词汇，统一提示"该用户名已被保留或禁止注册"

## 应用场景

该验证工具在以下API端点中被使用：

1. **用户注册** (`/auth/register`)
2. **修改用户名** (`/users/me/username`)
3. **更新个人资料** (`/users/me`)
4. **管理员更新用户信息** (`/users/{user_id}`)

## 注意事项

- 验证是大小写不敏感的
- 只检查完全匹配的保留词汇，允许包含保留词汇的用户名（如 "myadmin"）
- 错误信息统一为中文，符合用户体验要求
- 验证逻辑在服务端执行，确保安全性 