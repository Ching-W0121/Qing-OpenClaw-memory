"""
routes/matches.py - 匹配路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/matches", tags=["匹配"])

class UserProfile(BaseModel):
    """用户画像"""
    industry: str
    skills: List[str]
    tools: List[str]
    experience_years: int
    education: str
    expected_city: str
    expected_salary_min: int
    expected_salary_max: int

class Job(BaseModel):
    """职位"""
    id: str
    title: str
    company: str
    industry: str
    skills: List[str]
    tools: List[str]
    experience: str
    education: str
    city: str
    salary_min: int
    salary_max: int

class MatchRequest(BaseModel):
    """匹配请求"""
    user: UserProfile
    jobs: List[Job]

@router.post("/calculate")
async def calculate_match(request: MatchRequest):
    """计算匹配度"""
    from tools.matcher import MatchingEngine
    from tools.recommender import Recommender
    
    engine = MatchingEngine()
    recommender = Recommender()
    
    # 转换用户画像
    user = {
        "industry": request.user.industry,
        "skills": request.user.skills,
        "tools": request.user.tools,
        "experience_years": request.user.experience_years,
        "education": request.user.education,
        "expected_city": request.user.expected_city,
        "expected_salary_min": request.user.expected_salary_min,
        "expected_salary_max": request.user.expected_salary_max,
    }
    
    # 计算每个职位的匹配度
    matches = []
    for job in request.jobs:
        job_dict = {
            "industry": job.industry,
            "skills": job.skills,
            "tools": job.tools,
            "experience": job.experience,
            "education": job.education,
            "city": job.city,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
        }
        
        result = engine.calculate_match(user, job_dict)
        matches.append({
            "job_id": job.id,
            "job": job_dict,
            "match": result,
        })
    
    # 排序推荐
    ranked = recommender.rank(matches, top_n=len(matches))
    
    # 构建响应
    results = []
    for item in ranked:
        results.append({
            "job_id": item["job_id"],
            "job_title": item["job"].get("title", "N/A"),
            "company": item["job"].get("company", "N/A"),
            "match_rate": item["match"]["total"] * 100,
            "level": engine.get_match_level(item["match"]["total"]),
            "details": item["match"],
        })
    
    return {
        "status": "success",
        "count": len(results),
        "matches": results,
    }

@router.get("/recommend/{user_id}")
async def get_recommendations(user_id: str, top_n: int = 10):
    """获取推荐职位"""
    # 模拟数据
    return {
        "status": "success",
        "user_id": user_id,
        "top_n": top_n,
        "recommendations": [
            {
                "job_id": "job_001",
                "title": "高级品牌策划",
                "company": "某某广告公司",
                "match_rate": 85.0,
                "level": "很好匹配",
            },
            {
                "job_id": "job_002",
                "title": "品牌策划经理",
                "company": "某某互联网公司",
                "match_rate": 78.0,
                "level": "很好匹配",
            },
        ],
    }
