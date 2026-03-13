#!/usr/bin/env python3
"""
飞书记忆同步工具

在飞书中手动触发记忆同步的命令
"""

import json
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# 数据库路径
DB_PATH = Path(__file__).parent / 'database' / 'optimized_memory.db'

def get_recent_memories(platform=None, limit=10):
    """获取最近记忆"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 计算时间范围（最近 2 天）
    from datetime import timedelta
    cutoff_date = (datetime.now() - timedelta(days=2)).isoformat()
    
    if platform:
        cursor.execute('''
            SELECT timestamp, channel_id, content
            FROM episodes
            WHERE timestamp > ? AND channel_id LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (cutoff_date, f'{platform}_%', limit))
    else:
        cursor.execute('''
            SELECT timestamp, channel_id, content
            FROM episodes
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (cutoff_date, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    memories = []
    for row in results:
        platform = row['channel_id'].split('_')[0] if row['channel_id'] else 'unknown'
        memories.append({
            'timestamp': row['timestamp'],
            'platform': platform,
            'content': row['content']
        })
    
    return memories

def format_memories_for_feishu(memories, current_platform='feishu'):
    """格式化为飞书消息"""
    lines = []
    lines.append('[Memory Sync]')
    lines.append('=' * 40)
    lines.append(f'Platform: {current_platform}')
    lines.append(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    lines.append('')
    lines.append('Recent Memories:')
    
    for i, mem in enumerate(memories[:10], 1):
        platform_tag = '[FS]' if mem['platform'] == 'feishu' else '[PC]'
        time_str = mem['timestamp'].split('T')[1][:8] if 'T' in mem['timestamp'] else '?'
        content = mem['content'][:60]
        lines.append(f'{i}. {platform_tag} [{mem["platform"]}] {time_str}: {content}...')
    
    lines.append('')
    lines.append('=' * 40)
    lines.append(f'Total: {len(memories)} memories')
    
    return '\n'.join(lines)

def main():
    """主函数"""
    # 获取参数
    platform = sys.argv[1] if len(sys.argv) > 1 else 'feishu'
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    # 获取记忆
    memories = get_recent_memories(platform=None, limit=limit)
    
    # 格式化输出
    output = format_memories_for_feishu(memories, platform)
    
    # 输出到 stdout
    print(output)

if __name__ == '__main__':
    main()
