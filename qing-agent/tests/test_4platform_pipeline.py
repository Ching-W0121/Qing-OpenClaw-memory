"""
四平台 Pipeline 集成测试
测试：智联 + 前程 + 拉勾 + 猎聘
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.multi_platform_pipeline import run_pipeline

async def main():
    """主测试"""
    print("\n" + "="*60)
    print("四平台 Pipeline 集成测试")
    print("="*60)
    
    # 用户画像
    user_profile = {
        'target_jobs': ['品牌策划', '品牌宣传', '活动策划'],
        'expected_city': '深圳',
        'expected_salary_min': 8000,
        'expected_salary_max': 15000,
        'experience_years': 3,
        'education': '本科',
        'skills': ['品牌策划', '活动策划', '文案写作', '新媒体运营'],
        'tools': ['Office', 'Photoshop', '微信公众号'],
    }
    
    # 运行 Pipeline
    result = await run_pipeline(
        keyword='品牌策划',
        city='深圳',
        user_profile=user_profile
    )
    
    # 汇总
    search_result = result['search_result']
    summary = search_result['summary']
    
    print("\n" + "="*60)
    print("测试汇总")
    print("="*60)
    
    print(f"\n搜索关键词：{summary['keyword']}")
    print(f"城市：{summary['city']}")
    print(f"总耗时：{summary['total_duration']:.2f}s")
    
    print(f"\n平台统计:")
    for platform, stats in summary['platform_stats'].items():
        print(f"  {platform}: {stats['count']} 个职位 ({stats['duration']:.2f}s)")
    
    print(f"\n职位统计:")
    print(f"  总职位数：{summary['total_jobs']}")
    print(f"  去重后：{summary['unique_jobs']}")
    print(f"  重复移除：{summary['duplicates_removed']}")
    
    print(f"\n数据库保存：{result['saved_count']} 个职位")
    print(f"推荐数量：{len(result['recommendations'])} 个")
    
    # 验证
    success = (
        summary['unique_jobs'] > 0 and
        len(result['recommendations']) > 0
    )
    
    print("\n" + "="*60)
    if success:
        print("[SUCCESS] Pipeline 测试成功！")
    else:
        print("[WARN] Pipeline 测试完成，但数据可能不足")
    print("="*60)
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] 测试异常：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
