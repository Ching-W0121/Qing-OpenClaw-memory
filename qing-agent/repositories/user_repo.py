"""
User Repository - 用户数据访问层
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from repositories.base import BaseRepository
from database.models import User


class UserRepository(BaseRepository[User]):
    """用户 Repository"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.first(email=email)
    
    def get_by_name(self, name: str) -> Optional[User]:
        """根据姓名获取用户"""
        return self.first(name=name)
    
    def search(self, keyword: str, limit: int = 10) -> List[User]:
        """搜索用户（姓名或专业）"""
        return self.db.query(User).filter(
            (User.name.contains(keyword)) | 
            (User.major.contains(keyword))
        ).limit(limit).all()
    
    def update_expectations(self, user_id: int, expectations: Dict[str, Any]) -> Optional[User]:
        """更新用户期望"""
        return self.update(user_id, {"expectations": expectations})
    
    def update_skills(self, user_id: int, skills: List[str]) -> Optional[User]:
        """更新用户技能"""
        return self.update(user_id, {"skills": skills})
