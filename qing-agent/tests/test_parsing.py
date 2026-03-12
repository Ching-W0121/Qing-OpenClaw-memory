"""
测试真实页面解析
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qing_platform.zhilian_adapter import ZhilianAdapter

# 模拟真实页面快照数据（基于浏览器获取的结构）
MOCK_SNAPSHOT = {
    "elements": [
        {
            "type": "listitem",
            "children": [
                {"type": "link", "text": "市场营销主管", "url": "http://www.zhaopin.com/jobdetail/xxx1.htm"},
                {"type": "paragraph", "text": "1.5-2.5 万"},
                {"type": "generic", "text": "市场营销"},
                {"type": "generic", "text": "市场调研"},
                {"type": "generic", "text": "市场运营"},
                {"type": "text", "text": "深圳·罗湖·东晓"},
                {"type": "generic", "text": "5-10 年"},
                {"type": "generic", "text": "本科"},
                {"type": "link", "text": "深圳合聚新国际物流有限公司", "url": "http://www.zhaopin.com/companydetail/xxx1.htm"},
            ]
        },
        {
            "type": "listitem",
            "children": [
                {"type": "link", "text": "品牌策划", "url": "http://www.zhaopin.com/jobdetail/xxx2.htm"},
                {"type": "paragraph", "text": "1.2-1.9 万"},
                {"type": "generic", "text": "新媒体媒介"},
                {"type": "generic", "text": "户外媒介"},
                {"type": "text", "text": "深圳·龙岗·宝龙"},
                {"type": "generic", "text": "3-5 年"},
                {"type": "generic", "text": "学历不限"},
                {"type": "link", "text": "深圳源谷科技有限公司", "url": "http://www.zhaopin.com/companydetail/xxx2.htm"},
            ]
        },
        {
            "type": "listitem",
            "children": [
                {"type": "link", "text": "养老活动策划岗", "url": "http://www.zhaopin.com/jobdetail/xxx3.htm"},
                {"type": "paragraph", "text": "8000-16000 元·13 薪"},
                {"type": "generic", "text": "氛围很好"},
                {"type": "generic", "text": "庆典活动"},
                {"type": "text", "text": "深圳·罗湖·笋岗"},
                {"type": "generic", "text": "3-5 年"},
                {"type": "generic", "text": "大专"},
                {"type": "link", "text": "深圳孝天下养老服务有限公司", "url": "http://www.zhaopin.com/companydetail/xxx3.htm"},
            ]
        },
        # 非职位项（应该被过滤）
        {
            "type": "listitem",
            "children": [
                {"type": "link", "text": "上一页", "url": "#"},
            ]
        },
        {
            "type": "listitem",
            "children": [
                {"type": "link", "text": "下一页", "url": "#"},
            ]
        },
    ]
}

def mock_find_element(parent, selectors):
    """模拟查找元素"""
    if 'children' not in parent:
        return None
    
    for selector in selectors:
        for child in parent['children']:
            if selector == 'link' and child['type'] == 'link':
                return child
            elif selector == 'paragraph' and child['type'] == 'paragraph':
                return child
            elif selector == 'generic' and child['type'] == 'generic':
                return child
            elif selector == 'text' and child['type'] == 'text':
                return child
    return None

def mock_find_all_elements(parent, selectors):
    """模拟查找所有元素"""
    if 'children' not in parent:
        return []
    
    results = []
    for selector in selectors:
        for child in parent['children']:
            if selector == 'link' and child['type'] == 'link':
                results.append(child)
            elif selector == 'paragraph' and child['type'] == 'paragraph':
                results.append(child)
            elif selector == 'generic' and child['type'] == 'generic':
                results.append(child)
            elif selector == 'text' and child['type'] == 'text':
                results.append(child)
    return results

def mock_get_text(el):
    """模拟获取文本"""
    return el.get('text', '')

def mock_get_url(el):
    """模拟获取 URL"""
    return el.get('url', '')

def test_parse_job_element():
    """测试单个职位解析"""
    print("\n" + "=" * 60)
    print("测试：解析单个职位元素")
    print("=" * 60)
    
    adapter = ZhilianAdapter()
    
    # 替换辅助方法为模拟版本
    adapter._find_element = mock_find_element
    adapter._find_all_elements = mock_find_all_elements
    adapter._get_text = mock_get_text
    adapter._get_url = mock_get_url
    
    # 测试第一个职位
    job_el = MOCK_SNAPSHOT["elements"][0]
    job = adapter._parse_job_element(job_el)
    
    print(f"\n解析结果：")
    print(f"  职位：{job.get('title')}")
    print(f"  公司：{job.get('company')}")
    print(f"  薪资：{job.get('salary')}")
    print(f"  地点：{job.get('city')} - {job.get('district')}")
    print(f"  经验：{job.get('experience')}")
    print(f"  学历：{job.get('education')}")
    print(f"  技能：{job.get('skills')}")
    print(f"  URL: {job.get('url')}")
    
    checks = [
        (job.get('title') == '市场营销主管', "职位名称正确"),
        (job.get('salary') == '1.5-2.5 万', "薪资正确"),
        (job.get('city') == '深圳', "城市正确"),
        (job.get('district') == '罗湖', "区域正确"),
        (job.get('experience') == '5-10 年', "经验正确"),
        (job.get('education') == '本科', "学历正确"),
        (len(job.get('skills', [])) > 0, "有技能标签"),
    ]
    
    passed = sum(1 for check, _ in checks if check)
    print(f"\n检查项：{passed}/{len(checks)}")
    for check, desc in checks:
        status = "[OK]" if check else "[FAIL]"
        print(f"  {status} {desc}")
    
    return passed == len(checks)

def test_is_valid_job():
    """测试职位有效性检查"""
    print("\n" + "=" * 60)
    print("测试：职位有效性检查")
    print("=" * 60)
    
    adapter = ZhilianAdapter()
    
    test_cases = [
        ({"title": "市场营销主管"}, True, "正常职位"),
        ({"title": "品牌策划"}, True, "正常职位 2"),
        ({"title": "上一页"}, False, "分页链接"),
        ({"title": "下一页"}, False, "分页链接 2"),
        ({"title": "简历置顶"}, False, "广告"),
        ({"title": ""}, False, "空标题"),
    ]
    
    passed = 0
    for job, expected, desc in test_cases:
        result = adapter._is_valid_job(job)
        match = result == expected
        status = "[OK]" if match else "[FAIL]"
        print(f"  {status} {desc}: {result} (期望：{expected})")
        if match:
            passed += 1
    
    print(f"\n通过率：{passed}/{len(test_cases)}")
    return passed == len(test_cases)

def test_parse_search_results():
    """测试完整搜索结果解析"""
    print("\n" + "=" * 60)
    print("测试：解析搜索结果")
    print("=" * 60)
    
    adapter = ZhilianAdapter()
    
    # 替换辅助方法
    adapter._find_element = mock_find_element
    adapter._find_all_elements = mock_find_all_elements
    adapter._get_text = mock_get_text
    adapter._get_url = mock_get_url
    
    # 模拟快照
    snapshot = {"elements": MOCK_SNAPSHOT["elements"]}
    
    # 解析
    jobs = adapter.parse_search_results(snapshot, "品牌策划")
    
    print(f"\n解析到 {len(jobs)} 个有效职位")
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job.get('title')}")
        print(f"   公司：{job.get('company')}")
        print(f"   薪资：{job.get('salary')}")
        print(f"   地点：{job.get('city')} - {job.get('district')}")
    
    checks = [
        (len(jobs) >= 2, f"解析到至少 2 个职位（实际：{len(jobs)}）"),
        (jobs[0]['title'] == '市场营销主管', "第一个职位正确"),
        (jobs[1]['title'] == '品牌策划', "第二个职位正确"),
    ]
    
    passed = sum(1 for check, _ in checks if check)
    print(f"\n检查项：{passed}/{len(checks)}")
    for check, desc in checks:
        status = "[OK]" if check else "[FAIL]"
        print(f"  {status} {desc}")
    
    return passed == len(checks)

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("求职 Agent · 真实页面解析测试")
    print("=" * 60)
    
    tests = [
        ("职位有效性检查", test_is_valid_job),
        ("单个职位解析", test_parse_job_element),
        ("搜索结果解析", test_parse_search_results),
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
    success = main()
    sys.exit(0 if success else 1)
