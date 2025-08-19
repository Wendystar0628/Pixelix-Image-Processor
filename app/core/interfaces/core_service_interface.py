"""
核心服务桥接接口
定义UI层访问核心服务的桥接接口，与UpperLayerServiceInterface保持设计一致性
"""

from abc import ABC, abstractmethod
from typing import Any


class CoreServiceInterface(ABC):
    """核心服务桥接接口 - 提供核心层服务的统一访问点"""
    
    @abstractmethod
    def get_state_manager(self) -> Any:
        """获取状态管理器实例"""
        pass
    
    @abstractmethod
    def get_config_accessor(self) -> Any:
        """获取配置访问器实例"""
        pass
    
    @abstractmethod
    def get_tool_manager(self) -> Any:
        """获取工具管理器实例"""
        pass