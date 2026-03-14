#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Vault - 基于 SQLite 的长期记忆存储与语义检索系统

功能:
1. 存储记忆文本 + 向量嵌入 (豆包模型)
2. 语义检索 (余弦相似度 Top-K)
3. 自动集成到决策工作流

作者：青 (Qing)
创建日期：2026-03-14
"""

import sqlite3
import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import numpy as np

# ==================== 配置 ====================

DB_PATH = Path(__file__).parent / "memory_vault.db"
DOUBAO_API_KEY = "fddc1778-d04c-403e-8327-ab68ec1ec9dd"
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/embeddings"
DOUBAO_MODEL = "doubao-embedding-vision-251215"
EMBEDDING_DIM = 2048  # 豆包向量维度

# ==================== 数据库初始化 ====================

def init_database(db_path: Optional[Path] = None):
    """初始化记忆数据库"""
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建记忆表
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
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_access_count ON memories(access_count)")
    
    # 创建反思记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trigger_type TEXT NOT NULL,
            trigger_data JSON,
            analysis_result JSON,
            lessons_learned JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ 数据库初始化完成：{db_path}")
    return db_path

# ==================== 豆包 Embedding ====================

def get_embedding(text: str) -> np.ndarray:
    """调用豆包 API 获取文本向量嵌入"""
    headers = {
        "Authorization": f"Bearer {DOUBAO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": DOUBAO_MODEL,
        "encoding_format": "float",
        "input": [text]
    }
    
    try:
        response = requests.post(DOUBAO_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        embedding = result['data'][0]['embedding']
        
        return np.array(embedding, dtype=np.float32)
    
    except Exception as e:
        print(f"❌ 获取 embedding 失败：{e}")
        # 返回零向量作为降级
        return np.zeros(EMBEDDING_DIM, dtype=np.float32)

def compute_hash(text: str) -> str:
    """计算记忆文本的哈希值（用于去重）"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:32]

# ==================== 余弦相似度计算 ====================

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """计算两个向量的余弦相似度"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))

# ==================== 记忆操作 ====================

def add_memory(
    memory_text: str,
    memory_type: str = 'episodic',
    metadata: Optional[Dict] = None,
    db_path: Optional[Path] = None
) -> int:
    """
    添加记忆到数据库
    
    Args:
        memory_text: 记忆文本内容
        memory_type: 记忆类型 (episodic/semantic/error/learning)
        metadata: 额外元数据
        db_path: 数据库路径
    
    Returns:
        记忆 ID，如果已存在返回 -1
    """
    if db_path is None:
        db_path = DB_PATH
    
    # 计算哈希（去重）
    memory_hash = compute_hash(memory_text)
    
    # 生成 embedding
    print(f"🔍 生成 embedding...")
    embedding = get_embedding(memory_text)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查是否已存在
        cursor.execute("SELECT id FROM memories WHERE memory_hash = ?", (memory_hash,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️  记忆已存在 (ID: {existing[0]})")
            return -1
        
        # 插入新记忆
        cursor.execute("""
            INSERT INTO memories (memory_hash, memory_text, memory_type, embedding, embedding_dim, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            memory_hash,
            memory_text,
            memory_type,
            embedding.tobytes(),
            EMBEDDING_DIM,
            json.dumps(metadata or {}, ensure_ascii=False)
        ))
        
        conn.commit()
        memory_id = cursor.lastrowid
        
        print(f"✅ 记忆已添加 (ID: {memory_id}, 类型：{memory_type})")
        return memory_id
    
    except Exception as e:
        print(f"❌ 添加记忆失败：{e}")
        conn.rollback()
        return -1
    
    finally:
        conn.close()

def search_memory(
    query: str,
    top_k: int = 5,
    min_similarity: float = 0.5,
    memory_type: Optional[str] = None,
    db_path: Optional[Path] = None
) -> List[Dict]:
    """
    语义检索记忆
    
    Args:
        query: 搜索查询
        top_k: 返回最相关的 K 条记忆
        min_similarity: 最小相似度阈值
        memory_type: 过滤记忆类型
        db_path: 数据库路径
    
    Returns:
        相关记忆列表（按相似度排序）
    """
    if db_path is None:
        db_path = DB_PATH
    
    # 生成查询 embedding
    print(f"🔍 检索记忆：{query[:50]}...")
    query_embedding = get_embedding(query)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 获取所有记忆（可加类型过滤）
        if memory_type:
            cursor.execute("SELECT id, memory_text, memory_type, metadata, embedding FROM memories WHERE memory_type = ?")
            params = (memory_type,)
        else:
            cursor.execute("SELECT id, memory_text, memory_type, metadata, embedding FROM memories")
            params = ()
        
        rows = cursor.fetchall()
        
        # 计算相似度
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
        
        # 更新访问计数
        for result in results[:top_k]:
            cursor.execute("""
                UPDATE memories 
                SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (result['id'],))
        
        conn.commit()
        
        print(f"✅ 找到 {len(results)} 条相关记忆，返回 Top-{min(top_k, len(results))}")
        return results[:top_k]
    
    except Exception as e:
        print(f"❌ 检索失败：{e}")
        return []
    
    finally:
        conn.close()

def get_memory_stats(db_path: Optional[Path] = None) -> Dict:
    """获取记忆统计信息"""
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 总数
        cursor.execute("SELECT COUNT(*) FROM memories")
        total = cursor.fetchone()[0]
        
        # 按类型统计
        cursor.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
        by_type = dict(cursor.fetchall())
        
        # 最近访问
        cursor.execute("SELECT COUNT(*) FROM memories WHERE last_accessed IS NOT NULL")
        accessed = cursor.fetchone()[0]
        
        return {
            'total': total,
            'by_type': by_type,
            'accessed': accessed,
            'database': str(db_path)
        }
    
    finally:
        conn.close()

# ==================== 决策工作流集成 ====================

class MemoryVault:
    """记忆库 - 集成到决策工作流"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        init_database(self.db_path)
    
    def before_action(self, action_type: str, context: Dict) -> List[Dict]:
        """
        行动前检索相关记忆
        
        Args:
            action_type: 行动类型 (browser_act, git_push, file_operation 等)
            context: 行动上下文
        
        Returns:
            相关记忆列表
        """
        # 构建查询
        query = f"{action_type} {context.get('target', '')} {context.get('page_type', '')}"
        
        # 检索记忆
        memories = search_memory(query, top_k=3, min_similarity=0.6, db_path=self.db_path)
        
        # 显示警告
        if memories:
            print(f"\n⚠️  检索到 {len(memories)} 条相关记忆：")
            for i, mem in enumerate(memories, 1):
                print(f"\n{i}. [{mem['memory_type']}] 相似度：{mem['similarity']:.2f}")
                print(f"   {mem['memory_text'][:150]}...")
        
        return memories
    
    def after_action(self, outcome: str, action_type: str, details: Dict):
        """
        行动后记录结果
        
        Args:
            outcome: 结果 (success/failed/partial)
            action_type: 行动类型
            details: 详细信息
        """
        if outcome == 'failed':
            # 记录失败教训
            memory_text = f"{action_type} 失败：{details.get('error', '未知错误')}"
            add_memory(
                memory_text=memory_text,
                memory_type='error',
                metadata={
                    'action_type': action_type,
                    'outcome': outcome,
                    'details': details,
                    'timestamp': datetime.now().isoformat()
                },
                db_path=self.db_path
            )
        elif outcome == 'success':
            # 记录成功经验
            memory_text = f"{action_type} 成功：{details.get('method', '标准流程')}"
            add_memory(
                memory_text=memory_text,
                memory_type='learning',
                metadata={
                    'action_type': action_type,
                    'outcome': outcome,
                    'details': details,
                    'timestamp': datetime.now().isoformat()
                },
                db_path=self.db_path
            )
    
    def reflect(self, trigger_type: str, trigger_data: Dict, analysis: Dict):
        """
        记录反思结果
        
        Args:
            trigger_type: 触发类型 (periodic/error/user_feedback)
            trigger_data: 触发数据
            analysis: 分析结果
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO reflections (trigger_type, trigger_data, analysis_result, lessons_learned)
                VALUES (?, ?, ?, ?)
            """, (
                trigger_type,
                json.dumps(trigger_data, ensure_ascii=False),
                json.dumps(analysis.get('result', {}), ensure_ascii=False),
                json.dumps(analysis.get('lessons', []), ensure_ascii=False)
            ))
            
            conn.commit()
            print(f"✅ 反思已记录 (类型：{trigger_type})")
        
        finally:
            conn.close()

# ==================== 命令行工具 ====================

if __name__ == '__main__':
    import sys
    
    # 初始化数据库
    init_database()
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python memory_vault.py add <记忆文本> [类型]")
        print("  python memory_vault.py search <搜索查询> [top_k]")
        print("  python memory_vault.py stats")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'add':
        if len(sys.argv) < 3:
            print("❌ 请提供记忆文本")
            sys.exit(1)
        memory_text = sys.argv[2]
        memory_type = sys.argv[3] if len(sys.argv) > 3 else 'episodic'
        add_memory(memory_text, memory_type)
    
    elif command == 'search':
        if len(sys.argv) < 3:
            print("❌ 请提供搜索查询")
            sys.exit(1)
        query = ' '.join(sys.argv[2:-1]) if len(sys.argv) > 3 else sys.argv[2]
        top_k = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 5
        results = search_memory(query, top_k)
        
        print(f"\n📊 检索结果 ({len(results)} 条):")
        for i, mem in enumerate(results, 1):
            print(f"\n{i}. 相似度：{mem['similarity']:.2f} | 类型：{mem['memory_type']}")
            print(f"   {mem['memory_text']}")
    
    elif command == 'stats':
        stats = get_memory_stats()
        print(f"\n📊 记忆库统计:")
        print(f"   数据库：{stats['database']}")
        print(f"   总数：{stats['total']}")
        print(f"   已访问：{stats['accessed']}")
        print(f"   按类型:")
        for mem_type, count in stats['by_type'].items():
            print(f"     - {mem_type}: {count}")
    
    else:
        print(f"❌ 未知命令：{command}")
        sys.exit(1)
