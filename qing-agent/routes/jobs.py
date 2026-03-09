"""
routes/jobs.py - 职位路由 (JWT 认证版)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict

from auth.jwt_auth import get_current_user, require_auth, jwt_auth

router = APIRouter(prefix="/api/jobs", tags=["职位"])

class SearchRequest(BaseModel):
    """搜索请求"""
    keyword: str
    city: str = "深圳"
    page: int = 1

@router.post("/search")
async def search_jobs(
    request: SearchRequest,
    current_user: Dict = Depends(require_auth("read:jobs")),
):
    """
    搜索职位
    需要权限：read:jobs
    """
    from platform.adapter_factory import AdapterFactory
    
    # 使用智联招聘适配器（BOSS 直聘账号封禁中）
    adapter = AdapterFactory.get_adapter("zhilian")
    
    jobs = await adapter.search_jobs(
        keyword=request.keyword,
        city=request.city,
        page=request.page,
    )
    
    return {
        "status": "success",
        "count": len(jobs),
        "keyword": request.keyword,
        "city": request.city,
        "jobs": jobs,
        "user": current_user.get("email"),
    }

@router.get("/{job_id}")
async def get_job_detail(
    job_id: str,
    current_user: Dict = Depends(require_auth("read:jobs")),
):
    """
    获取职位详情
    需要权限：read:jobs
    """
    # 模拟数据
    return {
        "job_id": job_id,
        "detail": {
            "title": "品牌策划经理",
            "company": "某某科技公司",
            "industry": "互联网",
            "skills": ["品牌策划", "营销策划", "数据分析"],
            "tools": ["Office", "Photoshop"],
            "experience": "3-5 年",
            "education": "本科",
            "city": "深圳",
            "salary_min": 15000,
            "salary_max": 25000,
            "description": "负责品牌策划相关工作...",
            "url": f"https://example.com/job/{job_id}",
        },
        "user": current_user.get("email"),
    }
