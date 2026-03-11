#!/usr/bin/env python3
"""
记忆检索工具 - 三层记忆系统查询接口

用法:
    python memory_search.py --layer working          # 查询工作记忆
    python memory_search.py --layer episodic --today # 查询今日情景记忆
    python memory_search.py --layer semantic --type profile  # 查询用户画像
    python memory_search.py --query "今天做了什么"    # 智能路由查询
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_ROOT = Path(__file__).parent

def load_json(path):
    """加载 JSON 文件"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def load_jsonl(path):
    """加载 JSONL 文件"""
    entries = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
    except FileNotFoundError:
        return []
    return entries

def query_working():
    """查询工作记忆"""
    data = load_json(MEMORY_ROOT / 'working' / 'session_current.json')
    if not data:
        return {"error": "No active session"}
    return {
        "session_id": data.get("session_id"),
        "current_goal": data.get("current_goal"),
        "message_count": len(data.get("recent_messages", [])),
        "active_entities": data.get("active_entities", [])
    }

def query_episodic(date=None, since=None, until=None, keyword=None):
    """查询情景记忆"""
    if date:
        # 查询指定日期
        file = MEMORY_ROOT / 'episodic' / f"{date}.jsonl"
        entries = load_jsonl(file)
    elif since or until:
        # 时间范围查询（简化版：遍历所有文件）
        entries = []
        episodic_dir = MEMORY_ROOT / 'episodic'
        if episodic_dir.exists():
            for file in episodic_dir.glob("*.jsonl"):
                file_entries = load_jsonl(file)
                for entry in file_entries:
                    ts = entry.get("timestamp", "")
                    if since and ts < since:
                        continue
                    if until and ts > until:
                        continue
                    entries.append(entry)
    else:
        # 查询今日
        today = datetime.now().strftime("%Y-%m-%d")
        file = MEMORY_ROOT / 'episodic' / f"{today}.jsonl"
        entries = load_jsonl(file)
    
    # 关键词过滤
    if keyword:
        entries = [e for e in entries if keyword.lower() in str(e).lower()]
    
    return {
        "count": len(entries),
        "entries": entries[:20]  # 限制返回数量
    }

def query_semantic(type=None):
    """查询语义记忆"""
    result = {}
    
    if type == "profile" or type is None:
        result["profile"] = load_json(MEMORY_ROOT / 'semantic' / 'user_profile.json')
    
    if type == "preferences" or type is None:
        result["preferences"] = load_json(MEMORY_ROOT / 'semantic' / 'preferences.json')
    
    if type == "knowledge" or type is None:
        result["knowledge"] = load_json(MEMORY_ROOT / 'semantic' / 'knowledge_base.json')
    
    return result

def smart_query(query_text):
    """智能查询路由"""
    query_lower = query_text.lower()
    
    # 时间相关查询 → Episodic
    time_keywords = ["今天", "昨天", "刚才", "上周", "做什么", "做了什么"]
    if any(kw in query_lower for kw in time_keywords):
        if "刚才" in query_lower or "现在" in query_lower:
            return {"layer": "working", "result": query_working()}
        else:
            return {"layer": "episodic", "result": query_episodic()}
    
    # 偏好/画像查询 → Semantic
    profile_keywords = ["偏好", "喜欢", "画像", "目标", "薪资", "城市"]
    if any(kw in query_lower for kw in profile_keywords):
        return {"layer": "semantic", "result": query_semantic()}
    
    # 默认：搜索所有层
    return {
        "working": query_working(),
        "episodic": query_episodic(),
        "semantic": query_semantic()
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="记忆检索工具")
    parser.add_argument("--layer", choices=["working", "episodic", "semantic"], help="指定记忆层")
    parser.add_argument("--query", type=str, help="智能查询文本")
    parser.add_argument("--date", type=str, help="查询日期 (YYYY-MM-DD)")
    parser.add_argument("--since", type=str, help="开始时间 (YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--until", type=str, help="结束时间 (YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--keyword", type=str, help="关键词过滤")
    parser.add_argument("--type", type=str, help="语义记忆类型 (profile/preferences/knowledge)")
    
    args = parser.parse_args()
    
    if args.query:
        # 智能查询
        result = smart_query(args.query)
    elif args.layer == "working":
        result = query_working()
    elif args.layer == "episodic":
        result = query_episodic(args.date, args.since, args.until, args.keyword)
    elif args.layer == "semantic":
        result = query_semantic(args.type)
    else:
        # 默认显示索引
        result = load_json(MEMORY_ROOT / 'memory_index.json')
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
