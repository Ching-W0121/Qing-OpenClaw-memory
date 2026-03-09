"""
FastAPI 入口 - v1.3 (JWT 认证版)
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# 创建 FastAPI 应用
app = FastAPI(
    title="求职 Agent API",
    description="产品级求职 Agent 系统 - v1.3 (支持 JWT 认证)",
    version="1.3.0",
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
    print(f"[STARTUP] 求职 Agent API v1.2.0")
    print(f"[INFO] 服务地址：http://127.0.0.1:8000")
    print(f"[INFO] API 文档：http://127.0.0.1:8000/docs")
    print(f"\n按 Ctrl+C 停止服务\n")

@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理资源"""
    print("[SHUTDOWN] 服务关闭")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "求职 Agent API v1.3.0 (支持 JWT 认证)",
        "version": "1.3.0",
        "status": "running",
        "docs": "/docs",
        "auth_docs": "/auth/docs",
        "endpoints": {
            "users": "/api/users",
            "jobs": "/api/jobs",
            "matches": "/api/matches",
            "applications": "/api/applications",
            "health": "/health",
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
        "version": "1.3.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "circuit_breaker": cb.state.value,
            "limiter": "ok",
            "jwt_auth": "enabled",
        },
    }

@app.get("/auth/docs")
async def auth_docs():
    """JWT 认证文档"""
    return {
        "title": "JWT 认证文档",
        "version": "1.3.0",
        "auth0_domain": "qing-personal-domain.au.auth0.com",
        "api_audience": "https://qing-agent-api",
        "algorithm": "RS256",
        "jwks_url": "https://qing-personal-domain.au.auth0.com/.well-known/jwks.json",
        "permissions": {
            "read:jobs": "读取职位信息",
            "write:jobs": "写入职位信息/投递",
            "read:users": "读取用户信息",
            "write:users": "写入用户信息",
        },
        "usage": {
            "header": "Authorization: Bearer YOUR_ACCESS_TOKEN",
            "example": "curl -H 'Authorization: Bearer TOKEN' http://127.0.0.1:8000/api/jobs/search",
        },
    }

# 注册路由（带 JWT 认证）
from routes.users import router as users_router
from routes.jobs import router as jobs_router
from routes.matches import router as matches_router
from routes.applications import router as applications_router

# 所有 API 路由现在都受 JWT 保护
app.include_router(users_router)
app.include_router(jobs_router)
app.include_router(matches_router)
app.include_router(applications_router)

# 测试端点
@app.get("/api/test/match")
async def test_match():
    """测试匹配功能"""
    from tools.matcher import MatchingEngine
    
    engine = MatchingEngine()
    
    user = {
        "industry": "广告",
        "skills": ["品牌策划", "文案写作"],
        "tools": ["Photoshop"],
        "experience_years": 3,
        "education": "本科",
        "expected_city": "深圳",
        "expected_salary_min": 10000,
        "expected_salary_max": 15000,
    }
    
    job = {
        "industry": "广告",
        "skills": ["品牌策划", "营销策划"],
        "tools": ["Photoshop"],
        "experience": "3-5 年",
        "education": "本科",
        "city": "深圳",
        "salary_min": 12000,
        "salary_max": 18000,
    }
    
    result = engine.calculate_match(user, job)
    
    return {
        "match_score": result["total"],
        "match_level": engine.get_match_level(result["total"]),
        "details": result["details"],
    }

@app.get("/api/test/industry")
async def test_industry():
    """测试行业匹配"""
    from tools.industry_matcher import IndustryMatcher
    
    matcher = IndustryMatcher()
    
    test_cases = [
        ("广告", "广告"),
        ("广告", "品牌咨询"),
        ("品牌咨询", "营销策划"),
        ("广告", "电商"),
        ("广告", "金融"),
    ]
    
    results = []
    for user_ind, job_ind in test_cases:
        score = matcher.match(user_ind, job_ind)
        results.append({
            "user": user_ind,
            "job": job_ind,
            "score": score,
        })
    
    return {"results": results}

@app.get("/api/test/protection")
async def test_protection():
    """测试防封禁组件"""
    from tools.circuit_breaker import CircuitBreaker
    from tools.operation_limiter import OperationLimiter
    from tools.session_manager import SessionManager
    
    cb = CircuitBreaker()
    limiter = OperationLimiter()
    session = SessionManager()
    
    return {
        "circuit_breaker": cb.get_status(),
        "limiter": limiter.get_status(),
        "session_manager": session.get_session_info(),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
