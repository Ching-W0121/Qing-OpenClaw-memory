"""
BOSS 直聘实时测试 - HTTP 版本
使用标准 HTTP 请求测试 BOSS 直聘搜索功能
"""

import asyncio
import aiohttp
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 设置 UTF-8 编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from bs4 import BeautifulSoup
from fake_useragent import UserAgent


async def test_boss_search():
    """测试 BOSS 直聘搜索"""
    print("=" * 60)
    print("BOSS 直聘实时测试 - HTTP 版本")
    print("=" * 60)
    
    base_url = "https://www.zhipin.com"
    city_code = "101280600"  # 深圳
    keywords = ["品牌策划", "品牌宣传", "视觉设计"]
    
    headers = {
        "User-Agent": UserAgent().random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.zhipin.com/",
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for keyword in keywords:
            print(f"\n[测试] 关键词：{keyword}")
            print("-" * 40)
            
            url = f"{base_url}/web/geek/job?city={city_code}&query={keyword}&page=1"
            
            try:
                async with session.get(url, timeout=15) as response:
                    print(f"状态码：{response.status}")
                    
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 尝试查找职位列表
                        job_cards = soup.select('[class*="job-card"]')
                        
                        if job_cards:
                            print(f"找到 {len(job_cards)} 个职位")
                            
                            # 显示前 3 个
                            for i, card in enumerate(job_cards[:3], 1):
                                title_elem = card.select_one('[class*="job-name"]')
                                company_elem = card.select_one('[class*="company-name"]')
                                salary_elem = card.select_one('[class*="salary"]')
                                location_elem = card.select_one('[class*="location"]')
                                
                                print(f"\n  职位 {i}:")
                                print(f"    职位：{title_elem.text.strip() if title_elem else 'N/A'}")
                                print(f"    公司：{company_elem.text.strip() if company_elem else 'N/A'}")
                                print(f"    薪资：{salary_elem.text.strip() if salary_elem else 'N/A'}")
                                print(f"    地点：{location_elem.text.strip() if location_elem else 'N/A'}")
                        else:
                            print("未找到职位列表（可能页面结构变化或需要登录）")
                            
                            # 检查是否有验证码或登录提示
                            if "验证" in html or "登录" in html:
                                print("检测到验证码或登录要求")
                    
                    elif response.status == 403:
                        print("访问被拒绝 (403) - 可能触发反爬虫")
                    
                    elif response.status == 302:
                        print("重定向 (302) - 可能跳转到登录页")
                    
            except asyncio.TimeoutError:
                print("请求超时")
            except Exception as e:
                print(f"测试失败：{e}")
            
            # 间隔等待，避免触发风控
            await asyncio.sleep(3)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    # 检查依赖
    try:
        import aiohttp
        from bs4 import BeautifulSoup
        from fake_useragent import UserAgent
        print("依赖检查：OK")
    except ImportError as e:
        print(f"缺少依赖：{e}")
        print("请安装：pip install aiohttp beautifulsoup4 fake-useragent")
        sys.exit(1)
    
    asyncio.run(test_boss_search())
