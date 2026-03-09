"""
集成测试 - 测试 Pipeline 完整流程
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.industry_matcher import IndustryMatcher
from tools.matcher import MatchingEngine
from tools.jd_parser import JDParser
from tools.recommender import Recommender
from agent.planner import Planner

def test_industry_matcher():
    """测试行业匹配器"""
    print("\n" + "=" * 60)
    print("测试 1: 行业匹配器")
    print("=" * 60)
    
    matcher = IndustryMatcher()
    
    test_cases = [
        ("广告", "广告", 1.0, "完全相同"),
        ("广告", "品牌咨询", 0.8, "父子关系"),
        ("品牌咨询", "营销策划", 0.6, "同级关系"),
        ("广告", "电商", 0.3, "弱相关"),
        ("广告", "金融", 0.2, "无关"),
    ]
    
    passed = 0
    for user_ind, job_ind, expected, desc in test_cases:
        result = matcher.match(user_ind, job_ind)
        status = "[OK]" if abs(result - expected) < 0.01 else "[FAIL]"
        if abs(result - expected) < 0.01:
            passed += 1
        print(f"{status} {user_ind} → {job_ind} ({desc}): {result} (期望：{expected})")
    
    print(f"\n通过率：{passed}/{len(test_cases)}")
    return passed == len(test_cases)

def test_matching_engine():
    """测试匹配引擎"""
    print("\n" + "=" * 60)
    print("测试 2: 匹配引擎（7 维）")
    print("=" * 60)
    
    engine = MatchingEngine()
    
    # 测试用户画像
    user = {
        "industry": "广告",
        "skills": ["品牌策划", "文案写作", "营销策划"],
        "tools": ["Photoshop", "Office"],
        "experience_years": 3,
        "education": "本科",
        "expected_city": "深圳",
        "expected_salary_min": 10000,
        "expected_salary_max": 15000,
    }
    
    # 测试职位画像（高匹配）
    job_high = {
        "industry": "广告",
        "skills": ["品牌策划", "营销策划", "文案写作"],
        "tools": ["Photoshop"],
        "experience": "3-5 年",
        "education": "本科",
        "city": "深圳",
        "salary_min": 12000,
        "salary_max": 18000,
    }
    
    # 测试职位画像（低匹配）
    job_low = {
        "industry": "金融",
        "skills": ["数据分析", "SQL", "Python"],
        "tools": ["Excel"],
        "experience": "5-10 年",
        "education": "硕士",
        "city": "北京",
        "salary_min": 20000,
        "salary_max": 30000,
    }
    
    result_high = engine.calculate_match(user, job_high)
    result_low = engine.calculate_match(user, job_low)
    
    print(f"高匹配职位：{result_high['total']*100:.1f}%")
    print(f"  等级：{engine.get_match_level(result_high['total'])}")
    print(f"低匹配职位：{result_low['total']*100:.1f}%")
    print(f"  等级：{engine.get_match_level(result_low['total'])}")
    
    # 验证：高匹配应该 > 低匹配
    passed = result_high['total'] > result_low['total']
    print(f"\n验证：高匹配 > 低匹配 {'[OK]' if passed else '[FAIL]'}")
    
    return passed

def test_jd_parser():
    """测试 JD 解析器"""
    print("\n" + "=" * 60)
    print("测试 3: JD 解析器")
    print("=" * 60)
    
    parser = JDParser()
    
    test_jd = """
    职位：品牌策划经理
    薪资：12-18K·13 薪
    
    岗位职责：
    1. 负责品牌策划和推广工作
    2. 撰写文案和创意内容
    3. 策划和执行营销活动
    4. 数据分析与市场调研
    
    任职要求：
    1. 本科及以上学历，3-5 年相关工作经验
    2. 精通 Office 软件，熟练使用 Photoshop
    3. 具备良好的沟通表达能力和团队协作精神
    4. 有广告或互联网行业经验者优先
    
    公司规模：100-500 人，B 轮融资
    """
    
    result = parser.parse(test_jd)
    
    print(f"技能：{result['skills']}")
    print(f"工具：{result['tools']}")
    print(f"经验：{result['experience']}")
    print(f"学历：{result['education']}")
    print(f"行业：{result['industry']}")
    print(f"薪资：{result['salary']}")
    
    # 验证关键信息提取
    checks = [
        ("品牌策划" in result['skills'], "技能提取"),
        ("Office" in result['tools'], "工具提取"),
        ("3-5 年" in result['experience'], "经验提取"),
        ("本科" in result['education'], "学历提取"),
        ("广告" in result['industry'], "行业提取"),
        ("12-18K" in result['salary'], "薪资提取"),
    ]
    
    passed = sum(1 for check, _ in checks if check)
    print(f"\n通过率：{passed}/{len(checks)}")
    
    for check, name in checks:
        print(f"  {'[OK]' if check else '[FAIL]'} {name}")
    
    return passed == len(checks)

def test_planner():
    """测试 Agent 规划器"""
    print("\n" + "=" * 60)
    print("测试 4: Agent 规划器")
    print("=" * 60)
    
    planner = Planner()
    
    test_cases = [
        ("我想找工作", "find_job"),
        ("帮我推荐职位", "find_job"),
        ("我要投递这个职位", "apply"),
        ("分析一下市场趋势", "analyze_market"),
        ("随便说说", "find_job"),  # 默认
    ]
    
    passed = 0
    for input_text, expected_intent in test_cases:
        result = planner.analyze_intent(input_text)
        status = "[OK]" if result == expected_intent else "[FAIL]"
        if result == expected_intent:
            passed += 1
        print(f"{status} '{input_text}' → {result} (期望：{expected_intent})")
    
    print(f"\n通过率：{passed}/{len(test_cases)}")
    return passed == len(test_cases)

def test_recommender():
    """测试推荐引擎"""
    print("\n" + "=" * 60)
    print("测试 5: 推荐引擎")
    print("=" * 60)
    
    recommender = Recommender()
    
    # 模拟匹配结果
    matches = [
        {"job": {"title": "职位 A"}, "match": {"total": 0.85}},
        {"job": {"title": "职位 B"}, "match": {"total": 0.65}},
        {"job": {"title": "职位 C"}, "match": {"total": 0.92}},
        {"job": {"title": "职位 D"}, "match": {"total": 0.78}},
    ]
    
    # 测试排序
    ranked = recommender.rank(matches, top_n=3)
    
    print("排序结果（Top 3）：")
    for i, item in enumerate(ranked, 1):
        print(f"  {i}. {item['job']['title']}: {item['match']['total']*100:.1f}%")
    
    # 验证：应该是降序
    passed = all(
        ranked[i]['match']['total'] >= ranked[i+1]['match']['total']
        for i in range(len(ranked)-1)
    )
    
    print(f"\n验证：降序排列 {'[OK]' if passed else '[FAIL]'}")
    print(f"数量：{len(ranked)} (期望：3)")
    
    return passed and len(ranked) == 3

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("求职 Agent v1.1 · 集成测试")
    print("=" * 60)
    
    tests = [
        ("行业匹配器", test_industry_matcher),
        ("匹配引擎", test_matching_engine),
        ("JD 解析器", test_jd_parser),
        ("Agent 规划器", test_planner),
        ("推荐引擎", test_recommender),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n[ERROR] {name} 测试失败：{e}")
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
    success = main()
    sys.exit(0 if success else 1)
