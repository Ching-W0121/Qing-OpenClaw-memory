"""
职位去重工具
使用 hash(title + company + city) 去重
"""

import hashlib
from typing import List, Dict, Any

class JobDeduplicator:
    """职位去重器"""
    
    def __init__(self):
        self.seen_hashes = set()
    
    def _generate_hash(self, job: Dict[str, Any]) -> str:
        """生成职位唯一标识"""
        # 提取关键字段
        title = (job.get('title', '') or '').strip()
        company = (job.get('company', '') or '').strip()
        city = (job.get('city', '') or '').strip()
        
        # 组合成唯一字符串
        unique_str = f"{title}|{company}|{city}"
        
        # 生成 MD5 hash
        return hashlib.md5(unique_str.encode('utf-8')).hexdigest()
    
    def deduplicate(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        去重职位列表
        
        Args:
            jobs: 职位列表
        
        Returns:
            去重后的职位列表
        """
        unique_jobs = []
        
        for job in jobs:
            job_hash = self._generate_hash(job)
            
            if job_hash not in self.seen_hashes:
                self.seen_hashes.add(job_hash)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def reset(self):
        """重置已见 hash 集合"""
        self.seen_hashes = set()

def deduplicate_jobs(jobs: List[Dict[str, Any]], preserve_order=True) -> List[Dict[str, Any]]:
    """
    便捷函数：去重职位列表
    
    Args:
        jobs: 职位列表
        preserve_order: 是否保留原始顺序
    
    Returns:
        去重后的职位列表
    """
    deduplicator = JobDeduplicator()
    return deduplicator.deduplicate(jobs)
