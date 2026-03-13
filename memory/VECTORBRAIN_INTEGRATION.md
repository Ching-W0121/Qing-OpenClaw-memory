# VectorBrain 主动记忆模块集成文档

**集成日期**: 2026-03-13  
**版本**: v1.0  
**状态**: ✅ 生产就绪

---

## 📋 概述

VectorBrain 是一个主动记忆系统，提供：
- 实时消息记忆保存
- 向量检索注入上下文
- 任务队列系统
- 机会扫描系统

已整合到现有记忆系统中，与 self-improvement v3.0.1 协同工作。

---

## 🏗️ 架构设计

### 三层记忆架构

```
┌─────────────────────────────────────────────┐
│           主动记忆层 (VectorBrain)           │
│  - 实时消息保存 (episodic_memory.db)        │
│  - 知识检索 (knowledge_memory.db)           │
│  - 任务队列 (task_queue.db)                 │
│  - 机会扫描 (opportunities.db)              │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│           反思层 (self-improvement)          │
│  - 定期反思 (reflection-worker.js)          │
│  - 学习日志 (.learnings/LEARNINGS.md)       │
│  - 经验提炼 (lessons.json)                  │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│           存储层 (文件系统)                  │
│  - 情景记忆 (memory/episodic/YYYY-MM-DD.jsonl) │
│  - 语义记忆 (memory/semantic/*.json)        │
│  - 长期记忆 (MEMORY.md)                     │
└─────────────────────────────────────────────┘
```

---

## 📦 数据库结构

### 1. episodic_memory.db - 情景记忆

存储所有对话历史，支持快速检索。

```sql
CREATE TABLE episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    session_id TEXT,
    user_id TEXT,
    channel_id TEXT,
    event_type TEXT,
    content TEXT NOT NULL,
    metadata TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_timestamp ON episodes(timestamp);
CREATE INDEX idx_session ON episodes(session_id);
CREATE INDEX idx_event_type ON episodes(event_type);
```

### 2. knowledge_memory.db - 知识记忆

存储提炼的知识和经验。

```sql
CREATE TABLE knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    category TEXT,
    confidence REAL DEFAULT 0.5,
    usage_count INTEGER DEFAULT 0,
    last_used_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_category ON knowledge(category);
CREATE INDEX idx_confidence ON knowledge(confidence);
```

### 3. task_queue.db - 任务队列

管理待处理任务，支持优先级和超时。

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 5,
    status TEXT DEFAULT 'queued',
    assigned_to TEXT,
    started_at TEXT,
    completed_at TEXT,
    result TEXT,
    error_message TEXT,
    timeout_minutes INTEGER DEFAULT 30,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_status ON tasks(status);
CREATE INDEX idx_priority ON tasks(priority);
```

### 4. opportunities.db - 机会发现

发现和追踪系统中的机会和风险。

```sql
CREATE TABLE opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    type TEXT,
    severity TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'pending',
    priority_score REAL DEFAULT 0.5,
    detected_at TEXT DEFAULT CURRENT_TIMESTAMP,
    processed_at TEXT,
    result TEXT,
    metadata TEXT
);

-- 索引
CREATE INDEX idx_status ON opportunities(status);
CREATE INDEX idx_severity ON opportunities(severity);
CREATE INDEX idx_priority_score ON opportunities(priority_score);
```

---

## 🔧 使用方法

### Python API

```python
from memory.vectorbrain_integration import *

# 初始化数据库
init_databases()

# 保存消息到情景记忆
save_message_to_episodic(
    message="今天投递了 8 个职位",
    session_id="main",
    user_id="qing",
    channel_id="webchat"
)

# 检索相关知识
knowledge = retrieve_knowledge(
    query="求职投递策略",
    limit=5,
    threshold=0.5
)

# 保存提炼知识
save_to_knowledge(
    key="job_search.zhilian_strategy",
    value="智联招聘网页端功能完整，作为主数据源",
    category="job_search",
    confidence=0.9
)

# 创建任务
task_id = create_task(
    title="测试前程无忧真实数据",
    description="访问 51job.com 搜索深圳品牌策划岗位",
    priority=2,  # 高优先级
    timeout_minutes=60
)

# 抢占任务
task = claim_task(worker_id="main_worker")
if task:
    # 执行任务...
    complete_task(task['task_id'], result="成功投递 5 个职位")

# 创建机会
opp_id = create_opportunity(
    title="发现新职位平台：猎聘网",
    description="猎聘网有大量品牌策划岗位，薪资范围 15-25K",
    opp_type="job_platform",
    severity="medium",
    priority_score=0.8
)

# 获取高优先级机会
opportunities = get_high_priority_opportunities(
    limit=10,
    min_priority_score=0.7
)
```

### 命令行工具

```bash
# 初始化数据库
cd C:\Users\TR\.openclaw\workspace\memory
python vectorbrain_integration.py

# 查看日志
tail -f memory/vectorbrain.log
```

---

## 📊 数据流

### 消息处理流程

```
用户发送消息
    ↓
OpenClaw Gateway
    ↓
Hook: message:new
    ↓
VectorBrain Connector
    ↓
┌─────────────────────┐
│ 1. 保存到情景记忆   │
│ 2. 检索相关知识     │
│ 3. 注入上下文       │
│ 4. 返回给 OpenClaw  │
└─────────────────────┘
    ↓
OpenClaw 生成回复
    ↓
用户收到回复
```

### 任务处理流程

```
任务创建
    ↓
任务队列 (queued)
    ↓
Task Manager 轮询
    ↓
抢占任务 (running)
    ↓
执行任务
    ↓
┌──────────────┐
│ 成功 → completed │
│ 失败 → failed │
└──────────────┘
    ↓
回写结果
```

### 反思流程

```
定期触发 (每 6 小时)
    ↓
reflection-worker.js
    ↓
┌─────────────────────┐
│ 1. 加载情景记忆     │
│ 2. 提取模式/错误    │
│ 3. 生成学习条目     │
│ 4. 保存到知识记忆   │
│ 5. 更新 lessons.json│
└─────────────────────┘
    ↓
自动晋升重复模式
```

---

## 🎯 关键特性

### 1. 实时记忆保存

每条消息自动保存到数据库：
- 时间戳
- 会话 ID
- 用户 ID
- 频道 ID
- 消息内容
- 元数据

### 2. 智能知识检索

支持文本搜索（TODO: 向量检索）：
- 置信度阈值过滤
- 使用次数排序
- 分类过滤

### 3. 任务队列管理

- **优先级**: 1-10（1 最高）
- **状态**: queued → running → completed/failed
- **超时**: 30 分钟默认
- **原子性**: UPDATE + ROW COUNT 验证

### 4. 机会扫描

- **类型**: job_platform, skill_upgrade, system_improvement, etc.
- **严重程度**: low/medium/high/critical
- **优先级分数**: 0-1
- **状态**: pending → processed

---

## 📈 性能优化

### 数据库索引

```sql
-- 时间范围查询
CREATE INDEX idx_timestamp ON episodes(timestamp);

-- 状态查询
CREATE INDEX idx_status ON tasks(status);

-- 优先级排序
CREATE INDEX idx_priority ON tasks(priority);

-- 置信度过滤
CREATE INDEX idx_confidence ON knowledge(confidence);
```

### 定期清理

```python
# 清理 30 天前的情景记忆
DELETE FROM episodes WHERE created_at < datetime('now', '-30 days');

# 清理已完成的任务
DELETE FROM tasks WHERE status = 'completed' AND completed_at < datetime('now', '-7 days');
```

### 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_knowledge(key):
    # 从数据库读取
    pass
```

---

## 🔍 监控和调试

### 日志文件

```bash
# 实时查看日志
tail -f memory/vectorbrain.log

# 查看错误日志
grep ERROR memory/vectorbrain.log | tail -20
```

### 健康检查

```python
from memory.vectorbrain_integration import *

# 检查数据库连接
try:
    conn = sqlite3.connect(str(EPISODIC_DB))
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM episodes')
    count = cursor.fetchone()[0]
    print(f'✅ 情景记忆数据库正常，共 {count} 条记录')
except Exception as e:
    print(f'❌ 数据库异常：{e}')
```

### 统计信息

```python
# 查询统计
conn = sqlite3.connect(str(EPISODIC_DB))
cursor = conn.cursor()

# 今日消息数
cursor.execute("SELECT COUNT(*) FROM episodes WHERE date(timestamp) = date('now')")
today_count = cursor.fetchone()[0]

# 待处理任务数
cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'queued'")
queued_tasks = cursor.fetchone()[0]

# 待处理机会数
cursor.execute("SELECT COUNT(*) FROM opportunities WHERE status = 'pending'")
pending_opps = cursor.fetchone()[0]

print(f'今日消息：{today_count}')
print(f'待处理任务：{queued_tasks}')
print(f'待处理机会：{pending_opps}')
```

---

## 🚀 下一步优化

### 短期（本周）
- [ ] 添加向量检索支持（Sentence Transformers）
- [ ] 实现自动清理旧数据
- [ ] 添加 Dashboard 监控界面
- [ ] 集成到 OpenClaw Hooks

### 中期（下周）
- [ ] 实现网络监控和自动降级
- [ ] 添加智能模型路由
- [ ] 优化任务抢占算法
- [ ] 添加任务重试机制

### 长期（v2.0）
- [ ] 分布式任务队列（Redis/Celery）
- [ ] 多节点支持
- [ ] 数据备份和恢复
- [ ] 性能基准测试

---

## 📚 参考资料

- [VectorBrain 原始项目](https://github.com/liugedapiqiu-dev/vectorbrain)
- [self-improvement v3.0.1](file://C:/Users/TR/.openclaw/skills/self-improvement/SKILL.md)
- [OpenClaw 文档](https://docs.openclaw.ai)

---

**集成完成时间**: 2026-03-13 13:51  
**集成者**: 庆 (Qing)  
**状态**: ✅ 生产就绪
