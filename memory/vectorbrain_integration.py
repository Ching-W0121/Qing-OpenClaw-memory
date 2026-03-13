#!/usr/bin/env python3
"""
VectorBrain 主动记忆模块 - OpenClaw 集成版

功能：
- 实时消息记忆保存
- 向量检索注入上下文
- 任务队列系统
- 机会扫描系统

作者：庆 (Qing)
日期：2026-03-13
版本：v1.0 (融合 VectorBrain + self-improvement v3.0.1)
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import sqlite3

# 路径配置
WORKSPACE_ROOT = Path(__file__).parent.parent
MEMORY_ROOT = WORKSPACE_ROOT / 'memory'
EPISODIC_DIR = MEMORY_ROOT / 'episodic'
SEMANTIC_DIR = MEMORY_ROOT / 'semantic'
LEARNINGS_DIR = WORKSPACE_ROOT / '.learnings'
DB_DIR = MEMORY_ROOT / 'database'

# 数据库文件
EPISODIC_DB = DB_DIR / 'episodic_memory.db'
KNOWLEDGE_DB = DB_DIR / 'knowledge_memory.db'
TASK_DB = DB_DIR / 'task_queue.db'
OPPORTUNITY_DB = DB_DIR / 'opportunities.db'

# 确保目录存在
for dir_path in [EPISODIC_DIR, SEMANTIC_DIR, LEARNINGS_DIR, DB_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 日志配置
LOG_FILE = MEMORY_ROOT / 'vectorbrain.log'

def log(message, level='INFO'):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f'[{timestamp}] [{level}] {message}'
    print(log_msg, file=sys.stderr)
    
    # 写入日志文件
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    except Exception as e:
        print(f'写入日志失败：{e}', file=sys.stderr)


# ============== 数据库初始化 ==============

def init_databases():
    """初始化所有数据库"""
    init_episodic_db()
    init_knowledge_db()
    init_task_db()
    init_opportunity_db()
    log('✅ 数据库初始化完成')


def init_episodic_db():
    """初始化情景记忆数据库（对话历史）"""
    conn = sqlite3.connect(str(EPISODIC_DB))
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            session_id TEXT,
            user_id TEXT,
            channel_id TEXT,
            event_type TEXT,
            content TEXT NOT NULL,
            metadata TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引加速查询
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON episodes(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_session ON episodes(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON episodes(event_type)')
    
    conn.commit()
    conn.close()
    log('✅ 情景记忆数据库初始化完成')


def init_knowledge_db():
    """初始化知识记忆数据库（提炼知识）"""
    conn = sqlite3.connect(str(KNOWLEDGE_DB))
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            category TEXT,
            confidence REAL DEFAULT 0.5,
            usage_count INTEGER DEFAULT 0,
            last_used_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON knowledge(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_confidence ON knowledge(confidence)')
    
    conn.commit()
    conn.close()
    log('✅ 知识记忆数据库初始化完成')


def init_task_db():
    """初始化任务队列数据库"""
    conn = sqlite3.connect(str(TASK_DB))
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            priority INTEGER DEFAULT 5,
            status TEXT DEFAULT 'queued',
            assigned_to TEXT,
            started_at TEXT,
            completed_at TEXT,
            result TEXT,
            error_message TEXT,
            timeout_minutes INTEGER DEFAULT 30,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON tasks(priority)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_id ON tasks(task_id)')
    
    conn.commit()
    conn.close()
    log('✅ 任务队列数据库初始化完成')


def init_opportunity_db():
    """初始化机会发现数据库"""
    conn = sqlite3.connect(str(OPPORTUNITY_DB))
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            type TEXT,
            severity TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'pending',
            priority_score REAL DEFAULT 0.5,
            detected_at TEXT DEFAULT CURRENT_TIMESTAMP,
            processed_at TEXT,
            result TEXT,
            metadata TEXT
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON opportunities(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_severity ON opportunities(severity)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority_score ON opportunities(priority_score)')
    
    conn.commit()
    conn.close()
    log('✅ 机会发现数据库初始化完成')


# ============== 情景记忆（Episodic Memory） ==============

def save_message_to_episodic(message, session_id='main', user_id='user', channel_id='webchat'):
    """
    保存消息到情景记忆
    
    Args:
        message: 消息内容
        session_id: 会话 ID
        user_id: 用户 ID
        channel_id: 频道 ID
    
    Returns:
        bool: 保存是否成功
    """
    log(f'保存消息到情景记忆：{message[:50]}...')
    
    try:
        conn = sqlite3.connect(str(EPISODIC_DB))
        cursor = conn.cursor()
        
        # 插入消息记录
        cursor.execute('''
            INSERT INTO episodes (timestamp, session_id, user_id, channel_id, event_type, content, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            session_id,
            user_id,
            channel_id,
            'message',
            message,
            json.dumps({
                'saved_at': datetime.now().isoformat(),
                'source': 'vectorbrain_integration'
            }, ensure_ascii=False)
        ))
        
        conn.commit()
        conn.close()
        
        log(f'✅ 消息已保存到情景记忆')
        return True
        
    except Exception as e:
        log(f'❌ 保存消息失败：{e}', 'ERROR')
        return False


def load_recent_episodes(limit=50, days=2):
    """
    加载最近的对话记录
    
    Args:
        limit: 返回数量
        days: 最近几天
    
    Returns:
        list: 对话记录列表
    """
    log(f'加载最近 {days} 天的 {limit} 条对话记录')
    
    try:
        conn = sqlite3.connect(str(EPISODIC_DB))
        cursor = conn.cursor()
        
        # 计算时间范围
        from datetime import timedelta
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT timestamp, session_id, user_id, event_type, content, metadata
            FROM episodes
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (cutoff_date, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        episodes = [
            {
                'timestamp': row[0],
                'session_id': row[1],
                'user_id': row[2],
                'event_type': row[3],
                'content': row[4],
                'metadata': json.loads(row[5]) if row[5] else {}
            }
            for row in results
        ]
        
        log(f'✅ 加载到 {len(episodes)} 条对话记录')
        return episodes
        
    except Exception as e:
        log(f'❌ 加载对话记录失败：{e}', 'ERROR')
        return []


# ============== 知识记忆（Knowledge Memory） ==============

def save_to_knowledge(key, value, category='general', confidence=0.5):
    """
    保存提炼知识到知识记忆
    
    Args:
        key: 知识键（唯一标识）
        value: 知识内容
        category: 分类
        confidence: 置信度（0-1）
    
    Returns:
        bool: 保存是否成功
    """
    log(f'保存知识到知识记忆：{key}')
    
    try:
        conn = sqlite3.connect(str(KNOWLEDGE_DB))
        cursor = conn.cursor()
        
        # 使用 INSERT OR REPLACE 实现 upsert
        cursor.execute('''
            INSERT OR REPLACE INTO knowledge (key, value, category, confidence, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (key, value, category, confidence, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        log(f'✅ 知识已保存：{key}')
        return True
        
    except Exception as e:
        log(f'❌ 保存知识失败：{e}', 'ERROR')
        return False


def retrieve_knowledge(query, limit=5, threshold=0.5):
    """
    检索相关知识（简化版，实际应该用向量检索）
    
    Args:
        query: 查询文本
        limit: 返回数量
        threshold: 置信度阈值
    
    Returns:
        list: 相关知识列表
    """
    log(f'检索相关知识：{query[:50]}...')
    
    try:
        conn = sqlite3.connect(str(KNOWLEDGE_DB))
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
        
        knowledge_items = [
            {
                'key': row[0],
                'value': row[1],
                'category': row[2],
                'confidence': row[3],
                'usage_count': row[4]
            }
            for row in results
        ]
        
        log(f'✅ 检索到 {len(knowledge_items)} 条相关知识')
        return knowledge_items
        
    except Exception as e:
        log(f'❌ 检索知识失败：{e}', 'ERROR')
        return []


def increment_knowledge_usage(key):
    """增加知识使用次数"""
    try:
        conn = sqlite3.connect(str(KNOWLEDGE_DB))
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE knowledge
            SET usage_count = usage_count + 1, last_used_at = ?
            WHERE key = ?
        ''', (datetime.now().isoformat(), key))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        log(f'❌ 更新知识使用次数失败：{e}', 'ERROR')


# ============== 任务队列（Task Queue） ==============

def create_task(title, description='', priority=5, timeout_minutes=30):
    """
    创建任务
    
    Args:
        title: 任务标题
        description: 任务描述
        priority: 优先级（1-10，1 最高）
        timeout_minutes: 超时时间（分钟）
    
    Returns:
        str: 任务 ID
    """
    log(f'创建任务：{title} (优先级：{priority})')
    
    try:
        conn = sqlite3.connect(str(TASK_DB))
        cursor = conn.cursor()
        
        # 生成任务 ID
        task_id = f'task_{datetime.now().strftime("%Y%m%d%H%M%S")}_{os.getpid()}'
        
        cursor.execute('''
            INSERT INTO tasks (task_id, title, description, priority, status, timeout_minutes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (task_id, title, description, priority, 'queued', timeout_minutes))
        
        conn.commit()
        conn.close()
        
        log(f'✅ 任务已创建：{task_id}')
        return task_id
        
    except Exception as e:
        log(f'❌ 创建任务失败：{e}', 'ERROR')
        return None


def claim_task(worker_id='default_worker', timeout_minutes=30):
    """
    抢占任务（原子性操作）
    
    Args:
        worker_id: 工作节点 ID
        timeout_minutes: 超时时间
    
    Returns:
        dict: 任务信息，如果没有任务则返回 None
    """
    log(f'{worker_id} 尝试抢占任务')
    
    try:
        conn = sqlite3.connect(str(TASK_DB))
        cursor = conn.cursor()
        
        # 原子性抢占：UPDATE + ROW COUNT 验证
        cursor.execute('''
            UPDATE tasks
            SET status = 'running',
                assigned_to = ?,
                started_at = ?,
                updated_at = ?
            WHERE id = (
                SELECT id FROM tasks
                WHERE status = 'queued'
                ORDER BY priority ASC, created_at ASC
                LIMIT 1
            )
            AND (SELECT COUNT(*) FROM tasks WHERE status = 'queued') > 0
        ''', (worker_id, datetime.now().isoformat(), datetime.now().isoformat()))
        
        if cursor.rowcount == 0:
            conn.close()
            return None
        
        # 获取刚抢占的任务
        cursor.execute('''
            SELECT task_id, title, description, priority, timeout_minutes
            FROM tasks
            WHERE assigned_to = ? AND status = 'running'
            ORDER BY started_at DESC
            LIMIT 1
        ''', (worker_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            task = {
                'task_id': row[0],
                'title': row[1],
                'description': row[2],
                'priority': row[3],
                'timeout_minutes': row[4]
            }
            log(f'✅ {worker_id} 抢占到任务：{task["task_id"]}')
            return task
        
        return None
        
    except Exception as e:
        log(f'❌ 抢占任务失败：{e}', 'ERROR')
        return None


def complete_task(task_id, result=''):
    """完成任务"""
    log(f'完成任务：{task_id}')
    
    try:
        conn = sqlite3.connect(str(TASK_DB))
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks
            SET status = 'completed',
                completed_at = ?,
                result = ?,
                updated_at = ?
            WHERE task_id = ?
        ''', (datetime.now().isoformat(), result, datetime.now().isoformat(), task_id))
        
        conn.commit()
        conn.close()
        
        log(f'✅ 任务已完成：{task_id}')
        return True
        
    except Exception as e:
        log(f'❌ 完成任务失败：{e}', 'ERROR')
        return False


def fail_task(task_id, error_message=''):
    """失败任务"""
    log(f'失败任务：{task_id}')
    
    try:
        conn = sqlite3.connect(str(TASK_DB))
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks
            SET status = 'failed',
                completed_at = ?,
                error_message = ?,
                updated_at = ?
            WHERE task_id = ?
        ''', (datetime.now().isoformat(), error_message, datetime.now().isoformat(), task_id))
        
        conn.commit()
        conn.close()
        
        log(f'✅ 任务已标记失败：{task_id}')
        return True
        
    except Exception as e:
        log(f'❌ 失败任务失败：{e}', 'ERROR')
        return False


# ============== 机会扫描（Opportunity Scan） ==============

def create_opportunity(title, description='', opp_type='general', severity='medium', priority_score=0.5):
    """
    创建机会记录
    
    Args:
        title: 机会标题
        description: 机会描述
        opp_type: 类型
        severity: 严重程度（low/medium/high/critical）
        priority_score: 优先级分数（0-1）
    
    Returns:
        str: 机会 ID
    """
    log(f'创建机会：{title} (严重程度：{severity})')
    
    try:
        conn = sqlite3.connect(str(OPPORTUNITY_DB))
        cursor = conn.cursor()
        
        opportunity_id = f'opp_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        
        cursor.execute('''
            INSERT INTO opportunities (opportunity_id, title, description, type, severity, priority_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (opportunity_id, title, description, opp_type, severity, priority_score))
        
        conn.commit()
        conn.close()
        
        log(f'✅ 机会已创建：{opportunity_id}')
        return opportunity_id
        
    except Exception as e:
        log(f'❌ 创建机会失败：{e}', 'ERROR')
        return None


def get_high_priority_opportunities(limit=10, min_priority_score=0.7):
    """
    获取高优先级未处理机会
    
    Args:
        limit: 返回数量
        min_priority_score: 最小优先级分数
    
    Returns:
        list: 机会列表
    """
    log(f'获取高优先级机会 (min_score: {min_priority_score})')
    
    try:
        conn = sqlite3.connect(str(OPPORTUNITY_DB))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT opportunity_id, title, description, type, severity, priority_score, detected_at
            FROM opportunities
            WHERE status = 'pending' AND priority_score >= ?
            ORDER BY priority_score DESC, detected_at ASC
            LIMIT ?
        ''', (min_priority_score, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        opportunities = [
            {
                'opportunity_id': row[0],
                'title': row[1],
                'description': row[2],
                'type': row[3],
                'severity': row[4],
                'priority_score': row[5],
                'detected_at': row[6]
            }
            for row in results
        ]
        
        log(f'✅ 获取到 {len(opportunities)} 个高优先级机会')
        return opportunities
        
    except Exception as e:
        log(f'❌ 获取机会失败：{e}', 'ERROR')
        return []


def process_opportunity(opportunity_id, result=''):
    """标记机会已处理"""
    log(f'处理机会：{opportunity_id}')
    
    try:
        conn = sqlite3.connect(str(OPPORTUNITY_DB))
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE opportunities
            SET status = 'processed',
                processed_at = ?,
                result = ?
            WHERE opportunity_id = ?
        ''', (datetime.now().isoformat(), result, opportunity_id))
        
        conn.commit()
        conn.close()
        
        log(f'✅ 机会已处理：{opportunity_id}')
        return True
        
    except Exception as e:
        log(f'❌ 处理机会失败：{e}', 'ERROR')
        return False


# ============== 主入口 ==============

def main():
    """主函数"""
    log('=' * 60)
    log('🧠 VectorBrain 主动记忆模块启动')
    log('=' * 60)
    log(f'工作区：{WORKSPACE_ROOT}')
    log(f'记忆目录：{MEMORY_ROOT}')
    log(f'数据库目录：{DB_DIR}')
    log('=' * 60)
    
    # 初始化数据库
    init_databases()
    
    log('=' * 60)
    log('✅ VectorBrain 主动记忆模块已就绪')
    log('=' * 60)
    log('可用功能:')
    log('  - save_message_to_episodic() - 保存消息到情景记忆')
    log('  - retrieve_knowledge() - 检索相关知识')
    log('  - create_task() - 创建任务')
    log('  - create_opportunity() - 创建机会')
    log('=' * 60)


if __name__ == '__main__':
    main()
