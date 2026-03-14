#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Vault FAISS - FAISS + SQLite 双轨架构记忆系统

功能:
1. SQLite 持久化存储 (content + metadata)
2. FAISS 向量索引 (毫秒级检索)
3. sentence-transformers Embedding
4. 语义切片 (300-500 字/块)
5. LRU 缓存高频记忆

作者：青 (Qing)
创建日期：2026-03-14
版本：v3.0 (FAISS Edition)
"""

import sqlite3
import json
import hashlib
import pickle
import re
import sys
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import OrderedDict
import numpy as np

# ==================== 配置 ====================

DB_PATH = Path(__file__).parent / "memory_vault_faiss.db"
INDEX_PATH = Path(__file__).parent / "memory_vault_faiss.index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 维度

# 分块配置
CHUNK_SIZE = 400  # 每块最大字符数
CHUNK_OVERLAP = 50  # 块之间重叠

# LRU 缓存配置
LRU_CACHE_SIZE = 100

# ==================== LRU 缓存 ====================

class LRUCache:
    """LRU 缓存 - 高频访问记忆缓存"""
    
    def __init__(self, capacity: int = LRU_CACHE_SIZE):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Dict]:
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    def put(self, key: str, value: Dict):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)
    
    def clear(self):
        with self.lock:
            self.cache.clear()

# ==================== Embedding 模型 ====================

class EmbeddingModel:
    """sentence-transformers Embedding 模型"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = None
        self.lock = threading.Lock()
    
    def load(self):
        """懒加载模型"""
        if self.model is None:
            with self.lock:
                if self.model is None:
                    try:
                        from sentence_transformers import SentenceTransformer
                        print(f"🔧 加载 Embedding 模型：{self.model_name}...")
                        self.model = SentenceTransformer(self.model_name)
                        print(f"✅ 模型加载完成 (维度：{EMBEDDING_DIM})")
                    except ImportError:
                        print("⚠️  未安装 sentence-transformers，使用随机向量降级")
                        self.model = "random"
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """编码文本为向量"""
        self.load()
        
        if self.model == "random":
            # 降级：随机向量
            return np.random.rand(len(texts), EMBEDDING_DIM).astype(np.float32)
        
        with self.lock:
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return embeddings.astype(np.float32)
    
    def encode_single(self, text: str) -> np.ndarray:
        """编码单个文本"""
        return self.encode([text])[0]

# 全局 Embedding 模型实例
embedding_model = EmbeddingModel()

# ==================== 数据库初始化 ====================

def init_database(db_path: Optional[Path] = None):
    """初始化 SQLite 数据库"""
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建 memories 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_hash TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            memory_type TEXT DEFAULT 'episodic',
            metadata JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            access_count INTEGER DEFAULT 0,
            last_accessed TIMESTAMP
        )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_access_count ON memories(access_count)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_hash ON memories(memory_hash)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ SQLite 数据库已初始化：{db_path}")
    return db_path

# ==================== FAISS 索引 ====================

def init_faiss_index(existing_vectors: Optional[np.ndarray] = None):
    """初始化 FAISS 索引"""
    try:
        import faiss
        
        # 使用 HNSW 索引（支持高效 ANN 搜索）
        if existing_vectors is not None and len(existing_vectors) > 0:
            dim = existing_vectors.shape[1]
            index = faiss.IndexHNSWFlat(dim, 32)
            index.hnsw.efSearch = 64
            index.hnsw.efConstruction = 200
            index.add(existing_vectors)
            print(f"✅ FAISS HNSW 索引已构建 ({len(existing_vectors)} 条向量)")
        else:
            dim = EMBEDDING_DIM
            index = faiss.IndexHNSWFlat(dim, 32)
            index.hnsw.efSearch = 64
            print(f"✅ FAISS HNSW 索引已初始化 (维度：{dim})")
        
        return index
    
    except ImportError:
        print("⚠️  未安装 faiss-cpu，使用线性搜索降级")
        return "linear"

# ==================== 智能分块 ====================

def semantic_chunk(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """智能语义分块"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    paragraphs = re.split(r'\n\s*\n', text)
    
    current_chunk = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        if len(current_chunk) + len(para) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk)
            
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
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks if chunks else [text]

# ==================== 核心功能模块 ====================

class MemoryVaultFAISS:
    """FAISS + SQLite 双轨架构记忆系统"""
    
    def __init__(self, db_path: Optional[Path] = None, index_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.index_path = index_path or INDEX_PATH
        
        # 初始化数据库
        init_database(self.db_path)
        
        # 初始化 LRU 缓存
        self.cache = LRUCache(capacity=LRU_CACHE_SIZE)
        
        # 加载或创建 FAISS 索引
        self.index = self._load_or_create_index()
        
        # 加载 ID 映射
        self.id_mapping = self._load_id_mapping()
        
        print(f"✅ Memory Vault FAISS 已初始化")
        print(f"   SQLite: {self.db_path}")
        print(f"   FAISS 索引：{len(self.id_mapping)} 条向量")
        print(f"   LRU 缓存：{LRU_CACHE_SIZE} 条")
    
    def _load_or_create_index(self):
        """加载或创建 FAISS 索引"""
        import faiss
        
        # 尝试加载现有索引
        if self.index_path.exists():
            try:
                print(f"📂 加载 FAISS 索引：{self.index_path}")
                index = faiss.read_index(str(self.index_path))
                return index
            except Exception as e:
                print(f"⚠️  加载索引失败：{e}，重新构建")
        
        # 从数据库加载所有记忆并构建索引
        print("🔧 从数据库构建 FAISS 索引...")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, content FROM memories ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            contents = [row[1] for row in rows]
            vectors = embedding_model.encode(contents)
            index = init_faiss_index(vectors)
            
            # 保存索引
            faiss.write_index(index, str(self.index_path))
            print(f"✅ FAISS 索引已保存：{self.index_path}")
            
            return index
        else:
            return init_faiss_index()
    
    def _load_id_mapping(self) -> Dict[int, int]:
        """加载 ID 映射 (FAISS index -> SQLite id)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM memories ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        
        # FAISS index (从 0 开始) -> SQLite id
        return {i: row[0] for i, row in enumerate(rows)}
    
    def _save_id_mapping(self):
        """保存 ID 映射（隐含在索引顺序中）"""
        pass  # 不需要显式保存，顺序即映射
    
    def _compute_hash(self, text: str) -> str:
        """计算记忆哈希"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:32]
    
    def add_memory(self, text: str, memory_type: str = 'episodic', metadata: Optional[Dict] = None) -> int:
        """
        添加记忆（SQLite + FAISS 双写）
        
        Args:
            text: 记忆文本
            memory_type: 记忆类型
            metadata: 元数据
        
        Returns:
            SQLite 中的记忆 ID
        """
        # 分块处理
        chunks = semantic_chunk(text, CHUNK_SIZE, CHUNK_OVERLAP)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        inserted_ids = []
        
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 20:
                continue
            
            memory_hash = self._compute_hash(chunk)
            
            # 检查是否已存在
            cursor.execute("SELECT id FROM memories WHERE memory_hash = ?", (memory_hash,))
            if cursor.fetchone():
                continue
            
            # 插入 SQLite
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata['chunk_index'] = i
            chunk_metadata['chunk_total'] = len(chunks)
            
            cursor.execute("""
                INSERT INTO memories (memory_hash, content, memory_type, metadata)
                VALUES (?, ?, ?, ?)
            """, (memory_hash, chunk[:2000], memory_type, json.dumps(chunk_metadata, ensure_ascii=False)))
            
            sqlite_id = cursor.lastrowid
            inserted_ids.append(sqlite_id)
            
            # 添加到 FAISS
            vector = embedding_model.encode_single(chunk)
            faiss_index = len(self.id_mapping)
            self.index.add(vector.reshape(1, -1))
            self.id_mapping[faiss_index] = sqlite_id
        
        conn.commit()
        conn.close()
        
        # 实时保存 FAISS 索引
        import faiss
        faiss.write_index(self.index, str(self.index_path))
        
        if inserted_ids:
            print(f"✅ 已添加 {len(inserted_ids)} 条记忆到 SQLite + FAISS")
            return inserted_ids[0]
        else:
            print(f"⚠️  记忆已存在")
            return -1
    
    def search_memory(self, query: str, top_k: int = 5, min_similarity: float = 0.0) -> List[Dict]:
        """
        语义检索（FAISS 毫秒级定位 + SQLite 提取）
        
        Args:
            query: 搜索查询
            top_k: 返回最相关的 K 条
            min_similarity: 最小相似度阈值（0-1）
        
        Returns:
            相关记忆列表
        """
        import faiss
        
        # 检查缓存
        cache_key = f"{query}:{top_k}"
        cached = self.cache.get(cache_key)
        if cached:
            print(f"✅ 缓存命中：{query[:30]}...")
            return cached
        
        # 生成查询向量
        query_vector = embedding_model.encode_single(query)
        
        # FAISS 搜索（毫秒级）
        if isinstance(self.index, str):
            # 降级：线性搜索
            print("⚠️  使用线性搜索降级")
            return self._linear_search(query_vector, top_k)
        
        # FAISS HNSW 搜索
        D, I = self.index.search(query_vector.reshape(1, -1), top_k)
        
        # 转换距离为相似度
        distances = D[0]
        faiss_indices = I[0]
        
        # 根据 FAISS index 获取 SQLite id
        sqlite_ids = [self.id_mapping.get(idx, -1) for idx in faiss_indices if idx in self.id_mapping]
        
        if not sqlite_ids:
            return []
        
        # SQLite 提取完整记忆
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(sqlite_ids))
        cursor.execute(f"""
            SELECT id, content, memory_type, metadata, access_count
            FROM memories
            WHERE id IN ({placeholders})
            ORDER BY id
        """, sqlite_ids)
        
        rows = cursor.fetchall()
        
        # 更新访问计数
        for row in rows:
            cursor.execute("""
                UPDATE memories
                SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (row[0],))
        
        conn.commit()
        conn.close()
        
        # 构建结果
        results = []
        for i, row in enumerate(rows):
            memory_id, content, memory_type, metadata, access_count = row
            
            # 计算相似度（余弦相似度归一化）
            similarity = 1 / (1 + distances[i]) if i < len(distances) else 0
            
            if similarity >= min_similarity:
                results.append({
                    'id': memory_id,
                    'content': content,
                    'memory_type': memory_type,
                    'metadata': json.loads(metadata) if metadata else {},
                    'access_count': access_count,
                    'similarity': float(similarity)
                })
        
        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 存入缓存
        if results:
            self.cache.put(cache_key, results[:top_k])
        
        print(f"✅ FAISS 检索完成：{len(results)} 条相关记忆，返回 Top-{len(results[:top_k])}")
        return results[:top_k]
    
    def _linear_search(self, query_vector: np.ndarray, top_k: int) -> List[Dict]:
        """线性搜索降级方案"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, content FROM memories ORDER BY access_count DESC LIMIT 200")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return []
        
        # 计算所有向量
        contents = [row[1] for row in rows]
        vectors = embedding_model.encode(contents)
        
        # 计算余弦相似度
        def cosine_sim(v1, v2):
            return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        
        results = []
        for i, row in enumerate(rows):
            sim = cosine_sim(query_vector, vectors[i])
            results.append({
                'id': row[0],
                'content': row[1][:500],
                'similarity': float(sim)
            })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM memories")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
        by_type = dict(cursor.fetchall())
        
        cursor.execute("SELECT AVG(access_count) FROM memories")
        avg_access = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total': total,
            'by_type': by_type,
            'avg_access': avg_access,
            'faiss_vectors': len(self.id_mapping),
            'cache_size': len(self.cache.cache),
            'database': str(self.db_path)
        }

# ==================== 命令行工具 ====================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print("  python memory_vault_faiss.py add <文本> [类型]")
        print("  python memory_vault_faiss.py search <查询> [top_k]")
        print("  python memory_vault_faiss.py stats")
        print("  python memory_vault_faiss.py rebuild-index")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'add':
        if len(sys.argv) < 3:
            print("❌ 请提供文本")
            sys.exit(1)
        text = ' '.join(sys.argv[2:-1]) if len(sys.argv) > 3 else sys.argv[2]
        memory_type = sys.argv[-1] if sys.argv[-1] not in ['5', '10'] else 'episodic'
        
        vault = MemoryVaultFAISS()
        vault.add_memory(text, memory_type)
    
    elif command == 'search':
        if len(sys.argv) < 3:
            print("❌ 请提供查询")
            sys.exit(1)
        query = ' '.join(sys.argv[2:-1]) if len(sys.argv) > 3 else sys.argv[2]
        top_k = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 5
        
        vault = MemoryVaultFAISS()
        results = vault.search_memory(query, top_k=top_k)
        
        print(f"\n📊 检索结果 ({len(results)} 条):")
        for i, mem in enumerate(results, 1):
            print(f"\n{i}. 相似度：{mem['similarity']:.4f} | 类型：{mem['memory_type']}")
            print(f"   {mem['content'][:150]}...")
    
    elif command == 'stats':
        vault = MemoryVaultFAISS()
        stats = vault.get_stats()
        print(f"\n📊 Memory Vault FAISS 统计:")
        print(f"   数据库：{stats['database']}")
        print(f"   总数：{stats['total']}")
        print(f"   FAISS 向量：{stats['faiss_vectors']}")
        print(f"   平均访问：{stats['avg_access']:.1f}")
        print(f"   LRU 缓存：{stats['cache_size']}")
        print(f"   类型分布:")
        for mem_type, count in stats['by_type'].items():
            print(f"     - {mem_type}: {count}")
    
    elif command == 'rebuild-index':
        print("🔧 重建 FAISS 索引...")
        vault = MemoryVaultFAISS()
        import faiss
        faiss.write_index(vault.index, str(vault.index_path))
        print(f"✅ FAISS 索引已重建：{INDEX_PATH}")
    
    else:
        print(f"❌ 未知命令：{command}")
        sys.exit(1)
