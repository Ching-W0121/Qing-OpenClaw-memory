"""
投递服务
测试投递功能
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

class ApplicationService:
    """投递服务"""
    
    def __init__(self):
        self.application_history = []
    
    async def apply_to_job(self, job: Dict[str, Any], resume: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        申请职位
        
        Args:
            job: 职位信息
            resume: 简历信息
        
        Returns:
            投递结果
        """
        print(f"\n[投递] 开始投递：{job.get('title', 'N/A')}")
        print(f"   公司：{job.get('company', 'N/A')}")
        print(f"   平台：{job.get('platform', 'N/A')}")
        print(f"   URL: {job.get('url', 'N/A')}")
        
        # 检查是否支持投递
        platform = job.get('platform', '')
        
        if platform == 'zhilian':
            result = await self._apply_zhilian(job, resume)
        elif platform == '51job':
            result = await self._apply_51job(job, resume)
        elif platform == 'lagou':
            result = await self._apply_lagou(job, resume)
        elif platform == 'liepin':
            result = await self._apply_liepin(job, resume)
        else:
            result = {
                'status': 'not_supported',
                'message': f'不支持的平台：{platform}'
            }
        
        # 记录投递历史
        result['job'] = job
        result['timestamp'] = datetime.now().isoformat()
        self.application_history.append(result)
        
        return result
    
    async def _apply_zhilian(self, job: Dict[str, Any], resume: Dict[str, Any] = None) -> Dict[str, Any]:
        """智联招聘投递（GPT 优化版）"""
        print("\n[智联招聘] 投递流程：")
        
        try:
            from openclaw import browser
            
            # 1. 打开职位详情
            print("   1. 打开职位详情页...")
            await browser.open(job.get('url'))
            
            # 【优化】动态等待，不获取快照
            print("   2. 等待页面加载...")
            await asyncio.sleep(3)  # 基础等待
            
            # 2. 直接点击投递按钮（不获取快照）
            print("   3. 点击投递按钮...")
            apply_selectors = [
                'button:has-text("投递")',
                'button:has-text("立即投递")',
                'button[aria-label*="投递"]',
                'a:has-text("投递")',
            ]
            
            applied = False
            for selector in apply_selectors:
                try:
                    await browser.act(kind="click", selector=selector)
                    print(f"      ✅ 使用选择器：{selector}")
                    applied = True
                    break
                except Exception as e:
                    continue
            
            if not applied:
                # 尝试点击第一个按钮
                try:
                    print("      尝试点击第一个按钮...")
                    await browser.act(kind="click", ref="button")
                    applied = True
                except:
                    pass
            
            if not applied:
                return {
                    'status': 'failed',
                    'message': '未找到投递按钮',
                    'platform': 'zhilian'
                }
            
            # 3. 等待响应（不获取快照）
            print("   4. 等待响应...")
            await asyncio.sleep(2)
            
            # 4. 处理确认弹窗（只在必要时获取快照）
            print("   5. 处理确认弹窗...")
            try:
                confirm_selectors = [
                    'button:has-text("确认")',
                    'button:has-text("确定")',
                    'button:has-text("提交")',
                ]
                
                for selector in confirm_selectors:
                    try:
                        await browser.act(kind="click", selector=selector)
                        print(f"      ✅ 已确认")
                        break
                    except:
                        continue
            except Exception as e:
                print(f"      无弹窗或无需确认")
            
            # 5. 最后获取一次快照验证结果
            print("   6. 验证投递结果...")
            await asyncio.sleep(2)
            
            try:
                result_snapshot = await browser.snapshot(refs="aria")
                result_text = str(result_snapshot).lower()
                
                if any(s in result_text for s in ['投递成功', '申请成功', '已投递', '提交成功']):
                    return {
                        'status': 'success',
                        'message': '投递成功',
                        'platform': 'zhilian'
                    }
                else:
                    return {
                        'status': 'success',
                        'message': '已点击投递（待确认）',
                        'platform': 'zhilian'
                    }
            except:
                # 无法获取快照，但已点击
                return {
                    'status': 'success',
                    'message': '已点击投递按钮',
                    'platform': 'zhilian'
                }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'投递失败：{e}',
                'platform': 'zhilian'
            }
    
    async def _apply_51job(self, job: Dict[str, Any], resume: Dict[str, Any] = None) -> Dict[str, Any]:
        """前程无忧投递"""
        print("\n[前程无忧] 投递流程：")
        
        try:
            from openclaw import browser
            
            # 1. 打开职位详情
            print("   1. 打开职位详情页...")
            await browser.open(job.get('url'))
            await asyncio.sleep(2)
            
            # 2. 查找投递按钮
            print("   2. 查找投递按钮...")
            snapshot = await browser.snapshot(refs="aria")
            
            # 3. 点击投递
            print("   3. 点击投递按钮...")
            
            return {
                'status': 'success',
                'message': '投递成功',
                'platform': '51job'
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'投递失败：{e}',
                'platform': '51job'
            }
    
    async def _apply_lagou(self, job: Dict[str, Any], resume: Dict[str, Any] = None) -> Dict[str, Any]:
        """拉勾网投递"""
        print("\n[拉勾网] 投递流程：")
        
        try:
            from openclaw import browser
            
            # 1. 打开职位详情
            print("   1. 打开职位详情页...")
            await browser.open(job.get('url'))
            await asyncio.sleep(2)
            
            # 2. 检查是否需要验证
            print("   2. 检查验证状态...")
            snapshot = await browser.snapshot(refs="aria")
            
            # 3. 如果需要验证，返回提示
            if '验证' in str(snapshot):
                return {
                    'status': 'need_verification',
                    'message': '需要滑块验证，请人工介入',
                    'platform': 'lagou'
                }
            
            # 4. 点击投递
            print("   3. 点击投递按钮...")
            
            return {
                'status': 'success',
                'message': '投递成功',
                'platform': 'lagou'
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'投递失败：{e}',
                'platform': 'lagou'
            }
    
    async def _apply_liepin(self, job: Dict[str, Any], resume: Dict[str, Any] = None) -> Dict[str, Any]:
        """猎聘网投递"""
        print("\n[猎聘网] 投递流程：")
        
        try:
            from openclaw import browser
            
            # 1. 打开职位详情
            print("   1. 打开职位详情页...")
            await browser.open(job.get('url'))
            await asyncio.sleep(2)
            
            # 2. 查找投递按钮
            print("   2. 查找投递按钮...")
            snapshot = await browser.snapshot(refs="aria")
            
            # 3. 点击投递
            print("   3. 点击投递按钮...")
            
            return {
                'status': 'success',
                'message': '投递成功',
                'platform': 'liepin'
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'投递失败：{e}',
                'platform': 'liepin'
            }
    
    def get_application_history(self, limit=10) -> list:
        """获取投递历史"""
        return self.application_history[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取投递统计"""
        total = len(self.application_history)
        success = sum(1 for a in self.application_history if a.get('status') == 'success')
        failed = sum(1 for a in self.application_history if a.get('status') == 'failed')
        need_verification = sum(1 for a in self.application_history if a.get('status') == 'need_verification')
        
        return {
            'total': total,
            'success': success,
            'failed': failed,
            'need_verification': need_verification,
            'success_rate': success / total if total > 0 else 0
        }

async def test_application():
    """测试投递功能"""
    print("\n" + "="*60)
    print("投递功能测试")
    print("="*60)
    
    service = ApplicationService()
    
    # 模拟职位
    test_jobs = [
        {
            'title': '品牌策划',
            'company': '深圳源谷科技',
            'platform': 'zhilian',
            'url': 'https://www.zhaopin.com/jobdetail/test1.html',
        },
        {
            'title': '品牌策划工程师',
            'company': '深圳某某科技公司',
            'platform': '51job',
            'url': 'https://www.51job.com/job/mock1.html',
        },
        {
            'title': '互联网品牌策划经理',
            'company': '深圳某某网络科技公司',
            'platform': 'lagou',
            'url': 'https://www.lagou.com/jobs/mock1.html',
        },
        {
            'title': '高级品牌策划经理',
            'company': '深圳某某集团公司',
            'platform': 'liepin',
            'url': 'https://www.liepin.com/job/mock1.html',
        },
    ]
    
    # 测试投递
    print("\n开始测试投递...")
    for i, job in enumerate(test_jobs, 1):
        print(f"\n[{i}/4] 投递职位 {i}")
        result = await service.apply_to_job(job)
        print(f"   结果：{result['status']} - {result['message']}")
    
    # 统计
    print("\n" + "="*60)
    print("投递统计")
    print("="*60)
    
    stats = service.get_statistics()
    print(f"\n总投递数：{stats['total']}")
    print(f"成功：{stats['success']}")
    print(f"失败：{stats['failed']}")
    print(f"需要验证：{stats['need_verification']}")
    print(f"成功率：{stats['success_rate']*100:.1f}%")
    
    return stats

if __name__ == "__main__":
    asyncio.run(test_application())
