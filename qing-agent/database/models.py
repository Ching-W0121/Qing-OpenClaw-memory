"""
数据库模型定义
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
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

class Job(Base):
    """职位信息表"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))  # 职位名称
    company = Column(String(200))  # 公司
    city = Column(String(100))  # 城市
    district = Column(String(100))  # 区域
    salary_min = Column(Integer)  # 薪资下限
    salary_max = Column(Integer)  # 薪资上限
    experience = Column(String(50))  # 经验要求
    education = Column(String(50))  # 学历要求
    industry = Column(String(100))  # 行业
    skills = Column(JSON)  # 技能要求
    tools = Column(JSON)  # 工具要求
    platform = Column(String(50))  # 平台（BOSS/智联）
    url = Column(String(500))  # 职位链接
    jd_text = Column(Text)  # JD 原文
    created_at = Column(DateTime, default=datetime.now)

class Match(Base):
    """匹配记录表"""
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    match_score = Column(Float)  # 总匹配度
    industry_score = Column(Float)  # 行业匹配
    skill_score = Column(Float)  # 技能匹配
    experience_score = Column(Float)  # 经验匹配
    salary_score = Column(Float)  # 薪资匹配
    location_score = Column(Float)  # 地点匹配
    education_score = Column(Float)  # 学历匹配
    tools_score = Column(Float)  # 工具匹配
    created_at = Column(DateTime, default=datetime.now)

class Application(Base):
    """投递记录表"""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    status = Column(String(50))  # pending/submitted/interview/offer/rejected
    applied_at = Column(DateTime)  # 投递时间
    hr_reply = Column(Text)  # HR 回复
    notes = Column(Text)  # 备注
    created_at = Column(DateTime, default=datetime.now)
