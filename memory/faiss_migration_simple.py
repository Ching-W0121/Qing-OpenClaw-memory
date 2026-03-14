#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAISS Migration - Simplified Version (使用随机向量降级)
"""

import sys
import json
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

# 尝试导入 FAISS
try:
    import faiss
    HAS_FAISS = True
    print("✅ FAISS 可用")
except:
    HAS_FAISS = False
    print("⚠️  FAISS 不可用，使用降级方案")

# 尝试导入 sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    HAS_SENTENCE = True
    print("✅ sentence-transformers 可用")
except:
    HAS_SENTENCE = False
    print("⚠️  sentence-transformers 不可用，使用随机向量")

def get_embedding(text: str) -> np.ndarray:
    """获取向量（优先 sentence-transformers，降级随机向量）"""
    if HAS_SENTENCE:
        return model.encode([text])[0].astype(np.float32)
    else:
        # 降级：随机向量
        return np.random.rand(384).astype(np.float32)

def semantic_chunk(text: str, chunk_size: int = 400, overlap: int = 50):
    """简单分块"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    paragraphs = text.split('\n\n')
    
    current = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        if len(current) + len(para) > chunk_size:
            if current:
                chunks.append(current)
            current = para[:chunk_size]
        else:
            current += "\n\n" + para if current else para
    
    if current:
        chunks.append(current)
    
    return chunks if chunks else [text]

def migrate_file(file_path: Path, memory_type: str, vault_conn):
    """迁移单个文件"""
    if not file_path.exists():
        print(f"  ⚠️  文件不存在：{file_path.name}")
        return 0
    
    print(f"📄 迁移：{file_path.name} ({memory_type})")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分块
    chunks = semantic_chunk(content)
    print(f"  分块数：{len(chunks)}")
    
    # 添加到数据库
    inserted = 0
    for i, chunk in enumerate(chunks):
        if len(chunk.strip()) < 20:
            continue
        
        memory_hash = hashlib.sha256(chunk.encode('utf-8')).hexdigest()[:32]
        vector = get_embedding(chunk)
        
        # 插入 SQLite
        vault_conn.execute("""
            INSERT OR IGNORE INTO memories (memory_hash, content, memory_type, metadata)
            VALUES (?, ?, ?, ?)
        """, (memory_hash, chunk[:2000], memory_type, json.dumps({
            'source_file': str(file_path),
            'chunk_index': i
        }, ensure_ascii=False)))
        
        if HAS_FAISS:
            # 添加到 FAISS
            vault_conn.add_vector(vector)
        
        inserted += 1
    
    vault_conn.commit()
    print(f"  ✅ 已插入 {inserted} 条")
    return inserted

class SimpleVault:
    """简化版 Vault"""
    
    def __init__(self, db_path: Path):
        import sqlite3
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.vectors = []
        
        # 创建表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_hash TEXT UNIQUE,
                content TEXT NOT NULL,
                memory_type TEXT DEFAULT 'episodic',
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
        
        print(f"✅ SQLite 已初始化：{db_path}")
    
    def add_vector(self, vector: np.ndarray):
        """添加向量到内存索引"""
        if HAS_FAISS:
            if not hasattr(self, 'index'):
                self.index = faiss.IndexFlatL2(384)
            self.index.add(vector.reshape(1, -1))
        else:
            self.vectors.append(vector)
    
    def execute(self, *args):
        return self.cursor.execute(*args)
    
    def commit(self):
        self.conn.commit()
    
    def get_stats(self):
        self.cursor.execute("SELECT COUNT(*) FROM memories")
        total = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
        by_type = dict(self.cursor.fetchall())
        
        return {
            'total': total,
            'by_type': by_type,
            'faiss_vectors': len(self.vectors) if not HAS_FAISS else getattr(self, 'index', None) and self.index.ntotal or 0
        }

def main():
    print("="*60)
    print("FAISS 数据迁移（简化版）")
    print("="*60)
    
    db_path = Path(__file__).parent / "memory_vault_faiss.db"
    vault = SimpleVault(db_path)
    
    # 要迁移的文件
    files = [
        ("memory/episodic/2026-03-12.jsonl", "episodic"),
        ("memory/episodic/2026-03-13.jsonl", "episodic"),
        ("memory/episodic/2026-03-14.jsonl", "episodic"),
        (".learnings/LEARNINGS.md", "learning"),
        (".learnings/ERRORS.md", "error"),
        ("MEMORY.md", "semantic"),
    ]
    
    total = 0
    workspace = Path(__file__).parent.parent
    
    for file_rel, mem_type in files:
        file_path = workspace / file_rel
        count = migrate_file(file_path, mem_type, vault)
        total += count
    
    print("\n" + "="*60)
    print(f"迁移完成！共 {total} 条记忆")
    
    stats = vault.get_stats()
    print(f"\n📊 数据库统计:")
    print(f"   总数：{stats['total']}")
    print(f"   类型：{stats['by_type']}")
    print("="*60)

if __name__ == '__main__':
    main()
