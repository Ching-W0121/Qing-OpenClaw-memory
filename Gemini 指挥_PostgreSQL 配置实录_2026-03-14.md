# Gemini 老师指挥 - PostgreSQL 职位数据库配置实录

**咨询日期**: 2026-03-14 16:16  
**状态**: 🚧 进行中 - Gemini 老师分阶段指挥

---

## 🎯 Gemini 老师开场

> "你好，青（Qing）！很高兴看到你和庆的项目进展得这么顺利。既然环境已经准备就绪，我们现在就开始把这个"大脑"（数据库）从轻量级的 SQLite 升级到强大的 PostgreSQL 16。"

> "为了确保万无一失，我们分阶段进行。"

---

## 📋 配置流程（分阶段）

### 第一阶段：PostgreSQL 16 的安装与基础设置

#### 1. 下载与安装

**下载地址**: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

**选择**: Windows x86-64 对应的 16.x 版本

**安装要点**:
| 项目 | 设置 |
|------|------|
| **组件选择** | 勾选全部（PostgreSQL Server, pgAdmin 4, Stack Builder, Command Line Tools） |
| **超级用户密码** | 设置 `postgres` 用户的密码（务必记牢，稍后配置 .env 要用） |
| **端口** | 保持默认 `5432` |
| **地区 (Locale)** | 建议 `C` 或 `Chinese (Simplified), China` |

---

#### 2. 配置环境变量

**目的**: 让终端识别 `psql` 命令

**步骤**:
1. 按 `Win + S` 搜索"编辑系统环境变量"
2. 点击"环境变量" → 在"系统变量"中找到 `Path` → 点击"编辑"
3. 点击"新建"，添加 PostgreSQL 的 bin 目录路径：
   ```
   C:\Program Files\PostgreSQL\16\bin
   ```
4. 确定保存，重新打开新的终端（PowerShell 或 CMD）

---

### 第二阶段：创建数据库与专用用户

#### 执行命令

**1. 登录 PostgreSQL**（输入安装时设置的密码）:
```bash
psql -U postgres
```

**2. 创建数据库用户**（为项目单独创建用户，更安全）:
```sql
CREATE USER qing_admin WITH PASSWORD '你的自定义强密码';
```

**3. 创建数据库**:
```sql
CREATE DATABASE qing_jobs_db OWNER qing_admin;
```

**4. 退出**:
```sql
\q
```

---

### 第三阶段：修改 .env 激活配置

**文件**: `C:\Users\TR\.openclaw\workspace\qing-agent\.env`

**修改内容**:
```ini
# 原有的 SQLite（注释掉）
# DATABASE_URL=sqlite+aiosqlite:///./jobs.db

# 新的 PostgreSQL 配置 (使用 asyncpg 驱动)
DATABASE_URL=postgresql+asyncpg://qing_admin:你的自定义强密码@localhost:5432/qing_jobs_db

# 之前配置过的连接池参数确保存在
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

---

## ✅ 完成后反馈清单

Gemini 老师要求完成后反馈以下信息：

1. ✅ PostgreSQL 是否安装成功？
2. ✅ 在终端输入 `psql --version` 是否能正常显示版本号？
3. ✅ `.env` 文件是否已更新完毕？

---

## 🚀 下一步（待执行）

**一旦确认以上操作完成，Gemini 老师将立即指导**:
- Alembic 迁移脚本的生成
- 执行迁移创建表结构
- 验证数据库连接

---

## 💡 关键要点

| 阶段 | 关键操作 | 注意事项 |
|------|----------|----------|
| **安装** | 勾选全部组件 | 密码务必记牢 |
| **环境变量** | 添加 bin 路径 | 需要重新打开终端 |
| **数据库创建** | 单独创建用户 + 数据库 | 更安全的项目隔离 |
| **.env 配置** | 使用 asyncpg 驱动 | 连接池参数保留 |

---

**Gemini 老师鼓励**: "加油，青！"

---

**当前状态**: 等待庆确认是否开始执行第一阶段（PostgreSQL 安装）
