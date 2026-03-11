#!/usr/bin/env python3
"""
记忆 API - 简化的记忆文件访问接口
"""

import json
import struct
import lz4.frame
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# 导入合并工具
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memory_merge import load_memory_file, INDEX_MAGIC

@dataclass
class Memory:
    """记忆记录"""
    id: str
    date: int
    type: int
    title: str
    tags: List[str]
    timestamp: str
    content: Dict
    size: int

class MemoryDB:
    """记忆数据库"""
    
    def __init__(self, path: str = None):
        """初始化记忆数据库"""
        if path is None:
            # 默认路径
            workspace = os.path.expanduser(r'~\.openclaw\workspace')
            path = os.path.join(workspace, 'memory', 'memories.qmem')
        
        self.path = path
        self._index = None
        self._file_handle = None
    
    def open(self):
        """打开记忆文件"""
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"记忆文件不存在：{self.path}")
        
        self._index = load_memory_file(self.path)
        self._file_handle = open(self.path, 'rb')
        return self
    
    def close(self):
        """关闭记忆文件"""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
    
    def __enter__(self):
        return self.open()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def _read_entry(self, entry_meta) -> Memory:
        """读取单条记忆"""
        if not self._file_handle:
            raise RuntimeError("记忆文件未打开，请先调用 open()")
        
        # 计算数据区起始位置
        self._file_handle.seek(0)
        index_len = struct.unpack('>I', self._file_handle.read(4))[0]
        data_start = 4 + index_len
        
        # 定位到记录
        abs_offset = data_start + entry_meta.offset
        self._file_handle.seek(abs_offset)
        
        # 读取元数据
        meta_len = struct.unpack('>I', self._file_handle.read(4))[0]
        meta_compressed = self._file_handle.read(meta_len)
        meta = json.loads(lz4.frame.decompress(meta_compressed))
        
        # 读取内容
        content_len = struct.unpack('>I', self._file_handle.read(4))[0]
        content_compressed = self._file_handle.read(content_len)
        content = json.loads(lz4.frame.decompress(content_compressed))
        
        return Memory(
            id=meta['id'],
            date=meta['date'],
            type=meta['type'],
            title=meta['title'],
            tags=meta['tags'],
            timestamp=meta['timestamp'],
            content=content,
            size=meta['size']
        )
    
    def all(self) -> List[Memory]:
        """获取所有记忆"""
        if not self._index:
            self.open()
        
        return [self._read_entry(e) for e in self._index.entries]
    
    def get(self, entry_id: str) -> Optional[Memory]:
        """根据 ID 获取记忆"""
        if not self._index:
            self.open()
        
        entry_meta = next((e for e in self._index.entries if e.id == entry_id), None)
        if not entry_meta:
            return None
        
        return self._read_entry(entry_meta)
    
    def search(self, query: str) -> List[Memory]:
        """搜索记忆（全文搜索）"""
        if not self._index:
            self.open()
        
        results = []
        query_lower = query.lower()
        
        for entry_meta in self._index.entries:
            entry = self._read_entry(entry_meta)
            
            # 搜索标题、标签、内容
            searchable = f"{entry.title} {' '.join(entry.tags)} {json.dumps(entry.content)}".lower()
            
            if query_lower in searchable:
                results.append(entry)
        
        return results
    
    def search_by_date(self, start: int, end: int = None) -> List[Memory]:
        """按日期范围搜索"""
        if not self._index:
            self.open()
        
        if end is None:
            end = start
        
        results = []
        for entry_meta in self._index.entries:
            if start <= entry_meta.date <= end:
                results.append(self._read_entry(entry_meta))
        
        return results
    
    def search_by_tag(self, tag: str) -> List[Memory]:
        """按标签搜索"""
        if not self._index:
            self.open()
        
        results = []
        tag_lower = tag.lower()
        
        for entry_meta in self._index.entries:
            entry = self._read_entry(entry_meta)
            if any(tag_lower in t.lower() for t in entry.tags):
                results.append(entry)
        
        return results
    
    def latest(self, count: int = 5) -> List[Memory]:
        """获取最新的 N 条记忆"""
        if not self._index:
            self.open()
        
        # 按日期倒序
        sorted_entries = sorted(self._index.entries, key=lambda e: e.date, reverse=True)
        return [self._read_entry(e) for e in sorted_entries[:count]]
    
    def stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self._index:
            self.open()
        
        file_size = os.path.getsize(self.path)
        dates = [e.date for e in self._index.entries]
        
        return {
            'file': self.path,
            'file_size': file_size,
            'file_size_kb': file_size / 1024,
            'total_entries': self._index.total_entries,
            'index_size': len(self._index.entries) * 100,  # 估算
            'average_size': file_size / max(1, self._index.total_entries),
            'date_range': {
                'start': min(dates) if dates else None,
                'end': max(dates) if dates else None
            }
        }
    
    def summary(self) -> str:
        """生成记忆摘要"""
        if not self._index:
            self.open()
        
        lines = [
            f"📚 记忆数据库摘要",
            f"   文件：{os.path.basename(self.path)}",
            f"   大小：{os.path.getsize(self.path) / 1024:.1f} KB",
            f"   记录：{self._index.total_entries} 条",
            f"",
            f"📅 最近记忆:"
        ]
        
        # 最近 5 条
        sorted_entries = sorted(self._index.entries, key=lambda e: e.date, reverse=True)[:5]
        for entry_meta in sorted_entries:
            entry = self._read_entry(entry_meta)
            date_str = str(entry.date)
            tags = ', '.join(entry.tags) if entry.tags else '无标签'
            lines.append(f"   [{date_str}] {entry.title}")
            lines.append(f"           标签：{tags}")
        
        return '\n'.join(lines)

# ============== 便捷函数 ==============

def open_memory(path: str = None) -> MemoryDB:
    """打开记忆数据库"""
    return MemoryDB(path).open()

def search_memory(query: str, path: str = None) -> List[Memory]:
    """搜索记忆"""
    with MemoryDB(path) as db:
        return db.search(query)

def get_memory(entry_id: str, path: str = None) -> Optional[Memory]:
    """获取记忆"""
    with MemoryDB(path) as db:
        return db.get(entry_id)

def latest_memories(count: int = 5, path: str = None) -> List[Memory]:
    """获取最新记忆"""
    with MemoryDB(path) as db:
        return db.latest(count)

# ============== 命令行工具 ==============

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: memory_api.py <command> [args]")
        print("Commands:")
        print("  summary              - 显示记忆摘要")
        print("  stats                - 显示统计信息")
        print("  list [n]             - 列出最近 N 条记忆 (默认 5)")
        print("  search <query>       - 搜索记忆")
        print("  get <id>             - 获取指定记忆")
        print("  tag <tag>            - 按标签搜索")
        print("  date <YYYYMMDD>      - 按日期搜索")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    with MemoryDB() as db:
        if cmd == 'summary':
            print(db.summary())
        
        elif cmd == 'stats':
            stats = db.stats()
            print(f"\n[STATS]")
            print(f"  File:       {stats['file']}")
            print(f"  Size:       {stats['file_size_kb']:.1f} KB")
            print(f"  Entries:    {stats['total_entries']}")
            print(f"  Average:    {stats['average_size']:.0f} bytes/entry")
            if stats['date_range']['start']:
                print(f"  Date Range: {stats['date_range']['start']} - {stats['date_range']['end']}")
        
        elif cmd == 'list':
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            memories = db.latest(count)
            print(f"\n[LATEST {count} MEMORIES]")
            for m in memories:
                tags = ', '.join(m.tags) if m.tags else '-'
                print(f"  [{m.date}] {m.title}")
                print(f"           Tags: {tags}")
        
        elif cmd == 'search':
            query = ' '.join(sys.argv[2:])
            results = db.search(query)
            print(f"\n[SEARCH: {query}]")
            print(f"  Found: {len(results)} results")
            for m in results:
                print(f"  [{m.date}] {m.title}")
        
        elif cmd == 'get':
            entry_id = sys.argv[2]
            memory = db.get(entry_id)
            if memory:
                print(json.dumps(memory.content, indent=2, ensure_ascii=False))
            else:
                print(f"Not found: {entry_id}")
        
        elif cmd == 'tag':
            tag = sys.argv[2]
            results = db.search_by_tag(tag)
            print(f"\n[TAG: {tag}]")
            print(f"  Found: {len(results)} results")
            for m in results:
                print(f"  [{m.date}] {m.title}")
        
        elif cmd == 'date':
            date = int(sys.argv[2])
            results = db.search_by_date(date)
            print(f"\n[DATE: {date}]")
            print(f"  Found: {len(results)} results")
            for m in results:
                print(f"  [{m.date}] {m.title}")
        
        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)
