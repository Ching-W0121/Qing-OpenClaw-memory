"""
阶段 4 测试 - API 路由测试
"""

import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def wait_for_server(timeout=10):
    """等待服务器启动"""
    print("等待服务器启动...")
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=2)
            if resp.status_code == 200:
                print("服务器已就绪\n")
                return True
        except:
            pass
        time.sleep(0.5)
    
    print(f"服务器启动超时（{timeout}秒）\n")
    return False

def test_root():
    """测试根路径"""
    print("测试 1: 根路径")
    resp = requests.get(f"{BASE_URL}/")
    assert resp.status_code == 200
    data = resp.json()
    assert "求职 Agent API" in data["message"]
    print(f"  版本：{data['version']}")
    print(f"  端点：{list(data['endpoints'].keys())}\n")
    return True

def test_health():
    """测试健康检查"""
    print("测试 2: 健康检查")
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    print(f"  状态：{data['status']}")
    print(f"  版本：{data['version']}")
    print(f"  组件：{data['components']}\n")
    return True

def test_create_user():
    """测试创建用户"""
    print("测试 3: 创建用户")
    
    user_data = {
        "industry": "广告",
        "skills": ["品牌策划", "营销策划", "数据分析"],
        "tools": ["Office", "Photoshop"],
        "experience_years": 3,
        "education": "本科",
        "expected_city": "深圳",
        "expected_salary_min": 12000,
        "expected_salary_max": 18000,
    }
    
    resp = requests.post(f"{BASE_URL}/api/users/", json=user_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    
    user_id = data["user_id"]
    print(f"  用户 ID: {user_id}")
    print(f"  行业：{data['profile']['industry']}")
    print(f"  技能：{data['profile']['skills']}\n")
    
    return user_id

def test_get_user(user_id):
    """测试获取用户"""
    print("测试 4: 获取用户")
    
    resp = requests.get(f"{BASE_URL}/api/users/{user_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == user_id
    print(f"  用户 ID: {data['user_id']}")
    print(f"  行业：{data['profile']['industry']}\n")
    
    return True

def test_search_jobs():
    """测试搜索职位"""
    print("测试 5: 搜索职位")
    
    search_data = {
        "keyword": "品牌策划",
        "city": "深圳",
        "page": 1,
    }
    
    resp = requests.post(f"{BASE_URL}/api/jobs/search", json=search_data)
    assert resp.status_code == 200
    data = resp.json()
    
    print(f"  关键词：{data['keyword']}")
    print(f"  城市：{data['city']}")
    print(f"  数量：{data['count']}\n")
    
    return True

def test_calculate_match():
    """测试匹配计算"""
    print("测试 6: 匹配计算")
    
    match_data = {
        "user": {
            "industry": "广告",
            "skills": ["品牌策划", "营销策划", "数据分析"],
            "tools": ["Office", "Photoshop"],
            "experience_years": 3,
            "education": "本科",
            "expected_city": "深圳",
            "expected_salary_min": 12000,
            "expected_salary_max": 18000,
        },
        "jobs": [
            {
                "id": "job_001",
                "title": "高级品牌策划",
                "company": "某某广告公司",
                "industry": "广告",
                "skills": ["品牌策划", "营销策划"],
                "tools": ["Office", "Photoshop"],
                "experience": "3-5 年",
                "education": "本科",
                "city": "深圳",
                "salary_min": 15000,
                "salary_max": 25000,
            },
            {
                "id": "job_002",
                "title": "营销策划主管",
                "company": "某某互联网公司",
                "industry": "互联网",
                "skills": ["营销策划", "数据分析"],
                "tools": ["Office", "Excel"],
                "experience": "5-10 年",
                "education": "本科",
                "city": "深圳",
                "salary_min": 18000,
                "salary_max": 30000,
            },
        ],
    }
    
    resp = requests.post(f"{BASE_URL}/api/matches/calculate", json=match_data)
    assert resp.status_code == 200
    data = resp.json()
    
    print(f"  匹配数量：{data['count']}")
    for match in data["matches"]:
        print(f"  - {match['job_title']} ({match['company']}): {match['match_rate']:.1f}% - {match['level']}")
    print()
    
    return True

def test_get_recommendations(user_id):
    """测试推荐获取"""
    print("测试 7: 获取推荐")
    
    resp = requests.get(f"{BASE_URL}/api/matches/recommend/{user_id}?top_n=5")
    assert resp.status_code == 200
    data = resp.json()
    
    print(f"  用户 ID: {data['user_id']}")
    print(f"  推荐数量：{data['top_n']}")
    for rec in data["recommendations"]:
        print(f"  - {rec['title']} ({rec['company']}): {rec['match_rate']:.1f}%")
    print()
    
    return True

def test_submit_application(user_id):
    """测试投递提交"""
    print("测试 8: 提交投递")
    
    app_data = {
        "job_id": "job_001",
        "user_id": user_id,
        "resume_url": "https://example.com/resume.pdf",
    }
    
    resp = requests.post(f"{BASE_URL}/api/applications/submit", json=app_data)
    assert resp.status_code == 200
    data = resp.json()
    
    print(f"  投递 ID: {data['application_id']}")
    print(f"  职位 ID: {data['job_id']}")
    print(f"  状态：{data['status']}\n")
    
    return True

def test_get_applications(user_id):
    """测试获取投递记录"""
    print("测试 9: 获取投递记录")
    
    resp = requests.get(f"{BASE_URL}/api/applications/{user_id}")
    assert resp.status_code == 200
    data = resp.json()
    
    print(f"  用户 ID: {data['user_id']}")
    print(f"  投递数量：{data['count']}")
    for app in data["applications"]:
        print(f"  - {app['job_id']}: {app['status']}")
    print()
    
    return True

def test_protection():
    """测试防封禁组件"""
    print("测试 10: 防封禁组件")
    
    resp = requests.get(f"{BASE_URL}/api/test/protection")
    assert resp.status_code == 200
    data = resp.json()
    
    print(f"  熔断器：{data['circuit_breaker']['state']}")
    print(f"  限流器：搜索剩余 {data['limiter']['search']['remaining']} 次")
    print(f"  会话：{data['session_manager']['visit_count']} 次访问\n")
    
    return True

def main():
    """运行所有 API 测试"""
    print("=" * 60)
    print("求职 Agent v1.2 · 阶段 4 测试（API 路由）")
    print("=" * 60)
    print()
    
    # 等待服务器
    if not wait_for_server():
        print("\n[ERROR] 服务器未启动，请先运行：python main.py")
        return False
    
    tests = [
        ("根路径", test_root),
        ("健康检查", test_health),
        ("创建用户", test_create_user),
    ]
    
    results = []
    user_id = None
    
    # 运行前置测试
    for name, test_func in tests[:2]:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"[ERROR] {name} 测试失败：{e}\n")
            results.append((name, False))
    
    # 创建用户并获取 ID
    try:
        user_id = test_create_user()
        results.append(("创建用户", True))
    except Exception as e:
        print(f"[ERROR] 创建用户测试失败：{e}\n")
        results.append(("创建用户", False))
    
    # 使用 user_id 的测试
    if user_id:
        user_tests = [
            ("获取用户", lambda: test_get_user(user_id)),
            ("搜索职位", test_search_jobs),
            ("匹配计算", test_calculate_match),
            ("获取推荐", lambda: test_get_recommendations(user_id)),
            ("提交投递", lambda: test_submit_application(user_id)),
            ("获取投递记录", lambda: test_get_applications(user_id)),
            ("防封禁组件", test_protection),
        ]
        
        for name, test_func in user_tests:
            try:
                passed = test_func()
                results.append((name, passed))
            except Exception as e:
                print(f"[ERROR] {name} 测试失败：{e}\n")
                results.append((name, False))
    
    # 汇总结果
    print("=" * 60)
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
