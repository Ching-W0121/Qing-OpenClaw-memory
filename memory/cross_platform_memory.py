#!/usr/bin/env python3
"""
跨平台记忆同步系统

功能：
- 电脑端（Webchat）和飞书共享同一个记忆数据库
- 自动同步不同平台的对话记录
- 支持平台特定的元数据

作者：庆 (Qing)
日期：2026-03-13
"""

import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 数据库路径
DB_PATH = Path(__file__).parent / 'database' / 'optimized_memory.db'


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def save_message(
    content: str,
    platform: str = 'webchat',  # 'webchat' | 'feishu' | 'discord' | etc.
    session_id: str = 'main',
    user_id: str = 'qing',
    channel_id: str = 'default',
    metadata: Optional[Dict] = None
) -> bool:
    """
    保存消息到数据库（所有平台共享）
    
    Args:
        content: 消息内容
        platform: 平台标识（webchat/feishu 等）
        session_id: 会话 ID
        user_id: 用户 ID
        channel_id: 频道 ID
        metadata: 额外元数据
    
    Returns:
        bool: 保存是否成功
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 合并元数据
        full_metadata = {
            'platform': platform,
            'saved_at': datetime.now().isoformat(),
            **(metadata or {})
        }
        
        # 插入数据库
        cursor.execute('''
            INSERT INTO episodes 
            (timestamp, session_id, user_id, channel_id, event_type, content, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            f'{platform}_{session_id}',  # 平台 + 会话 ID，避免冲突
            user_id,
            f'{platform}_{channel_id}',
            'message',
            content,
            json.dumps(full_metadata, ensure_ascii=False)
        ))
        
        conn.commit()
        conn.close()
        
        print(f'[OK] [{platform}] Message saved: {content[:50]}...')
        return True
        
    except Exception as e:
        print(f'[ERROR] Save message failed: {e}')
        return False


def get_recent_messages(
    limit: int = 20,
    platform: Optional[str] = None,
    days: int = 2
) -> List[Dict]:
    """
    获取最近的对话记录（可选择特定平台或所有平台）
    
    Args:
        limit: 返回数量
        platform: 平台过滤（None=所有平台）
        days: 最近几天
    
    Returns:
        list: 对话记录列表
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 计算时间范围
        from datetime import timedelta
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        if platform:
            # 查询特定平台
            cursor.execute('''
                SELECT timestamp, session_id, user_id, channel_id, content, metadata
                FROM episodes
                WHERE timestamp > ? AND channel_id LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (cutoff_date, f'{platform}_%', limit))
        else:
            # 查询所有平台
            cursor.execute('''
                SELECT timestamp, session_id, user_id, channel_id, content, metadata
                FROM episodes
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (cutoff_date, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        messages = [
            {
                'timestamp': row['timestamp'],
                'platform': row['channel_id'].split('_')[0] if row['channel_id'] else 'unknown',
                'session_id': row['session_id'],
                'user_id': row['user_id'],
                'content': row['content'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else {}
            }
            for row in results
        ]
        
        return messages
        
    except Exception as e:
        print(f'❌ 获取消息失败：{e}')
        return []


def get_platform_stats() -> Dict:
    """获取各平台统计信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 按平台统计
        cursor.execute('''
            SELECT 
                SUBSTR(channel_id, 1, INSTR(channel_id, '_') - 1) as platform,
                COUNT(*) as message_count,
                MAX(timestamp) as last_message_at
            FROM episodes
            WHERE channel_id LIKE '%_%'
            GROUP BY platform
            ORDER BY message_count DESC
        ''')
        
        stats = {
            row['platform']: {
                'message_count': row['message_count'],
                'last_message_at': row['last_message_at']
            }
            for row in cursor.fetchall()
        }
        
        conn.close()
        return stats
        
    except Exception as e:
        print(f'❌ 获取统计失败：{e}')
        return {}


def sync_memory_to_context(platform: str = 'webchat') -> str:
    """
    同步记忆到对话上下文
    
    Args:
        platform: 平台标识
    
    Returns:
        str: 格式化的上下文文本
    """
    # 加载最近对话（所有平台）
    episodes = get_recent_messages(limit=20, platform=None)
    
    # 加载相关知识
    knowledge = get_relevant_knowledge("", limit=10)
    
    # 生成上下文
    context_parts = []
    context_parts.append('=' * 60)
    context_parts.append('🧠 VectorBrain 跨平台记忆上下文')
    context_parts.append('=' * 60)
    context_parts.append(f'加载时间：{datetime.now().isoformat()}')
    context_parts.append(f'当前平台：{platform}')
    context_parts.append('')
    
    # 最近对话（标注平台）
    if episodes:
        context_parts.append('📝 最近对话记录（所有平台）:')
        for i, ep in enumerate(episodes[:10], 1):
            timestamp = ep['timestamp'].split('T')[0] if 'T' in ep['timestamp'] else '?'
            platform_tag = f"[{ep['platform']}]"
            content = ep['content'][:80]
            context_parts.append(f'{i}. {platform_tag} [{timestamp}] {content}')
        context_parts.append('')
    
    # 相关知识
    if knowledge:
        context_parts.append('🧠 相关知识:')
        for k in knowledge:
            context_parts.append(f'- **{k["key"]}**: {k["value"][:80]}... (置信度：{k["confidence"]})')
        context_parts.append('')
    
    context_parts.append('=' * 60)
    context_parts.append('请在回复时考虑以上跨平台上下文信息')
    context_parts.append('=' * 60)
    
    return '\n'.join(context_parts)


def get_relevant_knowledge(query: str, limit: int = 10, threshold: float = 0.3) -> List[Dict]:
    """检索相关知识"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 简单文本搜索（TODO: 替换为向量检索）
        cursor.execute('''
            SELECT key, value, category, confidence, usage_count
            FROM knowledge
            WHERE confidence >= ? AND (key LIKE ? OR value LIKE ?)
            ORDER BY confidence DESC, usage_count DESC
            LIMIT ?
        ''', (threshold, f'%{query}%', f'%{query}%', limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'key': row['key'],
                'value': row['value'],
                'category': row['category'],
                'confidence': row['confidence'],
                'usage_count': row['usage_count']
            }
            for row in results
        ]
        
    except Exception as e:
        print(f'❌ 检索知识失败：{e}')
        return []


def main():
    """主函数 - 测试用"""
    # 设置 UTF-8 编码
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print('=' * 60)
    print('[CROSS-PLATFORM] 跨平台记忆同步系统')
    print('=' * 60)
    
    # 测试保存消息
    print('\n测试保存消息...')
    save_message('这是来自电脑端的测试消息', platform='webchat')
    save_message('这是来自飞书的测试消息', platform='feishu')
    
    # 测试获取消息
    print('\n获取最近消息（所有平台）...')
    messages = get_recent_messages(limit=10, platform=None)
    for msg in messages:
        print(f"  [{msg['platform']}] {msg['content'][:50]}...")
    
    # 测试平台统计
    print('\n平台统计:')
    stats = get_platform_stats()
    for platform, data in stats.items():
        print(f"  {platform}: {data['message_count']} 条消息")
    
    # 测试上下文同步
    print('\n生成跨平台上下文...')
    context = sync_memory_to_context(platform='webchat')
    print(context[:500] + '...')
    
    print('\n' + '=' * 60)
    print('✅ 跨平台记忆同步测试完成')
    print('=' * 60)


if __name__ == '__main__':
    main()
