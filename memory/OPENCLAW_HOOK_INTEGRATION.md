# OpenClaw 记忆钩子集成指南

**版本**: v1.0  
**日期**: 2026-03-14

---

## 🎯 目标

在 OpenClaw 决策工作流初期增加钩子，实现：
- 任务完成后自动记录记忆
- 反思记录自动写入数据库
- 记忆自我进化

---

## 🔧 集成步骤

### 1. 导入钩子模块

在 `memory/memory_guard.py` 或主工作流文件中添加：

```python
from memory_migration import MemoryHook

# 初始化钩子（在程序启动时）
memory_hook = MemoryHook()
```

---

### 2. 任务执行钩子

**修改任务执行函数**：

```python
# 原始代码
def execute_browser_action(action_type, context):
    try:
        result = browser.act(**context)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

# ✅ 添加钩子后
def execute_browser_action(action_type, context):
    try:
        result = browser.act(**context)
        
        # 📝 钩子：任务完成自动记录
        memory_hook.on_task_complete(
            task_name=action_type,
            outcome="success",
            details={"method": "standard_flow", "context": context}
        )
        
        return {"status": "success", "result": result}
    
    except Exception as e:
        # 📝 钩子：失败自动记录
        memory_hook.on_task_complete(
            task_name=action_type,
            outcome="failed",
            details={"error": str(e), "context": context}
        )
        
        return {"status": "failed", "error": str(e)}
```

---

### 3. 反思系统钩子

**修改反思函数**：

```python
# 原始代码
def run_reflection():
    episodes = read_recent_episodes(50)
    analysis = llm.analyze(episodes)
    update_lessons_json(analysis.lessons)
    return analysis

# ✅ 添加钩子后
def run_reflection():
    episodes = read_recent_episodes(50)
    analysis = llm.analyze(episodes)
    
    # 更新传统文件
    update_lessons_json(analysis.lessons)
    
    # 📝 钩子：反思记录自动写入数据库
    memory_hook.on_reflection({
        "trigger_type": "periodic",
        "trigger_data": {"episodes_count": len(episodes)},
        "analysis": analysis,
        "lessons": analysis.lessons
    })
    
    return analysis
```

---

### 4. 失败计数器钩子

**修改失败处理**：

```python
# 在 failure_tracker 中
def handle_failure(action_type, error):
    # 增加计数
    failure_count[action_type] += 1
    
    # 📝 钩子：失败自动记录
    memory_hook.on_task_complete(
        task_name=f"failure_{action_type}",
        outcome="failed",
        details={
            "error": str(error),
            "failure_count": failure_count[action_type],
            "threshold": 3
        }
    )
    
    # 达到阈值触发反思
    if failure_count[action_type] >= 3:
        memory_hook.on_reflection({
            "trigger_type": "error",
            "trigger_data": {
                "action_type": action_type,
                "failure_count": failure_count[action_type]
            },
            "lessons": [f"{action_type} 失败 3 次，需要换方法"]
        })
```

---

## 📋 完整集成示例

### memory/openclaw_hook_integration.py

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 记忆钩子集成模块

用法:
    from openclaw_hook_integration import setup_hooks
    
    # 在程序启动时设置钩子
    setup_hooks()
"""

from memory_migration import MemoryHook
from pathlib import Path

# 初始化钩子
memory_hook = MemoryHook()

def setup_hooks():
    """设置全局钩子"""
    print("✅ 记忆钩子已激活")
    print("   - on_task_complete: 任务完成自动记录")
    print("   - on_reflection: 反思记录自动写入")
    return memory_hook

def task_success(task_name: str, details: dict):
    """任务成功包装器"""
    memory_hook.on_task_complete(task_name, "success", details)

def task_failure(task_name: str, error: Exception, details: dict = None):
    """任务失败包装器"""
    memory_hook.on_task_complete(
        task_name, 
        "failed", 
        {"error": str(error), **(details or {})}
    )

def log_reflection(lessons: list, trigger_type: str = "manual"):
    """记录反思"""
    memory_hook.on_reflection({
        "trigger_type": trigger_type,
        "lessons": lessons
    })

# ==================== 使用示例 ====================

if __name__ == '__main__':
    # 设置钩子
    hook = setup_hooks()
    
    # 示例：任务成功
    task_success("browser_act", {"method": "standard"})
    
    # 示例：任务失败
    try:
        raise Exception("测试错误")
    except Exception as e:
        task_failure("git_push", e)
    
    # 示例：反思记录
    log_reflection(
        ["必须等待 10 秒让 React 完全加载"],
        trigger_type="error"
    )
```

---

## 🎯 实际集成点

### 1. browser 自动化

**文件**: `memory/memory_guard.py`

```python
# 在 check_before_action 函数后添加
def execute_with_hook(action_type, context):
    from openclaw import browser
    
    try:
        # 执行操作
        result = browser.act(kind=context['kind'], ref=context['ref'])
        
        # ✅ 成功钩子
        memory_hook.on_task_complete(
            task_name=action_type,
            outcome="success",
            details={"context": context}
        )
        
        return result
    
    except Exception as e:
        # ✅ 失败钩子
        memory_hook.on_task_complete(
            task_name=action_type,
            outcome="failed",
            details={"error": str(e), "context": context}
        )
        
        raise
```

---

### 2. Git 操作

**文件**: 任何 git 操作脚本

```python
# 在 git push 后添加
def git_push_with_hook():
    import subprocess
    
    try:
        result = subprocess.run(["git", "push"], capture_output=True)
        
        if result.returncode == 0:
            memory_hook.on_task_complete(
                task_name="git_push",
                outcome="success",
                details={"output": result.stdout.decode()}
            )
        else:
            memory_hook.on_task_complete(
                task_name="git_push",
                outcome="failed",
                details={"error": result.stderr.decode()}
            )
    
    except Exception as e:
        memory_hook.on_task_complete(
            task_name="git_push",
            outcome="failed",
            details={"error": str(e)}
        )
```

---

### 3. 文件操作

**文件**: 任何文件写入操作

```python
# 在文件写入后添加
def write_file_with_hook(file_path, content):
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        
        memory_hook.on_task_complete(
            task_name="file_write",
            outcome="success",
            details={"file": str(file_path), "size": len(content)}
        )
    
    except Exception as e:
        memory_hook.on_task_complete(
            task_name="file_write",
            outcome="failed",
            details={"error": str(e), "file": str(file_path)}
        )
```

---

### 4. 反思系统

**文件**: `memory/reflection-worker.js` 或 Python 版本

```python
# 在反思完成后添加
def run_reflection_with_hook():
    # 原有反思逻辑
    analysis = run_reflection()
    
    # ✅ 钩子：反思记录自动写入
    memory_hook.on_reflection({
        "trigger_type": "periodic",
        "trigger_data": {
            "episodes_analyzed": 50,
            "duration": "5 minutes"
        },
        "analysis": analysis,
        "lessons": analysis.get('lessons', [])
    })
```

---

## 📊 钩子效果监控

### 查看自动记录的记忆

```bash
cd memory
python memory_vault.py search "auto_generated" 10
```

### 统计钩子触发次数

```python
from memory_vault import search_memory

# 查询自动生成的记忆
auto_memories = search_memory("auto_generated", top_k=100)

print(f"钩子触发次数：{len(auto_memories)}")
print(f"任务完成：{len([m for m in auto_memories if 'hook' in m['metadata'] and m['metadata']['hook'] == 'on_task_complete'])}")
print(f"反思记录：{len([m for m in auto_memories if 'hook' in m['metadata'] and m['metadata']['hook'] == 'on_reflection'])}")
```

---

## ✅ 集成检查清单

- [ ] 导入 MemoryHook 模块
- [ ] 初始化钩子（程序启动时）
- [ ] 任务执行函数添加成功/失败钩子
- [ ] 反思系统添加反思记录钩子
- [ ] 失败计数器添加阈值触发钩子
- [ ] 测试钩子触发（手动执行任务）
- [ ] 验证数据库记录（search_memory）
- [ ] 监控钩子效果（统计触发次数）

---

## 🚀 最佳实践

### 1. 钩子命名规范

```python
# ✅ 好的命名
on_task_complete(task_name="browser_act", ...)
on_reflection({"trigger_type": "error", ...})

# ❌ 避免
on_task_complete(task_name="xxx", ...)  # 无意义名称
```

### 2. 元数据完整性

```python
# ✅ 完整元数据
{
    "task_name": "browser_act",
    "outcome": "success",
    "details": {
        "method": "standard",
        "duration": "5s",
        "context": {...}
    }
}

# ❌ 不完整
{"status": "ok"}
```

### 3. 避免重复记录

```python
# ✅ 检查是否已存在
if not memory_exists(task_name, outcome):
    memory_hook.on_task_complete(...)

# ❌ 无条件记录
memory_hook.on_task_complete(...)  # 可能重复
```

---

**版本**: v1.0  
**最后更新**: 2026-03-14  
**作者**: 青 (Qing)
