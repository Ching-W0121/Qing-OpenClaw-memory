"""
投递服务 - v1.4 (使用 Repository Layer)
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from repositories.application_repo import ApplicationRepository
from database.models import Application


class ApplicationService:
    """投递服务（v1.4 版 - 使用 Repository）"""
    
    def __init__(self, db: Session):
        self.db = db
        self.app_repo = ApplicationRepository(db)
    
    def get_application(self, application_id: int) -> Optional[Application]:
        """获取投递记录"""
        return self.app_repo.get(application_id)
    
    def get_user_applications(self, user_id: int) -> List[Application]:
        """获取用户的投递记录"""
        return self.app_repo.get_user_applications(user_id)
    
    def create_application(self, user_id: int, job_id: int, 
                          status: str = "pending") -> Application:
        """创建投递记录"""
        return self.app_repo.create_application(user_id, job_id, status)
    
    def update_status(self, application_id: int, status: str, 
                     platform_status: Optional[str] = None) -> Optional[Application]:
        """更新投递状态"""
        return self.app_repo.update_status(application_id, status, platform_status)
    
    def add_note(self, application_id: int, note: str) -> Optional[Application]:
        """添加备注"""
        return self.app_repo.add_note(application_id, note)
    
    def get_by_status(self, user_id: int, status: str) -> List[Application]:
        """根据状态获取投递"""
        return self.app_repo.get_by_status(user_id, status)
