#!/usr/bin/env python3
"""
记忆编码工具 - 将人类可读的记忆转换为紧凑的二进制格式
格式：自定义二进制 + LZ4 压缩 + Base85 编码
"""

import struct
import lz4.frame
import base64
import json
import zlib
from datetime import datetime
from enum import IntEnum
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

# ============== 常量定义 ==============

MAGIC = b'QMEM'  # Qing Memory
VERSION = 1
HEADER_SIZE = 16

# ============== 类型定义 ==============

class MemoryType(IntEnum):
    WORK_LOG = 1      # 工作日志
    LEARNING = 2      # 学习记录
    ERROR = 3         # 错误记录
    CONFIG = 4        # 配置变更
    MEETING = 5       # 会议记录
    TASK = 6          # 任务记录

class StatusCode(IntEnum):
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3
    CANCELLED = 4

# ============== 数据结构 ==============

@dataclass
class Event:
    title: str
    status: int
    timestamp: str
    tags: List[str]
    files_added: List[str]
    files_modified: List[str]
    metrics: Dict[str, Any]
    notes: str = ""

@dataclass
class MemoryRecord:
    date: int           # YYYYMMDD
    type: int           # MemoryType
    events: List[Event]
    progress: Dict[str, float]
    summary: str
    created_at: str

# ============== TLV 编码 ==============

TLV_TAGS = {
    'date': 0x01,
    'type': 0x02,
    'summary': 0x03,
    'events': 0x04,
    'progress': 0x05,
    'created_at': 0x06,
}

def encode_tlv(tag: int, value: bytes) -> bytes:
    """编码 TLV (Tag-Length-Value)"""
    return struct.pack('>BH', tag, len(value)) + value

def decode_tlv(data: bytes) -> Dict[int, bytes]:
    """解码 TLV"""
    result = {}
    offset = 0
    while offset < len(data):
        tag, length = struct.unpack('>BH', data[offset:offset+3])
        value = data[offset+3:offset+3+length]
        result[tag] = value
        offset += 3 + length
    return result

# ============== 编码/解码 ==============

def _encode_memory_raw(record: MemoryRecord) -> bytes:
    """将 MemoryRecord 编码为原始二进制格式（不含 Base85）"""
    
    # 1. 编码 Metadata (TLV)
    metadata = b''
    
    # Date
    metadata += encode_tlv(TLV_TAGS['date'], str(record.date).encode())
    
    # Type
    metadata += encode_tlv(TLV_TAGS['type'], struct.pack('>B', record.type))
    
    # Summary
    metadata += encode_tlv(TLV_TAGS['summary'], record.summary.encode('utf-8'))
    
    # Events (JSON 编码后压缩)
    events_json = json.dumps([asdict(e) for e in record.events]).encode('utf-8')
    events_compressed = lz4.frame.compress(events_json)
    metadata += encode_tlv(TLV_TAGS['events'], events_compressed)
    
    # Progress
    progress_json = json.dumps(record.progress).encode('utf-8')
    progress_compressed = lz4.frame.compress(progress_json)
    metadata += encode_tlv(TLV_TAGS['progress'], progress_compressed)
    
    # Created At
    metadata += encode_tlv(TLV_TAGS['created_at'], record.created_at.encode('utf-8'))
    
    # 2. 构建 Header
    flags = 0  # 保留位
    header = struct.pack('>4sBBHQ', MAGIC, VERSION, record.type, flags, len(metadata))
    
    # 3. 组合数据
    raw_data = header + metadata
    
    # 4. 计算 CRC32
    crc = zlib.crc32(raw_data) & 0xffffffff
    checksum = struct.pack('>I', crc)
    
    # 5. 最终二进制数据
    return raw_data + checksum

def encode_memory(record: MemoryRecord) -> str:
    """将 MemoryRecord 编码为 Base85 文本格式（兼容旧版）"""
    raw_data = _encode_memory_raw(record)
    return base64.b85encode(raw_data).decode('ascii')

def _decode_memory_raw(raw_data: bytes) -> MemoryRecord:
    """从原始二进制数据解码 MemoryRecord"""
    
    # 2. 验证 CRC32
    data = raw_data[:-4]
    stored_crc = struct.unpack('>I', raw_data[-4:])[0]
    calculated_crc = zlib.crc32(data) & 0xffffffff
    if stored_crc != calculated_crc:
        raise ValueError("CRC32 校验失败")
    
    # 3. 解析 Header
    magic, version, mem_type, flags, metadata_len = struct.unpack('>4sBBHQ', data[:16])
    
    if magic != MAGIC:
        raise ValueError(f"无效的 Magic: {magic}")
    if version != VERSION:
        raise ValueError(f"不支持的版本：{version}")
    
    # 4. 解析 Metadata
    metadata = data[16:16+metadata_len]
    tlv_data = decode_tlv(metadata)
    
    # 5. 提取字段
    date = int(tlv_data[TLV_TAGS['date']].decode())
    mem_type = struct.unpack('>B', tlv_data[TLV_TAGS['type']])[0]
    summary = tlv_data[TLV_TAGS['summary']].decode('utf-8')
    created_at = tlv_data[TLV_TAGS['created_at']].decode('utf-8')
    
    # 6. 解压缩 Events
    events_json = lz4.frame.decompress(tlv_data[TLV_TAGS['events']])
    events_data = json.loads(events_json)
    events = [Event(**e) for e in events_data]
    
    # 7. 解压缩 Progress
    progress_json = lz4.frame.decompress(tlv_data[TLV_TAGS['progress']])
    progress = json.loads(progress_json)
    
    return MemoryRecord(
        date=date,
        type=mem_type,
        events=events,
        progress=progress,
        summary=summary,
        created_at=created_at
    )

def decode_memory(encoded: str) -> MemoryRecord:
    """将 Base85 编码解码为 MemoryRecord（兼容旧版）"""
    raw_data = base64.b85decode(encoded.encode('ascii'))
    return _decode_memory_raw(raw_data)

def memory_from_file(path: str) -> MemoryRecord:
    """从文件读取记忆（自动检测二进制/Base85 格式）"""
    with open(path, 'rb') as f:
        raw_data = f.read()
    
    # 检测格式：如果前 4 字节是 Magic，则是二进制格式
    if raw_data[:4] == MAGIC:
        return _decode_memory_raw(raw_data)
    
    # 否则是 Base85 文本格式
    encoded = raw_data.decode('ascii')
    return decode_memory(encoded)

# ============== 工具函数 ==============

def memory_to_file(record: MemoryRecord, path: str, binary: bool = True):
    """将记忆写入文件"""
    raw_data = _encode_memory_raw(record)
    
    if binary:
        # 二进制模式
        with open(path, 'wb') as f:
            f.write(raw_data)
        encoded_size = len(raw_data)
    else:
        # Base85 文本模式（兼容旧格式）
        encoded = base64.b85encode(raw_data).decode('ascii')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(encoded)
        encoded_size = len(encoded.encode('utf-8'))
    
    original_size = len(json.dumps(asdict(record)).encode('utf-8'))
    mode = "binary" if binary else "base85"
    print(f"[OK] Memory written ({mode}): {path}")
    print(f"     Original: {original_size} bytes")
    print(f"     Encoded:  {encoded_size} bytes")
    print(f"     Ratio:    {encoded_size/original_size*100:.1f}%")



def memory_to_human(record: MemoryRecord) -> str:
    """将 MemoryRecord 转换为人类可读格式（用于调试）"""
    lines = [
        f"# {record.date} 记忆日志",
        f"类型：{MemoryType(record.type).name}",
        f"创建时间：{record.created_at}",
        "",
        "## 摘要",
        record.summary,
        "",
        "## 事件",
    ]
    
    for i, event in enumerate(record.events, 1):
        lines.extend([
            f"### {i}. {event.title}",
            f"状态：{StatusCode(event.status).name}",
            f"时间：{event.timestamp}",
            f"标签：{', '.join(event.tags)}",
            f"新增文件：{len(event.files_added)}",
            f"修改文件：{len(event.files_modified)}",
            f"指标：{event.metrics}",
        ])
        if event.notes:
            lines.append(f"备注：{event.notes}")
        lines.append("")
    
    lines.extend([
        "## 进度",
        json.dumps(record.progress, indent=2, ensure_ascii=False)
    ])
    
    return '\n'.join(lines)

# ============== 命令行工具 ==============

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: memory_tool.py <encode|decode|human> <input> [output] [--binary]")
        print("  --binary: Use binary format (smaller, default)")
        print("  --base85: Use Base85 text format (compatible)")
        sys.exit(1)
    
    binary_mode = '--binary' not in sys.argv  # Default to binary
    cmd = sys.argv[1]
    
    if cmd == 'encode':
        # 从 JSON 编码为二进制
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 转换为 dataclass 实例
        events = [Event(**e) for e in data['events']]
        record = MemoryRecord(
            date=data['date'],
            type=data['type'],
            events=events,
            progress=data['progress'],
            summary=data['summary'],
            created_at=data['created_at']
        )
        output = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != '--base85' else sys.argv[2].replace('.json', '.qmem')
        use_base85 = '--base85' in sys.argv
        memory_to_file(record, output, binary=not use_base85)
    
    elif cmd == 'decode':
        # 从二进制解码为 JSON
        record = memory_from_file(sys.argv[2])
        output = sys.argv[3] if len(sys.argv) > 3 else sys.argv[2].replace('.qmem', '.json')
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(asdict(record), f, indent=2, ensure_ascii=False)
        print(f"[OK] Decoded: {output}")
    
    elif cmd == 'human':
        # 从二进制转换为人类可读格式
        record = memory_from_file(sys.argv[2])
        output = sys.argv[3] if len(sys.argv) > 3 else sys.argv[2].replace('.qmem', '.md')
        with open(output, 'w', encoding='utf-8') as f:
            f.write(memory_to_human(record))
        print(f"[OK] Converted: {output}")
    
    else:
        print(f"未知命令：{cmd}")
        sys.exit(1)
