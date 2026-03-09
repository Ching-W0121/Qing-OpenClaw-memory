"""
缓存管理 - 替代 Redis
使用内存缓存（cachetools）
"""

from cachetools import TTLCache, LRUCache
import json
import os

class CacheManager:
    """缓存管理器（替代 Redis）"""
    
    def __init__(self, ttl=3600, max_size=1000):
        """
        初始化缓存管理器
        
        Args:
            ttl: 默认过期时间（秒）
            max_size: 最大缓存数量
        """
        # TTL 缓存：自动过期
        self.ttl_cache = TTLCache(maxsize=max_size, ttl=ttl)
        # LRU 缓存：最近最少使用淘汰
        self.lru_cache = LRUCache(maxsize=max_size)
        # 文件缓存目录
        self.file_cache_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'cache')
        os.makedirs(self.file_cache_dir, exist_ok=True)
    
    def get(self, key):
        """获取缓存"""
        return self.ttl_cache.get(key) or self.lru_cache.get(key)
    
    def set(self, key, value, use_ttl=True):
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            use_ttl: 是否使用 TTL 缓存（否则使用 LRU）
        """
        if use_ttl:
            self.ttl_cache[key] = value
        else:
            self.lru_cache[key] = value
    
    def delete(self, key):
        """删除缓存"""
        self.ttl_cache.pop(key, None)
        self.lru_cache.pop(key, None)
    
    def clear(self):
        """清空缓存"""
        self.ttl_cache.clear()
        self.lru_cache.clear()
    
    def get_stats(self):
        """获取缓存统计"""
        return {
            "ttl_cache_size": len(self.ttl_cache),
            "lru_cache_size": len(self.lru_cache),
            "ttl_cache_max_size": self.ttl_cache.maxsize,
            "lru_cache_max_size": self.lru_cache.maxsize,
        }
    
    def save_to_file(self, key, data):
        """保存数据到文件缓存"""
        file_path = os.path.join(self.file_cache_dir, f"{key}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, key):
        """从文件缓存加载数据"""
        file_path = os.path.join(self.file_cache_dir, f"{key}.json")
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)


# 全局缓存实例
cache = CacheManager(ttl=3600, max_size=1000)
