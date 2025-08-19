from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from PyQt6.QtCore import QObject, QPoint, pyqtSignal
from PyQt6.QtGui import QCursor

from ..interfaces import InteractiveWidgetInterface


class BaseTool(QObject):
    """
    基础工具类 - 所有工具的基类
    
    主要功能：
    - 工具激活/停用管理
    - 鼠标/键盘事件处理
    - 图像标签关联
    - 操作完成信号发送
    - 状态保存和恢复
    """
    
    # 操作完成信号（新增）
    operation_completed = pyqtSignal(object)  # 发送操作对象
    
    def __init__(self, interactive_widget: Optional[InteractiveWidgetInterface] = None):
        """初始化工具实例
        
        Args:
            interactive_widget: 交互组件接口实现，用于与UI交互
        """
        super().__init__()
        self._interactive_widget: Optional[InteractiveWidgetInterface] = interactive_widget
        self._is_active = False
        self._tool_state: Dict[str, Any] = {}  # 工具特定的状态
        
    def set_interactive_widget(self, interactive_widget: InteractiveWidgetInterface):
        """设置关联的交互组件接口
        
        Args:
            interactive_widget: 交互组件接口实现
        """
        self._interactive_widget = interactive_widget
    
    def get_interactive_widget(self) -> Optional[InteractiveWidgetInterface]:
        """获取交互组件接口
        
        Returns:
            交互组件接口实现，如果未设置则返回None
        """
        return self._interactive_widget
        
    @property
    def is_active(self) -> bool:
        """检查工具是否激活"""
        return self._is_active
        
    # 使用@abstractmethod装饰器，但不继承ABC
    @abstractmethod
    def activate(self):
        """激活工具，子类可重写执行特定逻辑"""
        self._is_active = True
        # 如果有交互组件，可以设置特定的光标
        if self._interactive_widget:
            try:
                self._set_tool_cursor()
            except Exception as e:
                print(f"设置工具光标失败: {e}")
        
    @abstractmethod
    def deactivate(self):
        """停用工具，子类可重写执行清理逻辑"""
        self._is_active = False
        # 重置光标为默认状态
        if self._interactive_widget:
            try:
                self._interactive_widget.set_cursor(QCursor())
            except Exception as e:
                print(f"重置光标失败: {e}")
    
    def _set_tool_cursor(self):
        """设置工具特定的光标，子类可重写"""
        # 默认实现，子类可以重写以设置特定光标
        pass
        
    def mouse_press_event(self, pos: QPoint, button: int, modifiers: int) -> bool:
        """处理鼠标按下事件，子类应重写"""
        return False
        
    def mouse_move_event(self, pos: QPoint, buttons: int, modifiers: int) -> bool:
        """处理鼠标移动事件，子类应重写"""
        return False
        
    def mouse_release_event(self, pos: QPoint, button: int, modifiers: int) -> bool:
        """处理鼠标释放事件，子类应重写"""
        return False
        
    def key_press_event(self, key: int, modifiers: int) -> bool:
        """处理键盘按下事件，子类可重写"""
        return False
        
    def key_release_event(self, key: int, modifiers: int) -> bool:
        """处理键盘释放事件，子类可重写"""
        return False
        
    def get_state(self) -> Dict[str, Any]:
        """获取工具状态，子类应重写"""
        return self._tool_state.copy()
        
    def set_state(self, state: Dict[str, Any]):
        """设置工具状态，子类应重写"""
        self._tool_state = state.copy()
    
    def _emit_operation(self, operation):
        """发送操作完成信号"""
        self.operation_completed.emit(operation)