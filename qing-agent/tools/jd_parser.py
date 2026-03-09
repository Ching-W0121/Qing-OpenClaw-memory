"""
JD 解析器 - 从职位描述提取结构化数据
增强版：扩展词库 + 优化提取逻辑
"""

import re

class JDParser:
    """JD 解析器（增强版）"""
    
    def __init__(self):
        # 技能词库（100+ 关键词）
        self.skill_keywords = [
            # 品牌/营销类
            "品牌策划", "营销策划", "品牌推广", "品牌管理", "市场策划",
            "活动策划", "活动执行", "公关", "媒介", "新媒体运营",
            "内容运营", "用户运营", "产品运营", "社群运营",
            "文案写作", "创意文案", "广告文案", "软文写作",
            "创意设计", "视觉设计", "平面设计", "UI 设计",
            "项目管理", "项目管理", "团队协作", "跨部门沟通",
            "数据分析", "市场调研", "用户研究", "竞品分析",
            "SEO", "SEM", "信息流广告", "精准营销",
            "直播运营", "短视频运营", "内容创作", "编导",
            # 通用技能
            "沟通表达", "逻辑思维", "创新能力", "执行力",
            "抗压能力", "学习能力", "领导力", "组织能力",
        ]
        
        # 工具词库（50+ 关键词）
        self.tool_keywords = [
            # Office 系列
            "Office", "Word", "Excel", "PPT", "PowerPoint",
            # 设计类
            "Photoshop", "PS", "Illustrator", "AI", "Sketch",
            "Figma", "XD", "InDesign", "ID", "CorelDRAW",
            # 数据分析
            "SQL", "Python", "R", "SPSS", "Tableau",
            "PowerBI", "Excel 高级", "VBA",
            # 办公协作
            "钉钉", "企业微信", "飞书", "Slack",
            "Teambition", "Trello", "Jira", "Notion",
            # 新媒体
            "微信公众号", "小红书", "抖音", "B 站", "微博",
            "知乎", "快手", "视频号",
            # 其他
            "XMind", "MindManager", "Visio", "Axure",
            "Final Cut", "Premiere", "AE", "After Effects",
        ]
        
        # 行业词库
        self.industry_keywords = [
            "广告", "互联网", "消费品", "科技", "文化传媒",
            "金融", "制造业", "服务业", "医疗健康", "教育",
            "房地产", "能源", "电商", "游戏", "影视",
            "音乐", "出版", "零售", "物流", "旅游",
            "餐饮", "酒店", "美容", "体育", "汽车",
        ]
        
        # 学历等级映射
        self.edu_levels = {
            "博士": 6,
            "硕士": 5,
            "本科": 4,
            "大专": 3,
            "中专": 2,
            "高中": 2,
            "初中": 1,
        }
        
        # 岗位类型关键词
        self.job_type_keywords = [
            "全职", "兼职", "实习", "外包", "劳务派遣",
            "初级", "中级", "高级", "资深", "专家", "首席",
            "助理", "专员", "主管", "经理", "总监", "副总裁", "总裁",
            "组长", "主管", "负责人",
        ]
    
    def parse(self, jd_text):
        """
        解析 JD 文本
        
        Args:
            jd_text: JD 原文
        
        Returns:
            dict: 结构化数据
        """
        if not jd_text:
            return self._empty_result()
        
        return {
            "skills": self._extract_skills(jd_text),
            "tools": self._extract_tools(jd_text),
            "experience": self._extract_experience(jd_text),
            "education": self._extract_education(jd_text),
            "industry": self._extract_industry(jd_text),
            "job_type": self._extract_job_type(jd_text),
            "salary": self._extract_salary(jd_text),
            "company_size": self._extract_company_size(jd_text),
        }
    
    def _empty_result(self):
        """返回空结果"""
        return {
            "skills": [],
            "tools": [],
            "experience": "不限",
            "education": "不限",
            "industry": "",
            "job_type": "全职",
            "salary": "",
            "company_size": "",
        }
    
    def _extract_skills(self, text):
        """提取技能关键词"""
        skills = []
        text_lower = text.lower()
        
        for skill in self.skill_keywords:
            # 不区分大小写匹配
            if skill.lower() in text_lower or skill in text:
                skills.append(skill)
        
        # 去重
        return list(dict.fromkeys(skills))
    
    def _extract_tools(self, text):
        """提取工具/软件"""
        tools = []
        text_lower = text.lower()
        
        for tool in self.tool_keywords:
            # 不区分大小写匹配
            if tool.lower() in text_lower or tool in text:
                tools.append(tool)
        
        # 去重
        return list(dict.fromkeys(tools))
    
    def _extract_experience(self, text):
        """提取经验要求"""
        # 优先匹配具体年限
        patterns = [
            r'(\d+-\d+ 年)',           # 3-5 年
            r'(\d+ 年以上)',            # 3 年以上
            r'(\d+ 年以下)',            # 3 年以下
            r'(\d+-\d+ 年经验)',        # 3-5 年经验
            r'(\d+ 年经验)',            # 3 年经验
            r'经验不限',                # 经验不限
            r'不限经验',                # 不限经验
            r'应届生',                  # 应届生
            r'应届',                    # 应届
            r'无经验要求',              # 无经验要求
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return "不限"
    
    def _extract_education(self, text):
        """提取学历要求"""
        # 按学历等级降序匹配（优先匹配高学历）
        edu_order = ["博士", "硕士", "本科", "大专", "中专", "高中", "初中"]
        
        for edu in edu_order:
            if edu in text:
                return edu
        
        # 检查"不限"
        if any(x in text for x in ["学历不限", "不限学历", "不限"]):
            return "不限"
        
        return "不限"
    
    def _extract_industry(self, text):
        """提取行业"""
        # 统计匹配的行业关键词
        industry_scores = {}
        
        for industry in self.industry_keywords:
            if industry in text:
                # 计算出现次数
                count = text.count(industry)
                industry_scores[industry] = count
        
        if not industry_scores:
            return ""
        
        # 返回出现次数最多的行业
        return max(industry_scores, key=industry_scores.get)
    
    def _extract_job_type(self, text):
        """提取岗位类型"""
        # 工作性质
        for job_type in ["全职", "兼职", "实习", "外包", "劳务派遣"]:
            if job_type in text:
                break
        else:
            job_type = "全职"  # 默认全职
        
        # 职位级别
        level_keywords = ["首席", "总裁", "副总裁", "总监", "经理", "主管", "组长", 
                         "专家", "资深", "高级", "中级", "初级", "助理", "专员"]
        
        level = ""
        for lvl in level_keywords:
            if lvl in text:
                level = lvl
                break
        
        # 组合结果
        if level:
            return f"{job_type} ({level})"
        else:
            return job_type
    
    def _extract_salary(self, text):
        """提取薪资信息"""
        patterns = [
            r'(\d+-\d+K)',              # 10-15K
            r'(\d+-\d+K·\d+ 薪)',       # 10-15K·13 薪
            r'(\d+-\d+ 万)',            # 15-20 万
            r'(\d+-\d+ 万/年)',         # 15-20 万/年
            r'(\d+-\d+ 万·\d+ 薪)',     # 15-20 万·13 薪
            r'(\d+K)',                  # 15K
            r'(\d+K·\d+ 薪)',           # 15K·13 薪
            r'(\d+-\d+ 元)',            # 10000-15000 元
            r'(\d+-\d+ 元/月)',         # 10000-15000 元/月
            r'薪资面议',                # 薪资面议
            r'面议',                    # 面议
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return ""
    
    def _extract_company_size(self, text):
        """提取公司规模"""
        patterns = [
            r'(\d+-\d+ 人)',            # 100-500 人
            r'(\d+ 人以上)',            # 1000 人以上
            r'(\d+ 人以下)',            # 100 人以下
            r'(\d+) 人',                # 100 人
            r'上市公司',                 # 上市公司
            r'天使轮',                  # 天使轮
            r'A 轮',                    # A 轮
            r'B 轮',                    # B 轮
            r'C 轮',                    # C 轮
            r'D 轮',                    # D 轮
            r'已上市',                  # 已上市
            r'未融资',                  # 未融资
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return ""
    
    def parse_to_profile(self, jd_text):
        """
        解析 JD 为职位画像（用于匹配）
        
        Args:
            jd_text: JD 原文
        
        Returns:
            dict: 职位画像
        """
        parsed = self.parse(jd_text)
        
        # 转换为匹配引擎可用的格式
        profile = {
            "skills": parsed["skills"],
            "tools": parsed["tools"],
            "industry": parsed["industry"],
            "experience": parsed["experience"],
            "education": parsed["education"],
        }
        
        # 解析经验年限
        exp_match = re.search(r'(\d+)', parsed["experience"])
        if exp_match:
            profile["experience_years"] = int(exp_match.group(1))
        else:
            profile["experience_years"] = 0
        
        return profile


# 测试代码
if __name__ == "__main__":
    parser = JDParser()
    
    # 测试 JD 文本
    test_jd = """
    职位：品牌策划经理
    薪资：12-18K·13 薪
    
    岗位职责：
    1. 负责品牌策划和推广工作
    2. 撰写文案和创意内容
    3. 策划和执行营销活动
    4. 数据分析与市场调研
    
    任职要求：
    1. 本科及以上学历，3-5 年相关工作经验
    2. 精通 Office 软件，熟练使用 Photoshop
    3. 具备良好的沟通表达能力和团队协作精神
    4. 有广告或互联网行业经验者优先
    
    公司规模：100-500 人，B 轮融资
    """
    
    result = parser.parse(test_jd)
    
    print("JD 解析结果：")
    print("=" * 50)
    print(f"技能：{result['skills']}")
    print(f"工具：{result['tools']}")
    print(f"经验：{result['experience']}")
    print(f"学历：{result['education']}")
    print(f"行业：{result['industry']}")
    print(f"岗位类型：{result['job_type']}")
    print(f"薪资：{result['salary']}")
    print(f"公司规模：{result['company_size']}")
    print("=" * 50)
    
    # 测试职位画像
    profile = parser.parse_to_profile(test_jd)
    print(f"\n职位画像：{profile}")
