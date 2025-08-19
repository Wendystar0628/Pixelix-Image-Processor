"""
基础操作对话框模块
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TypeVar, Generic, Union

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog

from ...core.models.operation_params import BaseOperationParams

# 定义一个泛型类型变量，用于表示子类中具体的参数数据类型
T = TypeVar('T', bound=BaseOperationParams)


class BaseOperationDialog(QDialog, Generic[T]):
    """
    所有操作对话框的抽象基类。
    定义了标准接口，以便 DialogManager 可以统一处理它们。
    支持基于dataclass的参数传递。
    """

    # 当对话框中的任何参数发生变化时（例如拖动滑块），应发出此信号
    # DialogManager 会监听此信号以实现实时预览
    params_changed = pyqtSignal(object)  # 使用object类型以支持任何dataclass参数
    apply_operation = pyqtSignal(object)  # 用于"确定"按钮，应用操作

    def __init__(self, parent=None, initial_params: Optional[Dict[str, Any]] = None):
        """
        初始化基础对话框。

        Args:
            parent: 父窗口部件。
            initial_params: 用于设置对话框初始状态的参数字典（向后兼容）。
        """
        super().__init__(parent)
        self.initial_params = initial_params if initial_params is not None else {}

    @abstractmethod
    def get_final_parameters(self) -> T:
        """
        获取对话框关闭时（例如点击"确定"）的最终参数。
        
        Returns:
            一个dataclass实例，包含所有参数值。
        """
        pass

    @abstractmethod
    def set_initial_parameters(self, params: Dict):
        """
        设置对话框的初始参数。
        当对话框打开时，用于恢复上次的设置。
        
        Args:
            params: 包含初始参数的字典（向后兼容）。
        """
        pass

    def _create_slider_and_label(self, *args, **kwargs):
        """这是一个示例辅助方法，实际实现将在子类中。"""
        pass

    def _connect_signals(self):
        """这是一个示例，子类应实现此方法来连接其UI控件的信号。"""
        pass 