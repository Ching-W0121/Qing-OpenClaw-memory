# Gemini 老师咨询 - PostgreSQL 环境配置指南

**咨询日期**: 2026-03-14 15:30  
**状态**: ✅ 已完成 - 获得完整 PostgreSQL 配置方案

---

## 🎯 Gemini 核心评价

> "从 SQLite 迁移到 PostgreSQL 是"青 Agent"走向生产级的关键一步。"

---

## 📊 一、PostgreSQL 安装与初始配置 (Windows)

### 推荐版本

**PostgreSQL 16**（当前最稳定的主流版本）

**优势**: 对 JSONB 的查询性能和并行逻辑处理有显著优化，非常适合 AI 解析需求。

---

### 安装步骤

| 步骤 | 操作 | 说明 |
|------|------|------|
| **1. 下载** | [EDB 官网](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) | Windows x86-64 安装包 |
| **2. 安装** | 运行 `.exe` | 勾选 PostgreSQL Server、pgAdmin 4、Command Line Tools |
| **3. 密码** | 设置 `postgres` 密码 | 超级用户密码（务必记住） |
| **4. 环境变量** | 添加到 PATH | `C:\Program Files\PostgreSQL\16\bin` |

---

### 初始数据库创建（命令行）

```bash
# 登录
psql -U postgres

# 执行 SQL（创建数据库和用户）
CREATE USER qing_admin WITH PASSWORD 'your_password';
CREATE DATABASE qing_agent_db OWNER qing_admin;
GRANT ALL PRIVILEGES ON DATABASE qing_agent_db TO qing_admin;
```

---

## 🔧 二、Python 连接与环境管理

### 推荐库

| 库 | 用途 | 说明 |
|------|------|------|
| **asyncpg** | 驱动 | Python 下连接 Postgres 最快的异步驱动 |
| **SQLAlchemy (v2.0+)** | ORM | 配合 FastAPI 使用异步路线 |

---

### 配置文件模板（.env）

```ini
# .env
DATABASE_URL=postgresql+asyncpg://qing_admin:your_password@localhost:5432/qing_agent_db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

---

### Python 连接代码示例

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 创建异步引擎，配置连接池
engine = create_async_engine(
    DATABASE_URL,
    pool_size=int(os.getenv("DB_POOL_SIZE", 10)),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", 5)),
    pool_recycle=3600,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# FastAPI Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

## 🔄 三、数据库迁移 (Alembic)

**不要手动执行 `CREATE TABLE`**。使用 Alembic 可以追踪版本，方便在不同机器（开发 vs 生产）同步结构。

### 安装与初始化

```bash
# 安装
pip install alembic

# 初始化
alembic init migrations
```

---

### 配置

**文件**: `alembic.ini`

**设置**: 数据库连接，或在 `env.py` 中动态读取 `.env`

---

### 生成迁移

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "create_jobs_table"

# 执行迁移
alembic upgrade head
```

---

## ⚡ 四、性能优化与 Windows 注意项

### 关键参数调整 (postgresql.conf)

Windows 下 PostgreSQL 默认配置很保守，建议修改以下参数以支持大量职位写入：

| 参数 | 建议值 | 说明 |
|------|--------|------|
| **shared_buffers** | 系统内存的 25% | 如 16GB 内存设为 4GB |
| **work_mem** | 16MB 或更高 | 优化复杂的 `ORDER BY` 排序 |
| **max_connections** | 100-200 | 配合 Python 连接池使用 |

---

### Windows 特有注意事项

| 注意项 | 说明 |
|--------|------|
| **权限问题** | 确保 `.openclaw\workspace` 所在磁盘分区没有严格的写入限制 |
| **防病毒软件** | 将 PostgreSQL 的数据目录（Data folder）加入 Windows Defender 的排除项，否则高频写入职位数据时会非常卡顿 |

---

## 💾 五、备份与恢复

### 自动备份脚本 (backup.bat)

```batch
@echo off
SET PGPASSWORD=your_password
"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe" -U qing_admin -h localhost qing_agent_db > C:\backups\qing_agent_%date:~0,4%%date:~5,2%%date:~8,2%.sql
```

**使用**: 创建批处理文件，利用 Windows 任务计划程序每天运行。

---

### 恢复流程

```bash
psql -U qing_admin -d qing_agent_db < backup_file.sql
```

---

## 📋 六、最佳实践建议

### 1. 开发 vs 生产环境

**强烈建议**: 开发环境也换成 PostgreSQL

**原因**:
- SQLite 不支持 JSONB 的高级索引
- SQLite 不支持 `ON CONFLICT` 这种 Postgres 特有的高级去重语法
- 保持环境一致能避免很多奇怪的 Bug

---

### 2. 日志记录

**建议**: 在 Postgres 中开启慢查询日志

**配置**:
```conf
log_min_duration_statement = 1000  # 记录超过 1 秒的查询
```

---

### 3. 连接池配置

**推荐**:
- `pool_size`: 10-20
- `max_overflow`: 5-10
- `pool_recycle`: 3600（1 小时）

---

## 📝 七、完整实施清单

### 立即实施（今日）
- [ ] 下载 PostgreSQL 16
- [ ] 安装 PostgreSQL（勾选 Server + pgAdmin + CLI Tools）
- [ ] 添加环境变量到 PATH
- [ ] 创建数据库和用户（`qing_agent_db` + `qing_admin`）
- [ ] 安装 Python 库：`pip install asyncpg sqlalchemy python-dotenv alembic`
- [ ] 创建 `.env` 配置文件
- [ ] 初始化 Alembic：`alembic init migrations`

### 短期实施（本周）
- [ ] 创建 jobs 表和 applications 表（通过 Alembic 迁移）
- [ ] 配置连接池
- [ ] 调整 postgresql.conf 参数（shared_buffers, work_mem）
- [ ] 添加 Windows Defender 排除项
- [ ] 创建自动备份脚本

### 长期实施（v2.0）
- [ ] 开发环境切换到 PostgreSQL
- [ ] 配置慢查询日志
- [ ] 监控连接池使用情况
- [ ] 定期清理过期职位数据（按月分区）

---

## 💡 八、GPT vs Gemini 建议对比

| 方面 | GPT 建议 | Gemini 建议 |
|------|----------|-------------|
| **数据库** | PostgreSQL + JSONB | ✅ 同左 |
| **驱动** | psycopg2 | **asyncpg**（异步更快） |
| **ORM** | SQLAlchemy v2.0 | ✅ 同左 |
| **迁移工具** | Alembic | ✅ 同左 |
| **开发环境** | SQLite → PostgreSQL | **直接用 PostgreSQL**（避免 Bug） |
| **性能优化** | 索引 + 分区 | shared_buffers + work_mem + 防病毒排除 |
| **备份** | pg_dump | ✅ 同左 + 批处理脚本 |

---

## 🚀 九、下一步建议

Gemini 老师最后问：
> "你需要我为你写一段 Python 代码，演示如何利用 FastAPI 接收抓取的数据并使用 unique_hash 进行'防重入库'吗？"

---

**感谢 Gemini 老师的详细指导！** 🙏
