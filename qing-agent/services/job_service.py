"""
职位服务 - v1.4 (使用 Repository Layer)
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from repositories.job_repo import JobRepository
from database.models import Job


class JobService:
    """职位服务（v1.4 版 - 使用 Repository）"""
    
    def __init__(self, db: Session):
        self.db = db
        self.job_repo = JobRepository(db)
    
    def get_job(self, job_id: int) -> Optional[Job]:
        """获取职位"""
        return self.job_repo.get(job_id)
    
    def get_job_by_platform_id(self, platform: str, source_platform_id: str) -> Optional[Job]:
        """根据平台 ID 获取职位"""
        return self.job_repo.get_by_platform_id(platform, source_platform_id)
    
    def create_job(self, data: Dict[str, Any]) -> Job:
        """创建职位"""
        return self.job_repo.create(data)
    
    def create_or_update_job(self, data: Dict[str, Any]) -> Job:
        """创建或更新职位（去重）"""
        return self.job_repo.create_or_update(data)
    
    def search_by_title(self, keyword: str, limit: int = 50) -> List[Job]:
        """根据标题搜索职位"""
        return self.job_repo.search_by_title(keyword, limit)
    
    def filter_by_location(self, city: str, district: Optional[str] = None) -> List[Job]:
        """根据地点过滤"""
        return self.job_repo.filter_by_location(city, district)
    
    def filter_by_salary(self, min_salary: int, max_salary: Optional[int] = None) -> List[Job]:
        """根据薪资过滤"""
        return self.job_repo.filter_by_salary(min_salary, max_salary)
    
    def get_recent_jobs(self, days: int = 7, limit: int = 100) -> List[Job]:
        """获取最近 N 天的职位"""
        return self.job_repo.get_recent(days, limit)
