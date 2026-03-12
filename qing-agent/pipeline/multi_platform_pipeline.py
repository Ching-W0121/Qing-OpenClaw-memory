"""
多平台职位搜索 Pipeline
并发从多个平台获取职位数据
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from qing_platform.zhilian_adapter import ZhilianAdapter
from qing_platform.job51_adapter import Job51Adapter
from qing_platform.lagou_adapter import LagouAdapter
from qing_platform.liepin_adapter import LiepinAdapter

from tools.deduplication import deduplicate_jobs
from tools.scorer import score_jobs
from services.job_repository import JobRepository

class MultiPlatformPipeline:
    """多平台职位搜索 Pipeline"""
    
    def __init__(self, platforms: List[str] = None):
        """
        初始化 Pipeline
        
        Args:
            platforms: 启用的平台列表，默认全部启用
        """
        self.platforms = platforms or ['zhilian', '51job', 'lagou', 'liepin']
        self.adapters = {}
        
        # 初始化适配器
        if 'zhilian' in self.platforms:
            self.adapters['zhilian'] = ZhilianAdapter()
        if '51job' in self.platforms:
            self.adapters['51job'] = Job51Adapter()
        if 'lagou' in self.platforms:
            self.adapters['lagou'] = LagouAdapter()
        if 'liepin' in self.platforms:
            self.adapters['liepin'] = LiepinAdapter()
        
        # 数据库
        self.repo = JobRepository()
    
    async def search_all_platforms(self, keyword: str, city: str = '深圳') -> Dict[str, Any]:
        """
        并发搜索所有平台
        
        Args:
            keyword: 搜索关键词
            city: 城市
        
        Returns:
            搜索结果（包含各平台数据和汇总）
        """
        print("\n" + "="*60)
        print(f"多平台搜索：{keyword} - {city}")
        print("="*60)
        
        start_time = datetime.now()
        
        # 并发搜索所有平台
        tasks = []
        for platform_name, adapter in self.adapters.items():
            task = self._search_single_platform(platform_name, adapter, keyword, city)
            tasks.append(task)
        
        # 等待所有平台完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 汇总结果
        all_jobs = []
        platform_stats = {}
        
        for result in results:
            if isinstance(result, Exception):
                print(f"[ERROR] 平台搜索失败：{result}")
                continue
            
            platform_name = result['platform']
            jobs = result['jobs']
            duration = result['duration']
            
            platform_stats[platform_name] = {
                'count': len(jobs),
                'duration': duration,
                'status': 'success'
            }
            
            all_jobs.extend(jobs)
        
        # 去重
        unique_jobs = deduplicate_jobs(all_jobs)
        
        # 统计
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        summary = {
            'keyword': keyword,
            'city': city,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'total_duration': total_duration,
            'total_jobs': len(all_jobs),
            'unique_jobs': len(unique_jobs),
            'duplicates_removed': len(all_jobs) - len(unique_jobs),
            'platform_stats': platform_stats,
        }
        
        return {
            'summary': summary,
            'all_jobs': all_jobs,
            'unique_jobs': unique_jobs,
        }
    
    async def _search_single_platform(self, platform_name: str, adapter, keyword: str, city: str) -> Dict[str, Any]:
        """搜索单个平台"""
        start_time = datetime.now()
        
        try:
            print(f"\n[{platform_name}] 开始搜索...")
            jobs = await adapter.search_jobs(keyword, city=city)
            duration = (datetime.now() - start_time).total_seconds()
            
            print(f"[{platform_name}] 完成：{len(jobs)} 个职位 ({duration:.2f}s)")
            
            return {
                'platform': platform_name,
                'jobs': jobs,
                'duration': duration,
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            print(f"[{platform_name}] 失败：{e} ({duration:.2f}s)")
            
            return {
                'platform': platform_name,
                'jobs': [],
                'duration': duration,
                'error': str(e),
            }
    
    def save_to_database(self, jobs: List[Dict[str, Any]]) -> int:
        """
        保存职位到数据库
        
        Args:
            jobs: 职位列表
        
        Returns:
            保存的职位数量
        """
        saved_count = 0
        for job in jobs:
            try:
                result = self.repo.save_job(job)
                if result:
                    saved_count += 1
            except Exception as e:
                print(f"[DB] 保存失败：{e}")
        
        return saved_count
    
    def process_and_recommend(self, jobs: List[Dict[str, Any]], user_profile: Dict[str, Any], top_n=10) -> List[Dict[str, Any]]:
        """
        处理职位并推荐
        
        Args:
            jobs: 职位列表
            user_profile: 用户画像
            top_n: 推荐数量
        
        Returns:
            推荐职位列表
        """
        # 评分
        scored_jobs = score_jobs(user_profile, jobs)
        
        # 排序
        ranked = sorted(
            scored_jobs,
            key=lambda x: x.get('total_score', 0),
            reverse=True
        )
        
        # 返回 Top N
        return ranked[:top_n]
    
    def close(self):
        """关闭资源"""
        self.repo.close()

async def run_pipeline(keyword: str = '品牌策划', city: str = '深圳', user_profile: Dict[str, Any] = None):
    """
    运行完整 Pipeline
    
    Args:
        keyword: 搜索关键词
        city: 城市
        user_profile: 用户画像
    
    Returns:
        搜索结果
    """
    # 默认用户画像
    if user_profile is None:
        user_profile = {
            'target_jobs': ['品牌策划', '品牌宣传', '活动策划'],
            'expected_city': '深圳',
            'expected_salary_min': 8000,
            'expected_salary_max': 15000,
            'experience_years': 3,
            'education': '本科',
            'skills': ['品牌策划', '活动策划', '文案写作', '新媒体运营'],
            'tools': ['Office', 'Photoshop', '微信公众号'],
        }
    
    # 初始化 Pipeline
    pipeline = MultiPlatformPipeline()
    
    try:
        # 1. 搜索所有平台
        search_result = await pipeline.search_all_platforms(keyword, city)
        
        # 2. 保存到数据库
        saved_count = pipeline.save_to_database(search_result['unique_jobs'])
        print(f"\n[DB] 保存 {saved_count} 个职位到数据库")
        
        # 3. 评分推荐
        recommendations = pipeline.process_and_recommend(
            search_result['unique_jobs'],
            user_profile,
            top_n=10
        )
        
        # 4. 显示推荐结果
        print("\n" + "="*60)
        print("推荐结果 (Top 5)")
        print("="*60)
        
        for i, job in enumerate(recommendations[:5], 1):
            score = job.get('total_score', 0) * 100
            print(f"\n{i}. {job.get('title', 'N/A')}")
            print(f"   匹配度：{score:.1f}%")
            print(f"   公司：{job.get('company', 'N/A')}")
            print(f"   薪资：{job.get('salary', 'N/A')}")
            print(f"   地点：{job.get('city', 'N/A')} - {job.get('district', 'N/A')}")
            print(f"   平台：{job.get('platform', 'N/A')}")
        
        return {
            'search_result': search_result,
            'recommendations': recommendations,
            'saved_count': saved_count,
        }
        
    finally:
        pipeline.close()

if __name__ == "__main__":
    asyncio.run(run_pipeline())
