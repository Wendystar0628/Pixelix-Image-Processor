"""
锐化滤波对话框模块
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout

from .spatial_filter_dialog_base import SpatialFilterDialog
from ....handlers.processing_handler import ProcessingHandler
from ....core.models.spatial_filter_params import SharpenParams


class SharpenDialog(SpatialFilterDialog):
    """
    锐化滤波参数调整对话框
    
    允许用户调整锐化强度、半径和阈值参数
    """
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        """初始化锐化滤波对话框"""
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("锐化滤波")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        """创建参数控制组"""
        # 锐化强度控制组
        strength_group, self.strength_slider, self.strength_label = self._create_slider_group(
            "锐化强度", 1, 50, 10  # 1.0对应10
        )
        main_layout.addWidget(strength_group)
        
        # 锐化半径控制组
        radius_group, self.radius_slider, self.radius_label = self._create_slider_group(
            "锐化半径", 1, 50, 10  # 1.0对应10
        )
        main_layout.addWidget(radius_group)
        
        # 阈值控制组
        threshold_group, self.threshold_slider, self.threshold_label = self._create_slider_group(
            "阈值", 0, 100, 0  # 0.0对应0
        )
        main_layout.addWidget(threshold_group)
        
        # 连接滑块值变化信号
        self.strength_slider.valueChanged.connect(self._update_strength_label)
        self.strength_slider.valueChanged.connect(self._emit_params_changed)
        
        self.radius_slider.valueChanged.connect(self._update_radius_label)
        self.radius_slider.valueChanged.connect(self._emit_params_changed)
        
        self.threshold_slider.valueChanged.connect(self._update_threshold_label)
        self.threshold_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        """连接滑块预览事件"""
        if self.processing_handler is not None:
            for slider in [self.strength_slider, self.radius_slider, self.threshold_slider]:
                slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
                slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_strength_label(self):
        """更新锐化强度标签"""
        value = self.strength_slider.value() / 10.0
        self.strength_label.setText(f"{value:.1f}")
    
    @pyqtSlot()
    def _update_radius_label(self):
        """更新锐化半径标签"""
        value = self.radius_slider.value() / 10.0
        self.radius_label.setText(f"{value:.1f}")
    
    @pyqtSlot()
    def _update_threshold_label(self):
        """更新阈值标签"""
        value = self.threshold_slider.value() / 10.0
        self.threshold_label.setText(f"{value:.1f}")
    
    @pyqtSlot()
    def _emit_params_changed(self):
        """发出参数变化信号"""
        params = SharpenParams(
            strength=self.strength_slider.value() / 10.0,
            radius=self.radius_slider.value() / 10.0,
            threshold=self.threshold_slider.value() / 10.0
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        """重置所有参数到默认值"""
        self.strength_slider.setValue(10)  # 1.0
        self.radius_slider.setValue(10)   # 1.0
        self.threshold_slider.setValue(0)  # 0.0
    
    def get_final_parameters(self) -> SharpenParams:
        """获取最终参数设置"""
        return SharpenParams(
            strength=self.strength_slider.value() / 10.0,
            radius=self.radius_slider.value() / 10.0,
            threshold=self.threshold_slider.value() / 10.0
        )
    
    def set_initial_parameters(self, params: Dict):
        """设置初始参数"""
        if params is None:
            return
        
        # 设置锐化强度
        strength = params.get('strength', 1.0)
        self.strength_slider.setValue(int(strength * 10))
        
        # 设置锐化半径
        radius = params.get('radius', 1.0)
        self.radius_slider.setValue(int(radius * 10))
        
        # 设置阈值
        threshold = params.get('threshold', 0.0)
        self.threshold_slider.setValue(int(threshold * 10))