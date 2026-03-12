"""
推送系统
每天定时推送最佳职位
"""

import asyncio
from datetime import datetime, time
from typing import List, Dict, Any

class PushNotifier:
    """职位推送器"""
    
    def __init__(self):
        self.push_history = []
    
    def create_daily_report(self, jobs: List[Dict[str, Any]], top_n=10) -> Dict[str, Any]:
        """
        生成每日职位报告
        
        Args:
            jobs: 职位列表（已评分）
            top_n: 推荐数量
        
        Returns:
            每日报告
        """
        # 按总分排序
        sorted_jobs = sorted(
            jobs,
            key=lambda x: x.get('total_score', 0),
            reverse=True
        )
        
        # 取 Top N
        top_jobs = sorted_jobs[:top_n]
        
        # 生成报告
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'total_jobs': len(jobs),
            'top_n': top_n,
            'recommendations': [],
            'summary': {
                'avg_salary': self._calculate_avg_salary(top_jobs),
                'city_distribution': self._calculate_city_distribution(top_jobs),
                'top_companies': self._extract_top_companies(top_jobs),
            }
        }
        
        # 生成推荐列表
        for i, job in enumerate(top_jobs, 1):
            rec = {
                'rank': i,
                'title': job.get('title', 'N/A'),
                'company': job.get('company', 'N/A'),
                'salary': job.get('salary', 'N/A'),
                'city': job.get('city', 'N/A'),
                'district': job.get('district', 'N/A'),
                'total_score': job.get('total_score', 0),
                'score_detail': job.get('score_detail', {}),
                'url': job.get('url', ''),
                'highlights': self._extract_highlights(job),
            }
            report['recommendations'].append(rec)
        
        return report
    
    def format_push_message(self, report: Dict[str, Any], platform='feishu') -> str:
        """
        格式化推送消息
        
        Args:
            report: 每日报告
            platform: 推送平台（feishu/wechat/discord）
        
        Returns:
            格式化后的消息
        """
        date = report['date']
        total = report['total_jobs']
        top_n = report['top_n']
        
        # 标题
        message = f"[青·求职日报 | {date}]\n\n"
        message += f"今日共抓取 {total} 个职位，为你推荐 Top {top_n}：\n\n"
        
        # 推荐列表
        for rec in report['recommendations']:
            rank = rec['rank']
            title = rec['title']
            company = rec['company']
            salary = rec['salary']
            location = f"{rec['city']}"
            if rec.get('district'):
                location += f"·{rec['district']}"
            
            score = rec['total_score'] * 100
            highlights = ' | '.join(rec.get('highlights', []))
            
            message += f"{rank}. {title}\n"
            message += f"   公司：{company}\n"
            message += f"   薪资：{salary} | 地点：{location}\n"
            message += f"   匹配度：{score:.1f}% | {highlights}\n\n"
        
        # 总结
        summary = report['summary']
        message += "今日概览：\n"
        message += f"   平均薪资：{summary['avg_salary']}\n"
        message += f"   热门区域：{', '.join(summary['city_distribution'][:3])}\n"
        
        return message
    
    def _calculate_avg_salary(self, jobs: List[Dict[str, Any]]) -> str:
        """计算平均薪资"""
        salaries = []
        for job in jobs:
            min_sal = job.get('salary_min', 0)
            max_sal = job.get('salary_max', 0)
            if min_sal > 0 or max_sal > 0:
                avg = (min_sal + max_sal) / 2
                if avg > 0:
                    salaries.append(avg)
        
        if not salaries:
            return "N/A"
        
        avg_salary = sum(salaries) / len(salaries)
        
        # 格式化
        if avg_salary >= 10000:
            return f"{avg_salary / 10000:.1f}万"
        else:
            return f"{avg_salary / 1000:.0f}K"
    
    def _calculate_city_distribution(self, jobs: List[Dict[str, Any]]) -> List[str]:
        """计算城市分布"""
        district_count = {}
        for job in jobs:
            district = job.get('district', '其他')
            if district:
                district_count[district] = district_count.get(district, 0) + 1
        
        # 排序
        sorted_districts = sorted(
            district_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [d[0] for d in sorted_districts[:5]]
    
    def _extract_top_companies(self, jobs: List[Dict[str, Any]]) -> List[str]:
        """提取知名公司"""
        known_keywords = ['科技', '集团', '股份', '有限', '实业', '传媒', '文化', '网络']
        
        companies = []
        for job in jobs:
            company = job.get('company', '')
            if company:
                for keyword in known_keywords:
                    if keyword in company and company not in companies:
                        companies.append(company)
                        break
        
        return companies[:5]
    
    def _extract_highlights(self, job: Dict[str, Any]) -> List[str]:
        """提取职位亮点"""
        highlights = []
        
        # 高薪
        salary_min = job.get('salary_min', 0)
        if salary_min >= 15000:
            highlights.append('高薪')
        
        # 匹配度高
        score = job.get('total_score', 0)
        if score >= 0.8:
            highlights.append('高匹配')
        elif score >= 0.7:
            highlights.append('匹配')
        
        # 经验要求友好
        experience = job.get('experience', '')
        if '1-3 年' in experience or '不限' in experience:
            highlights.append('经验友好')
        
        # 学历友好
        education = job.get('education', '')
        if '不限' in education or '大专' in education:
            highlights.append('学历友好')
        
        # HR 活跃
        hr_status = job.get('hr_status', '')
        if any(s in hr_status for s in ['刚刚', '今日', '6 小时', '立即']):
            highlights.append('HR 活跃')
        
        return highlights
    
    def save_push_history(self, report: Dict[str, Any]):
        """保存推送历史"""
        self.push_history.append(report)
        
        # 限制历史记录数量
        if len(self.push_history) > 30:
            self.push_history = self.push_history[-30:]

async def schedule_daily_push(jobs: List[Dict[str, Any]], push_time=time(9, 0)):
    """
    安排每日推送
    
    Args:
        jobs: 职位列表
        push_time: 推送时间（默认 9:00）
    """
    notifier = PushNotifier()
    
    # 生成报告
    report = notifier.create_daily_report(jobs, top_n=10)
    
    # 格式化消息
    message = notifier.format_push_message(report, platform='feishu')
    
    # 保存历史
    notifier.save_push_history(report)
    
    return {
        'report': report,
        'message': message,
        'scheduled_time': push_time.isoformat(),
    }
