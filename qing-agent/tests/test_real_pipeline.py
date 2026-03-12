"""
真实 Pipeline 测试 - 使用浏览器获取真实职位数据
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qing_platform.zhilian_adapter import ZhilianAdapter
from tools.matcher import MatchingEngine
from tools.recommender import Recommender

async def run_real_pipeline():
    """运行真实 Pipeline"""
    print("\n" + "=" * 60)
    print("真实 Pipeline 测试 - 智联招聘")
    print("=" * 60)
    
    # 初始化
    print("\n[1/5] 初始化组件...")
    adapter = ZhilianAdapter()
    matcher = MatchingEngine()
    recommender = Recommender()
    print("   [OK] 完成")
    
    # 用户画像
    print("\n[2/5] 用户画像...")
    user_profile = {
        "target_jobs": ["品牌策划", "品牌宣传", "活动策划"],
        "expected_city": "深圳",
        "expected_salary_min": 8000,
        "expected_salary_max": 15000,
        "experience_years": 3,
        "education": "本科",
        "skills": ["品牌策划", "活动策划", "文案写作", "新媒体运营"],
        "tools": ["Office", "Photoshop", "微信公众号"],
    }
    print("   [OK] 完成")
    
    # 搜索职位
    print("\n[3/5] 搜索职位...")
    keyword = "品牌策划"
    city = "深圳"
    print(f"   关键词：{keyword}")
    print(f"   城市：{city}")
    
    jobs = await adapter.search_jobs(keyword, city=city)
    print(f"   [OK] 找到 {len(jobs)} 个职位")
    
    if not jobs:
        print("   [FAIL] 没有找到职位")
        return False
    
    # 显示职位
    print("\n职位列表:")
    for i, job in enumerate(jobs[:5], 1):
        print(f"\n  {i}. {job.get('title', 'N/A')}")
        print(f"     公司：{job.get('company', 'N/A')}")
        print(f"     薪资：{job.get('salary', 'N/A')}")
        print(f"     地点：{job.get('city', 'N/A')} - {job.get('district', 'N/A')}")
        print(f"     经验：{job.get('experience', 'N/A')}")
        print(f"     学历：{job.get('education', 'N/A')}")
        print(f"     技能：{job.get('skills', [])[:3]}")
    
    # 匹配计算
    print("\n[4/5] 匹配计算...")
    matches = []
    for job in jobs:
        try:
            match_result = matcher.calculate_match(user_profile, job)
            matches.append({
                "job": job,
                "match": match_result
            })
        except Exception as e:
            print(f"   [WARN] 匹配失败：{e}")
            continue
    
    print(f"   [OK] 完成 {len(matches)} 个职位匹配")
    
    # 排序推荐
    print("\n[5/5] 排序推荐...")
    ranked = recommender.rank(matches, top_n=10)
    print(f"   [OK] 推荐 {len(ranked)} 个职位")
    
    # 显示推荐结果
    print("\n" + "=" * 60)
    print("推荐结果 (Top 5)")
    print("=" * 60)
    
    for i, item in enumerate(ranked[:5], 1):
        job = item["job"]
        match = item["match"]
        score = match.get("total", 0) * 100 if isinstance(match, dict) else 0
        
        print(f"\n{i}. {job.get('title', 'N/A')}")
        print(f"   匹配度：{score:.1f}%")
        print(f"   公司：{job.get('company', 'N/A')}")
        print(f"   薪资：{job.get('salary', 'N/A')}")
        print(f"   地点：{job.get('city', 'N/A')} - {job.get('district', 'N/A')}")
        print(f"   经验：{job.get('experience', 'N/A')}")
        print(f"   学历：{job.get('education', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    if len(ranked) > 0:
        print("\n[SUCCESS] Pipeline 测试成功！")
        return True
    else:
        print("\n[FAIL] 没有推荐结果")
        return False

async def main():
    try:
        success = await run_real_pipeline()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] 测试异常：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
