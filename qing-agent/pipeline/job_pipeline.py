"""
求职任务流水线
"""

from services.resume_service import ResumeService
from services.job_service import JobService
from services.match_service import MatchService
from tools.recommender import Recommender

class JobPipeline:
    """求职任务流水线"""
    
    def __init__(self):
        self.resume_service = ResumeService()
        self.job_service = JobService()
        self.match_service = MatchService()
        self.recommender = Recommender()
    
    async def run(self, user_id, keywords=None, top_n=10):
        """
        执行完整求职流程
        
        流程：
        1. 获取用户画像
        2. 搜索职位
        3. 解析 JD
        4. 计算匹配
        5. 排序推荐
        6. 返回结果
        """
        print(f"🚀 开始执行求职 Pipeline，用户：{user_id}")
        
        # 步骤 1: 获取用户画像
        print("📄 步骤 1: 获取用户画像")
        profile = await self.resume_service.get_profile(user_id)
        
        # 如果用户没有目标职位，使用传入的关键词
        search_keywords = keywords or profile.get('target_jobs') or ["品牌策划"]
        
        # 步骤 2: 搜索职位
        print(f"🔎 步骤 2: 搜索职位，关键词：{search_keywords}")
        jobs = []
        for keyword in search_keywords:
            keyword_jobs = await self.job_service.search(keyword, profile.get('expected_city'))
            jobs.extend(keyword_jobs)
        
        print(f"   找到 {len(jobs)} 个职位")
        
        # 步骤 3: 解析 JD（批量）
        print("📋 步骤 3: 解析 JD")
        parsed_jobs = await self.job_service.parse_details(jobs)
        print(f"   解析完成 {len(parsed_jobs)} 个职位")
        
        # 步骤 4: 计算匹配
        print("📊 步骤 4: 计算匹配度")
        matches = []
        for job in parsed_jobs:
            match_result = await self.match_service.calculate(profile, job)
            matches.append({
                "job": job,
                "match": match_result
            })
        
        # 步骤 5: 排序推荐
        print("🎯 步骤 5: 排序推荐")
        ranked = self.recommender.rank(matches, top_n=top_n)
        
        # 步骤 6: 保存结果
        print("💾 步骤 6: 保存结果")
        await self.match_service.save_matches(user_id, ranked)
        
        print(f"✅ Pipeline 完成，推荐 {len(ranked)} 个职位")
        
        return ranked
    
    async def run_with_apply(self, user_id, job_ids, keywords=None):
        """
        执行求职流程并自动投递
        
        Args:
            user_id: 用户 ID
            job_ids: 要投递的职位 ID 列表
            keywords: 搜索关键词
        
        Returns:
            list: 已投递的职位
        """
        # 先执行标准流程
        ranked = await self.run(user_id, keywords)
        
        # 筛选指定职位
        to_apply = [j for j in ranked if j["job"].get("id") in job_ids]
        
        # 执行投递
        for item in to_apply:
            await self.job_service.apply(item["job"], user_id)
        
        return to_apply
