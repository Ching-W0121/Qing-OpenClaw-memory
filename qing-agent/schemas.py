"""
Pydantic 模型 - v1.4
用于 API 请求和响应验证
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============== User ==============

class UserBase(BaseModel):
    name: Optional[str] = None
    education: Optional[str] = None
    major: Optional[str] = None
    experience_years: Optional[int] = None
    skills: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    industry: Optional[str] = None
    expected_city: Optional[str] = None
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None


class UserCreate(UserBase):
    name: str


class UserUpdate(UserBase):
    pass


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


# ============== Job ==============

class JobBase(BaseModel):
    title: str
    company: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    industry: Optional[str] = None
    skills: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    url: Optional[str] = None
    jd_text: Optional[str] = None


class JobCreate(JobBase):
    platform: str
    source_platform_id: str


class JobUpdate(JobBase):
    pass


class JobResponse(JobBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    platform: str
    source_platform_id: str
    created_at: datetime
    updated_at: datetime


# ============== Match ==============

class MatchBase(BaseModel):
    user_id: int
    job_id: int
    match_score: float
    match_vector: Optional[Dict[str, float]] = None
    match_details: Optional[Dict[str, Any]] = None


class MatchCreate(MatchBase):
    pass


class MatchResponse(MatchBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    industry_score: Optional[float] = None
    skill_score: Optional[float] = None
    experience_score: Optional[float] = None
    salary_score: Optional[float] = None
    location_score: Optional[float] = None
    education_score: Optional[float] = None
    tools_score: Optional[float] = None
    is_viewed: bool = False
    is_applied: bool = False
    rank: Optional[int] = None
    created_at: datetime


# ============== Application ==============

class ApplicationBase(BaseModel):
    user_id: int
    job_id: int
    status: str = "pending"
    notes: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    platform_status: Optional[str] = None
    notes: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    match_id: Optional[int] = None
    platform_status: Optional[str] = None
    applied_at: datetime
    hr_reply: Optional[str] = None
    created_at: datetime
    updated_at: datetime
