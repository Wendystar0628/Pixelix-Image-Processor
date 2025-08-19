"""
上层服务桥接接口
定义访问handlers和features层服务的桥接接口
"""

from abc import ABC, abstractmethod
from typing import Any


class UpperLayerServiceInterface(ABC):
    """上层服务桥接接口 - 提供handlers和features层服务的统一访问点"""
    
    @abstractmethod
    def get_app_controller(self) -> Any:
        """获取应用控制器实例"""
        pass
    
    @abstractmethod
    def get_file_handler(self) -> Any:
        """获取文件处理器实例"""
        pass
    
    @abstractmethod
    def get_processing_handler(self) -> Any:
        """获取处理器实例"""
        pass
    
    @abstractmethod
    def get_preset_handler(self) -> Any:
        """获取预设处理器实例"""
        pass
    
    @abstractmethod
    def get_batch_processing_handler(self) -> Any:
        """获取批处理处理器实例"""
        pass