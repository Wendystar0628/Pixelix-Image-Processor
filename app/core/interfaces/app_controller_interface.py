"""
应用控制器服务接口
"""

from abc import ABC, ABCMeta, abstractmethod
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QWidget


class AppControllerMeta(type(QObject), ABCMeta):
    """解决QObject和ABC元类冲突的自定义元类"""
    pass


class AppControllerInterface(QObject, ABC, metaclass=AppControllerMeta):
    """
    应用控制器服务的抽象接口
    
    定义了应用的主要业务操作流程，包括图像加载、保存、操作应用等。
    实现类负责协调各个子系统完成业务流程和PyQt信号机制。
    """
    
    # 图像加载相关方法
    @abstractmethod
    def open_image(self, parent_widget: QWidget) -> None:
        """打开图像文件"""
        pass
    
    @abstractmethod
    def open_recent_file(self, file_path: str) -> None:
        """打开最近的文件"""
        pass
    
    @abstractmethod
    def load_image_from_path(self, file_path: str) -> None:
        """从指定路径加载图像"""
        pass
    
    # 文件IO相关方法
    @abstractmethod
    def save_image(self, parent_widget: QWidget) -> None:
        """保存当前图像"""
        pass
    
    # 图像操作相关方法
    @abstractmethod
    def apply_simple_operation(self, op_id: str) -> None:
        """应用简单操作"""
        pass
    
    # 状态管理相关方法
    @abstractmethod
    def undo_last_operation(self) -> None:
        """撤销最后一个操作"""
        pass
    
    @abstractmethod
    def redo_last_operation(self) -> None:
        """重做最后一个操作"""
        pass
    
    @abstractmethod
    def clear_all_effects(self) -> None:
        """清除所有效果"""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """执行撤销操作"""
        pass
    
    @abstractmethod
    def redo(self) -> None:
        """执行重做操作"""
        pass
    
    @abstractmethod
    def can_undo(self) -> bool:
        """检查是否可以撤销"""
        pass
    
    @abstractmethod
    def can_redo(self) -> bool:
        """检查是否可以重做"""
        pass
    
    # 预设相关方法
    @abstractmethod
    def show_apply_preset_dialog(self) -> None:
        """显示应用预设对话框"""
        pass
    
    @abstractmethod
    def save_current_as_preset(self, parent_widget: QWidget) -> None:
        """将当前效果另存为预设"""
        pass
    
    @abstractmethod
    def delete_preset(self, parent_widget: QWidget) -> None:
        """删除预设"""
        pass
    
    # 批处理相关方法
    @abstractmethod
    def add_current_image_to_pool(self) -> None:
        """将当前图像添加到图像池"""
        pass
    
    @abstractmethod
    def add_images_to_pool(self, file_paths: list) -> None:
        """将多个图像添加到图像池"""
        pass
    
    @abstractmethod
    def show_import_folder_dialog(self, parent_widget: QWidget) -> None:
        """显示从文件夹导入图像的对话框"""
        pass
    
    # 对话框相关方法
    @abstractmethod
    def show_dialog(self, dialog_id: str) -> None:
        """显示指定的对话框"""
        pass