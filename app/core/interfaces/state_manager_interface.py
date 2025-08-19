"""
状态管理服务接口
"""

from abc import ABC, ABCMeta, abstractmethod
from typing import Dict, List, Optional, Any
import numpy as np
from PyQt6.QtCore import QObject

from ..commands.base_command import BaseCommand
from ..operations.base_operation import ImageOperation


class StateManagerMeta(type(QObject), ABCMeta):
    """解决QObject和ABC元类冲突的自定义元类"""
    pass


class StateManagerInterface(QObject, ABC, metaclass=StateManagerMeta):
    """
    应用状态管理服务的抽象接口
    
    定义了图像状态、流水线状态、工具状态等核心状态管理能力。
    实现类负责具体的状态管理逻辑和PyQt信号机制。
    """
    
    # 图像相关方法
    @abstractmethod
    def load_image(self, image, file_path=None):
        """加载图像"""
        pass
    
    @abstractmethod
    def clear_image(self):
        """清除当前图像"""
        pass
    
    @abstractmethod
    def is_image_loaded(self) -> bool:
        """检查是否有图像加载"""
        pass
    
    @abstractmethod
    def get_image_for_display(self) -> Optional[np.ndarray]:
        """获取用于显示的图像"""
        pass
    
    @abstractmethod
    def get_current_image(self) -> Optional[np.ndarray]:
        """获取当前图像"""
        pass
    
    @abstractmethod
    def get_original_image(self) -> Optional[np.ndarray]:
        """获取原始图像"""
        pass
    
    # 文件路径管理
    @abstractmethod
    def get_current_file_path(self) -> Optional[str]:
        """获取当前文件路径"""
        pass
    
    @abstractmethod
    def set_current_file_path(self, path: str):
        """设置当前文件路径"""
        pass
    
    # 流水线管理
    @abstractmethod
    def get_pipeline(self) -> List[ImageOperation]:
        """获取操作流水线"""
        pass
    
    @abstractmethod
    def execute_command(self, command: BaseCommand):
        """执行命令"""
        pass
    
    # 预览管理
    @abstractmethod
    def get_preview_params(self) -> Optional[Dict]:
        """获取预览参数"""
        pass
    
    @abstractmethod
    def cancel_preview(self):
        """取消预览"""
        pass
    
    # 交互和代理管理
    @abstractmethod
    def start_interaction(self):
        """开始交互模式"""
        pass
    
    @abstractmethod
    def end_interaction(self):
        """结束交互模式"""
        pass
    
    @abstractmethod
    def set_proxy_quality(self, quality_factor: float):
        """设置代理质量"""
        pass
    
    @abstractmethod
    def get_proxy_quality(self) -> float:
        """获取代理质量"""
        pass
    
    # 工具管理
    @property
    @abstractmethod
    def active_tool_name(self) -> Optional[str]:
        """获取当前活动工具名称"""
        pass
    
    @abstractmethod
    def set_active_tool(self, name: str) -> bool:
        """设置活动工具"""
        pass
    
    @abstractmethod
    def save_tool_state(self, tool_name: str, state: Dict[str, Any]):
        """保存工具状态"""
        pass
    
    @abstractmethod
    def get_tool_state(self, tool_name: str) -> Dict[str, Any]:
        """获取工具状态"""
        pass