#!/usr/bin/env python3
"""
记忆合并工具 - 将所有记忆合并到单个文件中
格式：单个二进制文件 + 索引 + LZ4 压缩
"""

import struct
import lz4.frame
import json
import zlib
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

# ============== 常量定义 ==============

MAGIC = b'QMEM'  # Qing Memory
INDEX_MAGIC = b'QIDX'  # Index Magic
VERSION = 1
ENTRY_HEADER_SIZE = 24

# ============== 数据结构 ==============

@dataclass
class MemoryEntry:
    """单条记忆记录"""
    id: str           # 唯一 ID (日期 + 序号)
    date: int         # YYYYMMDD
    type: int         # 记忆类型
    title: str        # 标题/摘要
    tags: List[str]   # 标签
    timestamp: str    # 创建时间
    content: Dict     # 完整内容 (JSON 对象)
    size: int         # 原始大小
    offset: int = 0   # 文件偏移量 (写入时填充)

@dataclass
class MemoryIndex:
    """记忆索引"""
    version: int
    created_at: str
    total_entries: int
    total_size: int
    entries: List[MemoryEntry]

# ============== 编码工具 ==============

def encode_entry(entry: MemoryEntry) -> bytes:
    """编码单条记忆记录"""
    # 内容压缩
    content_json = json.dumps(entry.content, ensure_ascii=False).encode('utf-8')
    content_compressed = lz4.frame.compress(content_json)
    
    # 元数据
    meta = {
        'id': entry.id,
        'date': entry.date,
        'type': entry.type,
        'title': entry.title,
        'tags': entry.tags,
        'timestamp': entry.timestamp,
        'size': entry.size
    }
    meta_json = json.dumps(meta, ensure_ascii=False).encode('utf-8')
    meta_compressed = lz4.frame.compress(meta_json)
    
    # 构建记录：[meta_len:4][meta][content_len:4][content]
    record = struct.pack('>I', len(meta_compressed)) + meta_compressed
    record += struct.pack('>I', len(content_compressed)) + content_compressed
    
    return record

def decode_entry(data: bytes) -> MemoryEntry:
    """解码单条记忆记录"""
    offset = 0
    
    # 读取元数据
    meta_len = struct.unpack('>I', data[offset:offset+4])[0]
    offset += 4
    meta_compressed = data[offset:offset+meta_len]
    offset += meta_len
    meta = json.loads(lz4.frame.decompress(meta_compressed))
    
    # 读取内容
    content_len = struct.unpack('>I', data[offset:offset+4])[0]
    offset += 4
    content_compressed = data[offset:offset+content_len]
    content = json.loads(lz4.frame.decompress(content_compressed))
    
    return MemoryEntry(
        id=meta['id'],
        date=meta['date'],
        type=meta['type'],
        title=meta['title'],
        tags=meta['tags'],
        timestamp=meta['timestamp'],
        content=content,
        size=meta['size']
    )

def encode_index(index: MemoryIndex) -> bytes:
    """编码索引"""
    # 索引内容
    index_data = {
        'version': index.version,
        'created_at': index.created_at,
        'total_entries': index.total_entries,
        'total_size': index.total_size,
        'entries': [
            {
                'id': e.id,
                'date': e.date,
                'type': e.type,
                'title': e.title,
                'tags': e.tags,
                'timestamp': e.timestamp,
                'size': e.size,
                'offset': e.offset
            }
            for e in index.entries
        ]
    }
    
    index_json = json.dumps(index_data, ensure_ascii=False).encode('utf-8')
    index_compressed = lz4.frame.compress(index_json)
    
    # 构建索引块：[INDEX_MAGIC:4][version:2][len:4][data]
    header = struct.pack('>4sHI', INDEX_MAGIC, VERSION, len(index_compressed))
    return header + index_compressed

def decode_index(data: bytes) -> MemoryIndex:
    """解码索引"""
    # 验证 Magic
    magic, version, data_len = struct.unpack('>4sHI', data[:10])
    if magic != INDEX_MAGIC:
        raise ValueError(f"无效的索引 Magic: {magic}")
    
    index_compressed = data[10:10+data_len]
    index_data = json.loads(lz4.frame.decompress(index_compressed))
    
    entries = [
        MemoryEntry(
            id=e['id'],
            date=e['date'],
            type=e['type'],
            title=e['title'],
            tags=e['tags'],
            timestamp=e['timestamp'],
            content={},  # 索引中不包含内容
            size=e['size'],
            offset=e['offset']
        )
        for e in index_data['entries']
    ]
    
    return MemoryIndex(
        version=index_data['version'],
        created_at=index_data['created_at'],
        total_entries=index_data['total_entries'],
        total_size=index_data['total_size'],
        entries=entries
    )

# ============== 文件操作 ==============

def create_memory_file(entries: List[MemoryEntry], output_path: str):
    """创建合并的记忆文件"""
    
    # 1. 编码所有记录
    encoded_entries = []
    total_size = 0
    
    for entry in entries:
        data = encode_entry(entry)
        entry.offset = total_size
        total_size += len(data)
        encoded_entries.append((entry, data))
    
    # 2. 创建索引
    index = MemoryIndex(
        version=VERSION,
        created_at=datetime.now().isoformat(),
        total_entries=len(entries),
        total_size=total_size,
        entries=[e[0] for e in encoded_entries]
    )
    
    # 3. 编码索引
    index_data = encode_index(index)
    
    # 4. 写入文件：[索引长度：4][索引][记录 1][记录 2]...
    with open(output_path, 'wb') as f:
        # 索引长度
        f.write(struct.pack('>I', len(index_data)))
        # 索引
        f.write(index_data)
        # 所有记录
        for entry, data in encoded_entries:
            f.write(data)
    
    file_size = os.path.getsize(output_path)
    print(f"[OK] Memory file created: {output_path}")
    print(f"     Entries:    {len(entries)}")
    print(f"     File size:  {file_size} bytes")
    print(f"     Index size: {len(index_data)} bytes")
    print(f"     Data size:  {total_size} bytes")
    
    return output_path

def load_memory_file(path: str) -> MemoryIndex:
    """加载记忆文件并返回索引"""
    with open(path, 'rb') as f:
        # 读取索引长度
        index_len = struct.unpack('>I', f.read(4))[0]
        # 读取索引
        index_data = f.read(index_len)
        index = decode_index(index_data)
    
    return index

def get_entry(index: MemoryIndex, entry_id: str, path: str) -> MemoryEntry:
    """根据 ID 获取记忆记录"""
    # 查找索引
    entry_meta = next((e for e in index.entries if e.id == entry_id), None)
    if not entry_meta:
        raise ValueError(f"未找到记忆：{entry_id}")
    
    # 读取记录
    with open(path, 'rb') as f:
        # 计算数据区起始位置
        index_len = struct.unpack('>I', f.read(4))[0]
        data_start = 4 + index_len
        
        # 定位到记录
        abs_offset = data_start + entry_meta.offset
        f.seek(abs_offset)
        
        # 读取元数据长度
        meta_len = struct.unpack('>I', f.read(4))[0]
        meta_compressed = f.read(meta_len)
        
        # 读取内容长度
        content_len = struct.unpack('>I', f.read(4))[0]
        content_compressed = f.read(content_len)
        
        # 解码
        meta = json.loads(lz4.frame.decompress(meta_compressed))
        content = json.loads(lz4.frame.decompress(content_compressed))
        
        return MemoryEntry(
            id=meta['id'],
            date=meta['date'],
            type=meta['type'],
            title=meta['title'],
            tags=meta['tags'],
            timestamp=meta['timestamp'],
            content=content,
            size=meta['size']
        )

def get_all_entries(index: MemoryIndex, path: str) -> List[MemoryEntry]:
    """获取所有记忆记录"""
    entries = []
    
    with open(path, 'rb') as f:
        # 跳过索引
        index_len = struct.unpack('>I', f.read(4))[0]
        f.seek(4 + index_len)
        
        # 读取所有记录
        for entry_meta in index.entries:
            f.seek(entry_meta.offset, os.SEEK_CUR if entries else os.SEEK_SET)
            # 重新计算绝对位置
            abs_offset = 4 + index_len + entry_meta.offset
            f.seek(abs_offset)
            
            # 读取记录
            meta_len = struct.unpack('>I', f.read(4))[0]
            f.seek(abs_offset)
            record_data = f.read(4 + meta_len + 4)  # 简化读取
            f.seek(abs_offset)
            
            # 完整读取
            meta_len = struct.unpack('>I', f.read(4))[0]
            meta_compressed = f.read(meta_len)
            content_len = struct.unpack('>I', f.read(4))[0]
            content_compressed = f.read(content_len)
            
            record_data = struct.pack('>I', meta_len) + meta_compressed + struct.pack('>I', content_len) + content_compressed
            entry = decode_entry(record_data)
            entries.append(entry)
    
    return entries

# ============== 转换工具 ==============

def convert_md_to_entry(md_path: str) -> Optional[MemoryEntry]:
    """将 Markdown 记忆转换为 MemoryEntry"""
    filename = os.path.basename(md_path)
    
    # 跳过非日志文件
    if not filename.startswith('2026-'):
        return None
    
    # 提取日期
    date_str = filename[:10]  # 2026-03-09
    try:
        date = int(date_str.replace('-', ''))
    except:
        return None
    
    # 读取内容
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题（第一行）
    lines = content.split('\n')
    title = lines[0].lstrip('#').strip() if lines else filename
    
    # 提取标签（从内容中推断）
    tags = []
    if '求职' in content or 'Agent' in content:
        tags.append('求职 Agent')
    if 'JWT' in content or 'Auth0' in content:
        tags.append('JWT')
    if 'SQLite' in content:
        tags.append('SQLite')
    if 'openViking' in content:
        tags.append('openViking')
    
    entry = MemoryEntry(
        id=date_str,
        date=date,
        type=1,  # WORK_LOG
        title=title,
        tags=tags,
        timestamp=datetime.now().isoformat(),
        content={'markdown': content, 'source_file': filename},
        size=len(content.encode('utf-8'))
    )
    
    return entry

def convert_json_to_entry(json_path: str) -> Optional[MemoryEntry]:
    """将 JSON 记忆转换为 MemoryEntry"""
    filename = os.path.basename(json_path)
    
    # 跳过测试文件
    if 'test' in filename.lower():
        return None
    
    # 提取日期
    date_str = filename.replace('.json', '').replace('.qmem', '')
    try:
        date = int(date_str.replace('-', ''))
    except:
        return None
    
    # 读取内容
    with open(json_path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    # 提取标题
    title = content.get('summary', filename)
    
    entry = MemoryEntry(
        id=date_str,
        date=date,
        type=content.get('type', 1),
        title=title,
        tags=[],
        timestamp=content.get('created_at', datetime.now().isoformat()),
        content=content,
        size=len(json.dumps(content).encode('utf-8'))
    )
    
    return entry

# ============== 命令行工具 ==============

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: memory_merge.py <command> [args]")
        print("Commands:")
        print("  merge [output.qmem]  - 合并所有记忆到单个文件")
        print("  list <file.qmem>     - 列出所有记忆")
        print("  get <file.qmem> <id> - 获取指定记忆")
        print("  stats <file.qmem>    - 显示统计信息")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'merge':
        # 合并所有记忆
        workspace = Path(r'C:\Users\TR\.openclaw\workspace')
        memory_dir = workspace / 'memory'
        output = sys.argv[2] if len(sys.argv) > 2 else str(memory_dir / 'memories.qmem')
        
        entries = []
        
        # 扫描记忆文件
        for f in memory_dir.glob('*.md'):
            if f.name.startswith('2026-'):
                entry = convert_md_to_entry(str(f))
                if entry:
                    entries.append(entry)
                    print(f"  [MD] {f.name}")
        
        for f in memory_dir.glob('*.json'):
            if f.name.startswith('2026-') and 'test' not in f.name.lower():
                entry = convert_json_to_entry(str(f))
                if entry:
                    entries.append(entry)
                    print(f"  [JSON] {f.name}")
        
        # 跳过 .qmem 文件（二进制格式，已在 JSON 中处理）
        # for f in memory_dir.glob('*.qmem'):
        #     if f.name.startswith('2026-') and 'test' not in f.name.lower():
        #         entry = convert_json_to_entry(str(f))
        #         if entry:
        #             entries.append(entry)
        #             print(f"  [QMEM] {f.name}")
        
        # 按日期排序
        entries.sort(key=lambda e: e.date)
        
        # 创建合并文件
        create_memory_file(entries, output)
    
    elif cmd == 'list':
        # 列出所有记忆
        path = sys.argv[2]
        index = load_memory_file(path)
        
        print(f"\n{'ID':<15} {'Date':<12} {'Type':<8} {'Title':<40} {'Tags'}")
        print("-" * 100)
        for entry in index.entries:
            date_str = str(entry.date)
            tags = ', '.join(entry.tags) if entry.tags else '-'
            print(f"{entry.id:<15} {date_str:<12} {entry.type:<8} {entry.title:<40} {tags}")
        print(f"\nTotal: {index.total_entries} entries")
    
    elif cmd == 'get':
        # 获取指定记忆
        path = sys.argv[2]
        entry_id = sys.argv[3]
        
        index = load_memory_file(path)
        entry = get_entry(index, entry_id, path)
        
        # 输出 JSON
        print(json.dumps(entry.content, indent=2, ensure_ascii=False))
    
    elif cmd == 'stats':
        # 显示统计信息
        path = sys.argv[2]
        index = load_memory_file(path)
        file_size = os.path.getsize(path)
        
        print(f"\n[STATS] Memory File Statistics")
        print(f"   File:     {path}")
        print(f"   Size:     {file_size} bytes ({file_size/1024:.1f} KB)")
        print(f"   Entries:  {index.total_entries}")
        print(f"   Index:    {len(encode_index(index))} bytes")
        print(f"   Average:  {file_size/index.total_entries:.0f} bytes/entry")
        
        if index.entries:
            dates = [e.date for e in index.entries]
            print(f"   Date:     {min(dates)} - {max(dates)}")
    
    else:
        print(f"未知命令：{cmd}")
        sys.exit(1)
