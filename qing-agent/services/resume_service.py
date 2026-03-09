"""
简历服务
"""

from tools.resume_parser import ResumeParser
from database.db import get_db
from database import models

class ResumeService:
    """简历服务"""
    
    def __init__(self):
        self.parser = ResumeParser()
    
    async def parse_and_save(self, file_path, user_id=None):
        """
        解析简历并保存
        
        Args:
            file_path: 简历文件路径
            user_id: 用户 ID（可选，更新现有用户）
        
        Returns:
            User: 用户对象
        """
        # 解析简历
        if file_path.endswith(".docx"):
            profile = self.parser.parse_docx(file_path)
        elif file_path.endswith(".pdf"):
            profile = self.parser.parse_pdf(file_path)
        else:
            raise ValueError("不支持的文件格式")
        
        # 保存到数据库
        db = next(get_db())
        
        if user_id:
            # 更新现有用户
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if not user:
                raise ValueError(f"用户不存在：{user_id}")
            
            for key, value in profile.items():
                if hasattr(user, key):
                    setattr(user, key, value)
        else:
            # 创建新用户
            user = models.User(**profile, resume_file=file_path)
            db.add(user)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    async def get_profile(self, user_id):
        """
        获取用户画像
        
        Args:
            user_id: 用户 ID
        
        Returns:
            dict: 用户画像
        """
        db = next(get_db())
        user = db.query(models.User).filter(models.User.id == user_id).first()
        
        if not user:
            raise ValueError(f"用户不存在：{user_id}")
        
        return {
            "id": user.id,
            "name": user.name,
            "education": user.education,
            "major": user.major,
            "experience_years": user.experience_years,
            "skills": user.skills or [],
            "tools": user.tools or [],
            "industry": user.industry,
            "target_jobs": user.target_jobs or [],
            "expected_city": user.expected_city,
            "expected_salary_min": user.expected_salary_min,
            "expected_salary_max": user.expected_salary_max,
        }
    
    async def update_profile(self, user_id, updates):
        """
        更新用户画像
        
        Args:
            user_id: 用户 ID
            updates: 更新字段 dict
        
        Returns:
            dict: 更新后的用户画像
        """
        db = next(get_db())
        user = db.query(models.User).filter(models.User.id == user_id).first()
        
        if not user:
            raise ValueError(f"用户不存在：{user_id}")
        
        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        
        return await self.get_profile(user_id)
