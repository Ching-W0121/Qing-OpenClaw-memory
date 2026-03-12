"""
测试职位详情页解析
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qing_platform.zhilian_adapter import ZhilianAdapter

# 模拟真实详情页快照数据
MOCK_DETAIL_SNAPSHOT = {
    "elements": [
        {"type": "heading", "level": 1, "text": "品牌策划"},
        {"type": "text", "text": "1.2-1.9 万"},
        {"type": "listitem", "text": "深圳-龙岗区"},
        {"type": "listitem", "text": "3-5 年"},
        {"type": "listitem", "text": "学历不限"},
        {"type": "listitem", "text": "全职"},
        {"type": "listitem", "text": "招 1 人"},
        {"type": "generic", "text": "新媒体媒介"},
        {"type": "generic", "text": "户外媒介"},
        {"type": "generic", "text": "海外媒介"},
        {"type": "generic", "text": "个人品牌"},
        {"type": "generic", "text": "海外品牌"},
        {"type": "text", "text": "1. 制定和执行品牌策略。"},
        {"type": "text", "text": "2. 设计品牌活动和推广方案。"},
        {"type": "text", "text": "3. 分析市场趋势，调整品牌定位。"},
        {"type": "text", "text": "4. 与设计团队合作完成品牌视觉识别系统。"},
        {"type": "text", "text": "5. 跟踪并评估品牌推广效果。"},
        {"type": "text", "text": "6. 持续优化品牌策略，保持与市场同步。"},
        {"type": "text", "text": "7. 配合其他部门实现品牌目标。"},
        {"type": "text", "text": "感兴趣联系我，欢迎加入我们的团队！"},
        {"type": "text", "text": "广东省深圳市龙岗区宝龙二路 3 号 5 号楼 12 层"},
        {"type": "button", "text": "电子设备制造，运营商/增值服务"},
        {"type": "button", "text": "20-99 人"},
        {"type": "heading", "level": 3, "text": "张丽芳/人事经理"},
        {"type": "generic", "text": "三日内活跃"},
        {"type": "link", "text": "深圳源谷科技有限公司"},
    ]
}

def mock_find_element(parent, selectors):
    """模拟查找元素"""
    if 'elements' not in parent:
        return None
    
    for selector in selectors:
        for el in parent['elements']:
            # heading[level=1]
            if selector == 'heading[level=1]' and el['type'] == 'heading' and el.get('level') == 1:
                return el
            # heading[level=3]
            elif selector == 'heading[level=3]' and el['type'] == 'heading' and el.get('level') == 3:
                return el
            # 通用类型匹配
            elif selector.startswith('heading') and el['type'] == 'heading':
                return el
            elif selector.startswith('text') and el['type'] == 'text':
                return el
            elif selector.startswith('listitem') and el['type'] == 'listitem':
                return el
            elif selector.startswith('generic') and el['type'] == 'generic':
                return el
            elif selector.startswith('button') and el['type'] == 'button':
                return el
            elif selector.startswith('link') and el['type'] == 'link':
                return el
    
    return None

def mock_find_all_elements(parent, selectors):
    """模拟查找所有元素"""
    if 'elements' not in parent:
        return []
    
    results = []
    for selector in selectors:
        for el in parent['elements']:
            if selector == 'text' and el['type'] == 'text':
                results.append(el)
            elif selector == 'listitem' and el['type'] == 'listitem':
                results.append(el)
            elif selector == 'generic' and el['type'] == 'generic':
                results.append(el)
            elif selector == 'button' and el['type'] == 'button':
                results.append(el)
            elif selector == 'heading' and el['type'] == 'heading':
                results.append(el)
            elif selector == 'link' and el['type'] == 'link':
                results.append(el)
    
    return results

def mock_get_text(el):
    """模拟获取文本"""
    return el.get('text', '')

def test_parse_job_detail():
    """测试职位详情解析"""
    print("\n" + "=" * 60)
    print("测试：解析职位详情")
    print("=" * 60)
    
    adapter = ZhilianAdapter()
    
    # 替换辅助方法
    adapter._find_element = mock_find_element
    adapter._find_all_elements = mock_find_all_elements
    adapter._get_text = mock_get_text
    
    # 解析
    snapshot = {"elements": MOCK_DETAIL_SNAPSHOT["elements"]}
    detail = adapter.parse_job_detail(snapshot)
    
    print(f"\n解析结果：")
    print(f"  职位：{detail.get('title')}")
    print(f"  公司：{detail.get('company')}")
    print(f"  薪资：{detail.get('salary')} ({detail.get('salary_min')}-{detail.get('salary_max')})")
    print(f"  地点：{detail.get('city')} - {detail.get('district')}")
    print(f"  经验：{detail.get('experience')}")
    print(f"  学历：{detail.get('education')}")
    print(f"  类型：{detail.get('job_type')}")
    print(f"  招聘：{detail.get('recruit_count')}")
    print(f"  行业：{detail.get('industry')}")
    print(f"  技能：{detail.get('skills')}")
    print(f"  HR: {detail.get('hr_name')} / {detail.get('hr_title')}")
    print(f"  HR 状态：{detail.get('hr_status')}")
    print(f"  详细地址：{detail.get('location')}")
    print(f"  描述：{len(detail.get('description', '').split(chr(10)))} 行")
    
    checks = [
        (detail.get('title') == '品牌策划', "职位名称正确"),
        (detail.get('salary') == '1.2-1.9 万', "薪资正确"),
        (detail.get('salary_min') > 0 and detail.get('salary_max') > 0, "薪资范围已解析"),
        (detail.get('city') == '深圳', "城市正确"),
        (detail.get('district') == '龙岗区', "区域正确"),
        (detail.get('experience') == '3-5 年', "经验正确"),
        (detail.get('education') == '学历不限', "学历正确"),
        (detail.get('job_type') == '全职', "工作类型正确"),
        (detail.get('recruit_count') == '招 1 人', "招聘人数正确"),
        (len(detail.get('skills', [])) >= 5, f"技能标签足够（{len(detail.get('skills', []))} 个）"),
        (detail.get('hr_name') == '张丽芳', "HR 姓名正确"),
        (detail.get('hr_title') == '人事经理', "HR 职位正确"),
        (detail.get('hr_status') == '三日内活跃', "HR 状态正确"),
        (len(detail.get('description', '').split('\n')) >= 7, f"职位描述完整（{len(detail.get('description', '').split(chr(10)))} 行）"),
    ]
    
    passed = sum(1 for check, _ in checks if check)
    print(f"\n检查项：{passed}/{len(checks)}")
    for check, desc in checks:
        status = "[OK]" if check else "[FAIL]"
        print(f"  {status} {desc}")
    
    return passed == len(checks)

def main():
    """主测试"""
    print("\n" + "=" * 60)
    print("求职 Agent · 职位详情页解析测试")
    print("=" * 60)
    
    try:
        passed = test_parse_job_detail()
        
        print("\n" + "=" * 60)
        print("测试结果")
        print("=" * 60)
        
        if passed:
            print("\n[SUCCESS] 职位详情解析测试通过！")
            return True
        else:
            print(f"\n[WARNING] 部分测试未通过")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] 测试异常：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
