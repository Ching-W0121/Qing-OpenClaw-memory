"""
数据库模型定义 - v1.4 (ChatGPT 老师建议版)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Index
from datetime import datetime
from database.db import Base


class User(Base):
    """用户信息表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))  # 姓名
    education = Column(String(50))  # 学历
    major = Column(String(100))  # 专业
    experience_years = Column(Integer)  # 工作年限
    skills = Column(JSON)  # 技能列表
    tools = Column(JSON)  # 工具/软件
    industry = Column(String(100))  # 行业
    target_jobs = Column(JSON)  # 目标职位
    expected_city = Column(String(100))  # 期望城市
    expected_salary_min = Column(Integer)  # 期望薪资下限
    expected_salary_max = Column(Integer)  # 期望薪资上限
    resume_file = Column(String(255))  # 简历文件路径
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_users_name', 'name'),
        Index('idx_users_industry', 'industry'),
    )


class Job(Base):
    """
    职位信息表
    
    ChatGPT 老师建议:
    - 增加 source_platform_id 字段（平台职位 ID）
    - 添加唯一索引 (platform, source_platform_id)
    - 添加标题索引用于搜索
    """
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)  # 平台（BOSS/智联等）
    source_platform_id = Column(String(100), nullable=False)  # 平台职位 ID（去重关键）
    
    title = Column(String(200), nullable=False)  # 职位名称
    company = Column(String(200))  # 公司
    city = Column(String(100), index=True)  # 城市
    district = Column(String(100))  # 区域
    salary_min = Column(Integer, index=True)  # 薪资下限
    salary_max = Column(Integer)  # 薪资上限
    experience = Column(String(50))  # 经验要求
    education = Column(String(50))  # 学历要求
    industry = Column(String(100), index=True)  # 行业
    skills = Column(JSON)  # 技能要求
    tools = Column(JSON)  # 工具要求
    url = Column(String(500))  # 职位链接
    jd_text = Column(Text)  # JD 原文
    requirements = Column(JSON)  # 职位要求解析结果（v1.4 新增）
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # ChatGPT 老师建议的唯一索引
    __table_args__ = (
        Index('idx_jobs_unique', 'platform', 'source_platform_id', unique=True),
        Index('idx_jobs_title', 'title'),  # 搜索优化
        Index('idx_jobs_location', 'city', 'district'),  # 地点查询优化
        Index('idx_jobs_salary', 'salary_min', 'salary_max'),  # 薪资范围查询
    )


class Match(Base):
    """
    匹配记录表
    
    ChatGPT 老师建议:
    - 增加 match_vector 字段（JSON，缓存匹配详情）
    - 添加用户 + 分数索引用于推荐排序
    """
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), index=True)
    
    match_score = Column(Float, index=True)  # 总匹配度
    match_vector = Column(JSON)  # v1.4 新增：匹配向量缓存 {industry: 0.9, skill: 0.8, ...}
    match_details = Column(JSON)  # 匹配详情（文本解释）
    
    # 各维度匹配分数（保留用于快速查询）
    industry_score = Column(Float)  # 行业匹配
    skill_score = Column(Float)  # 技能匹配
    experience_score = Column(Float)  # 经验匹配
    salary_score = Column(Float)  # 薪资匹配
    location_score = Column(Float)  # 地点匹配
    education_score = Column(Float)  # 学历匹配
    tools_score = Column(Float)  # 工具匹配
    
    # 状态标记
    is_viewed = Column(Integer, default=0)  # 是否已查看 (0/1)
    is_applied = Column(Integer, default=0)  # 是否已投递 (0/1)
    rank = Column(Integer)  # 推荐排名
    
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    # ChatGPT 老师建议的索引
    __table_args__ = (
        Index('idx_matches_user_score', 'user_id', 'match_score'),  # 推荐排序优化
    )


class Application(Base):
    """
    投递记录表
    
    ChatGPT 老师建议:
    - 增加 platform_status 字段（平台状态，与系统状态区分）
    - 添加用户 + 职位联合索引
    """
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)  # 关联的匹配记录
    
    status = Column(String(50), default="pending", index=True)  # 系统状态：pending/submitted/interview/offer/rejected
    platform_status = Column(String(50))  # v1.4 新增：平台状态（hr_viewed 等）
    
    applied_at = Column(DateTime, default=datetime.now, index=True)  # 投递时间
    hr_reply = Column(Text)  # HR 回复
    notes = Column(Text)  # 备注
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    
    # ChatGPT 老师建议的索引
    __table_args__ = (
        Index('idx_applications_user_job', 'user_id', 'job_id'),  # 查询优化
        Index('idx_applications_status', 'status'),  # 状态查询
    )
