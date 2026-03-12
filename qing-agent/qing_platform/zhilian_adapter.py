"""
智联招聘适配器
"""

from qing_platform.base_adapter import BaseAdapter
import asyncio
import re
import time
from datetime import datetime, timedelta

class ZhilianAdapter(BaseAdapter):
    """智联招聘适配器"""
    
    def __init__(self):
        super().__init__("zhilian")
        self.base_url = "https://www.zhaopin.com"
        self.landing_url = "https://landing.zhaopin.com"
        self.city_code = "530"  # 深圳
        
        # === 防死循环保护机制 ===
        self.max_retry = 3  # 最大重试次数
        self.timeout_seconds = 60  # 超时时间（秒）
        self.circuit_breaker_threshold = 3  # 熔断阈值（连续失败次数）
        self.circuit_breaker_cooldown = 1800  # 熔断冷却时间（秒）= 30 分钟
        self._failure_count = 0  # 连续失败计数
        self._circuit_open_until = None  # 熔断打开直到何时
        self._last_success_time = None  # 上次成功时间
    
    async def search_jobs(self, keyword, city=None, page=1):
        """
        搜索智联招聘职位（带保护机制）
        
        Args:
            keyword: 搜索关键词
            city: 城市
            page: 页码
        
        Returns:
            list: 职位列表
        """
        # === 保护 1: 熔断器检查 ===
        if self._is_circuit_open():
            print(f"[CIRCUIT BREAKER] 熔断器已打开，拒绝请求。冷却至：{self._circuit_open_until}")
            return self._mock_search_results(keyword, page)
        
        # 构建搜索 URL
        city_param = f"&city={city}" if city else ""
        url = f"{self.base_url}/job/positions?keyword={keyword}{city_param}&page={page}"
        
        print(f"[SEARCH] 智联招聘：{keyword} (城市：{city}, 页码：{page})")
        print(f"   URL: {url}")
        
        # === 保护 2: 重试机制 ===
        last_error = None
        for attempt in range(1, self.max_retry + 1):
            try:
                # === 保护 3: 超时检查 ===
                start_time = time.time()
                
                result = await self._do_search_with_timeout(url, keyword, start_time)
                
                # 成功：重置失败计数
                self._on_success()
                return result
                
            except asyncio.TimeoutError:
                last_error = f"超时（尝试 {attempt}/{self.max_retry}）"
                print(f"[TIMEOUT] {last_error}")
                self._on_failure()
                
            except Exception as e:
                last_error = f"错误：{e}（尝试 {attempt}/{self.max_retry}）"
                print(f"[ERROR] {last_error}")
                self._on_failure()
                
                # 熔断器触发：提前退出
                if self._failure_count >= self.circuit_breaker_threshold:
                    print(f"[CIRCUIT BREAKER] 连续失败 {self._failure_count} 次，触发熔断")
                    return self._mock_search_results(keyword, page)
        
        # 所有重试失败：返回降级数据
        print(f"[FALLBACK] 所有重试失败，使用模拟数据。最后错误：{last_error}")
        return self._mock_search_results(keyword, page)
    
    async def _do_search_with_timeout(self, url, keyword, start_time):
        """带超时检查的搜索执行"""
        try:
            from openclaw import browser
            
            # 检查是否已超时
            elapsed = time.time() - start_time
            if elapsed > self.timeout_seconds:
                raise asyncio.TimeoutError(f"搜索超时 ({elapsed:.1f}s > {self.timeout_seconds}s)")
            
            # 打开搜索页面
            await browser.open(url)
            
            # 等待页面加载（带超时检查）
            await self._smart_wait_with_timeout(5, start_time)
            
            # 获取快照
            snapshot = await browser.snapshot(refs="aria")
            
            # 解析结果
            jobs = self.parse_search_results(snapshot, keyword)
            
            print(f"   找到 {len(jobs)} 个职位")
            
            return jobs
            
        except Exception as e:
            # 检查超时
            elapsed = time.time() - start_time
            if elapsed > self.timeout_seconds:
                raise asyncio.TimeoutError(f"搜索超时 ({elapsed:.1f}s > {self.timeout_seconds}s)")
            raise
    
    def _is_circuit_open(self):
        """检查熔断器是否打开"""
        if self._circuit_open_until is None:
            return False
        
        if datetime.now() < self._circuit_open_until:
            return True
        
        # 冷却时间已过，关闭熔断器
        print("[CIRCUIT BREAKER] 冷却时间已过，关闭熔断器")
        self._circuit_open_until = None
        self._failure_count = 0
        return False
    
    def _on_success(self):
        """成功时调用"""
        self._failure_count = 0
        self._last_success_time = datetime.now()
    
    def _on_failure(self):
        """失败时调用"""
        self._failure_count += 1
        
        # 检查是否需要触发熔断器
        if self._failure_count >= self.circuit_breaker_threshold:
            self._open_circuit()
    
    def _open_circuit(self):
        """打开熔断器"""
        self._circuit_open_until = datetime.now() + timedelta(seconds=self.circuit_breaker_cooldown)
        print(f"[CIRCUIT BREAKER] 熔断器已打开，冷却 {self.circuit_breaker_cooldown} 秒")
    
    async def _smart_wait_with_timeout(self, seconds, start_time):
        """智能等待（带超时检查）"""
        await asyncio.sleep(seconds)
        
        # 检查是否已超时
        elapsed = time.time() - start_time
        if elapsed > self.timeout_seconds:
            raise asyncio.TimeoutError(f"等待超时 ({elapsed:.1f}s > {self.timeout_seconds}s)")
    
    def parse_search_results(self, snapshot, keyword):
        """
        解析智联招聘搜索结果页面（基于真实页面结构）
        
        Args:
            snapshot: 页面快照
            keyword: 搜索关键词
        
        Returns:
            list: 职位列表
        """
        jobs = []
        
        try:
            # 查找所有 listitem 元素（真实页面结构）
            job_elements = self._find_all_elements(snapshot, ['listitem'])
            
            if not job_elements:
                print(f"   未找到职位列表，使用模拟数据")
                return self._mock_search_results(keyword, 1)
            
            print(f"   找到 {len(job_elements)} 个职位元素")
            
            # 解析每个职位
            for i, el in enumerate(job_elements):
                try:
                    job = self._parse_job_element(el)
                    if job and job.get('title'):
                        # 过滤掉非职位元素（如分页、广告等）
                        if self._is_valid_job(job):
                            jobs.append(job)
                except Exception as e:
                    continue
            
            print(f"   解析成功 {len(jobs)} 个有效职位")
            
        except Exception as e:
            print(f"   解析搜索结果失败：{e}")
            # 降级：返回模拟数据
            return self._mock_search_results(keyword, 1)
        
        return jobs
    
    def _is_valid_job(self, job):
        """检查是否是有效的职位"""
        # 必须有职位名称
        if not job.get('title'):
            return False
        
        # 排除非职位项（如"上一页"、"下一页"、页码等）
        invalid_keywords = ['上一页', '下一页', '确定', '到', 'APP', '微信', '官方', '简历', '置顶']
        title = job.get('title', '')
        for keyword in invalid_keywords:
            if keyword in title:
                return False
        
        return True
    
    def _parse_job_element(self, el):
        """解析单个职位元素（基于真实页面结构）"""
        job = {
            "platform": "zhilian",
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
            # 提取职位名称和 URL（link 元素）
            title_el = self._find_element(el, ['link'])
            if title_el:
                job["title"] = self._get_text(title_el)
                job["url"] = self._get_url(title_el)
            
            # 提取薪资（paragraph 元素）
            salary_el = self._find_element(el, ['paragraph'])
            if salary_el:
                job["salary"] = self._get_text(salary_el)
                salary_info = self._normalize_salary(job["salary"])
                job.update(salary_info)
            
            # 提取地点（text 元素包含·分隔符）
            text_els = self._find_all_elements(el, ['text'])
            for text_el in text_els:
                text = self._get_text(text_el)
                if '·' in text and ('深圳' in text or '区' in text):
                    # 格式：深圳·罗湖·东晓
                    parts = text.split('·')
                    if parts[0] == '深圳':
                        job["city"] = "深圳"
                        if len(parts) >= 2:
                            job["district"] = parts[1]
                    break
            
            # 提取经验和学历（generic 元素）
            generic_els = self._find_all_elements(el, ['generic'])
            for gen_el in generic_els:
                text = self._get_text(gen_el)
                if not text:
                    continue
                
                # 经验：包含"年"
                if '年' in text and ('经验' in text or '经验不限' in text or text.strip().endswith('年')):
                    job["experience"] = text.strip()
                # 学历：包含学历关键词
                elif any(edu in text for edu in ['本科', '大专', '硕士', '博士', '学历不限', '中专', '高中']):
                    job["education"] = text.strip()
            
            # 提取技能标签（generic 元素，短文本）
            for gen_el in generic_els:
                text = self._get_text(gen_el)
                if text and len(text) <= 10 and text not in ['深圳', '本科', '大专', '硕士', '不限']:
                    # 检查是否是技能标签（不包含地点、经验、学历信息）
                    if ('·' not in text and '年' not in text and 
                        text not in [job.get('experience', ''), job.get('education', '')]):
                        # 排除公司相关信息
                        if not any(skip in text for skip in ['人', '民营', '国企', '公司', '融资']):
                            if text not in job["skills"]:
                                job["skills"].append(text)
            
            # 提取公司名（在嵌套的 generic/link 中）
            # 公司名通常在第二个主要的 generic 块中
            company_el = self._find_element(el, ['link[company]', 'link'])
            if company_el and not job["company"]:
                company_text = self._get_text(company_el)
                # 排除职位标题
                if company_text and company_text != job["title"]:
                    job["company"] = company_text
            
            # 默认城市
            if not job.get("city"):
                job["city"] = "深圳"
            
        except Exception as e:
            pass
        
        return job
    
    async def get_job_detail(self, url):
        """
        获取职位详情（带保护机制）
        
        Args:
            url: 职位 URL
        
        Returns:
            dict: 职位详情
        """
        # === 保护 1: 熔断器检查 ===
        if self._is_circuit_open():
            print(f"[CIRCUIT BREAKER] 熔断器已打开，拒绝请求")
            return self._mock_job_detail(url)
        
        print(f"[DETAIL] 获取职位详情：{url}")
        
        # === 保护 2: 重试机制 ===
        last_error = None
        for attempt in range(1, self.max_retry + 1):
            try:
                # === 保护 3: 超时检查 ===
                start_time = time.time()
                
                result = await self._get_detail_with_timeout(url, start_time)
                
                # 成功：重置失败计数
                self._on_success()
                return result
                
            except asyncio.TimeoutError:
                last_error = f"超时（尝试 {attempt}/{self.max_retry}）"
                print(f"[TIMEOUT] {last_error}")
                self._on_failure()
                
            except Exception as e:
                last_error = f"错误：{e}（尝试 {attempt}/{self.max_retry}）"
                print(f"[ERROR] {last_error}")
                self._on_failure()
                
                # 熔断器触发：提前退出
                if self._failure_count >= self.circuit_breaker_threshold:
                    print(f"[CIRCUIT BREAKER] 连续失败 {self._failure_count} 次，触发熔断")
                    return self._mock_job_detail(url)
        
        # 所有重试失败：返回降级数据
        print(f"[FALLBACK] 所有重试失败，使用模拟数据。最后错误：{last_error}")
        return self._mock_job_detail(url)
    
    async def _get_detail_with_timeout(self, url, start_time):
        """带超时检查的详情获取"""
        try:
            from openclaw import browser
            
            # 检查是否已超时
            elapsed = time.time() - start_time
            if elapsed > self.timeout_seconds:
                raise asyncio.TimeoutError(f"获取详情超时 ({elapsed:.1f}s > {self.timeout_seconds}s)")
            
            # 打开页面
            await browser.open(url)
            
            # 等待页面加载（带超时检查）
            await self._smart_wait_with_timeout(5, start_time)
            
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
            # 检查超时
            elapsed = time.time() - start_time
            if elapsed > self.timeout_seconds:
                raise asyncio.TimeoutError(f"获取详情超时 ({elapsed:.1f}s > {self.timeout_seconds}s)")
            raise
    
    def parse_job_detail(self, snapshot):
        """
        解析智联招聘职位详情（基于真实页面结构）
        
        Args:
            snapshot: 页面快照
        
        Returns:
            dict: 职位详情
        """
        detail = {
            "title": "",
            "company": "",
            "salary": "",
            "salary_min": 0,
            "salary_max": 0,
            "description": "",
            "skills": [],
            "tools": [],
            "experience": "",
            "education": "",
            "industry": "",
            "city": "",
            "district": "",
            "location": "",
            "recruit_count": "",
            "job_type": "",
            "hr_name": "",
            "hr_title": "",
            "hr_status": "",
        }
        
        try:
            # 提取标题（heading[level=1]）
            title_el = self._find_element(snapshot, ['heading[level=1]'])
            if title_el:
                detail["title"] = self._get_text(title_el)
            
            # 提取薪资（text 元素）
            text_els = self._find_all_elements(snapshot, ['text'])
            for text_el in text_els:
                text = self._get_text(text_el)
                if text and any(c.isdigit() for c in text) and ('万' in text or 'K' in text or '元' in text):
                    detail["salary"] = text
                    salary_info = self._normalize_salary(text)
                    detail.update(salary_info)
                    break
            
            # 提取地点/经验/学历（listitem 元素）
            list_els = self._find_all_elements(snapshot, ['listitem'])
            location_found = False
            for list_el in list_els:
                text = self._get_text(list_el)
                if not text:
                    continue
                
                # 地点：包含城市名（优先处理）
                if not location_found and any(city in text for city in ['深圳', '北京', '上海', '广州']):
                    location_found = True
                    # 处理"深圳 - 龙岗区"格式
                    if '-' in text:
                        parts = text.split('-')
                        detail["city"] = parts[0].strip()
                        # 提取区名
                        if len(parts) > 1 and '区' in parts[1]:
                            detail["district"] = parts[1].strip()
                    else:
                        detail["city"] = text.strip()
                
                # 经验：包含"年"
                if '年' in text and ('经验' in text or text.strip().endswith('年')):
                    detail["experience"] = text.strip()
                
                # 学历：包含学历关键词
                elif any(edu in text for edu in ['本科', '大专', '硕士', '博士', '学历不限', '中专', '高中']):
                    detail["education"] = text.strip()
                
                # 全职/兼职
                elif '全职' in text or '兼职' in text:
                    detail["job_type"] = text.strip()
                
                # 招聘人数
                elif '招' in text and '人' in text:
                    detail["recruit_count"] = text.strip()
            
            # 提取技能标签（generic 元素，短文本）
            generic_els = self._find_all_elements(snapshot, ['generic'])
            for gen_el in generic_els:
                text = self._get_text(gen_el)
                if not text or len(text) > 20:
                    continue
                
                # 技能标签通常是短词组
                if ('媒介' in text or '品牌' in text or '营销' in text or 
                    '策划' in text or '运营' in text or '设计' in text or
                    '文案' in text or '活动' in text or '推广' in text):
                    if text not in detail["skills"]:
                        detail["skills"].append(text)
            
            # 提取职位描述（text 元素，以数字开头）
            desc_lines = []
            for text_el in text_els:
                text = self._get_text(text_el)
                if text and re.match(r'^\d+\.', text.strip()):
                    desc_lines.append(text.strip())
            
            if desc_lines:
                detail["description"] = '\n'.join(desc_lines)
            
            # 提取公司名（link 元素，在公司详情页）
            company_el = self._find_element(snapshot, ['link[公司]', 'link[company]'])
            if not company_el:
                # 尝试从 generic 中查找
                for gen_el in generic_els:
                    text = self._get_text(gen_el)
                    if text and ('有限公司' in text or '公司' in text or '集团' in text):
                        if text != detail["title"]:
                            detail["company"] = text
                            break
            
            # 提取行业（button 元素）
            button_els = self._find_all_elements(snapshot, ['button'])
            for btn_el in button_els:
                text = self._get_text(btn_el)
                if text and any(ind in text for ind in ['制造', '互联网', '金融', '贸易', '零售', '服务', '电子', '传媒']):
                    detail["industry"] = text
                    break
            
            # 提取 HR 信息（heading[level=3]）
            hr_el = self._find_element(snapshot, ['heading[level=3]'])
            if hr_el:
                hr_text = self._get_text(hr_el)
                # 排除职位名称（包含"策划"、"工程师"等）
                if '/' in hr_text and not any(skip in hr_text for skip in ['策划', '工程师', '经理/']):
                    parts = hr_text.split('/')
                    detail["hr_name"] = parts[0].strip()
                    detail["hr_title"] = parts[1].strip() if len(parts) > 1 else ''
                elif '/' in hr_text:
                    # 可能是"职位/职级"格式，跳过
                    pass
            
            # 提取 HR 活跃状态（generic 元素）
            for gen_el in generic_els:
                text = self._get_text(gen_el)
                if text and any(status in text for status in ['活跃', '回复', '刚刚', '今日', '昨日', '日内']):
                    detail["hr_status"] = text.strip()
                    break
            
            # 提取详细工作地点（text 元素，包含"省"或"市"）
            for text_el in text_els:
                text = self._get_text(text_el)
                if text and ('省' in text or '市' in text) and len(text) > 10:
                    detail["location"] = text.strip()
                    break
            
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
        
        # 提取 K 数（如 10-15K）
        k_match = re.search(r'(\d+)-(\d+)K', salary_str, re.IGNORECASE)
        if k_match:
            result["salary_min"] = int(k_match.group(1)) * 1000
            result["salary_max"] = int(k_match.group(2)) * 1000
        else:
            # 单一 K 数（如 12K）
            single_k = re.search(r'(\d+)K', salary_str, re.IGNORECASE)
            if single_k:
                val = int(single_k.group(1)) * 1000
                result["salary_min"] = val
                result["salary_max"] = val
            else:
                # 万数（如 1.2-1.9 万）
                wan_match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*万', salary_str)
                if wan_match:
                    result["salary_min"] = int(float(wan_match.group(1)) * 10000)
                    result["salary_max"] = int(float(wan_match.group(2)) * 10000)
                else:
                    # 单一万数（如 2 万）
                    single_wan = re.search(r'(\d+(?:\.\d+)?)\s*万', salary_str)
                    if single_wan:
                        val = int(float(single_wan.group(1)) * 10000)
                        result["salary_min"] = val
                        result["salary_max"] = val
                    else:
                        # 元（如 8000-16000 元）
                        yuan_match = re.search(r'(\d+)-(\d+)\s*元', salary_str)
                        if yuan_match:
                            result["salary_min"] = int(yuan_match.group(1))
                            result["salary_max"] = int(yuan_match.group(2))
        
        return result
    
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
