"""
文件处理器接口模块

定义文件I/O操作的抽象接口。
"""

from abc import abstractmethod
from typing import Optional, Tuple, List
import numpy as np
from PyQt6.QtWidgets import QWidget

from .handler_interface_base import BaseHandlerInterface


class FileHandlerInterface(BaseHandlerInterface):
    """
    文件处理器抽象接口
    
    定义文件I/O操作的核心方法，包括文件对话框显示、图像加载保存等功能。
    """
    
    @abstractmethod
    def show_open_dialog(self, parent: QWidget) -> Optional[str]:
        """
        显示打开文件对话框
        
        Args:
            parent: 父窗口部件
            
        Returns:
            选择的文件路径，如果用户取消则返回None
        """
        pass
    
    @abstractmethod
    def show_save_dialog(self, parent: QWidget) -> Optional[str]:
        """
        显示保存文件对话框
        
        Args:
            parent: 父窗口部件
            
        Returns:
            选择的保存路径，如果用户取消则返回None
        """
        pass
    
    @abstractmethod
    def load_image_from_path(self, file_path: str) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        从路径加载图像
        
        Args:
            file_path: 图像文件路径
            
        Returns:
            (图像数据, 实际文件路径) 或 (None, file_path) 如果失败
        """
        pass
    
    @abstractmethod
    def save_image(self, image: np.ndarray, file_path: str) -> None:
        """
        保存图像到文件
        
        Args:
            image: 图像数据
            file_path: 保存路径
        """
        pass