"""
Job Repository - 职位数据访问层
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from repositories.base import BaseRepository
from database.models import Job


class JobRepository(BaseRepository[Job]):
    """职位 Repository"""
    
    def __init__(self, db: Session):
        super().__init__(Job, db)
    
    def get_by_platform_id(self, platform: str, source_platform_id: str) -> Optional[Job]:
        """根据平台 ID 获取职位"""
        return self.first(platform=platform, source_platform_id=source_platform_id)
    
    def search_by_title(self, keyword: str, limit: int = 50) -> List[Job]:
        """根据职位标题搜索"""
        return self.db.query(Job).filter(
            Job.title.contains(keyword)
        ).limit(limit).all()
    
    def search_by_company(self, company: str, limit: int = 50) -> List[Job]:
        """根据公司名称搜索"""
        return self.db.query(Job).filter(
            Job.company.contains(company)
        ).limit(limit).all()
    
    def filter_by_location(self, city: str, district: Optional[str] = None) -> List[Job]:
        """根据地点过滤职位"""
        query = self.db.query(Job).filter(Job.city == city)
        if district:
            query = query.filter(Job.district == district)
        return query.all()
    
    def filter_by_salary(self, min_salary: int, max_salary: Optional[int] = None) -> List[Job]:
        """根据薪资范围过滤"""
        query = self.db.query(Job).filter(Job.salary_min >= min_salary)
        if max_salary:
            query = query.filter(Job.salary_max <= max_salary)
        return query.all()
    
    def filter_by_platform(self, platform: str) -> List[Job]:
        """根据平台过滤"""
        return self.filter(platform=platform)
    
    def get_recent(self, days: int = 7, limit: int = 100) -> List[Job]:
        """获取最近 N 天的职位"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        return self.db.query(Job).filter(
            Job.created_at >= cutoff_date
        ).limit(limit).all()
    
    def create_or_update(self, data: Dict[str, Any]) -> Job:
        """创建或更新职位（根据平台 ID 去重）"""
        platform = data.get('platform')
        source_platform_id = data.get('source_platform_id')
        
        if platform and source_platform_id:
            existing = self.get_by_platform_id(platform, source_platform_id)
            if existing:
                # 更新现有职位
                for key, value in data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                self.db.commit()
                self.db.refresh(existing)
                return existing
        
        # 创建新职位
        return self.create(data)
