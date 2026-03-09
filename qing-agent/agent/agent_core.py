"""
Agent 核心
"""

from agent.planner import Planner
from pipeline.job_pipeline import JobPipeline

class AgentCore:
    """Agent 核心"""
    
    def __init__(self):
        self.planner = Planner()
        self.pipeline = JobPipeline()
    
    async def handle_request(self, user_input, user_id=None):
        """
        处理用户请求
        
        Args:
            user_input: 用户输入
            user_id: 用户 ID
        
        Returns:
            str: 响应文本
        """
        # 1. 分析意图
        intent = self.planner.analyze_intent(user_input)
        
        # 2. 生成计划
        context = {"user_id": user_id}
        tasks = self.planner.plan(intent, context)
        
        print(f"📋 意图：{intent}")
        print(f"📝 任务计划：{tasks}")
        
        # 3. 执行计划
        if intent == "find_job":
            result = await self.pipeline.run(user_id)
            return self._format_recommendations(result)
        
        elif intent == "apply":
            # 提取职位 ID
            job_ids = self._extract_job_ids(user_input)
            result = await self.pipeline.run_with_apply(user_id, job_ids)
            return self._format_apply_result(result)
        
        elif intent == "analyze_market":
            result = await self._analyze_market(user_id)
            return self._format_analysis(result)
        
        else:
            return "抱歉，我还没学会这个功能。"
    
    def _format_recommendations(self, matches):
        """格式化推荐结果"""
        if not matches:
            return "😅 没有找到匹配的职位。"
        
        output = "🎯 为您推荐以下职位：\n\n"
        
        for i, item in enumerate(matches, 1):
            job = item["job"]
            match = item["match"]
            
            output += f"{i}. **{job.get('title', '未知职位')}** - {job.get('company', '未知公司')}\n"
            output += f"   匹配度：{match['total']*100:.1f}%\n"
            output += f"   薪资：{job.get('salary', '面议')}\n"
            output += f"   地点：{job.get('city', '')}{job.get('district', '')}\n"
            output += f"   链接：{job.get('url', '')}\n\n"
        
        return output
    
    def _format_apply_result(self, applications):
        """格式化投递结果"""
        if not applications:
            return "😅 没有可投递的职位。"
        
        output = "✅ 投递完成：\n\n"
        
        for app in applications:
            job = app["job"]
            output += f"- {job.get('title', '')} - {job.get('company', '')}\n"
        
        return output
    
    async def _analyze_market(self, user_id):
        """分析市场趋势"""
        # TODO: 实现市场分析
        return {"trend": "市场需求稳定"}
    
    def _format_analysis(self, analysis):
        """格式化分析结果"""
        return f"📊 市场分析：{analysis}"
    
    def _extract_job_ids(self, user_input):
        """从用户输入提取职位 ID"""
        # TODO: 实现 ID 提取逻辑
        return []
