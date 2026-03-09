"""
任务规划器 - Agent 决策系统
"""

class Planner:
    """Agent 任务规划器"""
    
    def __init__(self):
        self.pipelines = {
            "find_job": [
                "parse_resume",
                "search_jobs",
                "parse_jd",
                "calculate_match",
                "rank_jobs",
                "recommend"
            ],
            "apply": [
                "open_job",
                "submit_application",
                "track_status"
            ],
            "analyze_market": [
                "search_jobs",
                "aggregate_stats",
                "generate_report"
            ]
        }
    
    def plan(self, intent, context=None):
        """
        根据用户意图生成任务计划
        
        Args:
            intent: 用户意图（find_job, apply, analyze_market）
            context: 上下文信息
        
        Returns:
            list: 任务列表
        """
        if intent not in self.pipelines:
            raise ValueError(f"未知意图：{intent}")
        
        base_tasks = self.pipelines[intent]
        
        # 根据上下文调整任务
        if context:
            if context.get("skip_resume_parse"):
                base_tasks = [t for t in base_tasks if t != "parse_resume"]
            
            if context.get("auto_apply"):
                base_tasks.append("auto_apply")
        
        return base_tasks
    
    def analyze_intent(self, user_input):
        """
        分析用户输入，识别意图
        
        Args:
            user_input: 用户输入文本
        
        Returns:
            str: 意图
        """
        user_input = user_input.lower()
        
        if any(word in user_input for word in ["找工", "求职", "推荐职位", "找工作"]):
            return "find_job"
        
        if any(word in user_input for word in ["投递", "申请", "报名", "应聘"]):
            return "apply"
        
        if any(word in user_input for word in ["分析", "市场", "趋势", "报告"]):
            return "analyze_market"
        
        return "find_job"  # 默认
