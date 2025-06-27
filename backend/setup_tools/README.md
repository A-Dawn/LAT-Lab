# LAT-Lab 系统设置工具

本目录包含了LAT-Lab博客系统的各种设置和管理工具。这些工具主要用于系统初始化、管理员账户创建等任务。

## 工具列表

### 1. 创建管理员用户

系统提供了两种方式创建管理员账户：

#### 交互式Python脚本 (create_admin_user.py)

这是一个交互式脚本，可以让你输入自定义的管理员用户信息：

```bash
# 在后端根目录执行
python setup_tools/create_admin_user.py

# 或者直接指定用户信息
python setup_tools/create_admin_user.py admin admin@example.com your_password
```

#### SQL脚本 (add_admin.sql)

这个脚本会创建一个预设的管理员用户：

```bash
# 在后端根目录执行
sqlite3 blog.db < setup_tools/add_admin.sql
```

**预设管理员信息**：
- 用户名: `admin`
- 密码: `admin123`
- 邮箱: `admin@latlab.example.com`

⚠️ **安全警告**：使用SQL脚本创建的管理员账户使用默认密码，请在生产环境中立即修改密码。

## 使用注意事项

1. 这些工具主要用于系统初始化阶段
2. 必须在数据库迁移完成后才能使用这些工具
3. 创建管理员账户后，请立即修改默认密码以确保安全
4. 在生产环境中，应当使用足够复杂的密码 