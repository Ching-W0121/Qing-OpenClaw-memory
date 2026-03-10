"""
Application Repository - 投递记录数据访问层
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from repositories.base import BaseRepository
from database.models import Application


class ApplicationRepository(BaseRepository[Application]):
    """投递记录 Repository"""
    
    def __init__(self, db: Session):
        super().__init__(Application, db)
    
    def get_user_applications(self, user_id: int) -> List[Application]:
        """获取用户的投递记录"""
        return self.db.query(Application).filter(
            Application.user_id == user_id
        ).order_by(Application.applied_at.desc()).all()
    
    def get_job_applications(self, job_id: int) -> List[Application]:
        """获取职位的投递记录"""
        return self.db.query(Application).filter(
            Application.job_id == job_id
        ).order_by(Application.applied_at.desc()).all()
    
    def get_application(self, user_id: int, job_id: int) -> Optional[Application]:
        """获取用户对某个职位的投递"""
        return self.first(user_id=user_id, job_id=job_id)
    
    def get_by_status(self, user_id: int, status: str) -> List[Application]:
        """根据状态获取投递记录"""
        return self.filter(user_id=user_id, status=status)
    
    def get_pending_applications(self, user_id: int) -> List[Application]:
        """获取待处理的投递"""
        return self.get_by_status(user_id, "pending")
    
    def get_interview_applications(self, user_id: int) -> List[Application]:
        """获取面试中的投递"""
        return self.get_by_status(user_id, "interview")
    
    def get_offer_applications(self, user_id: int) -> List[Application]:
        """获取 offer 的投递"""
        return self.get_by_status(user_id, "offer")
    
    def update_status(self, application_id: int, status: str, 
                      platform_status: Optional[str] = None) -> Optional[Application]:
        """更新投递状态"""
        data = {"status": status}
        if platform_status:
            data["platform_status"] = platform_status
        return self.update(application_id, data)
    
    def create_application(self, user_id: int, job_id: int, 
                          status: str = "pending") -> Application:
        """创建投递记录"""
        data = {
            "user_id": user_id,
            "job_id": job_id,
            "status": status,
            "applied_at": datetime.now(),
        }
        return self.create(data)
    
    def add_note(self, application_id: int, note: str) -> Optional[Application]:
        """添加备注"""
        app = self.get(application_id)
        if not app:
            return None
        
        existing_notes = app.notes or ""
        new_note = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {note}\n"
        return self.update(application_id, {"notes": existing_notes + new_note})
