"""
职位存储服务
将职位数据保存到 SQLite 数据库
"""

from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib

Base = declarative_base()

class Job(Base):
    """职位表"""
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_hash = Column(String(32), unique=True, index=True)  # 唯一标识
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    salary = Column(String(100))
    salary_min = Column(Float)
    salary_max = Column(Float)
    city = Column(String(50))
    district = Column(String(50))
    experience = Column(String(50))
    education = Column(String(50))
    skills = Column(Text)  # JSON 字符串
    industry = Column(String(100))
    description = Column(Text)
    url = Column(String(500))
    platform = Column(String(50))
    
    # 评分
    total_score = Column(Float)
    match_score = Column(Float)
    salary_score = Column(Float)
    city_score = Column(Float)
    keyword_score = Column(Float)
    industry_score = Column(Float)
    
    # 元数据
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'salary': self.salary,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'city': self.city,
            'district': self.district,
            'experience': self.experience,
            'education': self.education,
            'skills': self.skills,
            'industry': self.industry,
            'description': self.description,
            'url': self.url,
            'platform': self.platform,
            'total_score': self.total_score,
            'match_score': self.match_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class JobRepository:
    """职位仓库"""
    
    def __init__(self, db_path: str = 'sqlite:///qing_jobs.db'):
        self.engine = create_engine(db_path, echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def _generate_hash(self, job: Dict[str, Any]) -> str:
        """生成职位唯一 hash"""
        title = (job.get('title', '') or '').strip()
        company = (job.get('company', '') or '').strip()
        city = (job.get('city', '') or '').strip()
        unique_str = f"{title}|{company}|{city}"
        return hashlib.md5(unique_str.encode('utf-8')).hexdigest()
    
    def save_job(self, job: Dict[str, Any]) -> Optional[Job]:
        """
        保存单个职位（自动去重）
        
        Args:
            job: 职位字典
        
        Returns:
            保存的职位对象，如果已存在则返回 None
        """
        job_hash = self._generate_hash(job)
        
        # 检查是否已存在
        existing = self.session.query(Job).filter_by(job_hash=job_hash).first()
        if existing:
            # 更新现有职位
            for key, value in job.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.now()
            self.session.commit()
            return existing
        
        # 创建新职位
        new_job = Job(
            job_hash=job_hash,
            title=job.get('title', ''),
            company=job.get('company', ''),
            salary=job.get('salary', ''),
            salary_min=job.get('salary_min', 0),
            salary_max=job.get('salary_max', 0),
            city=job.get('city', ''),
            district=job.get('district', ''),
            experience=job.get('experience', ''),
            education=job.get('education', ''),
            skills=str(job.get('skills', [])),
            industry=job.get('industry', ''),
            description=job.get('description', ''),
            url=job.get('url', ''),
            platform=job.get('platform', 'zhilian'),
            total_score=job.get('total_score', 0),
            match_score=job.get('match_score', 0),
            salary_score=job.get('salary_score', 0),
            city_score=job.get('city_score', 0),
            keyword_score=job.get('keyword_score', 0),
            industry_score=job.get('industry_score', 0),
        )
        
        self.session.add(new_job)
        self.session.commit()
        return new_job
    
    def save_jobs(self, jobs: List[Dict[str, Any]]) -> int:
        """
        批量保存职位
        
        Args:
            jobs: 职位列表
        
        Returns:
            保存的职位数量（去重后）
        """
        saved_count = 0
        for job in jobs:
            result = self.save_job(job)
            if result:
                saved_count += 1
        return saved_count
    
    def get_recent_jobs(self, days=7, limit=100) -> List[Job]:
        """获取最近 N 天的职位"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        jobs = self.session.query(Job).filter(
            Job.created_at >= cutoff_date,
            Job.is_active == True
        ).order_by(Job.total_score.desc()).limit(limit).all()
        
        return jobs
    
    def get_top_jobs(self, limit=10) -> List[Job]:
        """获取评分最高的职位"""
        jobs = self.session.query(Job).filter(
            Job.is_active == True
        ).order_by(Job.total_score.desc()).limit(limit).all()
        
        return jobs
    
    def search_jobs(self, keyword: str, city: str = None, limit=50) -> List[Job]:
        """搜索职位"""
        query = self.session.query(Job).filter(
            Job.title.like(f'%{keyword}%'),
            Job.is_active == True
        )
        
        if city:
            query = query.filter(Job.city == city)
        
        jobs = query.order_by(Job.total_score.desc()).limit(limit).all()
        return jobs
    
    def count_jobs(self) -> int:
        """统计职位总数"""
        return self.session.query(Job).filter(Job.is_active == True).count()
    
    def close(self):
        """关闭会话"""
        self.session.close()
