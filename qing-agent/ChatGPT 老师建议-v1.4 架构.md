# ChatGPT GPT-5.3 老师的建议

**咨询日期**: 2026-03-10  
**文档版本**: v1.4 架构升级建议

---

## 📊 整体评价

> 这个文档的工程质量非常高，已经是接近真实 AI 产品团队的技术 RFC 水平！

结构上已经具备：
- 项目背景
- 架构图
- 当前问题
- 技术挑战
- 代码目标
- Schema 设计
- 时间计划

这在工程团队里就是 **技术决策文档 (Tech RFC)**。

---

## 一、架构合理性评价

### 青目前架构

```
FastAPI
  └─ Routes
      └─ Services
          └─ Adapters
              └─ Tools
                  └─ Memory(dict)  ← 问题所在
```

**这是非常标准的分层架构！**

### 优点
- ✅ 分层清晰
- ✅ 职责分离
- ✅ 易于测试

### 唯一问题
**存储层缺失**

系统现在是：
- ❌ Stateless (无状态)

而不是：
- ✅ Stateful System (有状态系统)

**结论**: SQLite 是必须的！

---

## 二、Schema 设计评估（很不错，但可优化）

### 青给出 4 张表
- users
- jobs
- matches
- applications

**逻辑是正确的！**

### 但我会做三个升级

### 1️⃣ Jobs 表必须增加字段

**现在**:
```
jobs
  - id
  - job_id
```

**问题**: job_id 不同平台可能重复

**建议增加**:
```
jobs
  - id
  - platform
  - source_platform_id  ← 新增
  - title
  - company
  - salary_min
  - salary_max
  - location
  - district
  - experience
  - education
  - description
  - skills
  - industry
  - url
  - crawled_at
  - updated_at
```

**唯一索引**:
```sql
CREATE UNIQUE INDEX idx_jobs_unique 
ON jobs(platform, source_platform_id);
```

---

### 2️⃣ Matches 表增加缓存机制

推荐系统会频繁计算，所以增加：

```
matches
  - id
  - user_id
  - job_id
  - match_score
  - match_vector  ← 新增 (JSON)
  - match_details
  - rank
  - is_viewed
  - is_applied
  - created_at
```

**match_vector 示例**:
```json
{
  "industry": 0.9,
  "skill": 0.8,
  "experience": 0.7
}
```

**未来可以做**: AI Explainability (可解释性)

---

### 3️⃣ Applications 表需要平台状态

**建议增加**:
```
applications
  - id
  - user_id
  - job_id
  - status
  - platform_status  ← 新增
  - applied_at
  - updated_at
  - notes
```

**platform_status 示例**:
- pending
- submitted
- hr_viewed
- interview
- offer
- reject

**原因**: 平台状态和系统状态不同

---

## 三、JSON 字段是否合理？

**结论**: 合理，但必须控制！

### 建议

**可以用 JSON**:
- ✅ resume_data
- ✅ skills
- ✅ expectations
- ✅ requirements
- ✅ match_vector

**必须用结构字段** (否则 SQL 查询会崩):
- ❌ location → 必须单独字段
- ❌ salary → 必须单独字段 (salary_min, salary_max)
- ❌ experience → 必须单独字段
- ❌ education → 必须单独字段

---

## 四、SQLite 索引优化

### 青目前的索引
- jobs.platform
- jobs.location
- matches.user
- matches.score
- applications.user
- applications.status

### 我建议增加

**职位搜索索引**:
```sql
CREATE INDEX idx_jobs_title ON jobs(title);
```

**推荐排序**:
```sql
CREATE INDEX idx_matches_user_score 
ON matches(user_id, match_score DESC);
```

**投递查询**:
```sql
CREATE INDEX idx_applications_user_job 
ON applications(user_id, job_id);
```

---

## 五、SQLAlchemy ORM 设计

青给出的 ORM 基本正确，但必须升级到 **SQLAlchemy 2.0 写法**！

### 推荐写法

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

然后：
```python
class User(Base):
    __tablename__ = "users"
    
    id = mapped_column(Integer, primary_key=True)
```

而不是旧版：
```python
declarative_base()  # ❌ 旧版
```

---

## 六、dict → ORM 迁移最佳方案

**千万不要直接替换 Service！**

### 正确做法：新增 Repository Layer

**架构升级**:
```
Routes
  └─ Services
      └─ Repositories  ← 新增
          └─ ORM
              └─ Database
```

### Repository 示例

```python
class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_data):
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
```

### Service 调用

```python
repo = UserRepository(db)
repo.create(data)
```

**这样 Service 层不用知道数据库细节！**

---

## 七、SQLite 连接池问题

**SQLite 其实不需要连接池！**

### 推荐配置

```python
engine = create_engine(
    "sqlite:///./data/qing_agent.db",
    connect_args={"check_same_thread": False},
)
```

### 原因

SQLite 本身是 **file-based DB**，连接池意义不大。

---

## 八、FastAPI 数据库最佳实践

你写的这个是正确模式：

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

使用：
```python
Depends(get_db)
```

这是 FastAPI 官方推荐方式！✅

---

## 九、事务管理

### 最佳方式：Service 层控制事务

**简单操作**:
```python
def create_user(db: Session, data):
    user = User(**data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

**复杂操作**:
```python
try:
    db.commit()
except:
    db.rollback()
```

---

## 十、是否需要 Alembic？

**答案**: 必须用！✅

因为未来 schema change 是必然的。

### 安装

```bash
pip install alembic
```

### 初始化

```bash
alembic init migrations
```

### 自动生成

```bash
alembic revision --autogenerate -m "Initial migration"
```

### 升级

```bash
alembic upgrade head
```

---

## 十一、BOSS 直聘问题（真实情况）

这个问题不是技术问题，是：**平台反爬策略**！

### BOSS 直聘现状

已经在网页端：**搜索结果 → APP 限制**

### 原因

他们现在主要流量在：**APP**

所以网页被限制。

### 可行方案

**方案 1（推荐）**: 增加平台
- 智联招聘 ✅ (已支持)
- 前程无忧
- 猎聘网

这三个网页端仍然正常！

**方案 2**: APP 自动化 (Appium)
- 复杂度高
- 维护成本大
- 不推荐

---

## 十二、v1.4 架构升级总结

### 需要添加的文件

| 文件 | 说明 | 优先级 |
|------|------|--------|
| `database/models.py` | SQLAlchemy 2.0 ORM 模型 | 🔴 |
| `database/db.py` | 数据库连接配置 | 🔴 |
| `repositories/base.py` | Repository 基类 | 🔴 |
| `repositories/user_repo.py` | 用户仓库 | 🔴 |
| `repositories/job_repo.py` | 职位仓库 | 🔴 |
| `alembic.ini` | Alembic 配置 | 🟡 |
| `migrations/` | 数据库迁移脚本 | 🟡 |

### 架构升级图

```
v1.3 架构:
FastAPI → Routes → Services → Memory(dict)

v1.4 架构:
FastAPI → Routes → Services → Repositories → ORM → SQLite
```

---

## 十三、代码质量评价

> 青的代码工程质量非常高！

- ✅ 分层清晰
- ✅ 职责分离
- ✅ 有测试意识
- ✅ 有文档习惯

**已经是产品级代码水平！**

---

**老师**: ChatGPT GPT-5.3  
**学生**: 青 (Qing)  
**日期**: 2026-03-10
