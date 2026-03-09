"""
推荐引擎
"""

class Recommender:
    """推荐引擎"""
    
    def __init__(self):
        pass
    
    def rank(self, matches, top_n=10):
        """
        按匹配度排序
        
        Args:
            matches: 匹配结果列表 [{"job": ..., "match": ...}]
            top_n: 返回前 N 个
        
        Returns:
            list: 排序后的推荐列表
        """
        # 按匹配度降序排序
        ranked = sorted(matches, key=lambda x: x["match"]["total"], reverse=True)
        
        # 返回 Top N
        return ranked[:top_n]
    
    def filter_by_threshold(self, matches, threshold=0.7):
        """
        按阈值过滤
        
        Args:
            matches: 匹配结果列表
            threshold: 匹配度阈值
        
        Returns:
            list: 过滤后的列表
        """
        return [m for m in matches if m["match"]["total"] >= threshold]
    
    def group_by_dimension(self, matches, dimension="industry"):
        """
        按维度分组
        
        Args:
            matches: 匹配结果列表
            dimension: 分组维度（industry, skill, etc.）
        
        Returns:
            dict: 分组结果
        """
        groups = {}
        
        for match in matches:
            job = match["job"]
            key = job.get(dimension, "未知")
            
            if key not in groups:
                groups[key] = []
            
            groups[key].append(match)
        
        # 每组内按匹配度排序
        for key in groups:
            groups[key] = sorted(groups[key], key=lambda x: x["match"]["total"], reverse=True)
        
        return groups
