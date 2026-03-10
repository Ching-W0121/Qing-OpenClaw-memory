"""
投递路由 - v1.4 (使用 Schema + Service + Repository)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database.db import get_db
from services.application_service import ApplicationService
from schemas import ApplicationCreate, ApplicationUpdate, ApplicationResponse

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("/submit", response_model=ApplicationResponse)
def submit_application(app_data: ApplicationCreate, db: Session = Depends(get_db)):
    """提交投递"""
    service = ApplicationService(db)
    return service.create_application(
        user_id=app_data.user_id,
        job_id=app_data.job_id,
        status=app_data.status
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)):
    """获取投递记录"""
    service = ApplicationService(db)
    app = service.get_application(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.get("/user/{user_id}", response_model=List[ApplicationResponse])
def get_user_applications(user_id: int, db: Session = Depends(get_db)):
    """获取用户的投递记录"""
    service = ApplicationService(db)
    return service.get_user_applications(user_id)


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    app_data: ApplicationUpdate,
    db: Session = Depends(get_db)
):
    """更新投递状态"""
    service = ApplicationService(db)
    
    update_data = app_data.model_dump(exclude_unset=True)
    
    # 单独处理备注
    notes = update_data.pop('notes', None)
    if notes:
        service.add_note(application_id, notes)
    
    # 更新状态
    if update_data:
        app = service.update_status(
            application_id,
            update_data.get('status', 'pending'),
            update_data.get('platform_status')
        )
    else:
        app = service.get_application(application_id)
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.get("/user/{user_id}/status/{status}", response_model=List[ApplicationResponse])
def get_by_status(user_id: int, status: str, db: Session = Depends(get_db)):
    """根据状态获取投递"""
    service = ApplicationService(db)
    return service.get_by_status(user_id, status)
