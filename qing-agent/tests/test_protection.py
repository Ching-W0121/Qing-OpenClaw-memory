"""
测试保护机制 - 防死循环
"""

import asyncio
import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qing_platform.zhilian_adapter import ZhilianAdapter

def test_circuit_breaker_init():
    """测试熔断器初始化"""
    print("\n" + "=" * 60)
    print("测试 1: 熔断器初始化")
    print("=" * 60)
    
    adapter = ZhilianAdapter()
    
    checks = [
        (adapter.max_retry == 3, f"max_retry = {adapter.max_retry} (期望：3)"),
        (adapter.timeout_seconds == 60, f"timeout = {adapter.timeout_seconds}s (期望：60s)"),
        (adapter.circuit_breaker_threshold == 3, f"熔断阈值 = {adapter.circuit_breaker_threshold} (期望：3)"),
        (adapter.circuit_breaker_cooldown == 1800, f"冷却时间 = {adapter.circuit_breaker_cooldown}s (期望：1800s)"),
        (adapter._failure_count == 0, f"初始失败计数 = {adapter._failure_count} (期望：0)"),
        (adapter._circuit_open_until is None, f"熔断器状态 = {'打开' if adapter._circuit_open_until else '关闭'} (期望：关闭)"),
    ]
    
    passed = 0
    for check, desc in checks:
        status = "[OK]" if check else "[FAIL]"
        print(f"{status} {desc}")
        if check:
            passed += 1
    
    print(f"\n通过率：{passed}/{len(checks)}")
    return passed == len(checks)

def test_on_success_failure():
    """测试成功/失败回调"""
    print("\n" + "=" * 60)
    print("测试 2: 成功/失败回调")
    print("=" * 60)
    
    adapter = ZhilianAdapter()
    
    # 模拟失败 3 次
    print("\n模拟失败 3 次：")
    for i in range(3):
        adapter._on_failure()
        print(f"  第{i+1}次失败后：failure_count = {adapter._failure_count}")
    
    # 检查熔断器是否打开
    circuit_open = adapter._failure_count >= adapter.circuit_breaker_threshold
    print(f"\n熔断器状态：{'打开' if circuit_open else '关闭'}")
    
    # 模拟成功 1 次
    print("\n模拟成功 1 次：")
    adapter._on_success()
    print(f"  成功后：failure_count = {adapter._failure_count}")
    
    checks = [
        (adapter._failure_count == 0, "成功后失败计数重置为 0"),
    ]
    
    passed = sum(1 for check, _ in checks if check)
    for check, desc in checks:
        status = "[OK]" if check else "[FAIL]"
        print(f"\n{status} {desc}")
    
    print(f"\n通过率：{passed}/{len(checks)}")
    return passed == len(checks)

async def test_retry_mechanism():
    """测试重试机制（模拟）"""
    print("\n" + "=" * 60)
    print("测试 3: 重试机制（模拟）")
    print("=" * 60)
    
    adapter = ZhilianAdapter()
    adapter.max_retry = 3
    
    # 模拟搜索（使用模拟数据，应该直接成功）
    print("\n调用 search_jobs（模拟数据）...")
    start = time.time()
    jobs = await adapter.search_jobs("品牌策划", city="深圳")
    elapsed = time.time() - start
    
    print(f"\n返回 {len(jobs)} 个职位")
    print(f"耗时：{elapsed:.2f}s")
    
    checks = [
        (len(jobs) > 0, "返回了职位数据"),
        (elapsed < 5, f"耗时合理 (< 5s)"),
    ]
    
    passed = sum(1 for check, _ in checks if check)
    for check, desc in checks:
        status = "[OK]" if check else "[FAIL]"
        print(f"\n{status} {desc}")
    
    print(f"\n通过率：{passed}/{len(checks)}")
    return passed == len(checks)

def test_circuit_breaker_manual():
    """手动测试熔断器"""
    print("\n" + "=" * 60)
    print("测试 4: 熔断器手动触发")
    print("=" * 60)
    
    adapter = ZhilianAdapter()
    
    # 手动触发熔断器
    print("\n手动触发熔断器...")
    adapter._failure_count = 3
    adapter._open_circuit()
    
    # 检查熔断器状态
    is_open = adapter._is_circuit_open()
    print(f"熔断器状态：{'打开' if is_open else '关闭'}")
    print(f"冷却至：{adapter._circuit_open_until}")
    
    checks = [
        (is_open, "熔断器已打开"),
        (adapter._circuit_open_until is not None, "冷却时间已设置"),
    ]
    
    passed = sum(1 for check, _ in checks if check)
    for check, desc in checks:
        status = "[OK]" if check else "[FAIL]"
        print(f"\n{status} {desc}")
    
    print(f"\n通过率：{passed}/{len(checks)}")
    return passed == len(checks)

async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("求职 Agent · 保护机制测试")
    print("=" * 60)
    
    tests = [
        ("熔断器初始化", test_circuit_breaker_init),
        ("成功/失败回调", test_on_success_failure),
        ("重试机制", test_retry_mechanism),
        ("熔断器手动触发", test_circuit_breaker_manual),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                passed = await test_func()
            else:
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
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\n总通过率：{passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("\n[SUCCESS] 所有测试通过！")
        return True
    else:
        print(f"\n[WARNING] {total_count - passed_count} 个测试失败")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
