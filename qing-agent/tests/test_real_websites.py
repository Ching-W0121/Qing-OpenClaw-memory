"""
真实网站测试 - BOSS 直聘 + 智联招聘
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_boss_zhipin():
    """测试 BOSS 直聘"""
    print("\n" + "=" * 60)
    print("测试：BOSS 直聘真实数据")
    print("=" * 60)
    
    try:
        from openclaw import browser
        
        # 打开 BOSS 直聘深圳站
        keyword = "品牌策划"
        url = f"https://www.zhipin.com/web/geek/job?city=101280600&query={keyword}&page=1"
        
        print(f"\n访问 BOSS 直聘...")
        print(f"关键词：{keyword}")
        print(f"URL: {url}")
        
        await browser.open(url)
        await asyncio.sleep(3)
        
        # 获取快照
        print("\n获取页面快照...")
        snapshot = await browser.snapshot(refs="aria")
        
        # 简单统计
        print("\n页面内容摘要：")
        print(f"  快照元素数量：{len(snapshot.get('elements', [])) if isinstance(snapshot, dict) else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] BOSS 直聘测试失败：{e}")
        return False

async def test_zhilian():
    """测试智联招聘"""
    print("\n" + "=" * 60)
    print("测试：智联招聘真实数据")
    print("=" * 60)
    
    try:
        from openclaw import browser
        
        # 打开智联招聘
        keyword = "品牌策划"
        url = f"https://www.zhaopin.com/sou/jl765/kwAJ0N4J3RAP914"
        
        print(f"\n访问智联招聘...")
        print(f"关键词：{keyword}")
        print(f"URL: {url}")
        
        await browser.open(url)
        await asyncio.sleep(3)
        
        # 获取快照
        print("\n获取页面快照...")
        snapshot = await browser.snapshot(refs="aria")
        
        # 简单统计
        print(f"\n页面内容摘要：")
        print(f"  快照元素数量：{len(snapshot.get('elements', [])) if isinstance(snapshot, dict) else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 智联招聘测试失败：{e}")
        return False

async def main():
    """主测试"""
    print("\n" + "=" * 60)
    print("真实网站数据测试")
    print("=" * 60)
    
    # 先试 BOSS 直聘
    boss_success = await test_boss_zhipin()
    
    if boss_success:
        print("\n[OK] BOSS 直聘访问成功！")
    else:
        print("\n[FAIL] BOSS 直聘访问失败，尝试智联招聘...")
        
        # 试智联招聘
        zhilian_success = await test_zhilian()
        
        if zhilian_success:
            print("\n[OK] 智联招聘访问成功！")
        else:
            print("\n[FAIL] 智联招聘也失败了")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
