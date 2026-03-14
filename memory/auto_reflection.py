#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Reflection Worker - 自动反思工作流

功能:
1. 定期触发反思（每 6 小时）
2. 失败 3 次触发反思
3. 用户纠正触发反思
4. 自动写入 SQLite + JSON 文件

作者：青 (Qing)
创建日期：2026-03-14
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from memory_migration import MemoryHook
from memory_vault_v2 import search_memory_optimized, get_memory_stats

# 初始化钩子
memory_hook = MemoryHook()

def read_recent_episodes(n: int = 50) -> list:
    """读取最近 N 条情景记忆"""
    results = search_memory_optimized(
        query="recent task action",
        top_k=n,
        min_similarity=0.3,
        memory_type="episodic"
    )
    return results

def analyze_episodes(episodes: list) -> dict:
    """分析情景记忆，提取教训"""
    # 简化分析：提取失败的任务
    lessons = []
    mistakes = []
    successes = []
    
    for ep in episodes:
        text = ep.get('memory_text', '')
        mem_type = ep.get('memory_type', '')
        
        if '失败' in text or 'failed' in text.lower():
            mistakes.append(text[:200])
            lessons.append(f"避免：{text[:100]}")
        elif '成功' in text or 'success' in text.lower():
            successes.append(text[:200])
            lessons.append(f"保持：{text[:100]}")
    
    return {
        'episodes_analyzed': len(episodes),
        'mistakes': mistakes[:10],
        'successes': successes[:10],
        'lessons': lessons[:20],
        'timestamp': datetime.now().isoformat()
    }

def run_periodic_reflection():
    """定期反思（每 6 小时）"""
    print("\n" + "="*60)
    print("定期反思 (Periodic Reflection)")
    print("="*60)
    
    # 读取最近情景记忆
    episodes = read_recent_episodes(50)
    print(f"📊 读取 {len(episodes)} 条情景记忆")
    
    # 分析
    analysis = analyze_episodes(episodes)
    print(f"📈 提取 {len(analysis['lessons'])} 条教训")
    
    # 触发钩子（自动写入 SQLite）
    memory_hook.on_reflection({
        "trigger_type": "periodic",
        "trigger_data": {
            "episodes_count": len(episodes),
            "interval": "6 hours"
        },
        "analysis": analysis,
        "lessons": analysis['lessons']
    })
    
    # 同时写入 JSON 文件（兼容旧系统）
    lessons_path = Path(__file__).parent.parent / ".learnings" / "LEARNINGS.md"
    if lessons_path.exists():
        with open(lessons_path, 'a', encoding='utf-8') as f:
            f.write(f"\n\n## [REFL-{datetime.now().strftime('%Y%m%d-%H%M')}] 定期反思\n\n")
            f.write(f"**时间**: {analysis['timestamp']}\n\n")
            f.write(f"**分析**: {len(episodes)} 条情景记忆\n\n")
            for lesson in analysis['lessons'][:5]:
                f.write(f"- {lesson}\n")
    
    print(f"✅ 反思已记录到 SQLite + LEARNINGS.md")
    print("="*60)
    
    return analysis

def run_error_reflection(task_name: str, failure_count: int):
    """错误触发反思（失败 3 次）"""
    print(f"\n🔴 错误反思：{task_name} 失败{failure_count}次")
    
    memory_hook.on_reflection({
        "trigger_type": "error",
        "trigger_data": {
            "task_name": task_name,
            "failure_count": failure_count
        },
        "lessons": [f"{task_name} 失败{failure_count}次，必须换方法"]
    })
    
    print(f"✅ 反思已记录")

def run_user_correction_reflection(correction_text: str):
    """用户纠正触发反思"""
    print(f"\n👤 用户纠正反思")
    
    memory_hook.on_reflection({
        "trigger_type": "user_feedback",
        "trigger_data": {
            "correction": correction_text
        },
        "lessons": [f"用户纠正：{correction_text[:100]}"]
    })
    
    print(f"✅ 反思已记录")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python auto_reflection.py periodic    # 定期反思")
        print("  python auto_reflection.py error <任务名> <失败次数>")
        print("  python auto_reflection.py user <纠正内容>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'periodic':
        run_periodic_reflection()
    
    elif command == 'error':
        if len(sys.argv) < 4:
            print("❌ 请提供任务名和失败次数")
            sys.exit(1)
        task_name = sys.argv[2]
        failure_count = int(sys.argv[3])
        run_error_reflection(task_name, failure_count)
    
    elif command == 'user':
        if len(sys.argv) < 3:
            print("❌ 请提供纠正内容")
            sys.exit(1)
        correction_text = ' '.join(sys.argv[2:])
        run_user_correction_reflection(correction_text)
    
    else:
        print(f"❌ 未知命令：{command}")
        sys.exit(1)
