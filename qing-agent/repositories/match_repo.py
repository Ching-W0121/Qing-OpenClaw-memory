"""
Match Repository - 匹配记录数据访问层
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from repositories.base import BaseRepository
from database.models import Match


class MatchRepository(BaseRepository[Match]):
    """匹配记录 Repository"""
    
    def __init__(self, db: Session):
        super().__init__(Match, db)
    
    def get_user_matches(self, user_id: int, limit: int = 50) -> List[Match]:
        """获取用户的匹配记录"""
        return self.db.query(Match).filter(
            Match.user_id == user_id
        ).order_by(Match.match_score.desc()).limit(limit).all()
    
    def get_job_matches(self, job_id: int, limit: int = 50) -> List[Match]:
        """获取职位的匹配记录"""
        return self.db.query(Match).filter(
            Match.job_id == job_id
        ).order_by(Match.match_score.desc()).limit(limit).all()
    
    def get_best_match(self, user_id: int, job_id: int) -> Optional[Match]:
        """获取用户对某个职位的最佳匹配"""
        return self.db.query(Match).filter(
            (Match.user_id == user_id) & (Match.job_id == job_id)
        ).order_by(Match.match_score.desc()).first()
    
    def get_top_recommendations(self, user_id: int, top_n: int = 10) -> List[Match]:
        """获取 Top N 推荐"""
        return self.db.query(Match).filter(
            Match.user_id == user_id
        ).order_by(Match.match_score.desc()).limit(top_n).all()
    
    def get_unviewed_matches(self, user_id: int) -> List[Match]:
        """获取未查看的匹配"""
        return self.db.query(Match).filter(
            (Match.user_id == user_id) & (Match.is_viewed == False)
        ).order_by(Match.match_score.desc()).all()
    
    def get_unapplied_matches(self, user_id: int) -> List[Match]:
        """获取未投递的匹配"""
        return self.db.query(Match).filter(
            (Match.user_id == user_id) & (Match.is_applied == False)
        ).order_by(Match.match_score.desc()).all()
    
    def mark_as_viewed(self, match_id: int) -> Optional[Match]:
        """标记为已查看"""
        return self.update(match_id, {"is_viewed": True})
    
    def mark_as_applied(self, match_id: int) -> Optional[Match]:
        """标记为已投递"""
        return self.update(match_id, {"is_applied": True})
    
    def create_match(self, user_id: int, job_id: int, match_score: float, 
                     match_vector: Dict[str, float], match_details: Dict[str, Any]) -> Match:
        """创建匹配记录"""
        data = {
            "user_id": user_id,
            "job_id": job_id,
            "match_score": match_score,
            "match_vector": match_vector,
            "match_details": match_details,
            "industry_score": match_vector.get("industry", 0),
            "skill_score": match_vector.get("skill", 0),
            "experience_score": match_vector.get("experience", 0),
            "salary_score": match_vector.get("salary", 0),
            "location_score": match_vector.get("location", 0),
            "education_score": match_vector.get("education", 0),
            "tools_score": match_vector.get("tools", 0),
        }
        return self.create(data)
