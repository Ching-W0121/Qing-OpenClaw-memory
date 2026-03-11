#!/usr/bin/env python3
"""
自然语言记忆检索 - 支持用户用自然语言查询记忆
示例：
- "上周我让你查了什么？"
- "我之前说过不喜欢什么？"
- "你帮我做过哪些事？"
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class MemorySearch:
    """记忆搜索引擎"""
    
    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            self.memory_dir = os.path.expanduser(r'~\.openclaw\workspace\memory')
        else:
            self.memory_dir = memory_dir
        
        self.requests_file = os.path.join(self.memory_dir, 'requests.json')
        self._requests = None
    
    def _load_requests(self):
        """加载请求记录"""
        if self._requests is None:
            if os.path.exists(self.requests_file):
                with open(self.requests_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._requests = data.get('requests', [])
            else:
                self._requests = []
    
    def _parse_time_range(self, query: str) -> tuple:
        """从查询中解析时间范围"""
        now = datetime.now()
        
        # 今天
        if any(word in query for word in ['今天', '今日', 'now', 'today']):
            return now.date(), now.date()
        
        # 昨天
        if any(word in query for word in ['昨天', '昨日', 'yesterday']):
            yesterday = now - timedelta(days=1)
            return yesterday.date(), yesterday.date()
        
        # 上周/最近 7 天
        if any(word in query for word in ['上周', '最近 7 天', '过去一周', 'last week']):
            end = now.date()
            start = end - timedelta(days=7)
            return start, end
        
        # 上周（自然周）
        if '上周' in query and '最近' not in query:
            # 计算上周一和周日
            last_week = now - timedelta(weeks=1)
            start = last_week - timedelta(days=last_week.weekday())
            end = start + timedelta(days=6)
            return start.date(), end.date()
        
        # 本月
        if any(word in query for word in ['本月', '这个月', 'this month']):
            start = now.replace(day=1).date()
            end = now.date()
            return start, end
        
        # 上个月
        if any(word in query for word in ['上月', '上个月', 'last month']):
            first_day = now.replace(day=1)
            last_month = first_day - timedelta(days=1)
            start = last_month.replace(day=1).date()
            end = last_month.date()
            return start, end
        
        # 所有时间（默认）
        return None, None
    
    def _parse_query_intent(self, query: str) -> str:
        """解析查询意图"""
        query_lower = query.lower()
        
        # 查询请求历史
        if any(word in query_lower for word in ['让我', '叫你', '你说', '请求', '查了什么', '做了什么']):
            return 'requests'
        
        # 查询用户偏好
        if any(word in query_lower for word in ['喜欢', '不喜欢', '偏好', '讨厌']):
            return 'preferences'
        
        # 查询项目进度
        if any(word in query_lower for word in ['进度', '进行到哪', '完成', '状态']):
            return 'projects'
        
        # 查询用户画像
        if any(word in query_lower for word in ['我是谁', '我的信息', '画像']):
            return 'profile'
        
        # 默认：搜索所有内容
        return 'all'
    
    def search(self, query: str) -> List[Dict]:
        """搜索记忆"""
        self._load_requests()
        
        # 解析时间范围
        start_date, end_date = self._parse_time_range(query)
        
        # 解析查询意图
        intent = self._parse_query_intent(query)
        
        results = []
        
        # 搜索请求历史
        if intent in ['requests', 'all']:
            for req in self._requests:
                # 时间过滤
                if start_date and end_date:
                    req_date = datetime.fromisoformat(req['timestamp']).date()
                    if not (start_date <= req_date <= end_date):
                        continue
                
                # 关键词匹配
                searchable = f"{req['user_request']} {req.get('summary', '')}".lower()
                if any(word in searchable for word in ['查', '搜索', '分析', '写', '创建']):
                    results.append({
                        'type': 'request',
                        'date': req['timestamp'][:10],
                        'request': req['user_request'],
                        'summary': req.get('summary', ''),
                        'success': req.get('execution', {}).get('success', False)
                    })
        
        return results
    
    def format_results(self, results: List[Dict]) -> str:
        """格式化搜索结果"""
        if not results:
            return "没有找到相关记忆"
        
        lines = [f"找到 {len(results)} 条相关记忆:\n"]
        
        for i, result in enumerate(results, 1):
            if result['type'] == 'request':
                status = "✅" if result['success'] else "⏳"
                lines.append(f"{i}. {status} [{result['date']}] {result['request'][:50]}")
                if result['summary']:
                    lines.append(f"   摘要：{result['summary'][:80]}")
        
        return '\n'.join(lines)
    
    def answer(self, query: str) -> str:
        """回答用户问题"""
        results = self.search(query)
        formatted = self.format_results(results)
        
        # 添加上下文
        if '上周' in query or '最近' in query:
            prefix = f"最近你让我做了以下事情:\n\n"
        elif '昨天' in query:
            prefix = f"昨天你让我做了以下事情:\n\n"
        elif '今天' in query:
            prefix = f"今天你让我做了以下事情:\n\n"
        else:
            prefix = f"找到以下相关记忆:\n\n"
        
        return prefix + formatted

# 命令行工具
if __name__ == '__main__':
    import sys
    
    search = MemorySearch()
    
    if len(sys.argv) < 2:
        print("Usage: memory_search.py <query>")
        print("Examples:")
        print('  memory_search.py "上周我让你查了什么？"')
        print('  memory_search.py "昨天我做了什么？"')
        print('  memory_search.py "你帮我做过哪些事？"')
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    answer = search.answer(query)
    print(answer)
