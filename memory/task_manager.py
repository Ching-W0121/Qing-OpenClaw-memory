#!/usr/bin/env python3
"""
VectorBrain 任务管理器

功能：
- 轮询任务队列
- 抢占并执行任务
- 回写执行结果
- 超时处理

作者：庆 (Qing)
日期：2026-03-13
"""

import os
import sys
import time
import signal
from pathlib import Path
from datetime import datetime, timedelta

# 导入 VectorBrain 模块
from vectorbrain_integration import (
    claim_task,
    complete_task,
    fail_task,
    log,
    TASK_DB
)

# 配置
WORKER_ID = f"worker_{os.getpid()}"
POLL_INTERVAL = 10  # 轮询间隔（秒）
TASK_TIMEOUT = 30 * 60  # 任务超时（秒）

# 运行标志
running = True

def signal_handler(sig, frame):
    """处理中断信号"""
    global running
    log(f'收到信号 {sig}，准备退出...')
    running = False

# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def execute_task(task):
    """
    执行任务
    
    Args:
        task: 任务字典
    
    Returns:
        str: 执行结果
    """
    log(f'执行任务：{task["title"]}')
    
    try:
        # 根据任务类型执行不同逻辑
        if '智联招聘' in task['title'] or 'zhilian' in task['title'].lower():
            result = execute_zhilian_task(task)
        elif '前程无忧' in task['title'] or '51job' in task['title'].lower():
            result = execute_job51_task(task)
        elif '拉勾' in task['title'] or 'lagou' in task['title'].lower():
            result = execute_lagou_task(task)
        elif '记忆同步' in task['title'] or 'memory' in task['title'].lower():
            result = execute_memory_sync_task(task)
        elif '反思' in task['title'] or 'reflection' in task['title'].lower():
            result = execute_reflection_task(task)
        else:
            result = f'未知任务类型，手动处理：{task["description"]}'
        
        log(f'✅ 任务执行完成：{task["task_id"]}')
        return result
        
    except Exception as e:
        log(f'❌ 任务执行失败：{e}', 'ERROR')
        raise


def execute_zhilian_task(task):
    """执行智联招聘相关任务"""
    log('执行智联招聘任务...')
    # TODO: 实现智联招聘自动化
    return '智联招聘任务执行完成（待实现）'


def execute_job51_task(task):
    """执行前程无忧相关任务"""
    log('执行前程无忧任务...')
    # TODO: 实现前程无忧自动化
    return '前程无忧任务执行完成（待实现）'


def execute_lagou_task(task):
    """执行拉勾网相关任务"""
    log('执行拉勾网任务...')
    # TODO: 实现拉勾网自动化
    return '拉勾网任务执行完成（待实现）'


def execute_memory_sync_task(task):
    """执行记忆同步任务"""
    log('执行记忆同步任务...')
    # TODO: 实现 GitHub 记忆同步
    return '记忆同步任务执行完成（待实现）'


def execute_reflection_task(task):
    """执行反思任务"""
    log('执行反思任务...')
    
    # 调用反思脚本
    import subprocess
    script_path = Path(__file__).parent / 'reflection-worker.js'
    
    result = subprocess.run(
        ['node', str(script_path)],
        capture_output=True,
        text=True,
        timeout=300  # 5 分钟超时
    )
    
    if result.returncode == 0:
        return f'反思任务执行成功\n{result.stdout}'
    else:
        raise Exception(f'反思任务执行失败：{result.stderr}')


def cleanup_timeout_tasks():
    """清理超时任务"""
    log('清理超时任务...')
    
    try:
        import sqlite3
        
        conn = sqlite3.connect(str(TASK_DB))
        cursor = conn.cursor()
        
        # 计算超时时间
        timeout_threshold = (datetime.now() - timedelta(seconds=TASK_TIMEOUT)).isoformat()
        
        # 标记超时任务为失败
        cursor.execute('''
            UPDATE tasks
            SET status = 'failed',
                error_message = ?,
                completed_at = ?,
                updated_at = ?
            WHERE status = 'running'
            AND started_at < ?
        ''', (
                f'Task timeout after {TASK_TIMEOUT} seconds',
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                timeout_threshold
            ))
        
        timeout_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if timeout_count > 0:
            log(f'✅ 清理了 {timeout_count} 个超时任务')
        else:
            log('没有超时任务')
            
    except Exception as e:
        log(f'❌ 清理超时任务失败：{e}', 'ERROR')


def main():
    """主函数"""
    log('=' * 60)
    log(f'🤖 VectorBrain 任务管理器启动')
    log('=' * 60)
    log(f'Worker ID: {WORKER_ID}')
    log(f'轮询间隔：{POLL_INTERVAL}秒')
    log(f'任务超时：{TASK_TIMEOUT}秒')
    log('=' * 60)
    
    tasks_executed = 0
    last_cleanup = datetime.now()
    
    while running:
        try:
            # 定期清理超时任务（每 5 分钟）
            if (datetime.now() - last_cleanup).seconds > 300:
                cleanup_timeout_tasks()
                last_cleanup = datetime.now()
            
            # 尝试抢占任务
            task = claim_task(worker_id=WORKER_ID)
            
            if task:
                log(f'📋 抢占到任务：{task["title"]} (优先级：{task["priority"]})')
                
                try:
                    # 执行任务
                    result = execute_task(task)
                    
                    # 完成任务
                    complete_task(task['task_id'], result=result)
                    tasks_executed += 1
                    
                except Exception as e:
                    # 失败任务
                    fail_task(task['task_id'], error_message=str(e))
                    log(f'❌ 任务失败：{e}', 'ERROR')
            else:
                # 没有任务，等待下一轮
                time.sleep(POLL_INTERVAL)
                
        except KeyboardInterrupt:
            log('收到中断信号，退出...')
            break
        except Exception as e:
            log(f'❌ 任务管理器异常：{e}', 'ERROR')
            time.sleep(POLL_INTERVAL)
    
    # 退出统计
    log('=' * 60)
    log(f'👋 任务管理器退出')
    log(f'执行任务数：{tasks_executed}')
    log('=' * 60)


if __name__ == '__main__':
    main()
