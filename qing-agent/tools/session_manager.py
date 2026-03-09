"""
会话管理器 - 防封禁核心组件

持久化会话管理，模拟"老用户"行为
"""

import time
import json
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SessionData:
    """会话数据"""
    session_id: str
    user_agent: str
    cookies: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_used_at: float = field(default_factory=time.time)
    visit_count: int = 0
    total_active_seconds: float = 0.0
    
    # 行为特征
    avg_session_duration: float = 0.0
    avg_pages_per_session: float = 0.0
    preferred_keywords: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "user_agent": self.user_agent,
            "cookies": self.cookies,
            "created_at": self.created_at,
            "last_used_at": self.last_used_at,
            "visit_count": self.visit_count,
            "total_active_seconds": self.total_active_seconds,
            "avg_session_duration": self.avg_session_duration,
            "avg_pages_per_session": self.avg_pages_per_session,
            "preferred_keywords": self.preferred_keywords,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SessionData":
        return cls(**data)


class SessionManager:
    """
    会话管理器
    
    特性：
    - 持久化会话（7 天或 50 次访问后清理）
    - 行为特征学习
    - Cookie 管理
    - 会话恢复
    """
    
    def __init__(self, cache_dir: str = ".session_cache"):
        self.cache_dir = cache_dir
        self._sessions: Dict[str, SessionData] = {}
        self._current_session: Optional[SessionData] = None
        
        # 配置
        self.max_age_days = 7
        self.max_visits = 50
        self.session_timeout_seconds = 3600  # 1 小时无活动过期
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 加载现有会话
        self._load_sessions()
    
    def _load_sessions(self):
        """加载持久化的会话"""
        cache_file = os.path.join(self.cache_dir, "sessions.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                for session_data in data.get("sessions", []):
                    session = SessionData.from_dict(session_data)
                    self._sessions[session.session_id] = session
                
                print(f"[SessionManager] 已加载 {len(self._sessions)} 个会话")
            except Exception as e:
                print(f"[SessionManager] 加载会话失败：{e}")
    
    def _save_sessions(self):
        """保存会话到持久化存储"""
        cache_file = os.path.join(self.cache_dir, "sessions.json")
        
        try:
            data = {
                "last_updated": time.time(),
                "sessions": [s.to_dict() for s in self._sessions.values()],
            }
            
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"[SessionManager] 已保存 {len(self._sessions)} 个会话")
        except Exception as e:
            print(f"[SessionManager] 保存会话失败：{e}")
    
    def _cleanup_old_sessions(self):
        """清理过期会话"""
        now = time.time()
        max_age_seconds = self.max_age_days * 86400
        
        to_remove = []
        for session_id, session in self._sessions.items():
            # 检查年龄
            if now - session.created_at > max_age_seconds:
                to_remove.append(session_id)
                continue
            
            # 检查访问次数
            if session.visit_count >= self.max_visits:
                to_remove.append(session_id)
                continue
            
            # 检查超时
            if now - session.last_used_at > self.session_timeout_seconds:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self._sessions[session_id]
            print(f"[SessionManager] 清理过期会话：{session_id}")
        
        if to_remove:
            self._save_sessions()
    
    def get_or_create_session(self) -> SessionData:
        """获取或创建会话"""
        self._cleanup_old_sessions()
        
        # 尝试恢复最近的会话
        if self._sessions:
            # 找到最近使用的会话
            recent = max(
                self._sessions.values(),
                key=lambda s: s.last_used_at
            )
            
            # 检查是否过期
            if time.time() - recent.last_used_at < self.session_timeout_seconds:
                self._current_session = recent
                recent.last_used_at = time.time()
                recent.visit_count += 1
                print(f"[SessionManager] 恢复会话：{recent.session_id} (访问 #{recent.visit_count})")
                self._save_sessions()
                return recent
        
        # 创建新会话
        import uuid
        new_session = SessionData(
            session_id=f"session_{uuid.uuid4().hex[:12]}",
            user_agent=self._generate_user_agent(),
            visit_count=1,  # 首次访问
        )
        
        self._sessions[new_session.session_id] = new_session
        self._current_session = new_session
        self._save_sessions()
        
        print(f"[SessionManager] 创建新会话：{new_session.session_id}")
        return new_session
    
    def _generate_user_agent(self) -> str:
        """生成用户代理"""
        # Windows + Chrome
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    
    def update_cookies(self, cookies: Dict[str, Any]):
        """更新 Cookie"""
        if self._current_session is None:
            self.get_or_create_session()
        
        self._current_session.cookies.update(cookies)
        self._save_sessions()
    
    def get_cookies(self) -> Dict[str, Any]:
        """获取 Cookie"""
        if self._current_session is None:
            self.get_or_create_session()
        
        return self._current_session.cookies.copy()
    
    def record_activity(self, duration_seconds: float = 0.0, keyword: Optional[str] = None):
        """记录活动"""
        if self._current_session is None:
            self.get_or_create_session()
        
        session = self._current_session
        session.last_used_at = time.time()
        session.total_active_seconds += duration_seconds
        
        # 更新平均会话时长
        session.avg_session_duration = (
            session.total_active_seconds / session.visit_count
        )
        
        # 记录偏好关键词
        if keyword and keyword not in session.preferred_keywords:
            session.preferred_keywords.append(keyword)
            if len(session.preferred_keywords) > 10:
                session.preferred_keywords.pop(0)
        
        self._save_sessions()
    
    def get_session_info(self) -> dict:
        """获取会话信息"""
        if self._current_session is None:
            self.get_or_create_session()
        
        session = self._current_session
        
        return {
            "session_id": session.session_id,
            "user_agent": session.user_agent,
            "created_at": datetime.fromtimestamp(session.created_at).isoformat(),
            "last_used_at": datetime.fromtimestamp(session.last_used_at).isoformat(),
            "visit_count": session.visit_count,
            "total_active_seconds": session.total_active_seconds,
            "avg_session_duration": session.avg_session_duration,
            "preferred_keywords": session.preferred_keywords,
            "cookie_count": len(session.cookies),
            "is_persistent": session.visit_count > 1,
        }
    
    def clear_session(self):
        """清除当前会话"""
        if self._current_session:
            session_id = self._current_session.session_id
            if session_id in self._sessions:
                del self._sessions[session_id]
            self._current_session = None
            self._save_sessions()
            print(f"[SessionManager] 已清除会话：{session_id}")
    
    def get_trust_score(self) -> float:
        """
        获取信任分数（0-1）
        
        基于：
        - 会话年龄
        - 访问次数
        - 平均会话时长
        """
        if self._current_session is None:
            return 0.0
        
        session = self._current_session
        score = 0.0
        
        # 会话年龄（最多 7 天满分）
        age_days = (time.time() - session.created_at) / 86400
        score += min(age_days / 7, 1.0) * 0.4
        
        # 访问次数（最多 50 次满分）
        score += min(session.visit_count / 50, 1.0) * 0.3
        
        # 平均会话时长（最多 10 分钟满分）
        avg_minutes = session.avg_session_duration / 60
        score += min(avg_minutes / 10, 1.0) * 0.3
        
        return score


# 使用示例
if __name__ == "__main__":
    manager = SessionManager()
    
    # 获取或创建会话
    session = manager.get_or_create_session()
    print("会话信息:", manager.get_session_info())
    
    # 模拟活动
    manager.record_activity(duration_seconds=300, keyword="品牌策划")
    manager.record_activity(duration_seconds=180, keyword="营销策划")
    
    # 获取信任分数
    trust_score = manager.get_trust_score()
    print(f"信任分数：{trust_score:.2f}")
    
    # 更新 Cookie
    manager.update_cookies({"test_cookie": "test_value"})
    print("Cookie:", manager.get_cookies())
