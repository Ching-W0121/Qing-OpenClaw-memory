#!/usr/bin/env python3
"""
飞书记忆查询命令

在飞书中发送命令查询记忆（包括电脑端）
"""

import json
import sys
import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta

# 数据库路径
DB_PATH = Path(__file__).parent / 'database' / 'optimized_memory.db'

# 设置 UTF-8 编码
sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', buffering=1, errors='replace')

def get_memories(query=None, platform=None, limit=20, days=7):
    """获取记忆"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    if query:
        # 搜索查询
        cursor.execute('''
            SELECT timestamp, channel_id, content
            FROM episodes
            WHERE timestamp > ? AND (content LIKE ? OR channel_id LIKE ?)
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (cutoff_date, f'%{query}%', f'%{query}%', limit))
    elif platform:
        # 按平台查询
        cursor.execute('''
            SELECT timestamp, channel_id, content
            FROM episodes
            WHERE timestamp > ? AND channel_id LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (cutoff_date, f'{platform}_%', limit))
    else:
        # 查询所有
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
        channel = row['channel_id']
        platform = channel.split('_')[0] if channel else 'unknown'
        memories.append({
            'timestamp': row['timestamp'],
            'platform': platform,
            'channel': channel,
            'content': row['content']
        })
    
    return memories

def format_memories(memories, include_stats=False):
    """格式化记忆输出"""
    if not memories:
        return '没有找到记忆记录'
    
    lines = []
    lines.append('🧠 记忆查询结果')
    lines.append('=' * 50)
    lines.append(f'时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    lines.append(f'数量：{len(memories)} 条')
    lines.append('')
    
    # 统计
    platform_counts = {}
    for mem in memories:
        p = mem['platform']
        platform_counts[p] = platform_counts.get(p, 0) + 1
    
    lines.append('平台分布:')
    for p, count in sorted(platform_counts.items()):
        icon = '📱' if p == 'feishu' else '💻' if p == 'webchat' else '📲'
        lines.append(f'  {icon} {p}: {count} 条')
    lines.append('')
    
    # 最近记忆
    lines.append('最近记忆:')
    for i, mem in enumerate(memories[:20], 1):
        time_str = mem['timestamp'].split('T')[1][:8] if 'T' in mem['timestamp'] else '?'
        platform_tag = '📱' if mem['platform'] == 'feishu' else '💻' if mem['platform'] == 'webchat' else '📲'
        content = mem['content'][:80].replace('\n', ' ')
        lines.append(f'{i}. {platform_tag} [{mem["platform"]}] {time_str}: {content}...')
    
    if len(memories) > 20:
        lines.append(f'... 还有 {len(memories) - 20} 条记忆')
    
    lines.append('')
    lines.append('=' * 50)
    lines.append('提示: 使用 /memory search <关键词> 搜索记忆')
    
    return '\n'.join(lines)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print('用法:')
        print('  python feishu_memory_command.py recent [limit]  - 查看最近记忆')
        print('  python feishu_memory_command.py search <关键词> - 搜索记忆')
        print('  python feishu_memory_command.py platform <平台> - 查看特定平台')
        print('  python feishu_memory_command.py stats           - 查看统计')
        return
    
    command = sys.argv[1]
    
    if command == 'recent':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        memories = get_memories(limit=limit, days=days)
        print(format_memories(memories))
    
    elif command == 'search':
        query = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else ''
        if not query:
            print('请提供搜索关键词')
            return
        memories = get_memories(query=query, limit=20, days=30)
        print(format_memories(memories))
    
    elif command == 'platform':
        platform = sys.argv[2] if len(sys.argv) > 2 else 'all'
        if platform == 'all':
            platform = None
        memories = get_memories(platform=platform, limit=20, days=7)
        print(format_memories(memories))
    
    elif command == 'stats':
        memories = get_memories(limit=1000, days=365)
        print(format_memories(memories, include_stats=True))
    
    else:
        print(f'未知命令：{command}')

if __name__ == '__main__':
    main()
