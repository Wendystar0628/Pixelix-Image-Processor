"""
图像视图面板模块
"""

from typing import Optional

from PyQt6.QtWidgets import QWidget, QScrollArea, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSignal

from app.ui.widgets.interactive_image_label import InteractiveImageLabel
from app.utils.image_utils import numpy_to_qpixmap
import numpy as np


class ImageViewPanel(QWidget):
    """
    图像视图面板类，负责显示和管理图像。
    """
    # 当用户请求加载图像时发出的信号
    request_load_image = pyqtSignal(str)
    
    def __init__(self, state_manager=None, image_processor=None, parent=None):
        """
        初始化图像视图面板
        
        Args:
            state_manager: 状态管理器（依赖注入）
            image_processor: 图像处理器（依赖注入） 
            parent: 父级部件
        """
        super().__init__(parent)
        
        # 保存依赖注入的组件
        self.state_manager = state_manager
        self.image_processor = image_processor
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI组件"""
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # 创建交互式图像标签
        self.image_label = InteractiveImageLabel()
        self.image_label.set_image(None)
        self.scroll_area.setWidget(self.image_label)
        
        # 设置图像标签的滚动区域，以便它可以调整滚动视图
        self.image_label.set_scroll_area(self.scroll_area)
        
        # 连接信号
        self.image_label.request_load_image.connect(self.request_load_image)
        
        # 将滚动区域添加到布局中
        layout.addWidget(self.scroll_area)
        
    def set_image(self, pixmap: Optional[QPixmap]):
        """
        设置要显示的图像
        
        Args:
            pixmap: 要显示的QPixmap对象
        """
        self.image_label.set_image(pixmap)
        
    def update_image(self, image: np.ndarray):
        """
        使用NumPy数组更新图像
        
        Args:
            image: NumPy格式的图像数据
        """
        pixmap = numpy_to_qpixmap(image)
        self.image_label.set_image(pixmap)
        
    def clear_image(self):
        """清除当前显示的图像"""
        self.image_label.set_image(None)
    
    def initial_render(self):
        """初始渲染图像视图"""
        # 确保显示最新的图像状态
        self.update_display()
    
    def update_display(self):
        """更新显示内容"""
        if self.state_manager:
            try:
                # 使用get_image_for_display方法获取当前显示图像
                current_image = self.state_manager.get_image_for_display()
                if current_image is not None:
                    # 将numpy数组转换为QPixmap并显示
                    pixmap = numpy_to_qpixmap(current_image)
                    self.set_image(pixmap)
                else:
                    # 清空显示
                    if self.image_label:
                        self.image_label.clear()
            except Exception as e:
                print(f"更新图像显示失败: {e}")
                import traceback
                traceback.print_exc()
                # 清空显示
                if self.image_label:
                    self.image_label.clear() 