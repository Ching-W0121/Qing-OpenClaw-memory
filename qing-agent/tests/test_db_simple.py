"""
数据库快速测试 - v1.4
不使用 pytest，直接测试 Repository Layer
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import SessionLocal, init_db
from repositories.user_repo import UserRepository
from repositories.job_repo import JobRepository
from repositories.match_repo import MatchRepository
from repositories.application_repo import ApplicationRepository

print("=" * 60)
print("🧪 v1.4 数据库测试")
print("=" * 60)

# 初始化数据库
print("\n[1/6] 初始化数据库...")
init_db()
print("✅ 数据库初始化成功")

# 获取会话
db = SessionLocal()

try:
    # 测试 1: 创建用户
    print("\n[2/6] 测试 UserRepository...")
    user_repo = UserRepository(db)
    user = user_repo.create({
        "name": "测试用户",
        "education": "本科",
        "major": "计算机科学与技术",
        "experience_years": 3,
        "skills": ["Python", "FastAPI"],
        "expected_city": "深圳",
        "expected_salary_min": 10000,
        "expected_salary_max": 15000,
    })
    print(f"✅ 创建用户成功：ID={user.id}, Name={user.name}")
    
    # 测试 2: 创建职位
    print("\n[3/6] 测试 JobRepository...")
    job_repo = JobRepository(db)
    job = job_repo.create({
        "platform": "zhilian",
        "source_platform_id": "TEST_001",
        "title": "Python 开发工程师",
        "company": "某某科技公司",
        "city": "深圳",
        "district": "南山区",
        "salary_min": 12000,
        "salary_max": 18000,
        "experience": "3-5 年",
        "education": "本科",
        "skills": ["Python", "FastAPI", "SQLAlchemy"],
    })
    print(f"✅ 创建职位成功：ID={job.id}, Title={job.title}")
    
    # 测试 3: 创建匹配
    print("\n[4/6] 测试 MatchRepository...")
    match_repo = MatchRepository(db)
    match = match_repo.create_match(
        user_id=user.id,
        job_id=job.id,
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
    print(f"✅ 创建匹配成功：ID={match.id}, Score={match.match_score}")
    
    # 测试 4: 创建投递
    print("\n[5/6] 测试 ApplicationRepository...")
    app_repo = ApplicationRepository(db)
    app = app_repo.create_application(
        user_id=user.id,
        job_id=job.id,
        status="pending"
    )
    print(f"✅ 创建投递成功：ID={app.id}, Status={app.status}")
    
    # 测试 5: 查询测试
    print("\n[6/6] 测试查询操作...")
    
    # 查询用户
    retrieved_user = user_repo.get(user.id)
    assert retrieved_user.name == "测试用户"
    print(f"✅ 查询用户成功：{retrieved_user.name}")
    
    # 查询职位
    retrieved_job = job_repo.get(job.id)
    assert retrieved_job.title == "Python 开发工程师"
    print(f"✅ 查询职位成功：{retrieved_job.title}")
    
    # 获取用户匹配
    user_matches = match_repo.get_user_matches(user.id)
    assert len(user_matches) == 1
    print(f"✅ 查询用户匹配成功：{len(user_matches)} 条")
    
    # 获取 Top 推荐
    top_recs = match_repo.get_top_recommendations(user.id, top_n=10)
    assert len(top_recs) == 1
    print(f"✅ 获取 Top 推荐成功：{len(top_recs)} 条")
    
    # 获取用户投递
    user_apps = app_repo.get_user_applications(user.id)
    assert len(user_apps) == 1
    print(f"✅ 查询用户投递成功：{len(user_apps)} 条")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！v1.4 架构运行正常")
    print("=" * 60)
    
    print(f"\n📊 测试数据:")
    print(f"   用户：{user.id}")
    print(f"   职位：{job.id}")
    print(f"   匹配：{match.id} (匹配度：{match.match_score:.0%})")
    print(f"   投递：{app.id}")
    
except Exception as e:
    print(f"\n❌ 测试失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

finally:
    db.close()
