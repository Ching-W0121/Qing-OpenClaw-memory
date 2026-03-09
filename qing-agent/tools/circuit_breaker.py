"""
熔断器 - 防封禁核心组件

3 次失败 → 5 分钟冷却 → 半开状态恢复
"""

import time
from enum import Enum
from typing import Optional, Callable, Any
from functools import wraps
import asyncio


class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"      # 正常状态
    OPEN = "open"          # 熔断状态
    HALF_OPEN = "half_open"  # 半开状态（试探恢复）


class CircuitBreaker:
    """
    熔断器实现
    
    状态转换：
    - CLOSED → OPEN: 失败次数达到阈值
    - OPEN → HALF_OPEN: 冷却时间到期
    - HALF_OPEN → CLOSED: 成功 1 次
    - HALF_OPEN → OPEN: 失败 1 次
    """
    
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: int = 300,  # 5 分钟
        half_open_max_calls: int = 1,
    ):
        """
        Args:
            failure_threshold: 失败阈值（达到多少次失败后熔断）
            recovery_timeout: 恢复超时（秒）
            half_open_max_calls: 半开状态允许的最大调用次数
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0
    
    @property
    def state(self) -> CircuitState:
        """获取当前状态"""
        # 检查是否应该从 OPEN 转为 HALF_OPEN
        if self._state == CircuitState.OPEN:
            if self._last_failure_time is None:
                return self._state
            
            elapsed = time.time() - self._last_failure_time
            if elapsed >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                print(f"[CircuitBreaker] 状态变更：OPEN → HALF_OPEN (冷却结束)")
        
        return self._state
    
    @property
    def is_closed(self) -> bool:
        return self.state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        return self.state == CircuitState.HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        通过熔断器调用函数
        
        Raises:
            CircuitBreakerOpenError: 熔断器打开时
        """
        if self.is_open:
            raise CircuitBreakerOpenError(
                f"熔断器已打开，请等待 {self.recovery_timeout} 秒后重试"
            )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        通过熔断器调用异步函数
        
        Raises:
            CircuitBreakerOpenError: 熔断器打开时
        """
        if self.is_open:
            raise CircuitBreakerOpenError(
                f"熔断器已打开，请等待 {self.recovery_timeout} 秒后重试"
            )
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """成功回调"""
        if self.is_half_open:
            self._half_open_calls += 1
            if self._half_open_calls >= self.half_open_max_calls:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._half_open_calls = 0
                print(f"[CircuitBreaker] 状态变更：HALF_OPEN → CLOSED (恢复成功)")
        else:
            self._failure_count = 0
            self._success_count += 1
    
    def _on_failure(self):
        """失败回调"""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self.is_half_open:
            self._state = CircuitState.OPEN
            print(f"[CircuitBreaker] 状态变更：HALF_OPEN → OPEN (恢复失败)")
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            print(
                f"[CircuitBreaker] 状态变更：CLOSED → OPEN "
                f"(失败 {self._failure_count} 次，达到阈值)"
            )
    
    def reset(self):
        """重置熔断器"""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._half_open_calls = 0
        print("[CircuitBreaker] 已重置")
    
    def get_status(self) -> dict:
        """获取状态信息"""
        return {
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "last_failure_time": self._last_failure_time,
            "time_until_recovery": self._time_until_recovery(),
        }
    
    def _time_until_recovery(self) -> Optional[int]:
        """计算距离恢复的时间（秒）"""
        if self._state != CircuitState.OPEN or self._last_failure_time is None:
            return None
        
        elapsed = time.time() - self._last_failure_time
        remaining = self.recovery_timeout - elapsed
        return max(0, int(remaining))


class CircuitBreakerOpenError(Exception):
    """熔断器打开异常"""
    pass


def circuit_breaker(cb: CircuitBreaker):
    """熔断器装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await cb.call_async(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)
        
        # 检测是否为异步函数
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# 使用示例
if __name__ == "__main__":
    async def test():
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10)
        
        print("初始状态:", cb.get_status())
        
        # 模拟 3 次失败
        async def failing_func():
            raise Exception("模拟失败")
        
        for i in range(3):
            try:
                await cb.call_async(failing_func)
            except Exception as e:
                print(f"第{i+1}次失败:", e)
        
        print("3 次失败后状态:", cb.get_status())
        
        # 尝试调用（应该被拒绝）
        try:
            await cb.call_async(failing_func)
        except CircuitBreakerOpenError as e:
            print("熔断器拒绝调用:", e)
        
        # 等待恢复
        print("等待 10 秒恢复...")
        await asyncio.sleep(10)
        
        print("恢复后状态:", cb.get_status())
        
        # 成功调用
        async def success_func():
            return "成功"
        
        result = await cb.call_async(success_func)
        print("成功调用结果:", result)
        print("最终状态:", cb.get_status())
    
    asyncio.run(test())
