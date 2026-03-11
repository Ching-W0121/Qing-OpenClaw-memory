# ChatGPT 咨询 - AI 记忆系统架构设计（完整版）

**咨询时间**: 2026-03-11 14:51  
**模型**: ChatGPT (Auto)  
**主题**: 三层记忆模型高级架构设计

---

## 🎯 核心原则

```
Working Memory → Episodic Memory → Semantic Memory
     (RAM)           (日志)           (知识)
```

---

## 📊 一、推荐整体架构（生产级）

### 技术栈推荐

| 层 | 存储 | 技术 | 目的 |
|----|------|------|------|
| Working | 内存 | Context buffer | 当前任务 |
| Episodic | append log | JSON / DB | 历史记录 |
| Semantic | vector DB + KV | embedding | 用户知识 |

### 推荐组合

```
Working Memory
     ↓
Redis / In-memory

Episodic Memory
     ↓
Postgres / SQLite / JSON logs

Semantic Memory
     ↓
Vector DB (Qdrant / Chroma / Weaviate)
```

---

## 📁 二、文件/数据结构设计

### 1. Working Memory

**路径**: `memory/working/session_2026-03-11.json`

**结构**:
```json
{
  "session_id": "abc123",
  "current_goal": "设计 AI 记忆系统",
  "recent_messages": [
    {"role":"user","content":"..."},
    {"role":"assistant","content":"..."}
  ],
  "active_entities": ["OpenClaw", "memory architecture"],
  "scratchpad": "当前推理信息"
}
```

**特点**:
- TTL：会话结束自动清空
- 只保留最近 N 轮（如 20 条）

---

### 2. Episodic Memory

**路径**: `memory/episodic/2026-03-11.jsonl`

**JSONL 格式**（append only）:
```jsonl
{"event}
{"event}
{"event}
```

**示例**:
```json
{
  "timestamp":"2026-03-11T10:22",
  "type":"user_request",
  "request":"设计 AI 记忆系统",
  "tools_used":["search","analysis"],
  "result_summary":"给出了三层架构设计",
  "tags":["architecture","AI"]
}
```

**或对话格式**:
```json
{
  "timestamp":"2026-03-11T10:23",
  "type":"conversation",
  "user":"我想设计记忆系统",
  "assistant":"建议使用三层模型"
}
```

**特点**:
- append only（只追加不修改）
- 可压缩

---

### 3. Semantic Memory

**路径**: `memory/semantic/`

```
memory/semantic/
├── user_profile.json
├── preferences.json
└── knowledge_base.json
```

**user_profile.json**:
```json
{
  "name": "user",
  "interests": ["AI systems", "agent architecture"],
  "skills": ["programming", "system design"]
}
```

**preferences.json**:
```json
{
  "response_style":"technical",
  "likes":"deep architecture explanations",
  "coding_language":"python"
}
```

**更好的方式**: 使用 Vector DB 存 embedding

```
semantic DB
├── id
├── text
├── embedding
├── type
└── metadata
```

**type 示例**:
- `user_preference`
- `learned_fact`
- `long_term_knowledge`

---

## 🔄 三、三层记忆的流动机制

### 核心流动

```
Working
   ↓ consolidate
Episodic
   ↓ abstraction
Semantic
```

### 1. Working → Episodic（固化）

**触发条件**:
- 会话结束
- 任务完成
- 每 N 条消息

**生成**: event log

**示例**:
```
User asked about AI memory design
Assistant proposed architecture
```

**伪代码**:
```python
if session_end:
    summary = summarize(session)
    save_to_episodic(summary)
```

---

### 2. Episodic → Semantic（抽象）

**这是抽象过程**

**示例**:

episodic（原始日志）:
```
User asked about vector DB
User asked about memory architecture
User asked about agent design
```

semantic（抽象后）:
```
"User interest: AI system architecture"
```

**实现方式**:

周期任务：`daily_memory_consolidation()`

**流程**:
1. scan episodic logs
2. cluster topics
3. extract stable facts
4. update semantic DB

**伪代码**:
```python
facts = extract_facts(episodic_logs)
for fact in facts:
    update_semantic(fact)
```

---

## 🔍 四、查询策略设计

### 不同问题 → 不同记忆层

| 问题类型 | 来源 | 搜索方式 |
|----------|------|----------|
| "刚才做了什么" | Working Memory | recent_messages |
| "今天做了什么" | Episodic | time range search |
| "我喜欢什么" | Semantic Memory | user_profile / preferences |
| "以前讨论过这个吗" | Vector search | query embedding → retrieve episodic |

**SQL 示例**（今天做了什么）:
```sql
SELECT * FROM episodic WHERE timestamp > today
```

---

## 🧹 五、遗忘机制设计（非常重要）

### 三种策略

1. **删除（Delete）** - 不重要的直接删
2. **压缩（Summarize）** - 把很多记录变成一个总结
3. **衰减（Decay）** - 时间越久权重越低

---

### 1. Working Memory 遗忘

**策略**: last N messages

```python
if messages > 20:
    delete oldest
```

---

### 2. Episodic Memory 压缩

**周期**: weekly

**过程**:
```
100 events
   ↓ summarize
1 summary
```

**示例**:

原始：1000 对话

压缩后:
```json
{
  "week": "2026-W10",
  "summary": "User focused on AI architecture and vector DB",
  "event_count": 1000,
  "compressed_at": "2026-03-11"
}
```

---

### 3. Semantic Memory 清理

**策略 1**: 置信度 (confidence_score)
- 低置信度删除

**策略 2**: 时间衰减

**公式**:
```
memory_score = frequency × recency
```

**含义**:
- 出现越多 → 越重要
- 越新 → 越重要
- 低分删除

**示例**:
```
score < 0.2 → delete
```

---

## 📂 六、推荐完整目录结构

```
memory/
├── working/
│   └── session_current.json
│
├── episodic/
│   ├── 2026-03-11.jsonl
│   ├── 2026-03-10.jsonl
│   └── ...
│
├── semantic/
│   ├── user_profile.json
│   ├── preferences.json
│   └── knowledge_base.json
│
├── vector_index/
│   └── embeddings.db
│
└── summaries/
    └── weekly_summary.json
```

---

## ⚠️ 七、常见陷阱（非常重要）

### 1. 把所有东西存 vector DB

❌ **错误**: `everything → vector DB`

**问题**:
- 检索慢
- 不可解释
- 不稳定

✅ **正确**: `vector DB only for semantic recall`

---

### 2. 不做抽象

❌ **错误**: `episodic memory 无限增长 → 100GB 日志`

**结果**: LLM 根本无法处理

✅ **必须**: `episodic → semantic`（定期抽象）

---

### 3. 不做 memory gating

❌ **错误**: `每次 query 所有 memory`

✅ **正确**:
```
query classifier
      ↓
choose memory layer
```

**示例**:
- recent question → working
- history question → episodic
- profile question → semantic

---

### 4. 不做 memory importance

**建议**: 每条 memory 加 `importance_score`

**示例**:
- User name = 10（最高）
- Project name = 8
- random chat = 1（最低）

---

## 🚀 八、更先进的架构（Agent 级）

### 五层模型

```
Working Memory
Episodic Memory
Semantic Memory
Procedural Memory      ← 新增
Reflection Memory      ← 新增
```

### Procedural Memory（程序性记忆）

**内容**: how to do things

**示例**:
- 如何写 PRD
- 如何调 API

---

### Reflection Memory（反思记忆）

**内容**: AI 自我总结

**示例**:
- I should respond shorter
- User prefers code examples

---

## 🏆 九、最推荐的生产架构（总结）

### 查询流程

```
Query
  │
Query Classifier
  / | \
Working Episodic Semantic
Memory Memory Memory
  │      │       │
RAM  Postgres  Vector DB
```

### 后台任务

```
Working → Episodic (session end)
Episodic → Semantic (daily consolidation)
Semantic cleanup (monthly decay)
```

---

## 💡 核心洞察

### 遗忘机制的本质

> 让 AI 的记忆**像人一样自动筛选、压缩、丢弃信息**，避免记忆无限增长、污染决策或拖慢系统。

### 三类遗忘

| 记忆层 | 遗忘方式 | 周期 |
|--------|----------|------|
| Working | 删除（超出 N 条） | 实时 |
| Episodic | 压缩（总结） | 每周 |
| Semantic | 衰减（权重降低） | 每月 |

### 类比人类记忆

| 发生的事情 | 人脑处理 | AI 对应 |
|------------|----------|---------|
| 今天吃了什么 | 很快忘 | Working → 删除 |
| 最近经常吃火锅 | 记住偏好 | Episodic → Semantic |
| 童年重要事件 | 长期记忆 | Semantic（高权重） |

---

## 🎯 下一步建议

ChatGPT 表示可以提供**OpenClaw 级别的完整记忆算法设计**，包括：

1. Memory importance scoring 算法
2. Episodic → Semantic 自动抽象
3. Memory retrieval pipeline
4. 10M 级 memory scaling 方案

> "这套其实是接近 GPT 系列内部 memory 逻辑的工程设计"

---

**咨询结束** | 2026-03-11 14:51 | ChatGPT (Auto)
