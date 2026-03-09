"""
平台适配器基类
定义所有招聘平台适配器的统一接口
"""

from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    """平台适配器基类"""
    
    def __init__(self, name):
        """
        初始化适配器
        
        Args:
            name: 平台名称（如"boss", "zhilian"）
        """
        self.name = name
    
    @abstractmethod
    async def search_jobs(self, keyword, city=None, page=1):
        """
        搜索职位
        
        Args:
            keyword: 搜索关键词
            city: 城市
            page: 页码
        
        Returns:
            list: 职位列表
        """
        pass
    
    @abstractmethod
    async def get_job_detail(self, url):
        """
        获取职位详情
        
        Args:
            url: 职位 URL
        
        Returns:
            dict: 职位详情
        """
        pass
    
    @abstractmethod
    async def apply(self, job_url, resume=None):
        """
        申请职位
        
        Args:
            job_url: 职位 URL
            resume: 简历文件路径或内容
        
        Returns:
            dict: 投递结果
        """
        pass
    
    @abstractmethod
    def parse_search_results(self, snapshot):
        """
        解析搜索结果
        
        Args:
            snapshot: 页面快照
        
        Returns:
            list: 职位列表
        """
        pass
    
    @abstractmethod
    def parse_job_detail(self, snapshot):
        """
        解析职位详情
        
        Args:
            snapshot: 页面快照
        
        Returns:
            dict: 职位详情
        """
        pass
    
    def _normalize_salary(self, salary_str):
        """
        标准化薪资字符串
        
        Args:
            salary_str: 原始薪资字符串（如"10-15K·13 薪"）
        
        Returns:
            dict: {min, max, months}
        """
        import re
        
        result = {"min": 0, "max": 0, "months": 12}
        
        if not salary_str:
            return result
        
        # 提取 K 数（如 10-15K）
        k_match = re.search(r'(\d+(?:\.\d+)?)[Kk]-(\d+(?:\.\d+)?)[Kk]', salary_str)
        if k_match:
            result["min"] = int(float(k_match.group(1)) * 1000)
            result["max"] = int(float(k_match.group(2)) * 1000)
        else:
            # 单一 K 数
            single_k = re.search(r'(\d+(?:\.\d+)?)[Kk]', salary_str)
            if single_k:
                val = int(float(single_k.group(1)) * 1000)
                result["min"] = val
                result["max"] = val
        
        # 提取月薪数（如 13 薪）
        month_match = re.search(r'(\d+) 薪', salary_str)
        if month_match:
            result["months"] = int(month_match.group(1))
        
        return result
    
    def _normalize_experience(self, exp_str):
        """
        标准化经验要求
        
        Returns:
            str: 标准化后的经验要求
        """
        if not exp_str:
            return "不限"
        
        # 清理常见变体
        exp_str = exp_str.strip()
        
        return exp_str
