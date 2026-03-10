"""
BOSS 直聘测试 - OpenClaw browser 工具版本
在 OpenClaw 会话中运行此脚本
"""

import asyncio


async def test_boss_with_browser():
    """使用 OpenClaw browser 工具测试 BOSS 直聘"""
    print("=" * 60)
    print("BOSS 直聘测试 - OpenClaw browser 工具")
    print("=" * 60)
    
    # 使用 OpenClaw browser 工具
    from openclaw import browser
    
    # 测试 URL
    url = "https://www.zhipin.com/web/geek/job?city=101280600&query=品牌策划&page=1"
    
    print(f"\n打开页面：{url}")
    
    try:
        # 打开页面
        await browser.open(url)
        
        # 等待页面加载
        await asyncio.sleep(5)
        
        # 获取快照
        snapshot = await browser.snapshot(refs="aria")
        
        print("\n页面快照获取成功")
        print(f"快照类型：{type(snapshot)}")
        
        # 尝试查找职位卡片
        selectors = [
            '[class*="job-card"]',
            '[class*="job-item"]',
            '.job-card',
            '.job-item',
        ]
        
        for selector in selectors:
            try:
                if hasattr(snapshot, 'querySelectorAll'):
                    elements = snapshot.querySelectorAll(selector)
                    if elements:
                        print(f"\n使用 selector '{selector}' 找到 {len(elements)} 个职位")
                        break
            except Exception as e:
                print(f"Selector '{selector}' 失败：{e}")
        else:
            print("\n未找到职位列表，可能需要调整 selector")
        
        # 显示部分快照内容
        if hasattr(snapshot, 'outerHTML'):
            print(f"\n页面标题：{snapshot.title if hasattr(snapshot, 'title') else 'N/A'}")
        
    except Exception as e:
        print(f"测试失败：{e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_boss_with_browser())
