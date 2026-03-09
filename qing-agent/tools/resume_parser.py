"""
简历解析器 - 增强版
从简历文档提取结构化用户画像
"""

import re

class ResumeParser:
    """简历解析器（增强版）"""
    
    def __init__(self):
        # 技能词库
        self.skill_keywords = [
            "品牌策划", "营销策划", "品牌推广", "市场策划",
            "活动策划", "活动执行", "公关", "媒介", "新媒体运营",
            "内容运营", "用户运营", "产品运营",
            "文案写作", "创意文案", "广告文案",
            "创意设计", "视觉设计", "平面设计",
            "项目管理", "团队协作", "跨部门沟通",
            "数据分析", "市场调研", "用户研究", "竞品分析",
            "沟通表达", "逻辑思维", "创新能力",
        ]
        
        # 工具词库
        self.tool_keywords = [
            "Office", "Word", "Excel", "PPT", "PowerPoint",
            "Photoshop", "PS", "Illustrator", "AI", "Sketch",
            "Figma", "XD", "SQL", "Python",
            "钉钉", "企业微信", "飞书",
            "微信公众号", "小红书", "抖音", "B 站",
        ]
        
        # 学历关键词
        self.edu_keywords = ["博士", "硕士", "本科", "大专", "中专", "高中"]
        
        # 常见专业
        self.major_keywords = [
            "市场营销", "广告学", "新闻传播", "中文", "汉语言文学",
            "设计", "艺术设计", "视觉传达", "数字媒体",
            "工商管理", "企业管理", "经济学", "管理学",
            "计算机", "软件工程", "信息技术",
        ]
    
    def parse_docx(self, file_path):
        """解析 Word 简历"""
        try:
            from docx import Document
        except ImportError:
            raise ImportError("请安装 python-docx: pip install python-docx")
        
        doc = Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        
        return self.extract_info(text)
    
    def parse_pdf(self, file_path):
        """解析 PDF 简历"""
        try:
            import PyPDF2
        except ImportError:
            raise ImportError("请安装 PyPDF2: pip install PyPDF2")
        
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join([page.extract_text() for page in reader.pages])
        
        return self.extract_info(text)
    
    def extract_info(self, text):
        """
        提取简历信息
        
        Args:
            text: 简历文本
        
        Returns:
            dict: 用户画像
        """
        if not text:
            return self._empty_profile()
        
        return {
            "name": self._extract_name(text),
            "education": self._extract_education(text),
            "major": self._extract_major(text),
            "experience_years": self._extract_experience_years(text),
            "skills": self._extract_skills(text),
            "tools": self._extract_tools(text),
            "industry": self._extract_industry(text),
            "target_jobs": self._extract_target_jobs(text),
            "expected_city": self._extract_expected_city(text),
            "expected_salary_min": self._extract_expected_salary(text, "min"),
            "expected_salary_max": self._extract_expected_salary(text, "max"),
        }
    
    def _empty_profile(self):
        """返回空画像"""
        return {
            "name": "",
            "education": "",
            "major": "",
            "experience_years": 0,
            "skills": [],
            "tools": [],
            "industry": "",
            "target_jobs": [],
            "expected_city": "",
            "expected_salary_min": 0,
            "expected_salary_max": 0,
        }
    
    def _extract_name(self, text):
        """提取姓名"""
        # 尝试匹配"姓名：xxx"或"名字：xxx"
        patterns = [
            r'姓 [名名]\s*[:：]?\s*([a-zA-Z\u4e00-\u9fa5]{2,4})',
            r'([a-zA-Z\u4e00-\u9fa5]{2,4})\s*\n.*(?:男 | 女)',  # 姓名后跟性别
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_education(self, text):
        """提取学历"""
        for edu in self.edu_keywords:
            if edu in text:
                return edu
        
        return ""
    
    def _extract_major(self, text):
        """提取专业"""
        for major in self.major_keywords:
            if major in text:
                return major
        
        return ""
    
    def _extract_experience_years(self, text):
        """提取工作年限"""
        patterns = [
            r'(\d+)\s*年 [工从]作 [经径]验',
            r'(\d+)\s*年 [相相]关 [经径]验',
            r'工 [作作] 年 [限限]\s*[:：]?\s*(\d+)',
            r'(\d+)\s*年 [以以上]',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        
        # 尝试从工作经历推断
        work_exp_matches = re.findall(r'(\d{4})\s*-\s*(\d{4}|\d{4} 年 | 至今)', text)
        if work_exp_matches:
            total_years = 0
            for start, end in work_exp_matches:
                start_year = int(start)
                if '至今' in end:
                    end_year = 2026  # 当前年份
                else:
                    end_year = int(re.search(r'\d{4}', end).group())
                total_years += end_year - start_year
            return total_years
        
        return 0
    
    def _extract_skills(self, text):
        """提取技能"""
        skills = []
        
        for skill in self.skill_keywords:
            if skill in text:
                skills.append(skill)
        
        return list(dict.fromkeys(skills))
    
    def _extract_tools(self, text):
        """提取工具"""
        tools = []
        
        for tool in self.tool_keywords:
            if tool in text:
                tools.append(tool)
        
        return list(dict.fromkeys(tools))
    
    def _extract_industry(self, text):
        """提取行业"""
        industry_keywords = ["广告", "互联网", "消费品", "科技", "文化传媒", "金融"]
        
        for industry in industry_keywords:
            if industry in text:
                return industry
        
        return ""
    
    def _extract_target_jobs(self, text):
        """提取目标职位"""
        # 尝试匹配"期望职位：xxx"
        patterns = [
            r'期 [望望] 职 [位位]\s*[:：]?\s*([^\n]+)',
            r'求 [求职职] 意 [向向]\s*[:：]?\s*([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                jobs_str = match.group(1)
                # 分割多个职位
                jobs = [j.strip() for j in re.split(r'[,,/]', jobs_str)]
                return jobs[:5]  # 最多 5 个
        
        return []
    
    def _extract_expected_city(self, text):
        """提取期望城市"""
        patterns = [
            r'期 [望望] 城 [城市市]\s*[:：]?\s*([^\n,，]+)',
            r'工 [作作] 地 [地点点]\s*[:：]?\s*([^\n,，]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        # 常见城市
        cities = ["深圳", "广州", "北京", "上海", "杭州", "成都"]
        for city in cities:
            if city in text:
                return city
        
        return ""
    
    def _extract_expected_salary(self, text, type="min"):
        """提取期望薪资"""
        patterns = [
            r'期 [望望] 薪 [薪资资]\s*[:：]?\s*(\d+)-(\d+)[Kk]',
            r'薪 [薪资资] 期 [望望]\s*[:：]?\s*(\d+)-(\d+)[Kk]',
            r'(\d+)-(\d+)[Kk]\s*/\s*月',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                min_sal = int(match.group(1)) * 1000
                max_sal = int(match.group(2)) * 1000
                
                if type == "min":
                    return min_sal
                else:
                    return max_sal
        
        return 0


# 测试代码
if __name__ == "__main__":
    parser = ResumeParser()
    
    # 测试简历文本
    test_resume = """
    张三
    男 | 28 岁 | 13800138000
    
    期望职位：品牌策划经理、营销策划
    期望城市：深圳
    期望薪资：12-18K
    
    教育背景：
    2014-2018  深圳大学  市场营销  本科
    
    工作经历：
    2018-2021  某某广告公司  品牌策划专员
    2021-至今  某某科技公司  高级品牌策划
    
    专业技能：
    - 熟悉品牌策划和营销策划流程
    - 擅长文案写作和创意构思
    - 具备数据分析能力
    - 熟练使用 Office、Photoshop
    
    自我评价：
    5 年广告行业经验，具备良好的沟通表达能力和团队协作精神。
    """
    
    result = parser.extract_info(test_resume)
    
    print("简历解析结果：")
    print("=" * 50)
    print(f"姓名：{result['name']}")
    print(f"学历：{result['education']}")
    print(f"专业：{result['major']}")
    print(f"工作年限：{result['experience_years']}年")
    print(f"技能：{result['skills']}")
    print(f"工具：{result['tools']}")
    print(f"行业：{result['industry']}")
    print(f"目标职位：{result['target_jobs']}")
    print(f"期望城市：{result['expected_city']}")
    print(f"期望薪资：{result['expected_salary_min']}-{result['expected_salary_max']}")
    print("=" * 50)
