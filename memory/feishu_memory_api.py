#!/usr/bin/env python3
"""
飞书记忆 API - HTTP 服务

提供 HTTP 接口让飞书机器人查询记忆
"""

import json
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# 数据库路径
DB_PATH = Path(__file__).parent / 'database' / 'optimized_memory.db'

class MemoryAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理 GET 请求"""
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        if parsed.path == '/memories':
            self.handle_get_memories(params)
        elif parsed.path == '/search':
            self.handle_search(params)
        elif parsed.path == '/stats':
            self.handle_stats()
        else:
            self.send_error(404, 'Not Found')
    
    def handle_get_memories(self, params):
        """获取记忆"""
        platform = params.get('platform', [None])[0]
        limit = int(params.get('limit', [20])[0])
        days = int(params.get('days', [7])[0])
        
        memories = get_memories(platform=platform, limit=limit, days=days)
        
        self.send_json({
            'success': True,
            'count': len(memories),
            'memories': memories
        })
    
    def handle_search(self, params):
        """搜索记忆"""
        query = params.get('q', [''])[0]
        limit = int(params.get('limit', [20])[0])
        
        if not query:
            self.send_json({'success': False, 'error': 'Missing query parameter'})
            return
        
        memories = get_memories(query=query, limit=limit, days=30)
        
        self.send_json({
            'success': True,
            'query': query,
            'count': len(memories),
            'memories': memories
        })
    
    def handle_stats(self):
        """获取统计"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # 总记忆数
        cursor.execute('SELECT COUNT(*) FROM episodes')
        total = cursor.fetchone()[0]
        
        # 按平台统计
        cursor.execute('''
            SELECT SUBSTR(channel_id, 1, INSTR(channel_id, '_') - 1) as platform, COUNT(*) as count
            FROM episodes
            GROUP BY platform
        ''')
        platforms = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 最近 7 天
        cutoff = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM episodes WHERE timestamp > ?', (cutoff,))
        week_count = cursor.fetchone()[0]
        
        conn.close()
        
        self.send_json({
            'success': True,
            'total': total,
            'platforms': platforms,
            'last_7_days': week_count
        })
    
    def send_json(self, data):
        """发送 JSON 响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        response = json.dumps(data, ensure_ascii=False)
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """日志"""
        print(f'[{datetime.now().strftime("%H:%M:%S")}] {args[0]}')


def get_memories(query=None, platform=None, limit=20, days=7):
    """获取记忆"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    if query:
        cursor.execute('''
            SELECT timestamp, channel_id, content
            FROM episodes
            WHERE timestamp > ? AND (content LIKE ? OR channel_id LIKE ?)
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (cutoff_date, f'%{query}%', f'%{query}%', limit))
    elif platform:
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
        channel = row['channel_id']
        platform = channel.split('_')[0] if channel else 'unknown'
        memories.append({
            'timestamp': row['timestamp'],
            'platform': platform,
            'channel': channel,
            'content': row['content']
        })
    
    return memories


def main():
    """启动 API 服务"""
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    
    server = HTTPServer(('localhost', port), MemoryAPIHandler)
    print(f'🧠 VectorBrain Memory API 启动')
    print(f'监听端口：http://localhost:{port}')
    print(f'')
    print(f'API 端点:')
    print(f'  GET /memories?platform=webchat&limit=10  - 获取记忆')
    print(f'  GET /search?q=关键词&limit=10            - 搜索记忆')
    print(f'  GET /stats                               - 获取统计')
    print(f'')
    print(f'按 Ctrl+C 停止服务')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n服务已停止')
        server.shutdown()


if __name__ == '__main__':
    main()
