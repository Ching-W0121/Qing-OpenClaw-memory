"""
操作限流器 - 防封禁核心组件

多维度限流：搜索次数/小时、详情次数/天、工作时长/天
"""

import time
from typing import Optional, Dict, List
from dataclasses import dataclass, field
from enum import Enum
import asyncio


class RateLimitType(Enum):
    """限流类型"""
    SEARCH = "search"           # 搜索操作
    DETAIL = "detail"           # 详情获取
    APPLY = "apply"             # 投递操作
    WORK_TIME = "work_time"     # 工作时长


@dataclass
class RateLimitConfig:
    """限流配置"""
    limit_type: RateLimitType
    max_count: int              # 最大次数
    window_seconds: int         # 时间窗口（秒）
    
    # 工作时长特殊配置
    max_hours_per_day: Optional[float] = None  # 每天最大工作小时数


@dataclass
class RateLimitState:
    """限流状态"""
    config: RateLimitConfig
    timestamps: List[float] = field(default_factory=list)
    total_work_seconds: float = 0.0
    day_start_timestamp: float = field(default_factory=lambda: 0.0)


class OperationLimiter:
    """
    操作限流器
    
    支持多维度限流：
    - 搜索：10 次/小时
    - 详情：30 次/天
    - 投递：20 次/天
    - 工作时长：4 小时/天
    """
    
    def __init__(self):
        self._limits: Dict[RateLimitType, RateLimitState] = {}
        self._work_start_time: Optional[float] = None
        self._total_work_seconds: float = 0.0
        
        # 初始化默认配置
        self._init_default_limits()
    
    def _init_default_limits(self):
        """初始化默认限流配置"""
        self._limits = {
            RateLimitType.SEARCH: RateLimitState(
                config=RateLimitConfig(
                    limit_type=RateLimitType.SEARCH,
                    max_count=10,
                    window_seconds=3600,  # 1 小时
                )
            ),
            RateLimitType.DETAIL: RateLimitState(
                config=RateLimitConfig(
                    limit_type=RateLimitType.DETAIL,
                    max_count=30,
                    window_seconds=86400,  # 1 天
                )
            ),
            RateLimitType.APPLY: RateLimitState(
                config=RateLimitConfig(
                    limit_type=RateLimitType.APPLY,
                    max_count=20,
                    window_seconds=86400,  # 1 天
                )
            ),
            RateLimitType.WORK_TIME: RateLimitState(
                config=RateLimitConfig(
                    limit_type=RateLimitType.WORK_TIME,
                    max_count=0,  # 不适用
                    window_seconds=86400,
                    max_hours_per_day=4.0,  # 4 小时/天
                )
            ),
        }
    
    def _reset_day_if_needed(self):
        """如果需要，重置每日计数器"""
        now = time.time()
        day_seconds = 86400
        
        for state in self._limits.values():
            # 检查是否需要重置天
            if state.day_start_timestamp == 0 or \
               now - state.day_start_timestamp >= day_seconds:
                state.day_start_timestamp = now
                state.timestamps = []
                if state.config.limit_type == RateLimitType.WORK_TIME:
                    state.total_work_seconds = 0.0
    
    def can_proceed(self, limit_type: RateLimitType) -> tuple[bool, str]:
        """
        检查是否可以继续操作
        
        Returns:
            (can_proceed, reason): 是否可以进行操作及原因
        """
        self._reset_day_if_needed()
        
        if limit_type not in self._limits:
            return True, ""
        
        state = self._limits[limit_type]
        config = state.config
        now = time.time()
        
        # 工作时长检查
        if limit_type == RateLimitType.WORK_TIME and config.max_hours_per_day:
            max_seconds = config.max_hours_per_day * 3600
            if state.total_work_seconds >= max_seconds:
                return False, f"今日工作时长已达上限 ({config.max_hours_per_day}小时)"
        
        # 次数限制检查
        # 清理过期时间戳
        cutoff = now - config.window_seconds
        state.timestamps = [ts for ts in state.timestamps if ts > cutoff]
        
        if len(state.timestamps) >= config.max_count:
            # 计算等待时间
            oldest = min(state.timestamps)
            wait_seconds = int(oldest + config.window_seconds - now) + 1
            return False, f"限流中，请等待 {wait_seconds} 秒"
        
        return True, ""
    
    def record(self, limit_type: RateLimitType, duration_seconds: float = 0.0):
        """
        记录一次操作
        
        Args:
            limit_type: 操作类型
            duration_seconds: 操作持续时间（用于工作时长统计）
        """
        self._reset_day_if_needed()
        
        if limit_type not in self._limits:
            return
        
        state = self._limits[limit_type]
        now = time.time()
        
        # 记录时间戳
        state.timestamps.append(now)
        
        # 工作时长统计
        if limit_type == RateLimitType.WORK_TIME:
            state.total_work_seconds += duration_seconds
        
        # 更新总工作时长
        if duration_seconds > 0:
            self._total_work_seconds += duration_seconds
    
    def start_work_session(self):
        """开始工作会话"""
        self._work_start_time = time.time()
        print(f"[OperationLimiter] 工作会话开始")
    
    def end_work_session(self):
        """结束工作会话"""
        if self._work_start_time is None:
            return
        
        duration = time.time() - self._work_start_time
        self.record(RateLimitType.WORK_TIME, duration)
        
        print(
            f"[OperationLimiter] 工作会话结束，"
            f"本次 {duration:.0f}秒，"
            f"今日累计 {self._total_work_seconds/3600:.1f}小时"
        )
        
        self._work_start_time = None
    
    def get_status(self) -> dict:
        """获取限流状态"""
        self._reset_day_if_needed()
        
        status = {}
        now = time.time()
        
        for limit_type, state in self._limits.items():
            config = state.config
            
            # 清理过期时间戳
            cutoff = now - config.window_seconds
            valid_count = len([ts for ts in state.timestamps if ts > cutoff])
            
            if limit_type == RateLimitType.WORK_TIME:
                status[limit_type.value] = {
                    "used_hours": state.total_work_seconds / 3600,
                    "max_hours": config.max_hours_per_day,
                    "remaining_hours": (config.max_hours_per_day or 0) - (state.total_work_seconds / 3600),
                }
            else:
                status[limit_type.value] = {
                    "used": valid_count,
                    "max": config.max_count,
                    "remaining": config.max_count - valid_count,
                    "window": f"{config.window_seconds/3600:.1f}小时" if config.window_seconds >= 3600 else f"{config.window_seconds}秒",
                }
        
        status["total_work_seconds"] = self._total_work_seconds
        status["total_work_hours"] = self._total_work_seconds / 3600
        
        return status
    
    def reset(self, limit_type: Optional[RateLimitType] = None):
        """重置限流器"""
        if limit_type:
            if limit_type in self._limits:
                self._limits[limit_type].timestamps = []
                if limit_type == RateLimitType.WORK_TIME:
                    self._limits[limit_type].total_work_seconds = 0.0
                print(f"[OperationLimiter] 已重置 {limit_type.value}")
        else:
            self._init_default_limits()
            self._total_work_seconds = 0.0
            self._work_start_time = None
            print("[OperationLimiter] 已完全重置")


class AdaptiveLimiter:
    """
    自适应限流器
    
    根据时间段调整限流阈值：
    - 阶段 1（0-2h）：30% 阈值
    - 阶段 2（2-4h）：60% 阈值
    - 阶段 3（4h+）：100% 阈值
    """
    
    def __init__(self, base_limiter: OperationLimiter):
        self.base_limiter = base_limiter
        self.start_time = time.time()
        self._current_phase = 1
    
    def _update_phase(self):
        """更新当前阶段"""
        elapsed_hours = (time.time() - self.start_time) / 3600
        
        if elapsed_hours < 2:
            self._current_phase = 1
        elif elapsed_hours < 4:
            self._current_phase = 2
        else:
            self._current_phase = 3
    
    def get_phase(self) -> int:
        """获取当前阶段"""
        self._update_phase()
        return self._current_phase
    
    def get_threshold(self) -> float:
        """获取当前阈值比例"""
        phase = self.get_phase()
        thresholds = {1: 0.3, 2: 0.6, 3: 1.0}
        return thresholds.get(phase, 1.0)
    
    def can_proceed(self, limit_type: RateLimitType) -> tuple[bool, str]:
        """
        检查是否可以继续操作（考虑自适应阈值）
        """
        can, reason = self.base_limiter.can_proceed(limit_type)
        
        if not can:
            return False, reason
        
        # 应用自适应阈值
        threshold = self.get_threshold()
        
        # 随机缓冲（30-60 秒）
        import random
        buffer = random.uniform(30, 60)
        
        # 在阈值较低时添加额外检查
        if threshold < 1.0:
            status = self.base_limiter.get_status()
            if limit_type.value in status:
                limit_status = status[limit_type.value]
                if "remaining" in limit_status:
                    # 如果剩余次数少于阈值的比例，拒绝
                    max_count = limit_status.get("max", 1)
                    min_remaining = int(max_count * threshold)
                    if limit_status["remaining"] < min_remaining:
                        return False, f"自适应限流：剩余次数不足（阶段{self._current_phase}）"
        
        return True, reason
    
    def get_status(self) -> dict:
        """获取状态"""
        base_status = self.base_limiter.get_status()
        base_status["adaptive_phase"] = self.get_phase()
        base_status["adaptive_threshold"] = self.get_threshold()
        return base_status


# 使用示例
if __name__ == "__main__":
    limiter = OperationLimiter()
    adaptive = AdaptiveLimiter(limiter)
    
    print("初始状态:", limiter.get_status())
    
    # 模拟搜索操作
    for i in range(12):
        can, reason = adaptive.can_proceed(RateLimitType.SEARCH)
        if can:
            limiter.record(RateLimitType.SEARCH)
            print(f"搜索 {i+1}: 允许")
        else:
            print(f"搜索 {i+1}: 拒绝 - {reason}")
    
    print("\n最终状态:", limiter.get_status())
