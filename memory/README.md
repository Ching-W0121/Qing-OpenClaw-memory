# 记忆系统使用指南

## 📁 文件结构

```
memory/
├── memories.qmem          # 合并的记忆文件（二进制格式）
├── *.md                   # 原始 Markdown 文件（保留备份）
└── *.json                 # 原始 JSON 文件（保留备份）

scripts/
├── memory_tool.py         # 单条记忆编码/解码工具
├── memory_merge.py        # 记忆合并工具
└── memory_api.py          # 记忆访问 API
```

---

## 🚀 快速开始

### 1. 查看记忆摘要

```bash
cd C:\Users\TR\.openclaw\workspace
python scripts/memory_api.py summary
```

**输出示例**:
```
📚 记忆数据库摘要
   文件：memories.qmem
   大小：23.6 KB
   记录：7 条

📅 最近记忆:
   [20260309] 2026-03-09 记忆日志
           标签：求职 Agent, JWT, SQLite
   ...
```

---

### 2. 查看统计信息

```bash
python scripts/memory_api.py stats
```

**输出示例**:
```
[STATS]
  File:       C:\Users\TR\.openclaw\workspace\memory\memories.qmem
  Size:       23.6 KB
  Entries:    7
  Average:    3452 bytes/entry
  Date Range: 20260306 - 20260309
```

---

### 3. 查看最近记忆

```bash
# 默认最近 5 条
python scripts/memory_api.py list

# 最近 10 条
python scripts/memory_api.py list 10
```

---

### 4. 搜索记忆

```bash
# 全文搜索
python scripts/memory_api.py search JWT

# 按标签搜索
python scripts/memory_api.py tag 求职 Agent

# 按日期搜索
python scripts/memory_api.py date 20260309
```

---

### 5. 获取指定记忆

```bash
python scripts/memory_api.py get 2026-03-09
```

---

## 💻 Python API

### 打开记忆数据库

```python
from scripts.memory_api import MemoryDB, open_memory

# 方式 1: 上下文管理器（推荐）
with MemoryDB() as db:
    memories = db.all()
    print(f"共有 {len(memories)} 条记忆")

# 方式 2: 手动打开
db = MemoryDB()
db.open()
# ... 使用 ...
db.close()

# 方式 3: 便捷函数
db = open_memory()
```

---

### 获取记忆

```python
# 获取所有记忆
memories = db.all()

# 获取指定 ID
memory = db.get("2026-03-09")

# 获取最新 N 条
latest = db.latest(5)
```

---

### 搜索记忆

```python
# 全文搜索
results = db.search("JWT 认证")

# 按标签搜索
results = db.search_by_tag("求职 Agent")

# 按日期范围搜索
results = db.search_by_date(20260309, 20260311)
```

---

### 访问记忆内容

```python
memory = db.get("2026-03-09")

print(f"ID:        {memory.id}")
print(f"日期：{memory.date}")
print(f"标题：{memory.title}")
print(f"标签：{memory.tags}")
print(f"内容：{memory.content}")  # 字典格式
```

---

## 🔧 高级功能

### 创建新记忆（Python）

```python
from scripts.memory_tool import MemoryRecord, Event, memory_to_file

# 创建记忆记录
record = MemoryRecord(
    date=20260311,
    type=1,  # WORK_LOG
    events=[
        Event(
            title="完成记忆系统开发",
            status=2,  # COMPLETED
            timestamp="2026-03-11T14:00:00",
            tags=["记忆系统", "工具开发"],
            files_added=["scripts/memory_api.py"],
            files_modified=[],
            metrics={"compression_ratio": 0.72},
            notes="二进制格式 + LZ4 压缩"
        )
    ],
    progress={"memory_system": 1.0},
    summary="完成记忆编码工具和合并系统",
    created_at="2026-03-11T14:00:00"
)

# 写入文件（JSON 格式，用于合并）
import json
from dataclasses import asdict

with open("memory/2026-03-11.json", "w", encoding="utf-8") as f:
    json.dump(asdict(record), f, indent=2, ensure_ascii=False)

# 重新合并
# python scripts/memory_merge.py merge
```

---

### 重新合并记忆

当你创建了新的记忆文件后：

```bash
python scripts/memory_merge.py merge memory/memories.qmem
```

这会扫描所有 `2026-*.md` 和 `2026-*.json` 文件，重新生成合并文件。

---

## 📊 性能对比

| 操作 | Markdown | 合并文件 (.qmem) |
|------|----------|------------------|
| 文件大小 | ~40 KB (7 条) | **23.6 KB** |
| 加载速度 | 慢（逐个读取） | **快（一次加载）** |
| 搜索速度 | 慢（全文扫描） | **快（索引加速）** |
| 压缩率 | 100% | **~60%** |

---

## 🎯 最佳实践

### 1. 每日创建记忆

```python
# 每天工作结束后创建记忆
python scripts/memory_tool.py encode memory/2026-03-11.json
```

### 2. 定期合并

```bash
# 每周合并一次
python scripts/memory_merge.py merge
```

### 3. 使用 API 访问

```python
# 在 Agent 代码中使用
from scripts.memory_api import open_memory

with open_memory() as db:
    # 获取昨天记忆
    yesterday = db.get("2026-03-10")
    
    # 搜索相关记忆
    results = db.search("求职 Agent")
```

---

## 📝 记忆格式

### JSON 格式（推荐）

```json
{
  "date": 20260311,
  "type": 1,
  "events": [
    {
      "title": "完成记忆系统开发",
      "status": 2,
      "timestamp": "2026-03-11T14:00:00",
      "tags": ["记忆系统", "工具开发"],
      "files_added": ["scripts/memory_api.py"],
      "files_modified": [],
      "metrics": {"compression_ratio": 0.72},
      "notes": "二进制格式 + LZ4 压缩"
    }
  ],
  "progress": {"memory_system": 1.0},
  "summary": "完成记忆编码工具和合并系统",
  "created_at": "2026-03-11T14:00:00"
}
```

### Markdown 格式（兼容）

系统会自动将 Markdown 文件转换为记忆条目，但推荐使用 JSON 格式以获得更好的压缩和检索性能。

---

## 🐛 故障排除

### 问题：找不到记忆文件

```bash
# 检查文件是否存在
ls memory/memories.qmem

# 如果不存在，重新合并
python scripts/memory_merge.py merge
```

### 问题：搜索结果为空

```bash
# 检查记忆内容
python scripts/memory_api.py list

# 尝试不同的搜索词
python scripts/memory_api.py search Agent
```

### 问题：编码错误

确保使用 UTF-8 编码：

```bash
$env:PYTHONUTF8=1
python scripts/memory_api.py summary
```

---

## 📚 相关文件

- `scripts/memory_tool.py` - 单条记忆编码/解码
- `scripts/memory_merge.py` - 记忆合并工具
- `scripts/memory_api.py` - 记忆访问 API
- `memory/memories.qmem` - 合并的记忆文件

---

**最后更新**: 2026-03-11  
**版本**: 1.0
