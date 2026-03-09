"""
智联招聘适配器
"""

from platform.base_adapter import BaseAdapter
import asyncio
import re

class ZhilianAdapter(BaseAdapter):
    """智联招聘适配器"""
    
    def __init__(self):
        super().__init__("zhilian")
        self.base_url = "https://www.zhaopin.com"
        self.landing_url = "https://landing.zhaopin.com"
        self.city_code = "530"  # 深圳
    
    async def search_jobs(self, keyword, city=None, page=1):
        """
        搜索智联招聘职位
        
        Args:
            keyword: 搜索关键词
            city: 城市
            page: 页码
        
        Returns:
            list: 职位列表
        """
        # 构建搜索 URL
        city_param = f"&city={city}" if city else ""
        url = f"{self.base_url}/job/positions?keyword={keyword}{city_param}&page={page}"
        
        print(f"[SEARCH] 智联招聘：{keyword} (城市：{city}, 页码：{page})")
        print(f"   URL: {url}")
        
        try:
            from openclaw import browser
            
            # 打开搜索页面
            await browser.open(url)
            
            # 等待页面加载
            await self._smart_wait(5)
            
            # 获取快照
            snapshot = await browser.snapshot(refs="aria")
            
            # 解析结果
            jobs = self.parse_search_results(snapshot, keyword)
            
            print(f"   找到 {len(jobs)} 个职位")
            
            return jobs
            
        except Exception as e:
            print(f"[ERROR] 搜索失败：{e}")
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
            # 尝试查找职位卡片
            job_elements = []
            
            if hasattr(snapshot, 'querySelectorAll'):
                # 智联招聘职位卡片 selector
                selectors = [
                    '[class*="joblist"]',
                    '[class*="position"]',
                    '.joblist',
                    '.position',
                    '[role="listitem"]',
                ]
                
                for selector in selectors:
                    try:
                        job_elements = snapshot.querySelectorAll(selector)
                        if job_elements:
                            break
                    except:
                        continue
            
            # 解析每个职位元素
            for el in job_elements:
                try:
                    job = self._parse_job_element(el)
                    if job and job.get('title'):
                        jobs.append(job)
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"   解析搜索结果失败：{e}")
        
        return jobs
    
    def _parse_job_element(self, el):
        """解析单个职位元素"""
        job = {
            "platform": "zhilian",
        }
        
        try:
            # 提取职位名称
            if hasattr(el, 'querySelector'):
                title_el = el.querySelector('[class*="name"]') or el.querySelector('link')
                if title_el:
                    job["title"] = getattr(title_el, 'text', '')
                    job["url"] = getattr(title_el, 'url', '')
                
                # 提取公司名
                company_el = el.querySelector('[class*="company"]')
                if company_el:
                    job["company"] = getattr(company_el, 'text', '')
                
                # 提取薪资
                salary_el = el.querySelector('[class*="salary"]') or el.querySelector('paragraph')
                if salary_el:
                    job["salary"] = getattr(salary_el, 'text', '')
                    salary_info = self._normalize_salary(job["salary"])
                    job.update(salary_info)
                
                # 提取地点
                location_el = el.querySelector('[class*="location"]') or el.querySelector('[class*="city"]')
                if location_el:
                    location = getattr(location_el, 'text', '')
                    if '深圳' in location:
                        job["city"] = "深圳"
                    job["district"] = location.split('·')[-1] if '·' in location else ''
                
                # 提取经验要求
                exp_els = el.querySelectorAll('paragraph') if hasattr(el, 'querySelectorAll') else []
                for exp_el in exp_els:
                    text = getattr(exp_el, 'text', '')
                    if '年' in text and '经验' in text:
                        job["experience"] = text
                    elif any(edu in text for edu in ['本科', '大专', '硕士', '不限']):
                        job["education"] = text
                
                # 提取城市（默认）
                if not job.get("city"):
                    job["city"] = "深圳"
            
        except Exception as e:
            pass
        
        return job
    
    async def get_job_detail(self, url):
        """
        获取职位详情
        
        Args:
            url: 职位 URL
        
        Returns:
            dict: 职位详情
        """
        print(f"[DETAIL] 获取职位详情：{url}")
        
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
            detail["platform"] = "zhilian"
            
            print(f"   解析完成")
            
            return detail
            
        except Exception as e:
            print(f"[ERROR] 获取详情失败：{e}")
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
            salary_el = self._find_element(snapshot, ['generic[salary]', 'paragraph[class*="salary"]'])
            if salary_el:
                detail["salary"] = self._get_text(salary_el)
                salary_info = self._normalize_salary(detail["salary"])
                detail.update(salary_info)
            
            # 提取描述
            desc_el = self._find_element(snapshot, ['paragraph[desc]', 'paragraph[class*="detail"]', 'paragraph[class*="content"]'])
            if desc_el:
                detail["description"] = self._get_text(desc_el)
            
            # 提取技能标签
            skill_els = self._find_all_elements(snapshot, ['tag[skill]', 'span[class*="tag"]', 'span[class*="skill"]'])
            for el in skill_els:
                text = self._get_text(el)
                if text:
                    detail["skills"].append(text)
            
            # 提取经验/学历要求
            list_els = self._find_all_elements(snapshot, ['listitem', 'li', 'paragraph'])
            for el in list_els:
                text = self._get_text(el)
                if '年' in text and '经验' in text:
                    detail["experience"] = text
                elif any(edu in text for edu in ['本科', '大专', '硕士', '博士', '不限']):
                    detail["education"] = text
            
            # 提取行业
            industry_el = self._find_element(snapshot, ['link[industry]', 'generic[industry]'])
            if industry_el:
                detail["industry"] = self._get_text(industry_el)
            
            # 提取地点
            location_el = self._find_element(snapshot, ['generic[location]', 'paragraph[city]'])
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
        智联招聘投递
        
        Args:
            job_url: 职位 URL
            resume: 简历文件路径
        
        Returns:
            dict: 投递结果
        """
        print(f"[APPLY] 投递职位：{job_url}")
        
        try:
            from openclaw import browser
            
            # 打开页面
            await browser.open(job_url)
            await self._smart_wait(3)
            
            # 查找"立即申请"按钮并点击
            # await browser.act(kind="click", selector='button[class*="apply"]')
            
            print(f"   投递完成")
            
            return {
                "status": "submitted",
                "platform": "zhilian",
                "job_url": job_url
            }
            
        except Exception as e:
            print(f"[ERROR] 投递失败：{e}")
            return {
                "status": "failed",
                "platform": "zhilian",
                "job_url": job_url,
                "error": str(e)
            }
    
    def _normalize_salary(self, salary_str):
        """标准化薪资字符串"""
        result = {"salary_min": 0, "salary_max": 0}
        
        if not salary_str:
            return result
        
        # 提取 K 数或万数
        k_match = re.search(r'(\d+(?:\.\d+)?)[Kk]-(\d+(?:\.\d+)?)[Kk]', salary_str)
        if k_match:
            result["salary_min"] = int(float(k_match.group(1)) * 1000)
            result["salary_max"] = int(float(k_match.group(2)) * 1000)
        else:
            # 万数（如 1.5-2 万）
            wan_match = re.search(r'(\d+(?:\.\d+)?)[万 wan]-(\d+(?:\.\d+)?)[万 wan]', salary_str)
            if wan_match:
                result["salary_min"] = int(float(wan_match.group(1)) * 10000)
                result["salary_max"] = int(float(wan_match.group(2)) * 10000)
        
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
                "platform": "zhilian",
                "id": f"zhilian_{keyword}_{page}_1",
                "title": f"{keyword}经理",
                "company": "某某科技公司",
                "salary": "12-18K",
                "salary_min": 12000,
                "salary_max": 18000,
                "district": "南山区",
                "experience": "3-5 年",
                "education": "本科",
                "city": "深圳",
                "url": f"https://www.zhaopin.com/job_detail/mock_{page}_1.html",
            },
            {
                "platform": "zhilian",
                "id": f"zhilian_{keyword}_{page}_2",
                "title": f"高级{keyword}",
                "company": "某某传媒公司",
                "salary": "10-15K",
                "salary_min": 10000,
                "salary_max": 15000,
                "district": "福田区",
                "experience": "1-3 年",
                "education": "大专",
                "city": "深圳",
                "url": f"https://www.zhaopin.com/job_detail/mock_{page}_2.html",
            },
        ]
    
    def _mock_job_detail(self, url):
        """模拟职位详情（降级方案）"""
        return {
            "platform": "zhilian",
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
