"""
行业匹配器 - Industry Graph
基于行业树计算行业相似度
"""

import json
import os

class IndustryMatcher:
    """行业匹配器"""
    
    def __init__(self, tree_file=None):
        """
        初始化行业匹配器
        
        Args:
            tree_file: 行业树 JSON 文件路径，默认使用 data/industry_tree.json
        """
        if tree_file is None:
            tree_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'industry_tree.json')
        
        with open(tree_file, 'r', encoding='utf-8') as f:
            self.tree = json.load(f)
        
        # 构建反向索引：子行业→父行业
        self.child_to_parent = {}
        for parent, children in self.tree.items():
            for child in children:
                self.child_to_parent[child] = parent
    
    def match(self, user_industry, job_industry):
        """
        计算行业相似度
        
        Args:
            user_industry: 用户所在行业
            job_industry: 职位所在行业
        
        Returns:
            float: 相似度分数 (0.2-1.0)
                1.0 - 完全相同
                0.8 - 父子关系
                0.6 - 同级关系
                0.3 - 弱相关
                0.2 - 无关
        """
        if not user_industry or not job_industry:
            return 0.5  # 未知行业，中等分数
        
        # 完全相同
        if user_industry == job_industry:
            return 1.0
        
        # 获取父行业
        user_parent = self.child_to_parent.get(user_industry, user_industry)
        job_parent = self.child_to_parent.get(job_industry, job_industry)
        
        # 父子关系检查
        if user_parent == job_parent:
            # 用户在父行业，职位在子行业
            if user_industry == user_parent and job_industry in self.tree.get(user_industry, []):
                return 0.8
            # 用户在子行业，职位在父行业
            if job_industry == job_parent and user_industry in self.tree.get(job_industry, []):
                return 0.8
            # 同级关系（同一父行业下的不同子行业）
            return 0.6
        
        # 弱相关检查（特定行业组合）
        weak_relations = {
            ("广告", "互联网"): 0.3,
            ("互联网", "广告"): 0.3,
            ("广告", "文化传媒"): 0.3,
            ("文化传媒", "广告"): 0.3,
            ("互联网", "科技"): 0.3,
            ("科技", "互联网"): 0.3,
            ("消费品", "服务业"): 0.3,
            ("服务业", "消费品"): 0.3,
            ("制造业", "科技"): 0.3,
            ("科技", "制造业"): 0.3,
        }
        
        relation = weak_relations.get((user_parent, job_parent), 0.2)
        return relation
    
    def get_parent(self, industry):
        """获取父行业"""
        return self.child_to_parent.get(industry, industry)
    
    def get_children(self, industry):
        """获取子行业列表"""
        return self.tree.get(industry, [])
    
    def get_all_industries(self):
        """获取所有行业（父 + 子）"""
        all_industries = set(self.tree.keys())
        for children in self.tree.values():
            all_industries.update(children)
        return list(all_industries)
    
    def is_valid_industry(self, industry):
        """检查行业是否有效"""
        return industry in self.get_all_industries()


# 测试代码
if __name__ == "__main__":
    matcher = IndustryMatcher()
    
    print("行业匹配器测试：")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        ("广告", "广告", 1.0),
        ("广告", "品牌咨询", 0.8),
        ("品牌咨询", "广告", 0.8),
        ("品牌咨询", "营销策划", 0.6),
        ("广告", "电商", 0.3),
        ("广告", "金融", 0.2),
        ("互联网", "AI", 0.8),
        ("AI", "电商", 0.6),
        ("科技", "互联网", 0.3),
    ]
    
    for user_ind, job_ind, expected in test_cases:
        result = matcher.match(user_ind, job_ind)
        status = "OK" if abs(result - expected) < 0.01 else "WARN"
        print(f"[{status}] {user_ind} -> {job_ind}: {result} (expected: {expected})")
    
    print("=" * 50)
    print(f"所有行业：{matcher.get_all_industries()}")
