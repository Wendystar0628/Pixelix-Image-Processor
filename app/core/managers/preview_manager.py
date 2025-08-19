from typing import Dict, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal


class PreviewManager(QObject):
    """
    预览管理器。
    
    负责管理实时预览状态 (preview_op_params)。
    继承自 QObject 以便能够发出信号。
    """
    
    # 当预览参数发生变化时发出信号
    preview_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.preview_op_params: Optional[Dict[str, Any]] = None  # 用于实时预览的操作参数
    
    def set_preview_params(self, params: Dict[str, Any]) -> None:
        """
        设置预览操作的参数并触发UI更新。
        
        Args:
            params: 一个包含操作类型和其参数的字典。
                   例如: {'op': 'brightness_contrast', 'brightness': 50, 'contrast': 10}
                   或者从dataclass.__dict__转换的字典，带有额外的'op'键。
        """
        self.preview_op_params = params
        self.preview_changed.emit()

    def clear_preview_params(self) -> None:
        """
        清除预览参数并触发UI更新以恢复到非预览状态。
        如果当前没有预览参数，则不会触发信号。
        """
        if self.preview_op_params is not None:
            self.preview_op_params = None
            self.preview_changed.emit()
    
    def has_preview(self) -> bool:
        """
        检查当前是否有预览参数。
        
        Returns:
            bool: 如果有预览参数则返回 True，否则返回 False
        """
        return self.preview_op_params is not None
    
    def get_preview_params(self) -> Optional[Dict[str, Any]]:
        """
        获取当前预览参数。
        
        Returns:
            Optional[Dict[str, Any]]: 当前预览参数，如果没有则返回 None
        """
        return self.preview_op_params 