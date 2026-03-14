# Memory Vault 使用指南

**基于 SQLite 的长期记忆存储与语义检索系统**

**创建日期**: 2026-03-14  
**版本**: v1.0

---

## 🗄️ 系统架构

```
┌─────────────────────────────────────────┐
│         用户/Agent 查询                  │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│      MemoryVault (决策工作流集成)        │
│  - before_action()  行动前检索记忆       │
│  - after_action()   行动后记录结果       │
│  - reflect()        记录反思结果         │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│      语义检索引擎                         │
│  - 豆包 Embedding 生成向量               │
│  - 余弦相似度计算                        │
│  - Top-K 检索                            │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│      SQLite 数据库 (memory_vault.db)     │
│  - memories 表 (记忆文本 + 向量)          │
│  - reflections 表 (反思记录)             │
└─────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 1. 初始化数据库

```python
from memory_vault import init_database

# 初始化（自动创建 memory_vault.db）
db_path = init_database()
```

### 2. 添加记忆

```python
from memory_vault import add_memory

# 添加错误记忆
add_memory(
    memory_text="动态网页操作必须等待 10 秒+snapshot 后立即使用 + 验证结果",
    memory_type='error'
)

# 添加学习记忆
add_memory(
    memory_text="browser 操作前必须检索记忆",
    memory_type='learning'
)

# 添加情景记忆
add_memory(
    memory_text="PostgreSQL 配置完成 5 张表已创建",
    memory_type='episodic',
    metadata={'project': 'qing-agent', 'status': 'success'}
)
```

### 3. 语义搜索

```python
from memory_vault import search_memory

# 搜索相关记忆
results = search_memory(
    query="browser 操作失败怎么办",
    top_k=3,
    min_similarity=0.5
)

# 输出结果
for mem in results:
    print(f"相似度：{mem['similarity']:.2f}")
    print(f"类型：{mem['memory_type']}")
    print(f"内容：{mem['memory_text']}")
```

### 4. 查看统计

```python
from memory_vault import get_memory_stats

stats = get_memory_stats()
print(f"总记忆数：{stats['total']}")
print(f"按类型：{stats['by_type']}")
```

---

## 🔧 集成到决策工作流

### 使用 MemoryVault 类

```python
from memory_vault import MemoryVault

# 初始化
vault = MemoryVault()

# ========== 行动前检索 ==========
# 例如：准备执行 browser_act 操作
action_type = "browser_act"
context = {
    "target": "GPT 输入框",
    "page_type": "React"
}

# 检索相关记忆（会自动显示警告）
memories = vault.before_action(action_type, context)

# 根据记忆调整行为
if memories:
    print("⚠️ 记忆中有相关错误，需要谨慎操作")
    # 应用记忆中的解决方案

# ========== 执行操作 ==========
try:
    # 执行 browser_act...
    outcome = "success"
    details = {"method": "等待 10 秒+snapshot 后立即使用"}
except Exception as e:
    outcome = "failed"
    details = {"error": str(e)}

# ========== 行动后记录 ==========
vault.after_action(outcome, action_type, details)

# ========== 记录反思 ==========
vault.reflect(
    trigger_type="error",
    trigger_data={"action": action_type, "error": details},
    analysis={
        "result": {"root_cause": "等待时间不足"},
        "lessons": ["必须等待 10 秒让 React 完全加载"]
    }
)
```

---

## 📊 数据库表结构

### memories 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| memory_hash | TEXT | 记忆哈希（去重用） |
| memory_text | TEXT | 记忆文本内容 |
| memory_type | TEXT | 类型 (episodic/semantic/error/learning) |
| embedding | BLOB | 向量嵌入 (2048 维 float32) |
| embedding_dim | INTEGER | 向量维度 (默认 2048) |
| metadata | JSON | 额外元数据 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| access_count | INTEGER | 访问次数 |
| last_accessed | TIMESTAMP | 最后访问时间 |

### reflections 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| trigger_type | TEXT | 触发类型 (periodic/error/user_feedback) |
| trigger_data | JSON | 触发数据 |
| analysis_result | JSON | 分析结果 |
| lessons_learned | JSON | 学到的教训 |
| created_at | TIMESTAMP | 创建时间 |

---

## 🎯 记忆类型说明

| 类型 | 用途 | 示例 |
|------|------|------|
| **episodic** | 情景记忆（日常事件） | "PostgreSQL 配置完成" |
| **semantic** | 语义记忆（知识/事实） | "React 页面会持续重新渲染" |
| **error** | 错误记录 | "动态页面元素失效" |
| **learning** | 学习记录/最佳实践 | "browser 操作前必须检索记忆" |

---

## 🔍 语义检索参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| query | str | 必填 | 搜索查询文本 |
| top_k | int | 5 | 返回最相关的 K 条记忆 |
| min_similarity | float | 0.5 | 最小相似度阈值 (0-1) |
| memory_type | str | None | 过滤记忆类型 |
| db_path | Path | 默认 | 数据库路径 |

---

## 💡 最佳实践

### 1. 行动前强制检索

```python
# 每次 browser 操作前
memories = vault.before_action("browser_act", {"target": "xxx"})
if memories:
    # 应用记忆中的教训
    pass
```

### 2. 失败后立即记录

```python
# 失败后
vault.after_action("failed", "browser_act", {"error": "元素失效"})
# 自动记录到数据库，类型=error
```

### 3. 定期反思

```python
# 每 6 小时或失败 3 次后
vault.reflect(
    trigger_type="periodic",
    trigger_data={"episodes": recent_50},
    analysis={"result": {...}, "lessons": [...]}
)
```

### 4. 设置合理的相似度阈值

- **高精度** (min_similarity=0.7): 返回非常相关的记忆
- **平衡** (min_similarity=0.5): 推荐默认值
- **高召回** (min_similarity=0.3): 返回更多相关记忆

---

## 🛠️ 命令行工具

### 添加记忆

```bash
cd memory
python memory_vault.py add "记忆文本" [类型]
# 示例
python memory_vault.py add "browser 操作前必须检索记忆" learning
```

### 搜索记忆

```bash
python memory_vault.py search "搜索查询" [top_k]
# 示例
python memory_vault.py search "browser 失败" 3
```

### 查看统计

```bash
python memory_vault.py stats
```

---

## 📈 性能优化

### 1. 批量添加

```python
# 避免循环单个添加
memories = ["记忆 1", "记忆 2", "记忆 3"]
for mem in memories:
    add_memory(mem)  # ✅ 可以接受
```

### 2. 缓存 Embedding

```python
# 对相同文本缓存 embedding
embedding_cache = {}

def get_embedding_cached(text):
    if text not in embedding_cache:
        embedding_cache[text] = get_embedding(text)
    return embedding_cache[text]
```

### 3. 索引优化

数据库已自动创建以下索引：
- `idx_memory_type` - 按类型过滤
- `idx_created_at` - 按时间排序
- `idx_access_count` - 热门记忆

---

## 🔐 API 配置

豆包 Embedding API 配置（已内置）：

```python
DOUBAO_API_KEY = "fddc1778-d04c-403e-8327-ab68ec1ec9dd"
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/embeddings/multimodal"
DOUBAO_MODEL = "doubao-embedding-vision-251215"
EMBEDDING_DIM = 2048
```

---

## ✅ 测试清单

- [x] 数据库初始化
- [x] 添加记忆（error/learning/episodic）
- [x] 语义搜索（余弦相似度）
- [x] 统计信息
- [x] MemoryVault 类集成
- [ ] 批量添加优化
- [ ] Embedding 缓存
- [ ] 自动反思触发

---

**版本**: v1.0  
**最后更新**: 2026-03-14  
**作者**: 青 (Qing)
