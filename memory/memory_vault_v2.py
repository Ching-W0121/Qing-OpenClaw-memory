#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Vault Optimizer - 分块存储优化模块

优化方案:
1. 按语义块分割大文件
2. 批量插入 SQLite（每块独立 Embedding）
3. SQL 语义检索（只加载 Top-K）
4. LRU 缓存高频访问记忆

作者：青 (Qing)
创建日期：2026-03-14
版本：v2.0
"""

import sqlite3
import json
import hashlib
import requests
import sys
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import OrderedDict
import numpy as np

# 设置控制台输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ==================== 配置 ====================

DB_PATH = Path(__file__).parent / "memory_vault.db"
DOUBAO_API_KEY = "fddc1778-d04c-403e-8327-ab68ec1ec9dd"
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/embeddings/multimodal"
DOUBAO_MODEL = "doubao-embedding-vision-251215"
EMBEDDING_DIM = 2048

# LRU 缓存配置
LRU_CACHE_SIZE = 100  # 缓存 100 条高频记忆

# 分块配置
CHUNK_SIZE = 300  # 每块最大字符数
CHUNK_OVERLAP = 50  # 块之间重叠字符数

# ==================== LRU 缓存 ====================

class LRUCache:
    """LRU 缓存 - 高频访问记忆缓存"""
    
    def __init__(self, capacity: int = LRU_CACHE_SIZE):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Dict]:
        """获取缓存"""
        with self.lock:
            if key in self.cache:
                # 移动到末尾（最近使用）
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    def put(self, key: str, value: Dict):
        """存入缓存"""
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            
            # 超出容量，删除最旧的
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()

# 全局缓存实例
memory_cache = LRUCache(capacity=LRU_CACHE_SIZE)

# ==================== 数据库优化 ====================

def init_optimized_database(db_path: Optional[Path] = None):
    """初始化优化的数据库（添加向量索引）"""
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 确保 memories 表存在
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_hash TEXT UNIQUE NOT NULL,
            memory_text TEXT NOT NULL,
            memory_type TEXT DEFAULT 'episodic',
            embedding BLOB NOT NULL,
            embedding_dim INTEGER DEFAULT 2048,
            metadata JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            access_count INTEGER DEFAULT 0,
            last_accessed TIMESTAMP
        )
    """)
    
    # 创建索引（优化查询）
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_access_count ON memories(access_count)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_hash ON memories(memory_hash)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ 优化的数据库已初始化：{db_path}")
    return db_path

# ==================== 智能分块 ====================

def semantic_chunk(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    智能语义分块（按自然段落分割）
    
    Args:
        text: 原始文本
        chunk_size: 每块最大字符数
        overlap: 块之间重叠字符数
    
    Returns:
        分块后的文本列表
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    
    # 按段落分割
    paragraphs = re.split(r'\n\s*\n', text)
    
    current_chunk = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # 如果当前段落 + 已有内容超过限制
        if len(current_chunk) + len(para) > chunk_size:
            # 保存当前块
            if current_chunk:
                chunks.append(current_chunk)
            
            # 如果单个段落超长，按句子切分
            if len(para) > chunk_size:
                sentences = re.split(r'[。！？.!?\n]', para)
                current_chunk = ""
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    
                    if len(current_chunk) + len(sent) > chunk_size - overlap:
                        chunks.append(current_chunk)
                        current_chunk = sent
                    else:
                        current_chunk += " " + sent if current_chunk else sent
            else:
                current_chunk = para
        else:
            current_chunk += "\n\n" + para if current_chunk else para
    
    # 保存最后一个块
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks if chunks else [text]

# 导入 re 模块
import re

# ==================== Embedding 生成 ====================

def get_embedding(text: str) -> np.ndarray:
    """调用豆包 API 获取文本向量嵌入"""
    headers = {
        "Authorization": f"Bearer {DOUBAO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": DOUBAO_MODEL,
        "encoding_format": "float",
        "input": [
            {"type": "text", "text": text}
        ]
    }
    
    try:
        response = requests.post(DOUBAO_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        embedding = result['data']['embedding']
        
        return np.array(embedding, dtype=np.float32)
    
    except Exception as e:
        print(f"❌ 获取 embedding 失败：{e}")
        return np.zeros(EMBEDDING_DIM, dtype=np.float32)

def batch_get_embeddings(texts: List[str]) -> List[np.ndarray]:
    """批量生成 Embedding（减少 API 调用）"""
    embeddings = []
    
    for i, text in enumerate(texts, 1):
        print(f"  生成 Embedding [{i}/{len(texts)}]...")
        emb = get_embedding(text)
        embeddings.append(emb)
    
    return embeddings

# ==================== 批量插入 ====================

def compute_hash(text: str) -> str:
    """计算记忆文本的哈希值"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:32]

def chunk_and_store_file(
    file_path: Path,
    memory_type: str = 'archived',
    db_path: Optional[Path] = None,
    batch_size: int = 10
) -> int:
    """
    分块存储文件到数据库
    
    Args:
        file_path: 文件路径
        memory_type: 记忆类型
        db_path: 数据库路径
        batch_size: 批量插入大小
    
    Returns:
        插入的记忆条数
    """
    if db_path is None:
        db_path = DB_PATH
    
    print(f"\n📄 处理：{file_path.name}")
    
    # 读取文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"  ❌ 读取失败：{e}")
        return 0
    
    # 智能分块
    chunks = semantic_chunk(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
    print(f"  📊 分块数：{len(chunks)}")
    
    # 批量插入
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    inserted = 0
    batch = []
    
    for i, chunk in enumerate(chunks, 1):
        if len(chunk.strip()) < 20:  # 跳过太短的块
            continue
        
        memory_hash = compute_hash(chunk)
        metadata = {
            'source_file': str(file_path),
            'chunk_index': i,
            'chunk_total': len(chunks),
            'file_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        batch.append((
            memory_hash,
            chunk[:2000],  # 限制长度
            memory_type,
            None,  # embedding 占位
            EMBEDDING_DIM,
            json.dumps(metadata, ensure_ascii=False)
        ))
        
        # 达到批量大小，插入数据库
        if len(batch) >= batch_size:
            inserted += insert_batch(cursor, batch)
            conn.commit()
            batch = []
    
    # 插入剩余块
    if batch:
        inserted += insert_batch(cursor, batch)
        conn.commit()
    
    conn.close()
    
    print(f"  ✅ 已插入 {inserted} 条记忆")
    return inserted

def insert_batch(cursor, batch: List[Tuple]) -> int:
    """批量插入（带 Embedding 生成）"""
    inserted = 0
    
    for item in batch:
        memory_hash, text, mem_type, _, emb_dim, metadata = item
        
        # 检查是否已存在
        cursor.execute("SELECT id FROM memories WHERE memory_hash = ?", (memory_hash,))
        if cursor.fetchone():
            continue
        
        # 生成 Embedding
        embedding = get_embedding(text)
        
        # 插入
        try:
            cursor.execute("""
                INSERT INTO memories (memory_hash, memory_text, memory_type, embedding, embedding_dim, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (memory_hash, text, mem_type, embedding.tobytes(), emb_dim, metadata))
            inserted += 1
        except sqlite3.IntegrityError:
            continue
    
    return inserted

# ==================== 高效语义检索 ====================

def search_memory_optimized(
    query: str,
    top_k: int = 5,
    min_similarity: float = 0.5,
    memory_type: Optional[str] = None,
    db_path: Optional[Path] = None,
    use_cache: bool = True
) -> List[Dict]:
    """
    优化的语义检索（只加载 Top-K，不加载全部）
    
    Args:
        query: 搜索查询
        top_k: 返回最相关的 K 条
        min_similarity: 最小相似度阈值
        memory_type: 过滤记忆类型
        db_path: 数据库路径
        use_cache: 使用 LRU 缓存
    
    Returns:
        相关记忆列表
    """
    if db_path is None:
        db_path = DB_PATH
    
    # 检查缓存
    cache_key = f"{query}:{top_k}:{memory_type}"
    if use_cache:
        cached = memory_cache.get(cache_key)
        if cached:
            print(f"✅ 缓存命中：{query[:30]}...")
            return cached
    
    # 生成查询 Embedding
    print(f"🔍 检索：{query[:50]}...")
    query_embedding = get_embedding(query)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 获取记忆（可加类型过滤）
        if memory_type:
            cursor.execute("""
                SELECT id, memory_text, memory_type, metadata, embedding 
                FROM memories 
                WHERE memory_type = ?
                ORDER BY access_count DESC
                LIMIT 100
            """, (memory_type,))
        else:
            cursor.execute("""
                SELECT id, memory_text, memory_type, metadata, embedding 
                FROM memories 
                ORDER BY access_count DESC
                LIMIT 200
            """)
        
        rows = cursor.fetchall()
        
        # 计算相似度（在内存中）
        results = []
        for row in rows:
            memory_id, memory_text, mem_type, metadata, embedding_bytes = row
            
            # 转换 embedding
            embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
            
            # 计算余弦相似度
            similarity = cosine_similarity(query_embedding, embedding)
            
            if similarity >= min_similarity:
                results.append({
                    'id': memory_id,
                    'memory_text': memory_text,
                    'memory_type': mem_type,
                    'metadata': json.loads(metadata) if metadata else {},
                    'similarity': similarity
                })
        
        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 取 Top-K
        top_results = results[:top_k]
        
        # 更新访问计数
        for result in top_results:
            cursor.execute("""
                UPDATE memories 
                SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (result['id'],))
        
        conn.commit()
        
        # 存入缓存
        if use_cache and top_results:
            memory_cache.put(cache_key, top_results)
        
        print(f"✅ 找到 {len(results)} 条相关记忆，返回 Top-{len(top_results)}")
        return top_results
    
    except Exception as e:
        print(f"❌ 检索失败：{e}")
        return []
    
    finally:
        conn.close()

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """计算余弦相似度"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))

# ==================== 统计信息 ====================

def get_memory_stats(db_path: Optional[Path] = None) -> Dict:
    """获取记忆统计信息"""
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM memories")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
        by_type = dict(cursor.fetchall())
        
        cursor.execute("SELECT COUNT(*) FROM memories WHERE last_accessed IS NOT NULL")
        accessed = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(access_count) FROM memories")
        avg_access = cursor.fetchone()[0] or 0
        
        return {
            'total': total,
            'by_type': by_type,
            'accessed': accessed,
            'avg_access': avg_access,
            'database': str(db_path),
            'cache_size': len(memory_cache.cache)
        }
    
    finally:
        conn.close()

# ==================== 命令行工具 ====================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print("  python memory_vault_v2.py optimize <文件路径> [类型]")
        print("  python memory_vault_v2.py search <查询> [top_k]")
        print("  python memory_vault_v2.py stats")
        print("  python memory_vault_v2.py cache-clear")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'optimize':
        if len(sys.argv) < 3:
            print("❌ 请提供文件路径")
            sys.exit(1)
        
        file_path = Path(sys.argv[2])
        memory_type = sys.argv[3] if len(sys.argv) > 3 else 'archived'
        
        init_optimized_database()
        chunk_and_store_file(file_path, memory_type)
    
    elif command == 'search':
        if len(sys.argv) < 3:
            print("❌ 请提供搜索查询")
            sys.exit(1)
        
        query = ' '.join(sys.argv[2:-1]) if len(sys.argv) > 3 else sys.argv[2]
        top_k = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 5
        
        results = search_memory_optimized(query, top_k=top_k)
        
        print(f"\n📊 检索结果 ({len(results)} 条):")
        for i, mem in enumerate(results, 1):
            print(f"\n{i}. 相似度：{mem['similarity']:.2f} | 类型：{mem['memory_type']}")
            print(f"   {mem['memory_text'][:100]}...")
    
    elif command == 'stats':
        stats = get_memory_stats()
        print(f"\n📊 记忆库统计:")
        print(f"   数据库：{stats['database']}")
        print(f"   总数：{stats['total']}")
        print(f"   已访问：{stats['accessed']}")
        print(f"   平均访问：{stats['avg_access']:.1f}")
        print(f"   LRU 缓存：{stats['cache_size']} 条")
        print(f"   类型分布:")
        for mem_type, count in stats['by_type'].items():
            print(f"     - {mem_type}: {count}")
    
    elif command == 'cache-clear':
        memory_cache.clear()
        print("✅ LRU 缓存已清空")
    
    else:
        print(f"❌ 未知命令：{command}")
        sys.exit(1)
