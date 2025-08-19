"""
预设处理器接口模块

定义预设管理操作的抽象接口。
"""

from abc import abstractmethod
from typing import List
from PyQt6.QtWidgets import QWidget

from .handler_interface_base import BaseHandlerInterface


class PresetHandlerInterface(BaseHandlerInterface):
    """
    预设处理器抽象接口
    
    定义预设管理操作的核心方法，包括预设保存、删除、加载等功能。
    """
    
    @abstractmethod
    def save_current_as_preset(self, parent: QWidget) -> None:
        """
        保存当前为预设
        
        Args:
            parent: 父窗口部件
        """
        pass
    
    @abstractmethod
    def delete_preset(self, parent: QWidget) -> None:
        """
        删除预设
        
        Args:
            parent: 父窗口部件
        """
        pass
    
    @abstractmethod
    def load_preset(self, preset_name: str) -> bool:
        """
        加载预设
        
        Args:
            preset_name: 预设名称
            
        Returns:
            是否加载成功
        """
        pass