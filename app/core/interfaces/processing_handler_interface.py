"""
图像处理器接口模块

定义图像处理操作的抽象接口。
"""

from abc import abstractmethod
from .handler_interface_base import BaseHandlerInterface


class ProcessingHandlerInterface(BaseHandlerInterface):
    """
    图像处理器抽象接口
    
    定义图像处理操作的核心方法，包括简单操作应用、效果清除等功能。
    """
    
    @abstractmethod
    def apply_simple_operation(self, op_id: str) -> None:
        """
        应用简单操作（无需参数的操作）
        
        Args:
            op_id: 操作标识符
        """
        pass
    
    @abstractmethod
    def clear_all_effects(self) -> None:
        """
        清除所有效果
        """
        pass
    
    @abstractmethod
    def apply_operation(self, operation) -> None:
        """
        应用操作对象
        
        Args:
            operation: 操作对象实例
        """
        pass