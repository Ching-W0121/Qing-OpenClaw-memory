"""
匹配服务
"""

from tools.matcher import MatchingEngine
from database.db import get_db
from database import models
from datetime import datetime

class MatchService:
    """匹配服务"""
    
    def __init__(self):
        self.engine = MatchingEngine()
    
    async def calculate(self, user_profile, job_profile):
        """
        计算匹配度
        
        Args:
            user_profile: 用户画像
            job_profile: 职位画像
        
        Returns:
            dict: 匹配结果
        """
        result = self.engine.calculate_match(user_profile, job_profile)
        return result
    
    async def save_matches(self, user_id, matches):
        """
        保存匹配结果到数据库
        
        Args:
            user_id: 用户 ID
            matches: 匹配结果列表
        """
        db = next(get_db())
        
        for item in matches:
            job = item["job"]
            match = item["match"]
            
            # 查找或创建职位记录
            job_record = db.query(models.Job).filter(models.Job.url == job.get('url', '')).first()
            if not job_record:
                job_record = models.Job(
                    title=job.get('title', ''),
                    company=job.get('company', ''),
                    city=job.get('city', ''),
                    platform=job.get('platform', ''),
                    url=job.get('url', ''),
                )
                db.add(job_record)
                db.commit()
                db.refresh(job_record)
            
            # 创建匹配记录
            match_record = models.Match(
                user_id=user_id,
                job_id=job_record.id,
                match_score=match["total"],
                industry_score=match["details"]["industry"],
                skill_score=match["details"]["skill"],
                experience_score=match["details"]["experience"],
                salary_score=match["details"]["salary"],
                location_score=match["details"]["location"],
                education_score=match["details"]["education"],
                tools_score=match["details"]["tools"]
            )
            
            db.add(match_record)
        
        db.commit()
    
    async def get_user_matches(self, user_id, limit=20):
        """
        获取用户的匹配记录
        
        Args:
            user_id: 用户 ID
            limit: 返回数量限制
        
        Returns:
            list: 匹配记录
        """
        db = next(get_db())
        
        matches = db.query(models.Match).filter(
            models.Match.user_id == user_id
        ).order_by(
            models.Match.match_score.desc()
        ).limit(limit).all()
        
        return matches
