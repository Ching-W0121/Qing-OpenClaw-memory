"""
routes/applications.py - 投递路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/api/applications", tags=["投递"])

class SubmitApplicationRequest(BaseModel):
    """投递请求"""
    job_id: str
    user_id: str
    resume_url: Optional[str] = None

# 内存存储（实际应使用数据库）
_applications_db = []

@router.post("/submit")
async def submit_application(request: SubmitApplicationRequest):
    """提交投递"""
    from platform.adapter_factory import AdapterFactory
    
    # 获取职位详情（模拟）
    job_url = f"https://example.com/job/{request.job_id}"
    
    # 使用适配器投递
    adapter = AdapterFactory.get_adapter("zhilian")
    result = await adapter.apply(job_url, request.resume_url)
    
    # 记录投递
    application = {
        "id": f"app_{len(_applications_db) + 1}",
        "job_id": request.job_id,
        "user_id": request.user_id,
        "job_url": job_url,
        "resume_url": request.resume_url,
        "status": result.get("status", "unknown"),
        "applied_at": datetime.now().isoformat(),
        "result": result,
    }
    _applications_db.append(application)
    
    return {
        "status": "success" if result.get("status") == "submitted" else "failed",
        "application_id": application["id"],
        "job_id": request.job_id,
        "user_id": request.user_id,
        "result": result,
    }

@router.get("/{user_id}")
async def get_applications(user_id: str):
    """获取投递记录"""
    user_apps = [app for app in _applications_db if app["user_id"] == user_id]
    
    return {
        "status": "success",
        "user_id": user_id,
        "count": len(user_apps),
        "applications": user_apps,
    }
