"""
匹配引擎 - 7 维匹配算法
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.industry_matcher import IndustryMatcher

class MatchingEngine:
    """匹配引擎（7 维）"""
    
    def __init__(self):
        self.industry_matcher = IndustryMatcher()
        self.weights = {
            "industry": 0.25,    # 行业匹配
            "skill": 0.25,       # 技能匹配
            "experience": 0.15,  # 经验匹配
            "salary": 0.10,      # 薪资匹配
            "location": 0.10,    # 地点匹配
            "education": 0.10,   # 学历匹配
            "tools": 0.05,       # 工具匹配
        }
    
    def calculate_match(self, user_profile, job_profile):
        """
        计算匹配度
        
        Args:
            user_profile: 用户画像 dict
            job_profile: 职位画像 dict
        
        Returns:
            dict: {
                "total": 总分 (0-1),
                "details": {各维度分数},
                "weights": 权重配置
            }
        """
        scores = {
            "industry": self._match_industry(user_profile, job_profile),
            "skill": self._match_skills(user_profile, job_profile),
            "experience": self._match_experience(user_profile, job_profile),
            "salary": self._match_salary(user_profile, job_profile),
            "location": self._match_location(user_profile, job_profile),
            "education": self._match_education(user_profile, job_profile),
            "tools": self._match_tools(user_profile, job_profile),
        }
        
        total_score = sum(
            scores[key] * self.weights[key]
            for key in scores
        )
        
        return {
            "total": total_score,
            "details": scores,
            "weights": self.weights
        }
    
    def _match_industry(self, user, job):
        """行业匹配（使用 IndustryMatcher）"""
        user_industry = user.get("industry", "")
        job_industry = job.get("industry", "")
        
        if not job_industry:
            return 0.5
        
        return self.industry_matcher.match(user_industry, job_industry)
    
    def _match_skills(self, user, job):
        """技能匹配（Jaccard 相似度）"""
        user_skills = set(user.get("skills", []))
        job_skills = set(job.get("skills", []))
        
        if not job_skills:
            return 1.0
        
        intersection = len(user_skills & job_skills)
        union = len(user_skills | job_skills)
        
        return intersection / union if union > 0 else 0.0
    
    def _match_experience(self, user, job):
        """经验匹配"""
        user_years = user.get("experience_years", 0)
        job_exp = job.get("experience", "")
        
        if not job_exp:
            return 0.8
        
        # 解析职位要求（如"1-3 年"、"3-5 年"、"不限"）
        min_years, max_years = self._parse_experience(job_exp)
        
        if min_years is None:  # 不限
            return 1.0
        
        if min_years <= user_years <= max_years:
            return 1.0
        elif user_years < min_years:
            return max(0.3, 1.0 - (min_years - user_years) * 0.2)
        else:
            return max(0.5, 1.0 - (user_years - max_years) * 0.1)
    
    def _match_salary(self, user, job):
        """薪资匹配"""
        user_min = user.get("expected_salary_min", 0)
        user_max = user.get("expected_salary_max", float('inf'))
        job_min = job.get("salary_min", 0)
        job_max = job.get("salary_max", 0)
        
        if not job_max:
            return 0.5
        
        # 检查重叠
        if job_max < user_min:
            return 0.2  # 职位薪资低于用户期望
        elif job_min > user_max:
            return 0.8  # 职位薪资高于用户期望（通常是好事）
        else:
            return 1.0  # 有重叠
    
    def _match_location(self, user, job):
        """地点匹配"""
        user_city = user.get("expected_city", "")
        job_city = job.get("city", "")
        job_district = job.get("district", "")
        
        if not job_city:
            return 0.5
        
        # 简单匹配（可扩展为城市层级匹配）
        if user_city == job_city:
            return 1.0
        elif user_city in job_city or job_city in user_city:
            return 0.8
        else:
            return 0.2
    
    def _match_education(self, user, job):
        """学历匹配"""
        user_edu = user.get("education", "")
        job_edu = job.get("education", "")
        
        if not job_edu or job_edu == "不限":
            return 1.0
        
        # 学历等级
        edu_levels = {
            "初中": 1,
            "高中": 2,
            "中专": 2,
            "大专": 3,
            "本科": 4,
            "硕士": 5,
            "博士": 6,
        }
        
        user_level = edu_levels.get(user_edu, 3)
        job_level = edu_levels.get(job_edu, 3)
        
        if user_level >= job_level:
            return 1.0
        else:
            return max(0.3, 1.0 - (job_level - user_level) * 0.2)
    
    def _match_tools(self, user, job):
        """工具匹配（Jaccard 相似度）"""
        user_tools = set(user.get("tools", []))
        job_tools = set(job.get("tools", []))
        
        if not job_tools:
            return 1.0
        
        intersection = len(user_tools & job_tools)
        union = len(user_tools | job_tools)
        
        return intersection / union if union > 0 else 0.0
    
    def _parse_experience(self, exp_str):
        """
        解析经验要求字符串
        
        Returns:
            (min_years, max_years) 或 (None, None) 表示不限
        """
        if not exp_str or "不限" in exp_str or "应届" in exp_str:
            return (None, None)
        
        # 提取数字（如"1-3 年"→(1, 3)）
        import re
        numbers = re.findall(r'\d+', exp_str)
        
        if len(numbers) >= 2:
            return (int(numbers[0]), int(numbers[1]))
        elif len(numbers) == 1:
            n = int(numbers[0])
            return (n, n + 2)  # 如"3 年以上"→(3, 5)
        else:
            return (None, None)
    
    def get_match_level(self, score):
        """
        根据分数返回匹配等级
        
        Returns:
            str: 匹配等级描述
        """
        if score >= 0.85:
            return "极佳匹配"
        elif score >= 0.75:
            return "很好匹配"
        elif score >= 0.65:
            return "较好匹配"
        elif score >= 0.55:
            return "一般匹配"
        else:
            return "匹配度低"


# 测试代码
if __name__ == "__main__":
    engine = MatchingEngine()
    
    # 测试用户画像
    user = {
        "industry": "广告",
        "skills": ["品牌策划", "文案写作", "创意设计"],
        "tools": ["Photoshop", "Illustrator"],
        "experience_years": 3,
        "education": "本科",
        "expected_city": "深圳",
        "expected_salary_min": 10000,
        "expected_salary_max": 15000,
    }
    
    # 测试职位画像
    job = {
        "industry": "广告",
        "skills": ["品牌策划", "营销策划", "文案写作"],
        "tools": ["Photoshop"],
        "experience": "3-5 年",
        "education": "本科",
        "city": "深圳",
        "district": "南山区",
        "salary_min": 12000,
        "salary_max": 18000,
    }
    
    result = engine.calculate_match(user, job)
    
    print("匹配结果：")
    print(f"总分：{result['total']*100:.1f}%")
    print(f"等级：{engine.get_match_level(result['total'])}")
    print("\n各维度：")
    for dim, score in result['details'].items():
        print(f"  {dim}: {score*100:.1f}%")
