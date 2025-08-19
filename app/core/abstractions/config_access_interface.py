"""核心层配置访问抽象接口"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class ConfigAccessInterface(ABC):
    """核心层配置访问抽象接口 - 最小接口原则"""
    
    @abstractmethod
    def get_rendering_mode(self) -> str:
        """获取渲染模式"""
        pass
    
    @abstractmethod
    def get_proxy_quality_factor(self) -> float:
        """获取代理质量因子"""
        pass
    
    @abstractmethod
    def get_window_geometry(self) -> Dict[str, int]:
        """获取窗口几何信息"""
        pass
    
    @abstractmethod
    def is_feature_enabled(self, feature: str) -> bool:
        """检查功能是否启用"""
        pass
    
    @abstractmethod
    def get_update_config(self) -> Dict[str, Any]:
        """获取更新配置"""
        pass