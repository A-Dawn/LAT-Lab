# 用户管理脚本

这个目录包含了系统管理脚本，用于数据库管理、用户创建等操作。

## create_user.py

此脚本用于在数据库中创建新用户，支持创建管理员或普通用户。

### 用法

```bash
python scripts/create_user.py [参数]
```

#### 可选参数

- `-u, --username`: 用户名
- `-e, --email`: 邮箱地址
- `-p, --password`: 密码（不推荐通过命令行传递，留空将安全提示输入）
- `-a, --admin`: 创建管理员用户（默认为普通用户）
- `--not-verified`: 标记用户为未验证状态（默认为已验证）

#### 示例

1. 交互式创建用户（推荐方式）：

```bash
python scripts/create_user.py
```

2. 创建管理员用户：

```bash
python scripts/create_user.py -a -u admin -e admin@example.com
```

3. 创建未验证的普通用户：

```bash
python scripts/create_user.py --not-verified -u testuser -e test@example.com
```

### 注意事项

- 如果数据库中没有任何用户，脚本会提醒您创建管理员账户
- 用户名至少需要3个字符
- 密码至少需要6个字符
- 脚本会检查用户名和邮箱是否已存在
- 默认创建的用户状态为"已验证"（可以直接登录） 