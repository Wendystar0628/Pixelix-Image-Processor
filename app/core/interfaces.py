from abc import ABC, abstractmethod, ABCMeta
from typing import Dict, List, Optional, Any

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

from .commands.base_command import BaseCommand
from .operations.base_operation import ImageOperation


class QObjectABCMeta(type(QObject), ABCMeta):
    """
    解决QObject和ABC的元类冲突的合并元类
    """
    pass


class IImageRepository(ABC):
    """图像仓库接口，负责管理图像资源。"""
    
    @abstractmethod
    def get_image_for_processing(self) -> Optional[np.ndarray]:
        """获取用于处理的原始图像。"""
        pass
        
    @abstractmethod
    def is_image_loaded(self) -> bool:
        """检查当前是否有图像加载。"""
        pass
        
    @abstractmethod
    def load_image(self, image: np.ndarray, file_path: Optional[str] = None):
        """加载一个新图像。"""
        pass
        
    @abstractmethod
    def get_current_file_path(self) -> Optional[str]:
        """获取当前打开的文件路径。"""
        pass
        
    @abstractmethod
    def set_current_file_path(self, file_path: str):
        """设置当前文件路径。"""
        pass


class IPipelineManager(QObject, ABC, metaclass=QObjectABCMeta):
    """操作流水线管理器接口，负责管理操作流水线和命令栈。"""
    
    pipeline_changed = pyqtSignal()
    
    @abstractmethod
    def execute_command(self, command: BaseCommand):
        """执行一个命令，修改状态，并管理历史记录。"""
        pass
        
    @abstractmethod
    def undo(self):
        """撤销上一个命令。"""
        pass
        
    @abstractmethod
    def redo(self):
        """重做上一个被撤销的命令。"""
        pass
        
    @abstractmethod
    def set_pipeline(self, pipeline: List[ImageOperation]):
        """设置当前操作流水线。"""
        pass
        
    @abstractmethod
    def clone_pipeline(self) -> List[ImageOperation]:
        """克隆当前操作流水线。"""
        pass
        
    @abstractmethod
    def clear_pipeline(self):
        """清空当前操作流水线。"""
        pass
        
    @abstractmethod
    def get_operation_params(self, op_id: str) -> Optional[Dict[str, Any]]:
        """从操作历史中获取指定操作的最新参数。"""
        pass


class IToolManager(QObject, ABC, metaclass=QObjectABCMeta):
    """工具管理器接口，负责工具的注册、激活和状态管理。"""
    
    tool_changed = pyqtSignal(str)
    
    @abstractmethod
    def register_tool(self, name: str, tool_type: str):
        """注册一个工具类型。"""
        pass
        
    @abstractmethod
    def set_active_tool(self, name: str) -> bool:
        """设置活动工具。"""
        pass
        
    @property
    @abstractmethod
    def active_tool_name(self) -> Optional[str]:
        """获取当前活动工具的名称。"""
        pass
        
    @abstractmethod
    def save_tool_state(self, tool_name: str, state: Dict[str, Any]):
        """保存工具的状态。"""
        pass
        
    @abstractmethod
    def get_tool_state(self, tool_name: str) -> Dict[str, Any]:
        """获取工具的状态。"""
        pass
        
    @abstractmethod
    def save_all_tool_states(self):
        """保存所有工具的状态到状态管理器。"""
        pass
        
    @abstractmethod
    def restore_all_tool_states(self):
        """从状态管理器恢复所有工具的状态。"""
        pass


class IPreviewManager(QObject, ABC, metaclass=QObjectABCMeta):
    """预览管理器接口，负责管理实时预览状态。"""
    
    preview_changed = pyqtSignal()
    
    @abstractmethod
    def set_preview_params(self, params: Dict):
        """设置预览操作的参数并触发UI更新。"""
        pass
        
    @abstractmethod
    def clear_preview_params(self):
        """清除预览参数并触发UI更新以恢复到非预览状态。"""
        pass
        
    @abstractmethod
    def has_preview(self) -> bool:
        """检查当前是否有预览参数。"""
        pass
        
    @abstractmethod
    def get_preview_params(self) -> Optional[Dict]:
        """获取当前预览参数。"""
        pass


class IPersistenceService(ABC):
    """持久化服务接口，负责序列化和反序列化操作。"""
    
    @staticmethod
    @abstractmethod
    def serialize_operation(operation: ImageOperation) -> Dict[str, Any]:
        """将操作序列化为字典。"""
        pass
        
    @staticmethod
    @abstractmethod
    def deserialize_operation(serialized: Dict[str, Any]) -> Optional[ImageOperation]:
        """从序列化字典创建操作实例。"""
        pass
        
    @abstractmethod
    def serialize_pipeline(self, pipeline_manager) -> List[Dict[str, Any]]:
        """将当前操作流水线序列化为字典列表。"""
        pass
        
    @abstractmethod
    def deserialize_pipeline(self, serialized: List[Dict[str, Any]]) -> List[ImageOperation]:
        """从序列化字典列表创建操作流水线。"""
        pass
        
    @abstractmethod
    def save_pipeline_to_file(self, pipeline_manager, file_path: str) -> bool:
        """将当前操作流水线保存到文件。"""
        pass
        
    @abstractmethod
    def load_pipeline_from_file(self, file_path: str) -> Optional[List[ImageOperation]]:
        """从文件加载操作流水线。"""
        pass
        
    @abstractmethod
    def serialize_tools_state(self, tool_manager) -> Dict[str, Any]:
        """
        序列化所有工具状态。
        
        Args:
            tool_manager: ToolManager 实例（新的基于 app.core.tools.tool_manager 的实现）
            
        Returns:
            Dict[str, Any]: 包含工具状态的字典
        """
        pass
        
    @abstractmethod
    def save_complete_state_to_file(self, pipeline_manager, tool_manager, file_path: str) -> bool:
        """将完整的应用程序状态保存到文件。"""
        pass
        
    @abstractmethod
    def load_complete_state_from_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """从文件加载完整的应用程序状态。"""
        pass


class IStateManager(QObject, ABC, metaclass=QObjectABCMeta):
    """状态管理器接口，作为各个子模块的聚合器和门面。"""
    
    state_changed = pyqtSignal()
    tool_changed = pyqtSignal(str)
    
    @abstractmethod
    def notify(self):
        """发出状态已改变的信号。"""
        pass
        
    @abstractmethod
    def load_image(self, image, file_path=None):
        """加载一个新图像。"""
        pass 