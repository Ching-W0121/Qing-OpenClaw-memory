"""
用户服务 - v1.4 (使用 Repository Layer)
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from repositories.user_repo import UserRepository
from database.models import User


class UserService:
    """用户服务（v1.4 版 - 使用 Repository）"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def get_user(self, user_id: int) -> Optional[User]:
        """获取用户"""
        return self.user_repo.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.user_repo.get_by_email(email)
    
    def create_user(self, data: Dict[str, Any]) -> User:
        """创建用户"""
        return self.user_repo.create(data)
    
    def update_user(self, user_id: int, data: Dict[str, Any]) -> Optional[User]:
        """更新用户"""
        return self.user_repo.update(user_id, data)
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        return self.user_repo.delete(user_id)
    
    def search_users(self, keyword: str, limit: int = 10) -> List[User]:
        """搜索用户"""
        return self.user_repo.search(keyword, limit)
    
    def update_expectations(self, user_id: int, expectations: Dict[str, Any]) -> Optional[User]:
        """更新用户期望"""
        return self.user_repo.update_expectations(user_id, expectations)
    
    def update_skills(self, user_id: int, skills: List[str]) -> Optional[User]:
        """更新用户技能"""
        return self.user_repo.update_skills(user_id, skills)
