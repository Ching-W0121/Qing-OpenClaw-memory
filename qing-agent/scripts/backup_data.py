"""
数据备份脚本 - 备份内存数据到云端/GitHub
用于 v1.4 升级前的数据保护
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# 设置 UTF-8 编码
sys.stdout.reconfigure(encoding='utf-8')

def backup_memory_data():
    """备份内存数据到云端"""
    
    # 项目根目录 (qing-agent)
    project_root = Path(__file__).parent.parent
    
    # 数据目录
    data_dir = project_root / 'data'
    
    # 备份目录
    backup_dir = project_root / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    # 时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f'backup_{timestamp}'
    backup_path.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("📦 数据备份 - v1.4 升级前")
    print("=" * 60)
    
    # 备份的文件
    files_to_backup = [
        'data/industry_tree.json',
        'data/qing_agent.db',  # 如果存在
        '.env',  # 环境变量
        'config/settings.py',  # 配置文件
    ]
    
    backed_up = []
    skipped = []
    
    for file_path in files_to_backup:
        src = project_root / file_path
        if src.exists():
            # 创建目标目录
            dest = backup_path / file_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            if src.is_file():
                shutil.copy2(src, dest)
            else:
                shutil.copytree(src, dest)
            
            backed_up.append(file_path)
            print(f"✅ {file_path}")
        else:
            skipped.append(file_path)
            print(f"⚠️  {file_path} (不存在，跳过)")
    
    # 创建备份清单
    manifest = {
        'backup_time': timestamp,
        'version': 'v1.3.0',
        'reason': 'Upgrade to v1.4.0',
        'files': backed_up,
        'skipped': skipped,
    }
    
    manifest_path = backup_path / 'MANIFEST.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 备份完成：{backup_path}")
    print(f"📝 备份清单：{manifest_path}")
    print(f"\n📊 统计:")
    print(f"   已备份：{len(backed_up)} 个文件")
    print(f"   跳过：{len(skipped)} 个文件")
    
    # Git 提交备份
    print(f"\n💾 提交到 Git...")
    os.system(f'git -C "{project_root}" add backups/')
    os.system(f'git -C "{project_root}" commit -m "💾 数据备份 - v1.4 升级前 ({timestamp})"')
    
    print(f"\n✅ 备份已提交到 Git")
    print(f"📍 可以随时通过 git checkout 恢复")
    
    return backup_path


if __name__ == '__main__':
    backup_memory_data()
