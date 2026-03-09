"""
routes/users.py - 用户路由 (JWT 认证版)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict

from auth.jwt_auth import get_current_user, require_auth

router = APIRouter(prefix="/api/users", tags=["用户"])

class UserProfile(BaseModel):
    """用户画像"""
    name: Optional[str] = None
    industry: str
    skills: List[str]
    tools: List[str]
    experience_years: int
    education: str
    expected_city: str
    expected_salary_min: int
    expected_salary_max: int

# 内存存储（实际应使用数据库）
_users_db = {}

@router.post("/")
async def create_user(
    profile: UserProfile,
    current_user: Dict = Depends(require_auth("write:users")),
):
    """
    创建用户画像
    需要权限：write:users
    """
    import uuid
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    _users_db[user_id] = profile.dict()
    
    return {
        "status": "success",
        "message": "用户画像已创建",
        "user_id": user_id,
        "profile": profile,
        "auth_user": current_user.get("email"),
    }

@router.get("/{user_id}")
async def get_user(
    user_id: str,
    current_user: Dict = Depends(require_auth("read:users")),
):
    """
    获取用户画像
    需要权限：read:users
    """
    if user_id not in _users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "user_id": user_id,
        "profile": _users_db[user_id],
        "auth_user": current_user.get("email"),
    }

@router.put("/{user_id}")
async def update_user(
    user_id: str,
    profile: UserProfile,
    current_user: Dict = Depends(require_auth("write:users")),
):
    """
    更新用户画像
    需要权限：write:users
    """
    if user_id not in _users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    _users_db[user_id] = profile.dict()
    
    return {
        "status": "success",
        "message": "用户画像已更新",
        "user_id": user_id,
        "auth_user": current_user.get("email"),
    }
