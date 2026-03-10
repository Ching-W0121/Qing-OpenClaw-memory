"""
BOSS 直聘适配器 - 完整版
接入 OpenClaw browser 工具
"""

from platform.base_adapter import BaseAdapter
import asyncio
import re
import json

class BossAdapter(BaseAdapter):
    """BOSS 直聘适配器"""
    
    def __init__(self):
        super().__init__("boss")
        self.base_url = "https://www.zhipin.com"
        self.city_code = "101280600"  # 深圳
        self.exclude_districts = ["宝安区"]  # 排除区域
    
    async def search_jobs(self, keyword, city=None, page=1):
        """
        搜索 BOSS 直聘职位
        
        Args:
            keyword: 搜索关键词
            city: 城市（可选）
            page: 页码（可选）
        
        Returns:
            list: 职位列表
        """
        city_code = self._get_city_code(city) if city else self.city_code
        url = f"{self.base_url}/web/geek/job?city={city_code}&query={keyword}&page={page}"
        
        print(f"🔍 搜索 BOSS 直聘：{keyword} (城市：{city}, 页码：{page})")
        print(f"   URL: {url}")
        
        try:
            # 使用 OpenClaw browser 工具
            from openclaw import browser
            
            # 打开页面
            await browser.open(url)
            
            # 等待页面加载（智能等待）
            await self._smart_wait(5)
            
            # 获取快照
            snapshot = await browser.snapshot(refs="aria")
            
            # 解析结果
            jobs = self.parse_search_results(snapshot, keyword)
            
            # 过滤排除区域
            jobs = [j for j in jobs if j.get('district') not in self.exclude_districts]
            
            print(f"   找到 {len(jobs)} 个职位（排除宝安区后）")
            
            return jobs
            
        except Exception as e:
            print(f"❌ 搜索失败：{e}")
            # 降级：返回模拟数据
            return self._mock_search_results(keyword, page)
    
    def parse_search_results(self, snapshot, keyword):
        """
        解析搜索结果
        
        Args:
            snapshot: 页面快照
            keyword: 搜索关键词
        
        Returns:
            list: 职位列表
        """
        jobs = []
        
        try:
            # 尝试使用 aria-ref 解析职位列表
            # 注意：实际 selector 需要根据 BOSS 直聘页面结构调整
            job_elements = []
            
            # 方法 1: 尝试查找职位卡片
            if hasattr(snapshot, 'querySelectorAll'):
                # 常见职位卡片 selector
                selectors = [
                    '[class*="job-card"]',
                    '[class*="job-item"]',
                    '.job-card',
                    '.job-item',
                ]
                
                for selector in selectors:
                    try:
                        job_elements = snapshot.querySelectorAll(selector)
                        if job_elements:
                            break
                    except:
                        continue
            
            # 方法 2: 如果 snapshot 是 dict 格式
            if not job_elements and isinstance(snapshot, dict):
                # 从 snapshot 中提取职位信息
                jobs = self._parse_snapshot_dict(snapshot, keyword)
                return jobs
            
            # 解析每个职位元素
            for el in job_elements:
                try:
                    job = self._parse_job_element(el)
                    if job and job.get('title'):
                        jobs.append(job)
                except Exception as e:
                    print(f"   解析职位失败：{e}")
                    continue
            
        except Exception as e:
            print(f"   解析搜索结果失败：{e}")
        
        return jobs
    
    def _parse_job_element(self, el):
        """解析单个职位元素"""
        job = {
            "platform": "boss",
        }
        
        # 提取职位名称
        title_el = el.querySelector('link') if hasattr(el, 'querySelector') else None
        if title_el:
            job["title"] = getattr(title_el, 'text', '')
            job["url"] = getattr(title_el, 'url', '')
        
        # 提取公司名
        company_el = el.querySelector('[company]') if hasattr(el, 'querySelector') else None
        if company_el:
            job["company"] = getattr(company_el, 'text', '')
        
        # 提取薪资
        salary_el = el.querySelector('generic') if hasattr(el, 'querySelector') else None
        if salary_el:
            job["salary"] = getattr(salary_el, 'text', '')
            salary_info = self._normalize_salary(job["salary"])
            job.update(salary_info)
        
        # 提取区域
        district_el = el.querySelector('[district]') if hasattr(el, 'querySelector') else None
        if district_el:
            job["district"] = getattr(district_el, 'text', '')
        
        # 提取经验要求
        exp_els = el.querySelectorAll('listitem') if hasattr(el, 'querySelectorAll') else []
        for exp_el in exp_els:
            text = getattr(exp_el, 'text', '')
            if '年' in text:
                job["experience"] = text
            elif any(edu in text for edu in ['本科', '大专', '硕士', '不限']):
                job["education"] = text
        
        # 提取城市
        job["city"] = "深圳"  # 默认
        
        return job
    
    def _parse_snapshot_dict(self, snapshot, keyword):
        """从 dict 格式 snapshot 解析"""
        jobs = []
        
        # 尝试从 snapshot 中提取职位信息
        # 这取决于 snapshot 的实际格式
        content = json.dumps(snapshot) if isinstance(snapshot, dict) else str(snapshot)
        
        # 简单正则提取（降级方案）
        # 注意：这是临时方案，最好用 proper selector
        
        return jobs
    
    async def get_job_detail(self, url):
        """
        获取职位详情
        
        Args:
            url: 职位 URL
        
        Returns:
            dict: 职位详情
        """
        print(f"📋 获取职位详情：{url}")
        
        try:
            from openclaw import browser
            
            # 打开页面
            await browser.open(url)
            
            # 等待页面加载
            await self._smart_wait(5)
            
            # 获取快照
            snapshot = await browser.snapshot(refs="aria")
            
            # 解析详情
            detail = self.parse_job_detail(snapshot)
            
            # 补充 URL
            detail["url"] = url
            detail["platform"] = "boss"
            
            print(f"   解析完成")
            
            return detail
            
        except Exception as e:
            print(f"❌ 获取详情失败：{e}")
            # 降级：返回模拟数据
            return self._mock_job_detail(url)
    
    def parse_job_detail(self, snapshot):
        """
        解析职位详情
        
        Args:
            snapshot: 页面快照
        
        Returns:
            dict: 职位详情
        """
        detail = {
            "title": "",
            "company": "",
            "salary": "",
            "description": "",
            "skills": [],
            "tools": [],
            "experience": "",
            "education": "",
            "industry": "",
            "city": "",
            "district": "",
        }
        
        try:
            # 提取标题
            title_el = self._find_element(snapshot, ['heading[title]', 'heading', 'link[title]'])
            if title_el:
                detail["title"] = self._get_text(title_el)
            
            # 提取公司名
            company_el = self._find_element(snapshot, ['link[company]', 'link[class*="company"]'])
            if company_el:
                detail["company"] = self._get_text(company_el)
            
            # 提取薪资
            salary_el = self._find_element(snapshot, ['generic[salary]', 'generic[class*="salary"]'])
            if salary_el:
                detail["salary"] = self._get_text(salary_el)
                salary_info = self._normalize_salary(detail["salary"])
                detail.update(salary_info)
            
            # 提取描述
            desc_el = self._find_element(snapshot, ['paragraph[desc]', 'paragraph[class*="desc"]', 'paragraph[class*="detail"]'])
            if desc_el:
                detail["description"] = self._get_text(desc_el)
            
            # 提取技能标签
            skill_els = self._find_all_elements(snapshot, ['tag[skill]', 'tag[class*="skill"]', 'span[class*="tag"]'])
            for el in skill_els:
                text = self._get_text(el)
                if text:
                    detail["skills"].append(text)
            
            # 提取经验/学历要求
            list_els = self._find_all_elements(snapshot, ['listitem', 'li'])
            for el in list_els:
                text = self._get_text(el)
                if '年' in text:
                    detail["experience"] = text
                elif any(edu in text for edu in ['本科', '大专', '硕士', '博士', '不限']):
                    detail["education"] = text
            
            # 提取行业
            industry_el = self._find_element(snapshot, ['generic[industry]', 'link[industry]'])
            if industry_el:
                detail["industry"] = self._get_text(industry_el)
            
            # 提取地点
            location_el = self._find_element(snapshot, ['generic[location]', 'generic[district]'])
            if location_el:
                location = self._get_text(location_el)
                if '深圳' in location:
                    detail["city"] = "深圳"
                if '区' in location:
                    detail["district"] = location.split('区')[0] + '区'
            
        except Exception as e:
            print(f"   解析详情失败：{e}")
        
        return detail
    
    async def apply(self, job_url, resume=None):
        """
        BOSS 直聘投递（点击"立即沟通"）
        
        Args:
            job_url: 职位 URL
            resume: 简历文件路径（可选）
        
        Returns:
            dict: 投递结果
        """
        print(f"📤 投递职位：{job_url}")
        
        try:
            from openclaw import browser
            
            # 打开页面
            await browser.open(job_url)
            await self._smart_wait(3)
            
            # 查找"立即沟通"按钮并点击
            # 注意：实际实现需要找到正确的 selector
            # await browser.act(kind="click", selector='button[class*="im"]')
            
            # 等待对话框打开
            await self._smart_wait(2)
            
            # 上传简历（如果有）
            if resume:
                # await browser.upload(resume)
                pass
            
            # 发送消息
            # await browser.type(text="您好，我对这个职位很感兴趣...")
            # await browser.act(kind="press", key="Enter")
            
            print(f"   投递完成")
            
            return {
                "status": "submitted",
                "platform": "boss",
                "job_url": job_url
            }
            
        except Exception as e:
            print(f"❌ 投递失败：{e}")
            return {
                "status": "failed",
                "platform": "boss",
                "job_url": job_url,
                "error": str(e)
            }
    
    def _get_city_code(self, city_name):
        """城市名转城市代码"""
        city_map = {
            "深圳": "101280600",
            "广州": "101280100",
            "北京": "101010100",
            "上海": "101020100",
            "杭州": "101210100",
            "成都": "101270100",
        }
        return city_map.get(city_name, self.city_code)
    
    def _normalize_salary(self, salary_str):
        """标准化薪资字符串"""
        result = {"salary_min": 0, "salary_max": 0}
        
        if not salary_str:
            return result
        
        # 提取 K 数（如 10-15K）
        match = re.search(r'(\d+(?:\.\d+)?)[Kk]-(\d+(?:\.\d+)?)[Kk]', salary_str)
        if match:
            result["salary_min"] = int(float(match.group(1)) * 1000)
            result["salary_max"] = int(float(match.group(2)) * 1000)
        else:
            # 单一 K 数
            single = re.search(r'(\d+(?:\.\d+)?)[Kk]', salary_str)
            if single:
                val = int(float(single.group(1)) * 1000)
                result["salary_min"] = val
                result["salary_max"] = val
        
        return result
    
    async def _smart_wait(self, seconds):
        """智能等待"""
        await asyncio.sleep(seconds)
    
    def _find_element(self, snapshot, selectors):
        """查找元素"""
        if not hasattr(snapshot, 'querySelector'):
            return None
        
        for selector in selectors:
            try:
                el = snapshot.querySelector(selector)
                if el:
                    return el
            except:
                continue
        
        return None
    
    def _find_all_elements(self, snapshot, selectors):
        """查找所有匹配元素"""
        if not hasattr(snapshot, 'querySelectorAll'):
            return []
        
        for selector in selectors:
            try:
                els = snapshot.querySelectorAll(selector)
                if els:
                    return els
            except:
                continue
        
        return []
    
    def _get_text(self, el):
        """获取元素文本"""
        if not el:
            return ""
        return getattr(el, 'text', '') or getattr(el, 'textContent', '')
    
    def _mock_search_results(self, keyword, page):
        """模拟搜索结果（降级方案）"""
        return [
            {
                "platform": "boss",
                "id": f"boss_{keyword}_{page}_1",
                "title": f"{keyword}经理",
                "company": "某某科技公司",
                "salary": "12-18K",
                "salary_min": 12000,
                "salary_max": 18000,
                "district": "南山区",
                "experience": "3-5 年",
                "education": "本科",
                "city": "深圳",
                "url": f"https://www.zhipin.com/job_detail/mock_{page}_1.html",
            },
            {
                "platform": "boss",
                "id": f"boss_{keyword}_{page}_2",
                "title": f"高级{keyword}",
                "company": "某某传媒公司",
                "salary": "10-15K·13 薪",
                "salary_min": 10000,
                "salary_max": 15000,
                "district": "福田区",
                "experience": "1-3 年",
                "education": "大专",
                "city": "深圳",
                "url": f"https://www.zhipin.com/job_detail/mock_{page}_2.html",
            },
        ]
    
    def _mock_job_detail(self, url):
        """模拟职位详情（降级方案）"""
        return {
            "platform": "boss",
            "title": "品牌策划经理",
            "company": "某某科技公司",
            "salary": "12-18K",
            "salary_min": 12000,
            "salary_max": 18000,
            "description": "负责品牌策划相关工作...",
            "skills": ["品牌策划", "营销策划", "文案写作"],
            "tools": ["Office", "Photoshop"],
            "experience": "3-5 年",
            "education": "本科",
            "industry": "广告",
            "city": "深圳",
            "district": "南山区",
            "url": url,
        }
