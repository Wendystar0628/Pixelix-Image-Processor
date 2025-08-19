"""交互组件接口实现"""

from typing import Tuple, Callable, Any
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import QPoint

from app.core.interfaces import InteractiveWidgetInterface


class WidgetImplementation(InteractiveWidgetInterface):
    """交互组件接口实现
    
    将InteractiveImageLabel适配为InteractiveWidgetInterface，
    为核心层提供UI交互能力的接口实现。
    """
    
    def __init__(self, widget):
        """初始化交互组件实现
        
        Args:
            widget: InteractiveImageLabel实例或其他兼容的交互组件
        """
        self._widget = widget
        self._event_handlers = {}
    
    def set_cursor(self, cursor: QCursor) -> None:
        """设置鼠标光标
        
        Args:
            cursor: 要设置的光标类型
        """
        try:
            self._widget.setCursor(cursor)
        except Exception as e:
            print(f"设置光标失败: {e}")
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """获取当前鼠标位置
        
        Returns:
            tuple: (x, y) 鼠标在组件中的相对坐标
        """
        try:
            pos = self._widget.mapFromGlobal(QCursor.pos())
            return (pos.x(), pos.y())
        except Exception as e:
            print(f"获取鼠标位置失败: {e}")
            return (0, 0)
    
    def update_display(self) -> None:
        """更新显示内容
        
        触发UI组件重新绘制，用于反映状态变化
        """
        try:
            self._widget.update()
        except Exception as e:
            print(f"更新显示失败: {e}")
    
    def bind_mouse_event(self, event_type: str, handler: Callable[[Any], None]) -> None:
        """绑定鼠标事件处理器
        
        Args:
            event_type: 事件类型（如 'click', 'move', 'press', 'release'）
            handler: 事件处理函数
        """
        try:
            # 存储事件处理器
            self._event_handlers[event_type] = handler
            
            # 根据事件类型连接到相应的Qt信号
            if event_type == 'selection_finished' and hasattr(self._widget, 'selection_finished'):
                self._widget.selection_finished.connect(handler)
            elif event_type == 'lasso_finished' and hasattr(self._widget, 'lasso_finished'):
                self._widget.lasso_finished.connect(handler)
            elif event_type == 'request_load_image' and hasattr(self._widget, 'request_load_image'):
                self._widget.request_load_image.connect(handler)
            else:
                print(f"不支持的事件类型: {event_type}")
                
        except Exception as e:
            print(f"绑定事件失败: {e}")
    
    def get_widget_size(self) -> Tuple[int, int]:
        """获取组件大小
        
        Returns:
            tuple: (width, height) 组件的像素尺寸
        """
        try:
            size = self._widget.size()
            return (size.width(), size.height())
        except Exception as e:
            print(f"获取组件大小失败: {e}")
            return (0, 0)
    
    def is_enabled(self) -> bool:
        """检查组件是否启用
        
        Returns:
            bool: True表示组件启用，False表示禁用
        """
        try:
            return self._widget.isEnabled()
        except Exception as e:
            print(f"检查组件状态失败: {e}")
            return False
    
    # 额外的便利方法，供UI层使用
    def get_widget(self):
        """获取原始组件实例
        
        Returns:
            原始的UI组件实例
        """
        return self._widget
    
    def set_interaction_mode(self, mode: str) -> None:
        """设置交互模式（如果组件支持）
        
        Args:
            mode: 交互模式字符串
        """
        try:
            if hasattr(self._widget, 'set_interaction_mode'):
                self._widget.set_interaction_mode(mode)
            elif hasattr(self._widget, 'interaction_mode'):
                # 处理枚举类型的交互模式
                from app.ui.widgets.interactive_image_label import InteractionMode
                mode_map = {
                    'none': InteractionMode.NONE,
                    'rect_selection': InteractionMode.RECT_SELECTION,
                    'lasso_selection': InteractionMode.LASSO_SELECTION,
                }
                if mode in mode_map:
                    self._widget.interaction_mode = mode_map[mode]
        except Exception as e:
            print(f"设置交互模式失败: {e}")
    
    def load_image_from_array(self, image_array) -> None:
        """从数组加载图像（如果组件支持）
        
        Args:
            image_array: numpy数组格式的图像数据
        """
        try:
            if hasattr(self._widget, 'load_image_from_array'):
                self._widget.load_image_from_array(image_array)
        except Exception as e:
            print(f"加载图像失败: {e}")