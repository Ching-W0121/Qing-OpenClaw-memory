"""
匹配路由 - v1.4 (使用 Schema + Service + Repository)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database.db import get_db
from services.match_service import MatchService
from schemas import MatchCreate, MatchResponse

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.post("/calculate", response_model=MatchResponse)
def calculate_match(match_data: MatchCreate, db: Session = Depends(get_db)):
    """计算匹配度并创建记录"""
    service = MatchService(db)
    return service.create_match(
        user_id=match_data.user_id,
        job_id=match_data.job_id,
        match_score=match_data.match_score,
        match_vector=match_data.match_vector,
        match_details=match_data.match_details
    )


@router.get("/recommend/{user_id}", response_model=List[MatchResponse])
def get_recommendations(user_id: int, top_n: int = 10, db: Session = Depends(get_db)):
    """获取 Top N 推荐"""
    service = MatchService(db)
    return service.get_top_recommendations(user_id, top_n)


@router.get("/user/{user_id}", response_model=List[MatchResponse])
def get_user_matches(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """获取用户的匹配记录"""
    service = MatchService(db)
    return service.get_user_matches(user_id, limit)


@router.post("/{match_id}/view", response_model=MatchResponse)
def mark_viewed(match_id: int, db: Session = Depends(get_db)):
    """标记为已查看"""
    service = MatchService(db)
    match = service.mark_as_viewed(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


@router.post("/{match_id}/apply", response_model=MatchResponse)
def mark_applied(match_id: int, db: Session = Depends(get_db)):
    """标记为已投递"""
    service = MatchService(db)
    match = service.mark_as_applied(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match
