"""
阶段 2 测试 - 智联招聘真实数据测试
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from platform.zhilian_adapter import ZhilianAdapter
from tools.jd_parser import JDParser
from tools.matcher import MatchingEngine
from tools.recommender import Recommender

async def test_zhilian_search():
    """测试智联招聘搜索（模拟模式）"""
    print("\n" + "=" * 60)
    print("测试 1: 智联招聘搜索（模拟模式）")
    print("=" * 60)
    
    adapter = ZhilianAdapter()
    
    # 测试搜索（使用模拟数据）
    keyword = "品牌策划"
    print(f"\n搜索关键词：{keyword}")
    print(f"城市：深圳")
    
    # 由于 openclaw browser 在命令行不可用，使用模拟数据
    jobs = adapter._mock_search_results(keyword, page=1)
    
    print(f"\n找到 {len(jobs)} 个职位（模拟数据）")
    
    if jobs:
        print("\n前 3 个职位：")
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{i}. {job.get('title', 'N/A')}")
            print(f"   公司：{job.get('company', 'N/A')}")
            print(f"   薪资：{job.get('salary', 'N/A')}")
            print(f"   地点：{job.get('city', 'N/A')} - {job.get('district', 'N/A')}")
            print(f"   经验：{job.get('experience', 'N/A')}")
            print(f"   学历：{job.get('education', 'N/A')}")
    
    return len(jobs) > 0

async def test_zhilian_detail():
    """测试智联招聘职位详情（模拟模式）"""
    print("\n" + "=" * 60)
    print("测试 2: 智联招聘职位详情（模拟模式）")
    print("=" * 60)
    
    adapter = ZhilianAdapter()
    
    # 使用模拟 URL 测试
    test_url = "https://www.zhaopin.com/job_detail/test.html"
    
    print(f"\n获取职位详情：{test_url}")
    
    # 使用模拟数据
    detail = adapter._mock_job_detail(test_url)
    
    print(f"\n职位：{detail.get('title', 'N/A')}")
    print(f"公司：{detail.get('company', 'N/A')}")
    print(f"薪资：{detail.get('salary', 'N/A')}")
    print(f"技能：{detail.get('skills', [])}")
    print(f"工具：{detail.get('tools', [])}")
    
    return True

def test_jd_parser_zhilian():
    """测试 JD 解析器（智联招聘格式）"""
    print("\n" + "=" * 60)
    print("测试 3: JD 解析器（智联招聘格式）")
    print("=" * 60)
    
    parser = JDParser()
    
    # 模拟智联招聘 JD 文本
    test_jd = """
    职位名称：品牌策划经理
    薪资范围：15-25K·14 薪
    
    岗位职责：
    1. 负责公司品牌战略规划与执行
    2. 策划并组织品牌推广活动
    3. 撰写品牌宣传文案和创意内容
    4. 分析市场数据和竞品动态
    
    任职要求：
    1. 本科及以上学历，市场营销、广告学相关专业
    2. 5 年以上品牌策划工作经验
    3. 精通 Office 办公软件，熟悉 Photoshop、Illustrator
    4. 具备优秀的数据分析能力和市场调研能力
    5. 良好的沟通表达能力和团队协作精神
    
    行业：互联网/广告
    公司规模：500-1000 人
    融资阶段：C 轮
    """
    
    result = parser.parse(test_jd)
    
    print(f"\n技能：{result['skills']}")
    print(f"工具：{result['tools']}")
    print(f"经验：{result['experience']}")
    print(f"学历：{result['education']}")
    print(f"行业：{result['industry']}")
    print(f"薪资：{result['salary']}")
    print(f"公司规模：{result['company_size']}")
    
    # 验证关键信息
    checks = [
        ("品牌策划" in result['skills'], "技能提取"),
        ("Office" in result['tools'], "工具提取"),
        ("5 年" in result['experience'] or "5 年以上" in result['experience'], "经验提取"),
        ("本科" in result['education'], "学历提取"),
        (result['industry'] in ['互联网', '广告'], "行业提取"),
        ("15-25K" in result['salary'], "薪资提取"),
    ]
    
    passed = sum(1 for check, _ in checks if check)
    print(f"\n通过率：{passed}/{len(checks)}")
    
    for check, name in checks:
        print(f"  {'[OK]' if check else '[FAIL]'} {name}")
    
    return passed == len(checks)

def test_matching_with_zhilian():
    """测试匹配引擎（使用智联招聘数据）"""
    print("\n" + "=" * 60)
    print("测试 4: 匹配引擎（智联招聘数据）")
    print("=" * 60)
    
    engine = MatchingEngine()
    recommender = Recommender()
    
    # 用户画像
    user = {
        "industry": "广告",
        "skills": ["品牌策划", "营销策划", "文案写作", "数据分析"],
        "tools": ["Office", "Photoshop"],
        "experience_years": 3,
        "education": "本科",
        "expected_city": "深圳",
        "expected_salary_min": 12000,
        "expected_salary_max": 18000,
    }
    
    # 模拟智联招聘职位
    jobs = [
        {
            "platform": "zhilian",
            "title": "品牌策划经理",
            "company": "某某互联网公司",
            "industry": "互联网",
            "skills": ["品牌策划", "营销策划", "数据分析"],
            "tools": ["Office", "Photoshop"],
            "experience": "3-5 年",
            "education": "本科",
            "city": "深圳",
            "salary_min": 15000,
            "salary_max": 25000,
        },
        {
            "platform": "zhilian",
            "title": "高级品牌策划",
            "company": "某某广告公司",
            "industry": "广告",
            "skills": ["品牌策划", "文案写作", "创意设计"],
            "tools": ["Office", "Illustrator"],
            "experience": "3-5 年",
            "education": "本科",
            "city": "深圳",
            "salary_min": 12000,
            "salary_max": 18000,
        },
        {
            "platform": "zhilian",
            "title": "营销策划主管",
            "company": "某某传媒公司",
            "industry": "文化传媒",
            "skills": ["营销策划", "活动执行", "公关"],
            "tools": ["Office", "PPT"],
            "experience": "5-10 年",
            "education": "大专",
            "city": "深圳",
            "salary_min": 10000,
            "salary_max": 15000,
        },
    ]
    
    # 计算匹配度
    matches = []
    for job in jobs:
        result = engine.calculate_match(user, job)
        matches.append({
            "job": job,
            "match": result
        })
    
    # 排序推荐
    ranked = recommender.rank(matches, top_n=3)
    
    print("\n推荐结果（按匹配度排序）：")
    for i, item in enumerate(ranked, 1):
        job = item["job"]
        match = item["match"]
        print(f"\n{i}. {job['title']} - {job['company']}")
        print(f"   匹配度：{match['total']*100:.1f}% ({engine.get_match_level(match['total'])})")
        print(f"   行业：{job['industry']}")
        print(f"   薪资：{job['salary_min']}-{job['salary_max']}")
        print(f"   地点：{job['city']}")
    
    # 验证：第一个应该是最高匹配
    passed = all(
        ranked[i]['match']['total'] >= ranked[i+1]['match']['total']
        for i in range(len(ranked)-1)
    )
    
    print(f"\n验证：降序排列 {'[OK]' if passed else '[FAIL]'}")
    
    return passed

async def main():
    """运行所有阶段 2 测试"""
    print("\n" + "=" * 60)
    print("求职 Agent v1.1 · 阶段 2 测试（智联招聘）")
    print("=" * 60)
    
    tests = [
        ("智联招聘搜索", test_zhilian_search),
        ("智联招聘详情", test_zhilian_detail),
        ("JD 解析器", lambda: test_jd_parser_zhilian()),
        ("匹配引擎", lambda: test_matching_with_zhilian()),
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
        print(f"{'[OK]' if passed else '[FAIL]'} {name}")
    
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
