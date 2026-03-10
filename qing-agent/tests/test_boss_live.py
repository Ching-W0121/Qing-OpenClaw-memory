"""
BOSS 直聘实时测试
测试实际 BOSS 直聘网站搜索功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 设置 UTF-8 编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from platform.boss_adapter import BossAdapter


async def test_boss_search():
    """测试 BOSS 直聘搜索"""
    print("=" * 60)
    print("BOSS 直聘实时测试")
    print("=" * 60)
    
    adapter = BossAdapter()
    
    # 测试关键词
    keywords = ["品牌策划", "品牌宣传", "视觉设计"]
    
    for keyword in keywords:
        print(f"\n🔍 测试关键词：{keyword}")
        print("-" * 40)
        
        try:
            # 搜索职位
            jobs = await adapter.search_jobs(keyword, city="深圳", page=1)
            
            if jobs:
                print(f"✅ 找到 {len(jobs)} 个职位")
                
                # 显示前 3 个职位详情
                for i, job in enumerate(jobs[:3], 1):
                    print(f"\n  职位 {i}:")
                    print(f"    公司：{job.get('company', 'N/A')}")
                    print(f"    职位：{job.get('title', 'N/A')}")
                    print(f"    薪资：{job.get('salary', 'N/A')}")
                    print(f"    地点：{job.get('district', 'N/A')}")
                    print(f"    链接：{job.get('url', 'N/A')}")
            else:
                print("⚠️  未找到职位（可能页面结构变化或需要登录）")
                
        except Exception as e:
            print(f"❌ 测试失败：{e}")
            import traceback
            traceback.print_exc()
        
        # 间隔等待，避免触发风控
        await asyncio.sleep(3)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_boss_search())
