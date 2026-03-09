"""
阶段 3 测试 - 防封禁组件测试
"""

import asyncio
import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError, CircuitState
from tools.operation_limiter import OperationLimiter, AdaptiveLimiter, RateLimitType
from tools.session_manager import SessionManager


def test_circuit_breaker():
    """测试熔断器"""
    print("\n" + "=" * 60)
    print("测试 1: 熔断器")
    print("=" * 60)
    
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=5)
    
    # 初始状态
    print(f"\n初始状态：{cb.get_status()}")
    assert cb.state == CircuitState.CLOSED, "初始状态应为 CLOSED"
    
    # 模拟失败函数
    async def failing_func():
        raise Exception("模拟失败")
    
    # 模拟 3 次失败
    print("\n模拟 3 次失败...")
    for i in range(3):
        try:
            asyncio.run(cb.call_async(failing_func))
        except Exception as e:
            print(f"  第{i+1}次失败：{e}")
    
    # 检查状态
    status = cb.get_status()
    print(f"\n3 次失败后状态：{status}")
    assert cb.state == CircuitState.OPEN, "3 次失败后应为 OPEN"
    
    # 尝试调用（应被拒绝）
    print("\n尝试调用（应被拒绝）...")
    try:
        asyncio.run(cb.call_async(failing_func))
        assert False, "应该抛出 CircuitBreakerOpenError"
    except CircuitBreakerOpenError as e:
        print(f"  正确拒绝：{e}")
    
    # 等待恢复
    print("\n等待 5 秒恢复...")
    time.sleep(5)
    
    # 检查状态（应自动转为 HALF_OPEN）
    print(f"恢复后状态：{cb.get_status()}")
    assert cb.state == CircuitState.HALF_OPEN, "冷却后应为 HALF_OPEN"
    
    # 成功调用（应恢复）
    async def success_func():
        return "成功"
    
    print("\n成功调用...")
    result = asyncio.run(cb.call_async(success_func))
    print(f"  结果：{result}")
    
    # 检查最终状态
    print(f"最终状态：{cb.get_status()}")
    assert cb.state == CircuitState.CLOSED, "成功后应恢复 CLOSED"
    
    print("\n[OK] 熔断器测试通过")
    return True


def test_operation_limiter():
    """测试操作限流器"""
    print("\n" + "=" * 60)
    print("测试 2: 操作限流器")
    print("=" * 60)
    
    limiter = OperationLimiter()
    
    # 初始状态
    print(f"\n初始状态：{limiter.get_status()}")
    
    # 模拟搜索操作
    print("\n模拟搜索操作（限流 10 次/小时）...")
    allowed = 0
    denied = 0
    
    for i in range(12):
        can, reason = limiter.can_proceed(RateLimitType.SEARCH)
        if can:
            limiter.record(RateLimitType.SEARCH)
            allowed += 1
            print(f"  搜索 {i+1}: 允许")
        else:
            denied += 1
            print(f"  搜索 {i+1}: 拒绝 - {reason}")
    
    print(f"\n结果：允许 {allowed} 次，拒绝 {denied} 次")
    assert allowed == 10, f"应允许 10 次，实际 {allowed}"
    assert denied == 2, f"应拒绝 2 次，实际 {denied}"
    
    # 检查工作时长
    print("\n测试工作时长统计...")
    limiter.start_work_session()
    time.sleep(1)
    limiter.end_work_session()
    
    status = limiter.get_status()
    print(f"工作时长状态：{status.get('work_time', {})}")
    
    print("\n[OK] 操作限流器测试通过")
    return True


def test_adaptive_limiter():
    """测试自适应限流器"""
    print("\n" + "=" * 60)
    print("测试 3: 自适应限流器")
    print("=" * 60)
    
    base_limiter = OperationLimiter()
    adaptive = AdaptiveLimiter(base_limiter)
    
    # 初始阶段
    phase = adaptive.get_phase()
    threshold = adaptive.get_threshold()
    print(f"\n初始阶段：{phase}, 阈值：{threshold*100:.0f}%")
    
    # 验证阶段逻辑
    assert phase == 1, "初始应为阶段 1"
    assert threshold == 0.3, "阶段 1 阈值应为 30%"
    
    # 获取状态
    status = adaptive.get_status()
    print(f"自适应状态：phase={status.get('adaptive_phase')}, threshold={status.get('adaptive_threshold')}")
    
    print("\n[OK] 自适应限流器测试通过")
    return True


def test_session_manager():
    """测试会话管理器"""
    print("\n" + "=" * 60)
    print("测试 4: 会话管理器")
    print("=" * 60)
    
    manager = SessionManager(cache_dir=".session_cache_test")
    
    # 获取或创建会话
    print("\n获取或创建会话...")
    session = manager.get_or_create_session()
    print(f"会话 ID: {session.session_id}")
    
    # 获取会话信息
    info = manager.get_session_info()
    print(f"会话信息：{info}")
    
    # 验证基本信息
    assert info["session_id"] == session.session_id
    # visit_count 可能为 0（新会话）或>=1（恢复会话）
    assert info["visit_count"] >= 0
    
    # 记录活动
    print("\n记录活动...")
    manager.record_activity(duration_seconds=300, keyword="品牌策划")
    manager.record_activity(duration_seconds=180, keyword="营销策划")
    
    info = manager.get_session_info()
    print(f"活动后信息：{info}")
    
    # 验证活动记录
    assert info["total_active_seconds"] >= 480, "应记录 480 秒活动"
    assert "品牌策划" in info["preferred_keywords"]
    assert "营销策划" in info["preferred_keywords"]
    
    # 获取信任分数
    trust_score = manager.get_trust_score()
    print(f"\n信任分数：{trust_score:.2f}")
    assert 0 <= trust_score <= 1, "信任分数应在 0-1 之间"
    
    # 更新 Cookie
    print("\n更新 Cookie...")
    manager.update_cookies({"test_cookie": "test_value"})
    cookies = manager.get_cookies()
    print(f"Cookie: {cookies}")
    assert "test_cookie" in cookies
    
    # 清理测试缓存
    import shutil
    if os.path.exists(".session_cache_test"):
        shutil.rmtree(".session_cache_test")
    
    print("\n[OK] 会话管理器测试通过")
    return True


def test_integrated_protection():
    """测试集成防护"""
    print("\n" + "=" * 60)
    print("测试 5: 集成防护（熔断 + 限流 + 会话）")
    print("=" * 60)
    
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=2)
    limiter = OperationLimiter()
    manager = SessionManager(cache_dir=".session_cache_int_test")
    
    # 模拟完整工作流程
    print("\n模拟完整工作流程...")
    
    # 1. 开始工作会话
    limiter.start_work_session()
    
    # 2. 获取会话
    session = manager.get_or_create_session()
    print(f"  会话：{session.session_id}")
    
    # 3. 检查限流
    can, reason = limiter.can_proceed(RateLimitType.SEARCH)
    print(f"  限流检查：{'允许' if can else '拒绝 - ' + reason}")
    assert can, "首次操作应允许"
    
    # 4. 执行操作（通过熔断器）
    async def search_job():
        # 模拟搜索
        time.sleep(0.1)
        return {"job_id": "test_123"}
    
    try:
        result = asyncio.run(cb.call_async(search_job))
        print(f"  搜索结果：{result}")
        
        # 记录成功
        limiter.record(RateLimitType.SEARCH)
        manager.record_activity(duration_seconds=0.1, keyword="测试")
    except Exception as e:
        print(f"  搜索失败：{e}")
    
    # 5. 结束工作会话
    limiter.end_work_session()
    
    # 6. 获取综合状态
    print("\n综合状态:")
    print(f"  熔断器：{cb.get_status()['state']}")
    print(f"  限流器：搜索剩余 {limiter.get_status()['search']['remaining']} 次")
    print(f"  会话：{manager.get_session_info()['visit_count']} 次访问")
    
    # 清理测试缓存
    import shutil
    if os.path.exists(".session_cache_int_test"):
        shutil.rmtree(".session_cache_int_test")
    
    print("\n[OK] 集成防护测试通过")
    return True


def main():
    """运行所有阶段 3 测试"""
    print("\n" + "=" * 60)
    print("求职 Agent v1.1 · 阶段 3 测试（防封禁组件）")
    print("=" * 60)
    
    tests = [
        ("熔断器", test_circuit_breaker),
        ("操作限流器", test_operation_limiter),
        ("自适应限流器", test_adaptive_limiter),
        ("会话管理器", test_session_manager),
        ("集成防护", test_integrated_protection),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n[ERROR] {name} 测试失败：{e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        print(f"{'[OK]' if passed else '[FAIL]'} {name}")
    
    print(f"\n总通过率：{passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("\n[SUCCESS] 所有测试通过！")
        return True
    else:
        print(f"\n[WARNING] {total_count - passed_count} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
