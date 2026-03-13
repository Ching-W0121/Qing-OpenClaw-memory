#!/usr/bin/env python3
"""
VectorBrain 上下文注入器

功能：
- 每次对话开始时自动加载记忆
- 检索相关上下文
- 生成记忆摘要注入对话

作者：庆 (Qing)
日期：2026-03-13
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 导入 VectorBrain 模块
from vectorbrain_integration import (
    load_recent_episodes,
    retrieve_knowledge,
    log,
    EPISODIC_DB,
    KNOWLEDGE_DB
)

# 配置
MEMORY_ROOT = Path(__file__).parent
CONTEXT_FILE = MEMORY_ROOT / 'context_cache.json'
MAX_EPISODES = 20  # 最多加载的对话记录数
MAX_KNOWLEDGE = 10  # 最多检索的知识点数


def load_context_from_query(query='', limit_episodes=20, limit_knowledge=10):
    """
    根据查询加载上下文
    
    Args:
        query: 用户消息/查询（可选）
        limit_episodes: 加载的对话记录数
        limit_knowledge: 检索的知识点数
    
    Returns:
        dict: 上下文信息
    """
    log(f'加载上下文：query="{query[:50]}..."')
    
    context = {
        'loaded_at': datetime.now().isoformat(),
        'query': query,
        'recent_episodes': [],
        'relevant_knowledge': [],
        'active_tasks': [],
        'pending_opportunities': [],
        'summary': ''
    }
    
    # 1. 加载最近的对话记录
    try:
        episodes = load_recent_episodes(limit=limit_episodes, days=2)
        context['recent_episodes'] = episodes
        log(f'✅ 加载到 {len(episodes)} 条对话记录')
    except Exception as e:
        log(f'❌ 加载对话记录失败：{e}', 'ERROR')
    
    # 2. 检索相关知识
    if query:
        try:
            knowledge = retrieve_knowledge(query, limit=limit_knowledge, threshold=0.3)
            context['relevant_knowledge'] = knowledge
            log(f'✅ 检索到 {len(knowledge)} 条相关知识')
        except Exception as e:
            log(f'❌ 检索知识失败：{e}', 'ERROR')
    
    # 3. 加载活跃任务
    try:
        import sqlite3
        conn = sqlite3.connect(str(Path(MEMORY_ROOT) / 'database' / 'task_queue.db'))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT task_id, title, priority, status, created_at
            FROM tasks
            WHERE status IN ('queued', 'running')
            ORDER BY priority ASC, created_at ASC
            LIMIT 10
        ''')
        
        tasks = [
            {
                'task_id': row[0],
                'title': row[1],
                'priority': row[2],
                'status': row[3],
                'created_at': row[4]
            }
            for row in cursor.fetchall()
        ]
        context['active_tasks'] = tasks
        conn.close()
        log(f'✅ 加载到 {len(tasks)} 个活跃任务')
    except Exception as e:
        log(f'❌ 加载任务失败：{e}', 'ERROR')
    
    # 4. 加载待处理机会
    try:
        import sqlite3
        conn = sqlite3.connect(str(Path(MEMORY_ROOT) / 'database' / 'opportunities.db'))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT opportunity_id, title, type, severity, priority_score
            FROM opportunities
            WHERE status = 'pending'
            ORDER BY priority_score DESC
            LIMIT 10
        ''')
        
        opportunities = [
            {
                'opportunity_id': row[0],
                'title': row[1],
                'type': row[2],
                'severity': row[3],
                'priority_score': row[4]
            }
            for row in cursor.fetchall()
        ]
        context['pending_opportunities'] = opportunities
        conn.close()
        log(f'✅ 加载到 {len(opportunities)} 个待处理机会')
    except Exception as e:
        log(f'❌ 加载机会失败：{e}', 'ERROR')
    
    # 5. 生成摘要
    context['summary'] = generate_context_summary(context)
    
    # 6. 缓存到文件
    save_context_to_cache(context)
    
    return context


def generate_context_summary(context):
    """
    生成上下文摘要
    
    Args:
        context: 上下文字典
    
    Returns:
        str: 摘要文本
    """
    summary_parts = []
    
    # 最近对话摘要
    if context['recent_episodes']:
        episodes = context['recent_episodes'][:5]  # 只看最近 5 条
        summary_parts.append('📝 最近对话:')
        for ep in episodes:
            timestamp = ep['timestamp'].split('T')[1][:8] if 'T' in ep['timestamp'] else '?'
            content = ep['content'][:100]
            summary_parts.append(f'  [{timestamp}] {content}')
    
    # 相关知识摘要
    if context['relevant_knowledge']:
        summary_parts.append('\n🧠 相关知识:')
        for k in context['relevant_knowledge'][:3]:
            summary_parts.append(f'  - {k["key"]}: {k["value"][:80]}...')
    
    # 活跃任务摘要
    if context['active_tasks']:
        summary_parts.append('\n📋 活跃任务:')
        for task in context['active_tasks']:
            priority_emoji = '🔴' if task['priority'] <= 3 else '🟡' if task['priority'] <= 6 else '🟢'
            summary_parts.append(f'  {priority_emoji} [{task["status"]}] {task["title"]}')
    
    # 待处理机会摘要
    if context['pending_opportunities']:
        summary_parts.append('\n💡 待处理机会:')
        for opp in context['pending_opportunities'][:3]:
            severity_emoji = '🔴' if opp['severity'] == 'critical' else '🟠' if opp['severity'] == 'high' else '🟡'
            summary_parts.append(f'  {severity_emoji} [{opp["type"]}] {opp["title"]}')
    
    return '\n'.join(summary_parts)


def save_context_to_cache(context):
    """保存上下文到缓存文件"""
    try:
        with open(CONTEXT_FILE, 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=2)
        log(f'✅ 上下文已缓存到 {CONTEXT_FILE}')
    except Exception as e:
        log(f'❌ 缓存上下文失败：{e}', 'ERROR')


def load_context_from_cache():
    """从缓存文件加载上下文"""
    try:
        if CONTEXT_FILE.exists():
            with open(CONTEXT_FILE, 'r', encoding='utf-8') as f:
                context = json.load(f)
            log(f'✅ 从缓存加载上下文')
            return context
    except Exception as e:
        log(f'❌ 加载缓存上下文失败：{e}', 'ERROR')
    return None


def format_context_for_llm(context):
    """
    格式化上下文为 LLM 可读的提示
    
    Args:
        context: 上下文字典
    
    Returns:
        str: 格式化的提示文本
    """
    prompt_parts = []
    
    prompt_parts.append('=' * 60)
    prompt_parts.append('🧠 VectorBrain 记忆上下文')
    prompt_parts.append('=' * 60)
    prompt_parts.append(f'加载时间：{context["loaded_at"]}')
    prompt_parts.append('')
    
    # 最近对话
    if context['recent_episodes']:
        prompt_parts.append('📝 最近对话记录:')
        for i, ep in enumerate(context['recent_episodes'][:10], 1):
            timestamp = ep['timestamp'].split('T')[0] if 'T' in ep['timestamp'] else '?'
            content = ep['content']
            prompt_parts.append(f'{i}. [{timestamp}] {content}')
        prompt_parts.append('')
    
    # 相关知识
    if context['relevant_knowledge']:
        prompt_parts.append('🧠 相关知识:')
        for k in context['relevant_knowledge']:
            prompt_parts.append(f'- **{k["key"]}**: {k["value"]} (置信度：{k["confidence"]})')
        prompt_parts.append('')
    
    # 活跃任务
    if context['active_tasks']:
        prompt_parts.append('📋 活跃任务:')
        for task in context['active_tasks']:
            prompt_parts.append(f'- [{task["status"].upper()}] {task["title"]} (优先级：{task["priority"]})')
        prompt_parts.append('')
    
    # 待处理机会
    if context['pending_opportunities']:
        prompt_parts.append('💡 待处理机会:')
        for opp in context['pending_opportunities']:
            prompt_parts.append(f'- [{opp["severity"].upper()}] {opp["title"]} (分数：{opp["priority_score"]})')
        prompt_parts.append('')
    
    prompt_parts.append('=' * 60)
    prompt_parts.append('请在回复时考虑以上上下文信息')
    prompt_parts.append('=' * 60)
    
    return '\n'.join(prompt_parts)


def main():
    """主函数 - 测试用"""
    # 设置 UTF-8 编码
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print('=' * 60)
    print('[VectorBrain] 上下文注入器')
    print('=' * 60)
    
    # 测试加载上下文
    query = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else ''
    context = load_context_from_query(query=query)
    
    # 打印摘要
    print('\n' + context['summary'])
    
    # 打印格式化后的 LLM 提示
    print('\n' + format_context_for_llm(context))


if __name__ == '__main__':
    main()
