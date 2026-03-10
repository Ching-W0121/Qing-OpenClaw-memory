"""
匹配服务 - v1.4 (使用 Repository Layer)
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from repositories.match_repo import MatchRepository
from database.models import Match


class MatchService:
    """匹配服务（v1.4 版 - 使用 Repository）"""
    
    def __init__(self, db: Session):
        self.db = db
        self.match_repo = MatchRepository(db)
    
    def get_match(self, match_id: int) -> Optional[Match]:
        """获取匹配记录"""
        return self.match_repo.get(match_id)
    
    def get_user_matches(self, user_id: int, limit: int = 50) -> List[Match]:
        """获取用户的匹配记录"""
        return self.match_repo.get_user_matches(user_id, limit)
    
    def get_top_recommendations(self, user_id: int, top_n: int = 10) -> List[Match]:
        """获取 Top N 推荐"""
        return self.match_repo.get_top_recommendations(user_id, top_n)
    
    def create_match(self, user_id: int, job_id: int, 
                    match_score: float, match_vector: Dict[str, float],
                    match_details: Dict[str, Any]) -> Match:
        """创建匹配记录"""
        return self.match_repo.create_match(
            user_id=user_id,
            job_id=job_id,
            match_score=match_score,
            match_vector=match_vector,
            match_details=match_details
        )
    
    def mark_as_viewed(self, match_id: int) -> Optional[Match]:
        """标记为已查看"""
        return self.match_repo.mark_as_viewed(match_id)
    
    def mark_as_applied(self, match_id: int) -> Optional[Match]:
        """标记为已投递"""
        return self.match_repo.mark_as_applied(match_id)
