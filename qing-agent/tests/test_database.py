"""
数据库测试 - v1.4
测试 Repository Layer 和数据库操作
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.db import Base, get_db
from database.models import User, Job, Match, Application
from repositories.user_repo import UserRepository
from repositories.job_repo import JobRepository
from repositories.match_repo import MatchRepository
from repositories.application_repo import ApplicationRepository


# 测试数据库（内存 SQLite）
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


class TestUserRepository:
    """测试用户 Repository"""
    
    def test_create_user(self, db):
        """测试创建用户"""
        repo = UserRepository(db)
        user = repo.create({
            "name": "测试用户",
            "education": "本科",
            "major": "计算机",
            "experience_years": 3,
        })
        
        assert user.id is not None
        assert user.name == "测试用户"
        assert user.education == "本科"
    
    def test_get_user(self, db):
        """测试获取用户"""
        repo = UserRepository(db)
        created = repo.create({"name": "张三", "education": "本科"})
        retrieved = repo.get(created.id)
        
        assert retrieved is not None
        assert retrieved.name == "张三"
    
    def test_update_user(self, db):
        """测试更新用户"""
        repo = UserRepository(db)
        created = repo.create({"name": "李四", "education": "专科"})
        updated = repo.update(created.id, {"education": "本科"})
        
        assert updated.education == "本科"
    
    def test_delete_user(self, db):
        """测试删除用户"""
        repo = UserRepository(db)
        created = repo.create({"name": "王五"})
        success = repo.delete(created.id)
        
        assert success is True
        assert repo.get(created.id) is None
    
    def test_get_by_email(self, db):
        """测试根据邮箱查询"""
        repo = UserRepository(db)
        repo.create({"name": "赵六", "email": "zhaoliu@example.com"})
        user = repo.get_by_email("zhaoliu@example.com")
        
        assert user is not None
        assert user.name == "赵六"


class TestJobRepository:
    """测试职位 Repository"""
    
    def test_create_job(self, db):
        """测试创建职位"""
        repo = JobRepository(db)
        job = repo.create({
            "platform": "zhilian",
            "source_platform_id": "test_001",
            "title": "Python 工程师",
            "company": "测试公司",
            "city": "深圳",
            "salary_min": 10000,
        })
        
        assert job.id is not None
        assert job.title == "Python 工程师"
    
    def test_unique_index(self, db):
        """测试唯一索引（平台 + 职位 ID）"""
        repo = JobRepository(db)
        repo.create({
            "platform": "boss",
            "source_platform_id": "job_123",
            "title": "职位 A",
        })
        
        # 相同 platform + source_platform_id 应该失败
        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            repo.create({
                "platform": "boss",
                "source_platform_id": "job_123",
                "title": "职位 A 重复",
            })
    
    def test_search_by_title(self, db):
        """测试根据标题搜索"""
        repo = JobRepository(db)
        repo.create({"platform": "zhilian", "source_platform_id": "1", "title": "Java 工程师"})
        repo.create({"platform": "zhilian", "source_platform_id": "2", "title": "Python 工程师"})
        
        jobs = repo.search_by_title("工程师")
        assert len(jobs) == 2


class TestMatchRepository:
    """测试匹配 Repository"""
    
    def test_create_match(self, db):
        """测试创建匹配"""
        # 先创建用户和职位
        user_repo = UserRepository(db)
        job_repo = JobRepository(db)
        match_repo = MatchRepository(db)
        
        user = user_repo.create({"name": "用户 A"})
        job = job_repo.create({
            "platform": "zhilian",
            "source_platform_id": "job_001",
            "title": "测试职位",
        })
        
        match = match_repo.create_match(
            user_id=user.id,
            job_id=job.id,
            match_score=0.85,
            match_vector={"skill": 0.8, "experience": 0.9},
            match_details={"reason": "匹配度高"}
        )
        
        assert match.match_score == 0.85
        assert match.match_vector == {"skill": 0.8, "experience": 0.9}
    
    def test_get_top_recommendations(self, db):
        """测试获取 Top 推荐"""
        user_repo = UserRepository(db)
        job_repo = JobRepository(db)
        match_repo = MatchRepository(db)
        
        user = user_repo.create({"name": "用户 B"})
        job1 = job_repo.create({"platform": "zhilian", "source_platform_id": "1", "title": "职位 1"})
        job2 = job_repo.create({"platform": "zhilian", "source_platform_id": "2", "title": "职位 2"})
        
        match_repo.create_match(user.id, job1.id, 0.7, {}, {})
        match_repo.create_match(user.id, job2.id, 0.9, {}, {})
        
        top = match_repo.get_top_recommendations(user.id, top_n=1)
        assert len(top) == 1
        assert top[0].match_score == 0.9


class TestApplicationRepository:
    """测试投递 Repository"""
    
    def test_create_application(self, db):
        """测试创建投递"""
        user_repo = UserRepository(db)
        job_repo = JobRepository(db)
        app_repo = ApplicationRepository(db)
        
        user = user_repo.create({"name": "用户 C"})
        job = job_repo.create({"platform": "zhilian", "source_platform_id": "1", "title": "职位"})
        
        app = app_repo.create_application(user.id, job.id, "pending")
        
        assert app.status == "pending"
        assert app.user_id == user.id
        assert app.job_id == job.id
    
    def test_update_status(self, db):
        """测试更新状态"""
        user_repo = UserRepository(db)
        job_repo = JobRepository(db)
        app_repo = ApplicationRepository(db)
        
        user = user_repo.create({"name": "用户 D"})
        job = job_repo.create({"platform": "zhilian", "source_platform_id": "1", "title": "职位"})
        app = app_repo.create_application(user.id, job.id, "pending")
        
        updated = app_repo.update_status(app.id, "interview", "hr_viewed")
        
        assert updated.status == "interview"
        assert updated.platform_status == "hr_viewed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
