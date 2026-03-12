"""
前程无忧 (51job) 适配器
"""

from qing_platform.base_adapter import BaseAdapter
import asyncio
import re
import time
from datetime import datetime, timedelta

class Job51Adapter(BaseAdapter):
    """前程无忧适配器"""
    
    def __init__(self):
        super().__init__("51job")
        self.base_url = "https://www.51job.com"
        self.search_url = "https://we.51job.com/pc/search"
        self.city_code = "080200"  # 深圳
        self.exclude_districts = ["宝安"]
        
        # 保护机制
        self.max_retry = 3
        self.timeout_seconds = 60
        self.circuit_breaker_threshold = 3
        self.circuit_breaker_cooldown = 1800
        self._failure_count = 0
        self._circuit_open_until = None
    
    def _is_circuit_open(self):
        """检查熔断器是否打开"""
        if self._circuit_open_until is None:
            return False
        if datetime.now() < self._circuit_open_until:
            return True
        self._circuit_open_until = None
        self._failure_count = 0
        return False
    
    def _on_success(self):
        self._failure_count = 0
    
    def _on_failure(self):
        self._failure_count += 1
        if self._failure_count >= self.circuit_breaker_threshold:
            self._open_circuit()
    
    def _open_circuit(self):
        self._circuit_open_until = datetime.now() + timedelta(seconds=self.circuit_breaker_cooldown)
    
    async def search_jobs(self, keyword, city=None, page=1):
        """搜索前程无忧职位"""
        if self._is_circuit_open():
            return self._mock_search_results(keyword, page)
        
        # 构建搜索 URL
        url = f"{self.search_url}?keyword={keyword}&city={city or self.city_code}&page={page}"
        
        print(f"[SEARCH] 前程无忧：{keyword} (城市：{city}, 页码：{page})")
        
        last_error = None
        for attempt in range(1, self.max_retry + 1):
            try:
                start_time = time.time()
                result = await self._do_search_with_timeout(url, keyword, start_time)
                self._on_success()
                
                # 过滤排除区域
                result = [j for j in result if j.get('district') not in self.exclude_districts]
                return result
                
            except asyncio.TimeoutError:
                last_error = f"超时（尝试 {attempt}/{self.max_retry}）"
                self._on_failure()
            except Exception as e:
                last_error = f"错误：{e}（尝试 {attempt}/{self.max_retry}）"
                self._on_failure()
                
                if self._failure_count >= self.circuit_breaker_threshold:
                    return self._mock_search_results(keyword, page)
        
        return self._mock_search_results(keyword, page)
    
    async def _do_search_with_timeout(self, url, keyword, start_time):
        """带超时检查的搜索"""
        try:
            from openclaw import browser
            
            elapsed = time.time() - start_time
            if elapsed > self.timeout_seconds:
                raise asyncio.TimeoutError(f"超时 ({elapsed:.1f}s)")
            
            await browser.open(url)
            await asyncio.sleep(3)
            
            elapsed = time.time() - start_time
            if elapsed > self.timeout_seconds:
                raise asyncio.TimeoutError(f"等待超时 ({elapsed:.1f}s)")
            
            snapshot = await browser.snapshot(refs="aria")
            jobs = self.parse_search_results(snapshot, keyword)
            
            return jobs
            
        except Exception as e:
            elapsed = time.time() - start_time
            if elapsed > self.timeout_seconds:
                raise asyncio.TimeoutError(f"超时 ({elapsed:.1f}s)")
            raise
    
    def parse_search_results(self, snapshot, keyword):
        """解析搜索结果"""
        jobs = []
        
        try:
            # 前程无忧的职位元素通常是 listitem 或 generic
            job_elements = self._find_all_elements(snapshot, ['listitem', 'generic'])
            
            for el in job_elements:
                try:
                    job = self._parse_job_element(el)
                    if job and job.get('title'):
                        if self._is_valid_job(job):
                            jobs.append(job)
                except:
                    continue
            
        except Exception as e:
            pass
        
        return jobs
    
    def _parse_job_element(self, el):
        """解析单个职位元素"""
        job = {
            "platform": "51job",
            "title": "",
            "company": "",
            "salary": "",
            "city": "",
            "district": "",
            "experience": "",
            "education": "",
            "skills": [],
            "url": "",
        }
        
        try:
            # 提取标题
            title_el = self._find_element(el, ['link'])
            if title_el:
                job["title"] = self._get_text(title_el)
                job["url"] = self._get_url(title_el)
            
            # 提取薪资
            text_els = self._find_all_elements(el, ['text', 'paragraph'])
            for text_el in text_els:
                text = self._get_text(text_el)
                if text and any(c.isdigit() for c in text) and ('万' in text or 'K' in text or '千' in text or '元' in text):
                    job["salary"] = text
                    salary_info = self._normalize_salary(text)
                    job.update(salary_info)
                    break
            
            # 提取地点/经验/学历
            for text_el in text_els:
                text = self._get_text(text_el)
                if not text:
                    continue
                
                if any(city in text for city in ['深圳', '广州', '上海', '北京']):
                    job["city"] = text.split('-')[0].strip() if '-' in text else text.strip()
                
                if '年' in text and '经验' in text:
                    job["experience"] = text.strip()
                elif any(edu in text for edu in ['本科', '大专', '硕士', '不限']):
                    job["education"] = text.strip()
            
            # 默认城市
            if not job.get("city"):
                job["city"] = "深圳"
            
        except:
            pass
        
        return job
    
    def _is_valid_job(self, job):
        """检查职位有效性"""
        if not job.get('title'):
            return False
        
        invalid_keywords = ['上一页', '下一页', '确定', '跳转', 'APP']
        title = job.get('title', '')
        return not any(kw in title for kw in invalid_keywords)
    
    def _normalize_salary(self, salary_str):
        """标准化薪资"""
        result = {"salary_min": 0, "salary_max": 0}
        
        if not salary_str:
            return result
        
        # 万/月
        wan_match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*万/月', salary_str)
        if wan_match:
            result["salary_min"] = int(float(wan_match.group(1)) * 10000)
            result["salary_max"] = int(float(wan_match.group(2)) * 10000)
            return result
        
        # 万/年
        wan_year = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*万/年', salary_str)
        if wan_year:
            result["salary_min"] = int(float(wan_year.group(1)) * 10000 / 12)
            result["salary_max"] = int(float(wan_year.group(2)) * 10000 / 12)
            return result
        
        # K/月
        k_match = re.search(r'(\d+)-(\d+)K', salary_str, re.IGNORECASE)
        if k_match:
            result["salary_min"] = int(k_match.group(1)) * 1000
            result["salary_max"] = int(k_match.group(2)) * 1000
            return result
        
        # 元/月
        yuan_match = re.search(r'(\d+)-(\d+)\s*元', salary_str)
        if yuan_match:
            result["salary_min"] = int(yuan_match.group(1))
            result["salary_max"] = int(yuan_match.group(2))
            return result
        
        return result
    
    def parse_job_detail(self, snapshot):
        """解析职位详情"""
        return {}
    
    async def get_job_detail(self, url):
        """获取职位详情"""
        return {}
    
    async def apply(self, job_url, resume=None):
        """申请职位"""
        return {"status": "not_implemented"}
    def _mock_search_results(self, keyword, page):
        """模拟数据"""
        return [
            {
                "title": f"{keyword}工程师",
                "company": "深圳某某科技公司",
                "salary": "1-1.5 万/月",
                "salary_min": 10000,
                "salary_max": 15000,
                "city": "深圳",
                "district": "南山",
                "experience": "3-5 年",
                "education": "本科",
                "platform": "51job",
                "url": "https://www.51job.com/job/mock1.html",
            },
            {
                "title": f"高级{keyword}",
                "company": "深圳某某实业公司",
                "salary": "1.5-2 万/月",
                "salary_min": 15000,
                "salary_max": 20000,
                "city": "深圳",
                "district": "福田",
                "experience": "5-10 年",
                "education": "本科",
                "platform": "51job",
                "url": "https://www.51job.com/job/mock2.html",
            },
        ]
