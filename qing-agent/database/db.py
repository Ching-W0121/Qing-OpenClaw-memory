"""
数据库连接管理 - SQLite (SQLAlchemy 2.0 版)

ChatGPT 老师建议:
- 使用 DeclarativeBase 替代 declarative_base()
- SQLite 不需要连接池
- check_same_thread=False 允许跨线程访问
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

# 数据库路径
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'qing_agent.db')
DATABASE_URL = f"sqlite:///{db_path}"

# ChatGPT 老师建议：SQLite 不需要连接池
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 需要
    echo=False,  # 生产环境关闭 SQL 日志
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ChatGPT 老师建议：SQLAlchemy 2.0 写法
class Base(DeclarativeBase):
    """SQLAlchemy 2.0 基类"""
    pass


def init_db():
    """初始化数据库（创建表）"""
    from database import models
    Base.metadata.create_all(bind=engine)
    print(f"✅ 数据库初始化完成：{db_path}")


def get_db():
    """
    获取数据库会话（FastAPI Depends 使用）
    
    ChatGPT 老师评价：这是 FastAPI 官方推荐方式 ✅
    
    Yields:
        Session: 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
