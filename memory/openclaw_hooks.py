#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Hook Integration - 统一钩子集成模块

用法:
    from openclaw_hooks import task_success, task_failure, log_reflection
    
    # 任务成功
    task_success("browser_act", {"method": "standard"})
    
    # 任务失败
    task_failure("git_push", Exception("连接失败"))
    
    # 反思记录
    log_reflection(["必须等待 10 秒"], "error")
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from memory_migration import MemoryHook

# 全局钩子实例
memory_hook = MemoryHook()

# 失败计数器
_failure_counts = {}

def task_success(task_name: str, details: dict):
    """
    任务成功包装器
    
    Args:
        task_name: 任务名称
        details: 详细信息
    """
    memory_hook.on_task_complete(task_name, "success", details)
    print(f"📝 记忆已记录：{task_name} (成功)")

def task_failure(task_name: str, error: Exception, details: dict = None):
    """
    任务失败包装器
    
    Args:
        task_name: 任务名称
        error: 异常对象
        details: 详细信息
    """
    # 增加失败计数
    _failure_counts[task_name] = _failure_counts.get(task_name, 0) + 1
    count = _failure_counts[task_name]
    
    # 记录失败
    memory_hook.on_task_complete(
        task_name, 
        "failed", 
        {"error": str(error), **(details or {})}
    )
    print(f"📝 失败已记录：{task_name} (失败{count}次)")
    
    # 达到阈值，触发反思
    if count >= 3:
        log_reflection(
            [f"{task_name} 失败 3 次，需要换方法"],
            "error",
            {"task_name": task_name, "error": str(error)}
        )
        # 重置计数
        _failure_counts[task_name] = 0

def log_reflection(lessons: list, trigger_type: str = "manual", trigger_data: dict = None):
    """
    记录反思
    
    Args:
        lessons: 教训列表
        trigger_type: 触发类型 (periodic/error/user_feedback/manual)
        trigger_data: 触发数据
    """
    memory_hook.on_reflection({
        "trigger_type": trigger_type,
        "trigger_data": trigger_data or {},
        "lessons": lessons
    })
    print(f"📝 反思已记录：{len(lessons)} 条教训 ({trigger_type})")

def setup_hooks():
    """设置钩子（在程序启动时调用）"""
    print("✅ 记忆钩子已激活")
    print("   - task_success: 任务成功自动记录")
    print("   - task_failure: 任务失败自动记录 + 反思触发")
    print("   - log_reflection: 反思自动写入")
    return memory_hook

# ==================== 使用示例 ====================

if __name__ == '__main__':
    # 设置钩子
    setup_hooks()
    
    # 示例：任务成功
    task_success("browser_act", {"method": "standard", "duration": "5s"})
    
    # 示例：任务失败
    try:
        raise Exception("测试错误")
    except Exception as e:
        task_failure("git_push", e)
    
    # 示例：反思记录
    log_reflection(
        ["必须等待 10 秒让 React 完全加载", "操作前必须检索记忆"],
        trigger_type="error",
        trigger_data={"action": "browser_act"}
    )
    
    # 示例：用户纠正
    log_reflection(
        ["用户纠正：不要编造数据，实事求是"],
        trigger_type="user_feedback"
    )
    
    print("\n✅ 所有钩子测试完成")
