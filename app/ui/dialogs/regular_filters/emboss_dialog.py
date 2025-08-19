"""
浮雕滤镜对话框模块
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout

from .regular_filter_dialog_base import RegularFilterDialog
from ....handlers.processing_handler import ProcessingHandler
from ....core.models.regular_filter_params import EmbossParams


class EmbossDialog(RegularFilterDialog):
    """
    浮雕滤镜参数调整对话框
    
    允许用户调整浮雕方向和深度参数
    """
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        """初始化浮雕滤镜对话框"""
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("浮雕滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        """创建参数控制组"""
        # 浮雕方向控制组
        direction_items = [
            "右下 (0°)", "下 (45°)", "左下 (90°)", "左 (135°)",
            "左上 (180°)", "上 (225°)", "右上 (270°)", "右 (315°)"
        ]
        direction_group, self.direction_combo = self._create_combo_group(
            "浮雕方向", direction_items, 0
        )
        main_layout.addWidget(direction_group)
        
        # 浮雕深度控制组
        depth_group, self.depth_slider, self.depth_label = self._create_slider_group(
            "浮雕深度", 1, 50, 10  # 1.0对应10
        )
        main_layout.addWidget(depth_group)
        
        # 连接信号
        self.direction_combo.currentIndexChanged.connect(self._emit_params_changed)
        self.depth_slider.valueChanged.connect(self._update_depth_label)
        self.depth_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        """连接滑块预览事件"""
        if self.processing_handler is not None:
            self.depth_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.depth_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_depth_label(self):
        """更新浮雕深度标签"""
        value = self.depth_slider.value() / 10.0
        self.depth_label.setText(f"{value:.1f}")
    
    @pyqtSlot()
    def _emit_params_changed(self):
        """发出参数变化信号"""
        params = EmbossParams(
            direction=self.direction_combo.currentIndex(),
            depth=self.depth_slider.value() / 10.0
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        """重置所有参数到默认值"""
        self.direction_combo.setCurrentIndex(0)
        self.depth_slider.setValue(10)  # 1.0
    
    def get_final_parameters(self) -> EmbossParams:
        """获取最终参数设置"""
        return EmbossParams(
            direction=self.direction_combo.currentIndex(),
            depth=self.depth_slider.value() / 10.0
        )
    
    def set_initial_parameters(self, params: Dict):
        """设置初始参数"""
        if params is None:
            return
        
        # 设置浮雕方向
        direction = params.get('direction', 0)
        self.direction_combo.setCurrentIndex(direction)
        
        # 设置浮雕深度
        depth = params.get('depth', 1.0)
        self.depth_slider.setValue(int(depth * 10))