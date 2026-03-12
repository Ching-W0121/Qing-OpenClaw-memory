"""
测试真实智联招聘网站（不登录）
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qing_platform.zhilian_adapter import ZhilianAdapter

async def test_real_search():
    """测试真实搜索（需要浏览器）"""
    print("\n" + "=" * 60)
    print("测试：真实智联招聘搜索")
    print("=" * 60)
    
    adapter = ZhilianAdapter()
    
    # 测试搜索
    keyword = "品牌策划"
    city = "深圳"
    
    print(f"\n搜索关键词：{keyword}")
    print(f"城市：{city}")
    print(f"最大重试：{adapter.max_retry}")
    print(f"超时时间：{adapter.timeout_seconds}s")
    print(f"熔断阈值：{adapter.circuit_breaker_threshold}")
    
    print("\n开始搜索...")
    jobs = await adapter.search_jobs(keyword, city=city, page=1)
    
    print(f"\n返回 {len(jobs)} 个职位")
    
    if jobs:
        print("\n前 3 个职位：")
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{i}. {job.get('title', 'N/A')}")
            print(f"   公司：{job.get('company', 'N/A')}")
            print(f"   薪资：{job.get('salary', 'N/A')}")
            print(f"   地点：{job.get('city', 'N/A')} - {job.get('district', 'N/A')}")
            print(f"   URL: {job.get('url', 'N/A')[:80]}...")
    
    return len(jobs) > 0

async def main():
    """主测试"""
    print("\n" + "=" * 60)
    print("求职 Agent · 真实智联招聘测试")
    print("=" * 60)
    
    try:
        passed = await test_real_search()
        
        print("\n" + "=" * 60)
        print("测试结果")
        print("=" * 60)
        
        if passed:
            print("\n[SUCCESS] 真实搜索测试通过！")
            return True
        else:
            print("\n[WARNING] 真实搜索测试失败")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] 测试异常：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
