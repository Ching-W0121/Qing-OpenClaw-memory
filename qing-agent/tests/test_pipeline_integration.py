"""
JobPipeline 集成测试
测试完整的求职流程
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qing_platform.zhilian_adapter import ZhilianAdapter
from tools.jd_parser import JDParser
from tools.matcher import MatchingEngine
from tools.recommender import Recommender

async def test_pipeline():
    """测试简化版 Pipeline"""
    print("\n" + "=" * 60)
    print("JobPipeline 集成测试")
    print("=" * 60)
    
    # 初始化组件
    print("\n[1/6] 初始化组件...")
    adapter = ZhilianAdapter()
    parser = JDParser()
    matcher = MatchingEngine()
    recommender = Recommender()
    print("   [OK] 组件初始化完成")
    
    # 步骤 1: 搜索职位
    print("\n[2/6] 搜索职位...")
    keyword = "品牌策划"
    city = "深圳"
    print(f"   关键词：{keyword}")
    print(f"   城市：{city}")
    
    jobs = await adapter.search_jobs(keyword, city=city)
    print(f"   [OK] 找到 {len(jobs)} 个职位")
    
    if not jobs:
        print("   [FAIL] 没有找到职位，测试结束")
        return False
    
    # 步骤 2: 解析职位（已经解析过了）
    print("\n[3/6] 职位信息...")
    print(f"   [OK] {len(jobs)} 个职位已解析")
    
    # 显示前 3 个职位
    for i, job in enumerate(jobs[:3], 1):
        print(f"\n   职位 {i}:")
        print(f"     标题：{job.get('title', 'N/A')}")
        print(f"     公司：{job.get('company', 'N/A')}")
        print(f"     薪资：{job.get('salary', 'N/A')}")
        print(f"     地点：{job.get('city', 'N/A')} - {job.get('district', 'N/A')}")
        print(f"     经验：{job.get('experience', 'N/A')}")
        print(f"     学历：{job.get('education', 'N/A')}")
        print(f"     技能：{job.get('skills', [])[:3]}")
    
    # 步骤 3: 模拟用户画像
    print("\n[4/6] 用户画像...")
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
    print(f"   目标职位：{user_profile['target_jobs']}")
    print(f"   期望城市：{user_profile['expected_city']}")
    print(f"   期望薪资：{user_profile['expected_salary_min']}-{user_profile['expected_salary_max']}")
    print(f"   工作经验：{user_profile['experience_years']}年")
    print(f"   学历：{user_profile['education']}")
    print(f"   技能：{user_profile['skills']}")
    print("   [OK] 用户画像已加载")
    
    # 步骤 4: 计算匹配度
    print("\n[5/6] 计算匹配度...")
    matches = []
    for job in jobs:
        try:
            match_result = matcher.calculate_match(user_profile, job)
            matches.append({
                "job": job,
                "match": match_result
            })
        except Exception as e:
            print(f"   [WARN] 职位匹配失败：{e}")
            continue
    
    print(f"   [OK] 完成 {len(matches)} 个职位的匹配计算")
    
    # 步骤 5: 排序推荐
    print("\n[6/6] 排序推荐...")
    ranked = recommender.rank(matches, top_n=10)
    print(f"   [OK] 推荐 {len(ranked)} 个职位")
    
    # 显示推荐结果
    print("\n" + "=" * 60)
    print("推荐结果 (Top 5)")
    print("=" * 60)
    
    for i, item in enumerate(ranked[:5], 1):
        job = item["job"]
        match = item["match"]
        # 匹配度可能是 total 或 total_score
        score = match.get("total", 0) if isinstance(match, dict) else match
        score_percent = score * 100 if isinstance(score, (int, float)) else 0
        
        print(f"\n{i}. {job.get('title', 'N/A')}")
        print(f"   匹配度：{score_percent:.1f}%")
        print(f"   公司：{job.get('company', 'N/A')}")
        print(f"   薪资：{job.get('salary', 'N/A')}")
        print(f"   地点：{job.get('city', 'N/A')} - {job.get('district', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    if len(ranked) > 0:
        print("\n[SUCCESS] Pipeline 测试成功！")
        return True
    else:
        print("\n[FAIL] Pipeline 测试失败：没有推荐结果")
        return False

async def main():
    """主函数"""
    try:
        success = await test_pipeline()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] 测试异常：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
