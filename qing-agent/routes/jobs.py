"""
职位路由 - v1.4 (使用 Schema + Service + Repository)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.db import get_db
from services.job_service import JobService
from schemas import JobCreate, JobResponse

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    """创建职位"""
    service = JobService(db)
    return service.create_job(job_data.model_dump())


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """获取职位详情"""
    service = JobService(db)
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/search", response_model=List[JobResponse])
def search_jobs(
    keyword: Optional[str] = None,
    city: Optional[str] = None,
    district: Optional[str] = None,
    min_salary: Optional[int] = None,
    max_salary: Optional[int] = None,
    platform: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db)
):
    """搜索职位"""
    service = JobService(db)
    
    jobs = []
    if keyword:
        jobs = service.search_by_title(keyword, limit)
    elif city:
        jobs = service.filter_by_location(city, district)
    elif min_salary:
        jobs = service.filter_by_salary(min_salary, max_salary)
    elif platform:
        jobs = service.job_repo.filter(platform=platform)
    else:
        jobs = service.get_recent_jobs(limit=limit)
    
    return jobs


@router.get("/recent", response_model=List[JobResponse])
def get_recent_jobs(days: int = 7, limit: int = 100, db: Session = Depends(get_db)):
    """获取最近 N 天的职位"""
    service = JobService(db)
    return service.get_recent_jobs(days, limit)
