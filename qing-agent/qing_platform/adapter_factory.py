"""
适配器工厂
统一管理所有平台适配器
"""

from platform.boss_adapter import BossAdapter
from platform.zhilian_adapter import ZhilianAdapter

# 占位导入，后续实现
# from platform.liepin_adapter import LiepinAdapter

class AdapterFactory:
    """适配器工厂"""
    
    _adapters = {
        "boss": BossAdapter,
        "zhilian": ZhilianAdapter,
        # "liepin": LiepinAdapter,    # 待实现
    }
    
    _instances = {}  # 单例缓存
    
    @classmethod
    def get_adapter(cls, platform):
        """
        获取平台适配器（单例模式）
        
        Args:
            platform: 平台名称
        
        Returns:
            BaseAdapter 实例
        """
        if platform not in cls._adapters:
            raise ValueError(f"不支持的平台：{platform}。支持的平台：{list(cls._adapters.keys())}")
        
        # 返回单例
        if platform not in cls._instances:
            cls._instances[platform] = cls._adapters[platform]()
        
        return cls._instances[platform]
    
    @classmethod
    def register_adapter(cls, platform, adapter_class):
        """
        注册新适配器
        
        Args:
            platform: 平台名称
            adapter_class: 适配器类
        """
        cls._adapters[platform] = adapter_class
        print(f"✅ 已注册平台适配器：{platform}")
    
    @classmethod
    def list_adapters(cls):
        """列出所有已注册的适配器"""
        return list(cls._adapters.keys())
