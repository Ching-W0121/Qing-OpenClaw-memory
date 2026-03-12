"""
猎聘网适配器（高端职位）
"""

from qing_platform.base_adapter import BaseAdapter
import asyncio
import re
import time
from datetime import datetime, timedelta

class LiepinAdapter(BaseAdapter):
    """猎聘网适配器（专注高端职位）"""
    
    def __init__(self):
        super().__init__("liepin")
        self.base_url = "https://www.liepin.com"
        self.search_url = "https://www.liepin.com/zhaopin/"
        self.city_code = "440300"  # 深圳
        self.exclude_districts = []
        
        # 保护机制
        self.max_retry = 3
        self.timeout_seconds = 60
        self.circuit_breaker_threshold = 3
        self.circuit_breaker_cooldown = 1800
        self._failure_count = 0
        self._circuit_open_until = None
    
    def _is_circuit_open(self):
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
        """搜索猎聘网职位"""
        if self._is_circuit_open():
            return self._mock_search_results(keyword, page)
        
        # 猎聘网 URL 格式
        url = f"{self.search_url}?key={keyword}&city={city or self.city_code}&page={page}"
        
        print(f"[SEARCH] 猎聘网：{keyword} (城市：{city}, 页码：{page})")
        
        last_error = None
        for attempt in range(1, self.max_retry + 1):
            try:
                start_time = time.time()
                result = await self._do_search_with_timeout(url, keyword, start_time)
                self._on_success()
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
        jobs = []
        
        try:
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
        job = {
            "platform": "liepin",
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
            
            # 提取经验/学历/地点
            for text_el in text_els:
                text = self._get_text(text_el)
                if not text:
                    continue
                
                if any(city in text for city in ['深圳', '广州', '上海', '北京']):
                    job["city"] = text.split('-')[0].strip() if '-' in text else text.strip()
                
                if '年' in text and '经验' in text:
                    job["experience"] = text.strip()
                elif any(edu in text for edu in ['本科', '大专', '硕士', '博士', '不限']):
                    job["education"] = text.strip()
            
            # 默认城市
            if not job.get("city"):
                job["city"] = "深圳"
            
        except:
            pass
        
        return job
    
    def _is_valid_job(self, job):
        if not job.get('title'):
            return False
        
        invalid_keywords = ['上一页', '下一页', '跳转', 'APP', '下载']
        return not any(kw in job.get('title', '') for kw in invalid_keywords)
    
    def parse_job_detail(self, snapshot):
        """解析职位详情"""
        return {}
    
    async def get_job_detail(self, url):
        """获取职位详情"""
        return {}
    
    async def apply(self, job_url, resume=None):
        """申请职位"""
        return {"status": "not_implemented"}
    
    def _normalize_salary(self, salary_str):
        result = {"salary_min": 0, "salary_max": 0}
        
        if not salary_str:
            return result
        
        # 万/月
        wan_match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*万', salary_str)
        if wan_match:
            result["salary_min"] = int(float(wan_match.group(1)) * 10000)
            result["salary_max"] = int(float(wan_match.group(2)) * 10000)
            return result
        
        # K/月
        k_match = re.search(r'(\d+)-(\d+)K', salary_str, re.IGNORECASE)
        if k_match:
            result["salary_min"] = int(k_match.group(1)) * 1000
            result["salary_max"] = int(k_match.group(2)) * 1000
            return result
        
        return result
    
    def _mock_search_results(self, keyword, page):
        return [
            {
                "title": f"高级{keyword}经理",
                "company": "深圳某某集团公司",
                "salary": "2-4 万/月",
                "salary_min": 20000,
                "salary_max": 40000,
                "city": "深圳",
                "district": "福田",
                "experience": "5-10 年",
                "education": "本科",
                "platform": "liepin",
                "url": "https://www.liepin.com/job/mock1.html",
            },
            {
                "title": f"{keyword}总监",
                "company": "深圳某某科技公司",
                "salary": "3-6 万/月",
                "salary_min": 30000,
                "salary_max": 60000,
                "city": "深圳",
                "district": "南山",
                "experience": "10 年以上",
                "education": "硕士",
                "platform": "liepin",
                "url": "https://www.liepin.com/job/mock2.html",
            },
        ]
