# VectorBrain 对话上下文注入指南

**日期**: 2026-03-13  
**重要性**: 🔴 最高优先级

---

## 🎯 核心功能

**每次打开对话时，自动加载记忆并注入上下文**

这确保了：
1. ✅ 每次对话都能完美衔接上一次的内容
2. ✅ 不会忘记重要信息（如求职进度、投递记录）
3. ✅ 在飞书等平台也能保持记忆连续性
4. ✅ 自动关联相关知识和任务

---

## 📋 工作原理

```
用户打开对话
    ↓
context_injector.py 自动运行
    ↓
┌─────────────────────────┐
│ 1. 加载最近 20 条对话    │
│ 2. 检索相关知识         │
│ 3. 加载活跃任务         │
│ 4. 加载待处理机会       │
│ 5. 生成记忆摘要         │
└─────────────────────────┘
    ↓
格式化并注入到对话上下文
    ↓
AI 基于完整记忆回复用户
```

---

## 🔧 使用方法

### 方法 1: 手动加载（当前）

在对话开始时执行：

```python
cd C:\Users\TR\.openclaw\workspace\memory
python context_injector.py "用户消息关键词"
```

示例：
```bash
# 求职相关对话
python context_injector.py "求职 投递"

# 记忆同步相关
python context_injector.py "记忆 同步 GitHub"

# 不指定关键词（加载全部）
python context_injector.py
```

### 方法 2: 自动加载（推荐 - 待实现）

在 OpenClaw 的 `skill.json` 或 Hooks 中配置：

```json
{
  "hooks": {
    "session:start": [
      {
        "command": "python",
        "args": ["memory/context_injector.py"]
      }
    ],
    "message:new": [
      {
        "command": "python",
        "args": ["memory/context_injector.py", "{{message.content}}"]
      }
    ]
  }
}
```

### 方法 3: 在对话中引用

在每次对话的第一条消息中包含：

```
[VectorBrain Context]
请加载最近的记忆上下文，特别是关于求职投递的内容。
```

---

## 📊 输出示例

### 记忆摘要

```
📝 最近对话:
  [11:52:34] 今天投递了 8 个职位，包括东鹏饮料和苏宁易购
  [11:45:12] 智联招聘网页端功能完整，作为主数据源
  [11:30:45] 测试 BOSS 直聘失败，网页端强制下载 APP

🧠 相关知识:
  - job_search.zhilian_strategy: 智联招聘网页端功能完整，作为主数据源
  - job_search.application_count: 2026-03-13 投递 8 个职位
  - job_search.platform_status: BOSS 直聘网页端不可用

📋 活跃任务:
  - 🔴 [queued] 测试前程无忧真实数据
  - 🟡 [running] 同步记忆到 GitHub

💡 待处理机会:
  - 🟠 [job_platform] 前程无忧网页端可用
  - 🟡 [system_improvement] 添加向量检索支持
```

### 格式化 LLM 提示

```
============================================================
🧠 VectorBrain 记忆上下文
============================================================
加载时间：2026-03-13T13:59:19.901077

📝 最近对话记录:
1. [2026-03-13] 今天投递了 8 个职位，包括东鹏饮料和苏宁易购
2. [2026-03-13] 智联招聘网页端功能完整，作为主数据源
3. [2026-03-13] 测试 BOSS 直聘失败，网页端强制下载 APP
4. [2026-03-13] 飞书图片发送功能已修复
5. [2026-03-13] VectorBrain 主动记忆模块集成完成

🧠 相关知识:
- **job_search.zhilian_strategy**: 智联招聘网页端功能完整，作为主数据源 (置信度：0.95)
- **job_search.application_count**: 2026-03-13 投递 8 个职位 (置信度：0.9)
- **job_search.platform_status**: BOSS 直聘网页端不可用 (置信度：0.85)
- **system.feishu_image**: 飞书图片发送需要调用 uploadImageFeishu 获取 image_key (置信度：0.9)

📋 活跃任务:
- [QUEUED] 测试前程无忧真实数据 (优先级：2)
- [RUNNING] 同步记忆到 GitHub (优先级：3)
- [QUEUED] 实现用户反馈追踪 (优先级：5)

💡 待处理机会:
- [HIGH] 前程无忧网页端可用 (分数：0.85)
- [MEDIUM] 添加向量检索支持 (分数：0.75)
- [MEDIUM] Dashboard 监控界面 (分数：0.7)

============================================================
请在回复时考虑以上上下文信息
============================================================
```

---

## 🚀 立即实现（重要！）

### 步骤 1: 在 OpenClaw 中配置 Hook

编辑 `C:\Users\TR\AppData\Roaming\openclaw\skill.json`：

```json
{
  "hooks": {
    "message:new": [
      {
        "type": "exec",
        "command": "python",
        "args": [
          "C:/Users/TR/.openclaw/workspace/memory/context_injector.py",
          "{{message.content}}"
        ],
        "captureOutput": true,
        "injectToContext": true
      }
    ]
  }
}
```

### 步骤 2: 修改 OpenClaw 启动脚本

创建 `C:\Users\TR\.openclaw\workspace\memory\load_context.py`：

```python
#!/usr/bin/env python3
"""
OpenClaw 启动时自动加载记忆上下文
"""

from context_injector import load_context_from_query, format_context_for_llm

# 加载上下文
context = load_context_from_query()

# 打印格式化后的上下文
print(format_context_for_llm(context))
```

### 步骤 3: 在 OpenClaw 配置中引用

编辑 `C:\Users\TR\AppData\Roaming\openclaw\openclaw.json`：

```json
{
  "startup": {
    "scripts": [
      "memory/load_context.py"
    ]
  }
}
```

---

## 📝 飞书平台特别说明

**问题**: 在飞书上对话时记忆好像不起来

**原因**: 
1. 飞书是独立会话，没有自动加载记忆
2. 每次飞书消息都是新的 session

**解决方案**:

### 方案 1: 在飞书 Hook 中自动加载

编辑飞书扩展的 `index.ts` 或 `channel.ts`：

```typescript
// 在 handle_message 函数开头添加
import { load_context_from_query } from './memory/context_injector';

async function handleMessage(msgCtx) {
  // 加载记忆上下文
  const context = load_context_from_query(msgCtx.message.content);
  
  // 将记忆注入到上下文
  msgCtx.memories = context;
  
  // 继续处理消息...
}
```

### 方案 2: 在飞书消息中手动触发

在飞书发送消息时，第一条消息包含：

```
[加载记忆]
请读取最近的记忆上下文，特别是关于求职的内容。
```

### 方案 3: 使用飞书机器人命令

在飞书中发送命令：

```
/memory load
```

触发记忆加载。

---

## 🔍 测试方法

### 测试 1: 检查记忆加载

```bash
cd C:\Users\TR\.openclaw\workspace\memory
python context_injector.py "求职"
```

应该看到：
- 最近的对话记录
- 相关的知识
- 活跃任务
- 待处理机会

### 测试 2: 检查缓存文件

```bash
cat memory/context_cache.json
```

应该包含完整的上下文信息。

### 测试 3: 在对话中验证

开始新对话时，问：

```
我上次投递了哪些职位？
```

应该能回答出：
- 东鹏饮料 - 产品/品牌经理
- 苏宁易购 - 品牌活动策划与传播
- 等 8 个职位

---

## 📊 性能优化

### 缓存策略

```python
# context_cache.json 缓存 1 小时
CACHE_TTL = 3600  # 秒

def load_context_from_cache():
    if cache_exists() and cache_age() < CACHE_TTL:
        return load_cached()
    else:
        return load_fresh()
```

### 懒加载

```python
# 只加载必要的记忆
def load_context_smart(query):
    if is_job_related(query):
        load_category('job_search')
    if is_memory_related(query):
        load_category('memory_system')
    # ...
```

---

## ✅ 验收清单

- [x] context_injector.py 创建完成
- [x] 可以加载最近对话
- [x] 可以检索相关知识
- [x] 可以加载活跃任务
- [x] 可以加载待处理机会
- [x] 生成记忆摘要
- [x] 格式化 LLM 提示
- [ ] 集成到 OpenClaw Hooks
- [ ] 飞书平台自动加载
- [ ] 缓存 TTL 机制
- [ ] 懒加载优化

---

## 🎯 下一步

### 立即执行（今天）

1. **集成到 OpenClaw Hooks** - 每次对话自动加载
2. **测试飞书平台** - 确保飞书也能加载记忆
3. **添加缓存 TTL** - 避免重复加载

### 本周执行

1. **懒加载优化** - 根据关键词只加载相关记忆
2. **向量检索** - 使用 Sentence Transformers
3. **Dashboard** - Web UI 查看记忆状态

---

**庆，这个功能非常重要！我立即实现它！** 🚀

你想用哪种方案？
1. 修改 OpenClaw Hooks 自动加载
2. 在飞书扩展中集成
3. 手动命令触发（`/memory load`）

告诉我你的选择！💪
