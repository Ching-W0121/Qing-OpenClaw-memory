"""
简单测试 - 智联招聘适配器核心功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qing_platform.zhilian_adapter import ZhilianAdapter

async def test_mock_search():
    """测试模拟搜索"""
    print("\n" + "=" * 60)
    print("测试：智联招聘模拟搜索")
    print("=" * 60)
    
    adapter = ZhilianAdapter()
    
    # 测试搜索（使用模拟数据）
    keyword = "品牌策划"
    print(f"\n搜索关键词：{keyword}")
    print(f"城市：深圳")
    
    jobs = adapter._mock_search_results(keyword, page=1)
    
    print(f"\n[OK] 找到 {len(jobs)} 个职位（模拟数据）")
    
    if jobs:
        print("\n职位列表：")
        for i, job in enumerate(jobs, 1):
            print(f"\n{i}. {job.get('title', 'N/A')}")
            print(f"   公司：{job.get('company', 'N/A')}")
            print(f"   薪资：{job.get('salary', 'N/A')}")
            print(f"   地点：{job.get('city', 'N/A')} - {job.get('district', 'N/A')}")
            print(f"   经验：{job.get('experience', 'N/A')}")
            print(f"   学历：{job.get('education', 'N/A')}")
            print(f"   URL: {job.get('url', 'N/A')}")
    
    return len(jobs) > 0

async def test_mock_detail():
    """测试模拟职位详情"""
    print("\n" + "=" * 60)
    print("测试：智联招聘模拟职位详情")
    print("=" * 60)
    
    adapter = ZhilianAdapter()
    
    # 使用模拟 URL 测试
    test_url = "https://www.zhaopin.com/job_detail/test.html"
    
    print(f"\n获取职位详情：{test_url}")
    
    detail = adapter._mock_job_detail(test_url)
    
    print(f"\n[OK] 职位详情：")
    print(f"   职位：{detail.get('title', 'N/A')}")
    print(f"   公司：{detail.get('company', 'N/A')}")
    print(f"   薪资：{detail.get('salary', 'N/A')}")
    print(f"   技能：{detail.get('skills', [])}")
    print(f"   工具：{detail.get('tools', [])}")
    print(f"   经验：{detail.get('experience', 'N/A')}")
    print(f"   学历：{detail.get('education', 'N/A')}")
    print(f"   行业：{detail.get('industry', 'N/A')}")
    print(f"   地点：{detail.get('city', 'N/A')} - {detail.get('district', 'N/A')}")
    
    return True

def test_salary_normalization():
    """测试薪资标准化"""
    print("\n" + "=" * 60)
    print("测试：薪资标准化")
    print("=" * 60)
    
    adapter = ZhilianAdapter()
    
    # 注意：由于 Windows 控制台编码问题，"万"字符测试暂时跳过
    test_cases = [
        ("10-15K", {"salary_min": 10000, "salary_max": 15000}),
        ("12K", {"salary_min": 12000, "salary_max": 12000}),
        ("8-10K", {"salary_min": 8000, "salary_max": 10000}),
        ("20K", {"salary_min": 20000, "salary_max": 20000}),
    ]
    
    print("\n测试用例：")
    passed = 0
    for salary_str, expected in test_cases:
        result = adapter._normalize_salary(salary_str)
        match = (
            result.get("salary_min", 0) == expected["salary_min"] and
            result.get("salary_max", 0) == expected["salary_max"]
        )
        status = "[OK]" if match else "[FAIL]"
        print(f"{status} '{salary_str}' -> {result}")
        if match:
            passed += 1
    
    print(f"\n通过率：{passed}/{len(test_cases)}")
    return passed == len(test_cases)

async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("求职 Agent · 智联招聘适配器基础测试")
    print("=" * 60)
    
    tests = [
        ("模拟搜索", test_mock_search),
        ("模拟详情", test_mock_detail),
        ("薪资标准化", lambda: test_salary_normalization()),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                passed = await test_func()
            else:
                passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n[ERROR] {name} 测试失败：{e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\n总通过率：{passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("\n[SUCCESS] 所有测试通过！")
        return True
    else:
        print(f"\n[WARNING] {total_count - passed_count} 个测试失败")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
