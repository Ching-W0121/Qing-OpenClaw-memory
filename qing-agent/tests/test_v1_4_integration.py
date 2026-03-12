"""
v1.4 集成测试
测试：去重 + 评分 + 推送
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.deduplication import deduplicate_jobs
from tools.scorer import score_jobs
from tools.push_notifier import PushNotifier

def test_deduplication():
    """测试职位去重"""
    print("\n" + "="*60)
    print("测试 1: 职位去重")
    print("="*60)
    
    # 模拟数据（含重复）
    jobs = [
        {'title': '品牌策划', 'company': '深圳源谷科技', 'city': '深圳', 'district': '龙岗'},
        {'title': '品牌策划', 'company': '深圳源谷科技', 'city': '深圳', 'district': '龙岗'},  # 重复
        {'title': '品牌文案策划', 'company': '深圳冰燃传媒', 'city': '深圳', 'district': '龙岗'},
        {'title': '内容策划', 'company': '华润雪花', 'city': '深圳', 'district': '宝安'},
        {'title': '内容策划', 'company': '华润雪花', 'city': '深圳', 'district': '宝安'},  # 重复
    ]
    
    print(f"\n原始数据：{len(jobs)} 个职位")
    
    # 去重
    unique_jobs = deduplicate_jobs(jobs)
    
    print(f"去重后：{len(unique_jobs)} 个职位")
    
    # 验证
    expected = 3
    passed = len(unique_jobs) == expected
    
    print(f"\n期望：{expected} 个，实际：{len(unique_jobs)} 个")
    print(f"结果：{'[OK]' if passed else '[FAIL]'}")
    
    return passed

def test_scoring():
    """测试职位评分"""
    print("\n" + "="*60)
    print("测试 2: 职位评分")
    print("="*60)
    
    # 用户画像
    user_profile = {
        'target_jobs': ['品牌策划', '品牌宣传', '活动策划'],
        'expected_city': '深圳',
        'expected_salary_min': 8000,
        'expected_salary_max': 15000,
        'experience_years': 3,
        'education': '本科',
    }
    
    # 职位数据
    jobs = [
        {
            'title': '品牌策划',
            'company': '深圳源谷科技',
            'city': '深圳',
            'district': '龙岗',
            'salary': '1.2-1.9 万',
            'salary_min': 12000,
            'salary_max': 19000,
        },
        {
            'title': '内容策划',
            'company': '华润雪花',
            'city': '深圳',
            'district': '宝安',
            'salary': '1.5-2 万',
            'salary_min': 15000,
            'salary_max': 20000,
        },
    ]
    
    print(f"\n用户画像：")
    print(f"  期望职位：{user_profile['target_jobs']}")
    print(f"  期望城市：{user_profile['expected_city']}")
    print(f"  期望薪资：{user_profile['expected_salary_min']}-{user_profile['expected_salary_max']}")
    
    # 评分
    scored_jobs = score_jobs(user_profile, jobs)
    
    print(f"\n评分结果：")
    for i, job in enumerate(scored_jobs, 1):
        score = job['total_score'] * 100
        print(f"\n{i}. {job['title']}")
        print(f"   总分：{score:.1f}")
        print(f"   匹配度：{job['score_detail']['match_score']*100:.1f}")
        print(f"   薪资：{job['score_detail']['salary_score']*100:.1f}")
        print(f"   城市：{job['score_detail']['city_score']*100:.1f}")
    
    # 验证
    passed = all('total_score' in job for job in scored_jobs)
    print(f"\n结果：{'[OK]' if passed else '[FAIL]'}")
    
    return passed

def test_push_report():
    """测试推送报告"""
    print("\n" + "="*60)
    print("测试 3: 推送报告")
    print("="*60)
    
    notifier = PushNotifier()
    
    # 模拟已评分职位
    jobs = [
        {
            'title': '品牌策划',
            'company': '深圳源谷科技',
            'city': '深圳',
            'district': '龙岗',
            'salary': '1.2-1.9 万',
            'salary_min': 12000,
            'salary_max': 19000,
            'total_score': 0.85,
            'hr_status': '刚刚活跃',
        },
        {
            'title': '内容策划',
            'company': '华润雪花',
            'city': '深圳',
            'district': '宝安',
            'salary': '1.5-2 万·13 薪',
            'salary_min': 15000,
            'salary_max': 20000,
            'total_score': 0.78,
            'hr_status': '6 小时内回复',
        },
        {
            'title': '品牌文案策划',
            'company': '深圳冰燃传媒',
            'city': '深圳',
            'district': '龙岗',
            'salary': '1-1.5 万',
            'salary_min': 10000,
            'salary_max': 15000,
            'total_score': 0.72,
            'hr_status': '3 日内活跃',
        },
    ]
    
    # 生成报告
    report = notifier.create_daily_report(jobs, top_n=3)
    
    print(f"\n报告生成：")
    print(f"  日期：{report['date']}")
    print(f"  总职位数：{report['total_jobs']}")
    print(f"  推荐数：{report['top_n']}")
    print(f"  平均薪资：{report['summary']['avg_salary']}")
    print(f"  热门区域：{report['summary']['city_distribution']}")
    
    # 格式化消息
    message = notifier.format_push_message(report, platform='feishu')
    
    print(f"\n推送消息预览：")
    print("-" * 60)
    print(message)
    print("-" * 60)
    
    # 验证
    passed = (
        len(report['recommendations']) == 3 and
        '平均薪资' in message and
        '匹配度' in message
    )
    print(f"\n结果：{'[OK]' if passed else '[FAIL]'}")
    
    return passed

def test_highlights():
    """测试亮点提取"""
    print("\n" + "="*60)
    print("测试 4: 亮点提取")
    print("="*60)
    
    notifier = PushNotifier()
    
    test_jobs = [
        {
            'title': '品牌策划',
            'salary_min': 15000,
            'total_score': 0.85,
            'experience': '1-3 年',
            'hr_status': '刚刚活跃',
        },
        {
            'title': '内容策划',
            'salary_min': 10000,
            'total_score': 0.72,
            'experience': '3-5 年',
            'education': '大专',
            'hr_status': '3 日内活跃',
        },
    ]
    
    print("\n亮点提取测试：")
    for i, job in enumerate(test_jobs, 1):
        highlights = notifier._extract_highlights(job)
        print(f"\n职位 {i}: {job['title']}")
        print(f"  亮点：{highlights}")
    
    # 验证
    job1_highlights = notifier._extract_highlights(test_jobs[0])
    job2_highlights = notifier._extract_highlights(test_jobs[1])
    
    passed = (
        '💰 高薪' in job1_highlights and
        '🎯 高匹配' in job1_highlights and
        '💬 HR 活跃' in job1_highlights and
        '🎓 学历友好' in job2_highlights
    )
    
    print(f"\n结果：{'[OK]' if passed else '[FAIL]'}")
    
    return passed

def main():
    """主测试"""
    print("\n" + "="*60)
    print("青·求职 Agent v1.4 集成测试")
    print("="*60)
    
    tests = [
        ("职位去重", test_deduplication),
        ("职位评分", test_scoring),
        ("推送报告", test_push_report),
        ("亮点提取", test_highlights),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n[ERROR] {name} 测试失败：{e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 汇总
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\n总通过率：{passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("\n[SUCCESS] v1.4 所有测试通过！")
        return True
    else:
        print(f"\n[WARNING] {total_count - passed_count} 个测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
