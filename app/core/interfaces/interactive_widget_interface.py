"""交互式组件抽象接口"""

from abc import ABC, abstractmethod
from typing import Tuple, Callable, Any
from PyQt6.QtGui import QCursor


class InteractiveWidgetInterface(ABC):
    """交互式组件抽象接口
    
    定义核心层与UI交互组件的抽象接口，提供鼠标操作、显示更新等核心功能。
    核心层通过此接口与UI组件交互，避免直接依赖具体的UI实现。
    """
    
    @abstractmethod
    def set_cursor(self, cursor: QCursor) -> None:
        """设置鼠标光标
        
        Args:
            cursor: 要设置的光标类型
        """
        pass
    
    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        """获取当前鼠标位置
        
        Returns:
            tuple: (x, y) 鼠标在组件中的相对坐标
        """
        pass
    
    @abstractmethod
    def update_display(self) -> None:
        """更新显示内容
        
        触发UI组件重新绘制，用于反映状态变化
        """
        pass
    
    @abstractmethod
    def bind_mouse_event(self, event_type: str, handler: Callable[[Any], None]) -> None:
        """绑定鼠标事件处理器
        
        Args:
            event_type: 事件类型（如 'click', 'move', 'press', 'release'）
            handler: 事件处理函数
        """
        pass
    
    @abstractmethod
    def get_widget_size(self) -> Tuple[int, int]:
        """获取组件大小
        
        Returns:
            tuple: (width, height) 组件的像素尺寸
        """
        pass
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """检查组件是否启用
        
        Returns:
            bool: True表示组件启用，False表示禁用
        """
        pass