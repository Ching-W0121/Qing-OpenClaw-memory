"""
职位评分工具
综合评分：匹配度 + 薪资 + 城市 + 关键词 + 行业
"""

from typing import Dict, Any, List

class JobScorer:
    """职位评分器"""
    
    def __init__(self):
        # 权重配置
        self.weights = {
            'match_score': 0.40,      # 匹配度 40%
            'salary_score': 0.25,     # 薪资 25%
            'city_score': 0.15,       # 城市 15%
            'keyword_score': 0.10,    # 关键词 10%
            'industry_score': 0.10,   # 行业 10%
        }
        
        # 期望城市
        self.expected_cities = ['深圳']
        
        # 优先区域
        self.preferred_districts = ['南山', '福田', '罗湖', '龙岗', '宝安', '龙华']
        
        # 排除区域
        self.excluded_districts = ['宝安']  # 可根据需要调整
        
        # 关键词权重
        self.priority_keywords = ['品牌策划', '品牌宣传', '活动策划', '新媒体', '内容策划']
    
    def calculate_score(self, user_profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算职位综合评分
        
        Args:
            user_profile: 用户画像
            job: 职位信息
        
        Returns:
            评分详情
        """
        # 1. 匹配度评分（来自 matcher）
        match_score = self._calculate_match_score(user_profile, job)
        
        # 2. 薪资评分
        salary_score = self._calculate_salary_score(user_profile, job)
        
        # 3. 城市评分
        city_score = self._calculate_city_score(user_profile, job)
        
        # 4. 关键词评分
        keyword_score = self._calculate_keyword_score(user_profile, job)
        
        # 5. 行业评分
        industry_score = self._calculate_industry_score(user_profile, job)
        
        # 加权总分
        total_score = (
            match_score * self.weights['match_score'] +
            salary_score * self.weights['salary_score'] +
            city_score * self.weights['city_score'] +
            keyword_score * self.weights['keyword_score'] +
            industry_score * self.weights['industry_score']
        )
        
        return {
            'total_score': total_score,
            'match_score': match_score,
            'salary_score': salary_score,
            'city_score': city_score,
            'keyword_score': keyword_score,
            'industry_score': industry_score,
            'weights': self.weights,
        }
    
    def _calculate_match_score(self, user_profile: Dict[str, Any], job: Dict[str, Any]) -> float:
        """计算匹配度评分（0-1）"""
        # 如果 job 已经有 match 结果，直接使用
        if 'match' in job and isinstance(job['match'], dict):
            match = job['match']
            # 归一化到 0-1
            total = match.get('total', 0)
            if isinstance(total, (int, float)):
                # 如果 total 是百分比（>1），归一化
                return min(total / 100.0, 1.0) if total > 1 else total
        
        # 否则使用默认值
        return 0.5
    
    def _calculate_salary_score(self, user_profile: Dict[str, Any], job: Dict[str, Any]) -> float:
        """计算薪资评分（0-1）"""
        expected_min = user_profile.get('expected_salary_min', 8000)
        expected_max = user_profile.get('expected_salary_max', 15000)
        
        job_min = job.get('salary_min', 0)
        job_max = job.get('salary_max', 0)
        
        if job_min == 0 and job_max == 0:
            return 0.5  # 无薪资信息
        
        # 计算重叠度
        overlap_min = max(expected_min, job_min)
        overlap_max = min(expected_max, job_max)
        
        if overlap_min > overlap_max:
            # 无重叠
            if job_min > expected_max:
                # 职位薪资高于期望，加分
                return min(1.0, 0.8 + (job_min - expected_max) / expected_max * 0.2)
            else:
                # 职位薪资低于期望
                return max(0.2, job_max / expected_min * 0.5)
        
        # 有重叠，计算重叠比例
        job_range = job_max - job_min if job_max > job_min else job_min
        overlap_range = overlap_max - overlap_min
        
        if job_range > 0:
            overlap_ratio = overlap_range / job_range
        else:
            overlap_ratio = 1.0
        
        return min(overlap_ratio, 1.0)
    
    def _calculate_city_score(self, user_profile: Dict[str, Any], job: Dict[str, Any]) -> float:
        """计算城市评分（0-1）"""
        expected_city = user_profile.get('expected_city', '深圳')
        job_city = job.get('city', '')
        job_district = job.get('district', '')
        
        # 城市匹配
        if expected_city in job_city or job_city in expected_city:
            city_match = 1.0
        else:
            city_match = 0.3
        
        # 区域加分/减分
        district_score = 0.5
        if job_district:
            if job_district in self.preferred_districts:
                district_score = 0.8
            if job_district in self.excluded_districts:
                district_score = 0.3
        
        return (city_match + district_score) / 2
    
    def _calculate_keyword_score(self, user_profile: Dict[str, Any], job: Dict[str, Any]) -> float:
        """计算关键词评分（0-1）"""
        target_jobs = user_profile.get('target_jobs', [])
        job_title = job.get('title', '').lower()
        
        # 检查职位标题是否包含目标关键词
        matches = 0
        for keyword in target_jobs:
            if keyword.lower() in job_title:
                matches += 1
        
        if matches == 0:
            # 检查优先级关键词
            for keyword in self.priority_keywords:
                if keyword.lower() in job_title:
                    return 0.7
            return 0.4
        
        # 匹配比例
        return min(matches / len(target_jobs), 1.0) * 0.8 + 0.2
    
    def _calculate_industry_score(self, user_profile: Dict[str, Any], job: Dict[str, Any]) -> float:
        """计算行业评分（0-1）"""
        # 优先行业
        preferred_industries = ['互联网', '传媒', '广告', '营销', '文化传播', '科技']
        
        job_industry = job.get('industry', '')
        
        if not job_industry:
            return 0.5
        
        # 检查是否包含优先行业关键词
        for industry in preferred_industries:
            if industry in job_industry:
                return 0.9
        
        return 0.6

def score_jobs(user_profile: Dict[str, Any], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    便捷函数：为职位列表评分
    
    Args:
        user_profile: 用户画像
        jobs: 职位列表
    
    Returns:
        带评分的职位列表
    """
    scorer = JobScorer()
    
    scored_jobs = []
    for job in jobs:
        score_result = scorer.calculate_score(user_profile, job)
        job_with_score = job.copy()
        job_with_score['score_detail'] = score_result
        job_with_score['total_score'] = score_result['total_score']
        scored_jobs.append(job_with_score)
    
    return scored_jobs
