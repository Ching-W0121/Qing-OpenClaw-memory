"""
职位服务
"""

from platform.adapter_factory import AdapterFactory
from database.cache import cache
from database.db import get_db
from database import models
from datetime import datetime

class JobService:
    """职位服务"""
    
    def __init__(self):
        self.adapters = {}
    
    def _get_adapter(self, platform):
        """获取平台适配器（单例）"""
        if platform not in self.adapters:
            self.adapters[platform] = AdapterFactory.get_adapter(platform)
        return self.adapters[platform]
    
    async def search(self, keyword, city=None, platforms=None):
        """
        搜索职位（多平台）
        
        Args:
            keyword: 搜索关键词
            city: 城市
            platforms: 平台列表，默认 ["boss"]
        
        Returns:
            list: 职位列表
        """
        if platforms is None:
            platforms = ["boss"]
        
        all_jobs = []
        
        for platform in platforms:
            # 检查缓存
            cache_key = f"search:{platform}:{keyword}:{city}"
            cached = cache.get(cache_key)
            
            if cached:
                print(f"✅ 缓存命中：{cache_key}")
                all_jobs.extend(cached)
                continue
            
            # 搜索
            adapter = self._get_adapter(platform)
            jobs = await adapter.search_jobs(keyword, city)
            
            # 缓存 1 小时
            cache.set(cache_key, jobs, use_ttl=True)
            
            all_jobs.extend(jobs)
        
        return all_jobs
    
    async def parse_details(self, jobs):
        """
        批量解析职位详情
        
        Args:
            jobs: 职位列表
        
        Returns:
            list: 解析后的职位详情
        """
        parsed = []
        
        for job in jobs:
            # 检查缓存
            cache_key = f"job:{job['platform']}:{job.get('url', job.get('id'))}"
            cached = cache.get(cache_key)
            
            if cached:
                parsed.append(cached)
                continue
            
            # 解析详情
            adapter = self._get_adapter(job['platform'])
            detail = await adapter.get_job_detail(job['url'])
            
            # 合并数据
            job.update(detail)
            
            # 缓存 24 小时
            cache.set(cache_key, job, use_ttl=True)
            
            parsed.append(job)
        
        return parsed
    
    async def apply(self, job, user_id):
        """
        申请职位
        
        Args:
            job: 职位 dict
            user_id: 用户 ID
        
        Returns:
            dict: 投递结果
        """
        adapter = self._get_adapter(job['platform'])
        
        # 获取用户简历
        resume = await self._get_user_resume(user_id)
        
        # 执行投递
        result = await adapter.apply(job['url'], resume)
        
        # 保存投递记录
        await self._save_application(user_id, job, result)
        
        return result
    
    async def _get_user_resume(self, user_id):
        """获取用户简历"""
        db = next(get_db())
        user = db.query(models.User).filter(models.User.id == user_id).first()
        
        if not user:
            raise ValueError(f"用户不存在：{user_id}")
        
        return user.resume_file
    
    async def _save_application(self, user_id, job, result):
        """保存投递记录"""
        db = next(get_db())
        
        # 查找或创建职位记录
        job_record = db.query(models.Job).filter(models.Job.url == job['url']).first()
        if not job_record:
            job_record = models.Job(
                title=job.get('title', ''),
                company=job.get('company', ''),
                city=job.get('city', ''),
                platform=job.get('platform', ''),
                url=job.get('url', ''),
            )
            db.add(job_record)
            db.commit()
            db.refresh(job_record)
        
        # 创建投递记录
        application = models.Application(
            user_id=user_id,
            job_id=job_record.id,
            status=result.get('status', 'submitted'),
            applied_at=datetime.now(),
        )
        
        db.add(application)
        db.commit()
