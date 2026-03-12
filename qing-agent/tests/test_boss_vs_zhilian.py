"""
BOSS 直聘 vs 智联招聘 对比测试
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qing_platform.boss_adapter import BossAdapter
from qing_platform.zhilian_adapter import ZhilianAdapter
from tools.matcher import MatchingEngine
from tools.recommender import Recommender

async def test_platform(adapter, platform_name):
    """测试平台"""
    print(f"\n{'='*60}")
    print(f"测试平台：{platform_name}")
    print(f"{'='*60}")
    
    keyword = "品牌策划"
    city = "深圳"
    
    print(f"\n搜索：{keyword} - {city}")
    jobs = await adapter.search_jobs(keyword, city=city)
    
    print(f"\n找到 {len(jobs)} 个职位")
    
    if jobs:
        print(f"\n前 3 个职位:")
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{i}. {job.get('title', 'N/A')}")
            print(f"   公司：{job.get('company', 'N/A')}")
            print(f"   薪资：{job.get('salary', 'N/A')}")
            print(f"   地点：{job.get('city', 'N/A')} - {job.get('district', 'N/A')}")
    
    return jobs

async def main():
    """主测试"""
    print("\n" + "="*60)
    print("BOSS 直聘 vs 智联招聘 对比测试")
    print("="*60)
    
    # 初始化
    boss_adapter = BossAdapter()
    zhilian_adapter = ZhilianAdapter()
    
    # 测试 BOSS 直聘
    boss_jobs = await test_platform(boss_adapter, "BOSS 直聘")
    
    # 测试智联招聘
    zhilian_jobs = await test_platform(zhilian_adapter, "智联招聘")
    
    # 对比
    print(f"\n{'='*60}")
    print("对比结果")
    print(f"{'='*60}")
    print(f"BOSS 直聘：{len(boss_jobs)} 个职位")
    print(f"智联招聘：{len(zhilian_jobs)} 个职位")
    
    if len(boss_jobs) > 0:
        print(f"\n[OK] BOSS 直聘测试成功！")
    else:
        print(f"\n[WARN] BOSS 直聘返回空数据（可能是模拟数据）")
    
    if len(zhilian_jobs) > 0:
        print(f"[OK] 智联招聘测试成功！")
    else:
        print(f"[WARN] 智联招聘返回空数据")

if __name__ == "__main__":
    asyncio.run(main())
