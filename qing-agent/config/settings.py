"""
配置文件
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API 配置
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/qing_agent.db")

# 缓存配置
CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))  # 1 小时
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", 1000))

# AI 配置（可选）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-zh")

# 业务配置
MAX_RECOMMEND = int(os.getenv("MAX_RECOMMEND", 10))
MATCH_THRESHOLD = float(os.getenv("MATCH_THRESHOLD", 0.7))

# BOSS 直聘配置
BOSS_CITY_CODE = os.getenv("BOSS_CITY_CODE", "101280600")  # 深圳
BOSS_EXCLUDE_DISTRICTS = os.getenv("BOSS_EXCLUDE_DISTRICTS", "宝安区").split(",")

# 限流配置
SEARCH_LIMIT_PER_HOUR = int(os.getenv("SEARCH_LIMIT_PER_HOUR", 10))
JOB_DETAIL_LIMIT_PER_DAY = int(os.getenv("JOB_DETAIL_LIMIT_PER_DAY", 30))
