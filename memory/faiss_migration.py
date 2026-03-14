#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAISS Migration Script - 数据迁移脚本

从现有记忆文件迁移到 FAISS + SQLite 双轨架构
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from memory_vault_faiss import MemoryVaultFAISS
    HAS_FAISS = True
    print("✅ FAISS 模式")
except:
    from memory_vault_v2 import add_memory, search_memory_optimized
    HAS_FAISS = False
    print("⚠️  降级模式（使用 v2.0）")

# 需要迁移的文件
FILES_TO_MIGRATE = [
    ("memory/episodic/2026-03-11.jsonl", "episodic"),
    ("memory/episodic/2026-03-12.jsonl", "episodic"),
    ("memory/episodic/2026-03-13.jsonl", "episodic"),
    ("memory/episodic/2026-03-14.jsonl", "episodic"),
    ("memory/semantic/lessons.json", "semantic"),
    ("memory/semantic/strategies.json", "semantic"),
    ("memory/semantic/mistakes.json", "semantic"),
    (".learnings/LEARNINGS.md", "learning"),
    (".learnings/ERRORS.md", "error"),
    ("MEMORY.md", "semantic"),
    ("AGENTS.md", "semantic"),
    ("TOOLS.md", "semantic"),
]

def migrate_all():
    """迁移所有记忆文件"""
    print("="*60)
    print("FAISS 数据迁移")
    print("="*60)
    
    workspace = Path(__file__).parent.parent
    total_migrated = 0
    
    if HAS_FAISS:
        vault = MemoryVaultFAISS()
    
    for file_rel_path, memory_type in FILES_TO_MIGRATE:
        file_path = workspace / file_rel_path
        
        if not file_path.exists():
            print(f"\n⚠️  文件不存在：{file_rel_path}")
            continue
        
        print(f"\n📄 迁移：{file_rel_path} ({memory_type})")
        
        if HAS_FAISS:
            # FAISS 模式
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            vault.add_memory(content, memory_type, {'source_file': file_rel_path})
            total_migrated += 1
        else:
            # 降级模式
            print("  ⚠️  降级模式：跳过 FAISS 迁移")
    
    print("\n" + "="*60)
    print(f"迁移完成！共 {total_migrated} 个文件")
    print("="*60)
    
    if HAS_FAISS:
        stats = vault.get_stats()
        print(f"\n📊 数据库统计:")
        print(f"   总数：{stats['total']} 条")
        print(f"   FAISS 向量：{stats['faiss_vectors']}")

if __name__ == '__main__':
    migrate_all()
