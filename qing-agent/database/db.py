"""
数据库连接管理 - SQLite
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库路径
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'qing_agent.db')
DATABASE_URL = f"sqlite:///{db_path}"

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 需要
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基类
Base = declarative_base()

def init_db():
    """初始化数据库（创建表）"""
    from database import models
    Base.metadata.create_all(bind=engine)
    print(f"✅ 数据库初始化完成：{db_path}")

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
