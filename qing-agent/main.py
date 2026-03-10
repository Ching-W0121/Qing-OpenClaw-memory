"""
FastAPI 入口 - v1.4 (SQLite + Repository 版)

ChatGPT 老师建议的架构升级:
- Repository Layer 数据访问层
- SQLAlchemy 2.0
- Alembic 数据库迁移
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# 创建 FastAPI 应用
app = FastAPI(
    title="求职 Agent API",
    description="产品级求职 Agent 系统 - v1.4 (SQLite + Repository)",
    version="1.4.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    print("=" * 60)
    print("🚀 求职 Agent API v1.4.0 启动")
    print("=" * 60)
    print(f"[INFO] 服务地址：http://127.0.0.1:8000")
    print(f"[INFO] API 文档：http://127.0.0.1:8000/docs")
    print(f"[INFO] 架构：FastAPI + SQLAlchemy 2.0 + Repository")
    print(f"[INFO] 数据库：SQLite + Alembic")
    print(f"\n按 Ctrl+C 停止服务\n")
    
    # 初始化数据库
    from database.db import init_db
    init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理资源"""
    print("[SHUTDOWN] 服务关闭")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "求职 Agent API v1.4.0 (SQLite + Repository)",
        "version": "1.4.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "users": "/api/users",
            "jobs": "/api/jobs",
            "matches": "/api/matches",
            "applications": "/api/applications",
            "health": "/health",
        },
        "architecture": {
            "database": "SQLite + Alembic",
            "orm": "SQLAlchemy 2.0",
            "pattern": "Repository + Service",
            "schemas": "Pydantic v2",
        },
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    from tools.circuit_breaker import CircuitBreaker
    from tools.operation_limiter import OperationLimiter
    
    cb = CircuitBreaker()
    limiter = OperationLimiter()
    
    return {
        "status": "healthy",
        "version": "1.4.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "circuit_breaker": cb.state.value,
            "limiter": "ok",
            "database": "connected",
            "repository": "enabled",
        },
    }


# 注册路由
from routes import users, jobs, matches, applications

app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(matches.router)
app.include_router(applications.router)


# 测试数据初始化
@app.post("/init/test-data")
async def init_test_data():
    """初始化测试数据"""
    from database.db import SessionLocal
    from repositories.user_repo import UserRepository
    from repositories.job_repo import JobRepository
    from repositories.match_repo import MatchRepository
    from repositories.application_repo import ApplicationRepository
    
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        job_repo = JobRepository(db)
        match_repo = MatchRepository(db)
        app_repo = ApplicationRepository(db)
        
        # 创建测试用户
        test_user = user_repo.create({
            "name": "测试用户",
            "education": "本科",
            "major": "计算机科学与技术",
            "experience_years": 3,
            "skills": ["Python", "FastAPI", "SQLAlchemy"],
            "tools": ["Git", "Docker"],
            "industry": "互联网",
            "expected_city": "深圳",
            "expected_salary_min": 10000,
            "expected_salary_max": 15000,
        })
        
        # 创建测试职位
        test_job = job_repo.create({
            "platform": "zhilian",
            "source_platform_id": "test_001",
            "title": "Python 开发工程师",
            "company": "某某科技公司",
            "city": "深圳",
            "district": "南山区",
            "salary_min": 12000,
            "salary_max": 18000,
            "experience": "3-5 年",
            "education": "本科",
            "industry": "互联网",
            "skills": ["Python", "FastAPI"],
            "url": "https://example.com/job/001",
        })
        
        # 创建测试匹配
        test_match = match_repo.create_match(
            user_id=test_user.id,
            job_id=test_job.id,
            match_score=0.85,
            match_vector={
                "industry": 0.9,
                "skill": 0.8,
                "experience": 0.8,
                "salary": 0.9,
                "location": 1.0,
                "education": 1.0,
                "tools": 0.7,
            },
            match_details={"reason": "技能和经验匹配度高"}
        )
        
        # 创建测试投递
        test_app = app_repo.create_application(
            user_id=test_user.id,
            job_id=test_job.id,
            status="pending"
        )
        
        return {
            "message": "测试数据初始化完成",
            "user_id": test_user.id,
            "job_id": test_job.id,
            "match_id": test_match.id,
            "application_id": test_app.id,
        }
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
