"""
素描滤镜对话框模块
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout

from .regular_filter_dialog_base import RegularFilterDialog
from ....handlers.processing_handler import ProcessingHandler
from ....core.models.regular_filter_params import SketchParams


class SketchDialog(RegularFilterDialog):
    """
    素描滤镜参数调整对话框
    
    允许用户调整线条强度、对比度和背景色参数
    """
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        """初始化素描滤镜对话框"""
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("素描滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        """创建参数控制组"""
        # 线条强度控制组
        line_strength_group, self.line_strength_slider, self.line_strength_label = self._create_slider_group(
            "线条强度", 1, 50, 10  # 1.0对应10
        )
        main_layout.addWidget(line_strength_group)
        
        # 对比度控制组
        contrast_group, self.contrast_slider, self.contrast_label = self._create_slider_group(
            "对比度", 1, 50, 10  # 1.0对应10
        )
        main_layout.addWidget(contrast_group)
        
        # 背景色控制组
        background_group, self.background_slider, self.background_label = self._create_slider_group(
            "背景色 (灰度)", 0, 255, 255
        )
        main_layout.addWidget(background_group)
        
        # 连接信号
        self.line_strength_slider.valueChanged.connect(self._update_line_strength_label)
        self.line_strength_slider.valueChanged.connect(self._emit_params_changed)
        
        self.contrast_slider.valueChanged.connect(self._update_contrast_label)
        self.contrast_slider.valueChanged.connect(self._emit_params_changed)
        
        self.background_slider.valueChanged.connect(self._update_background_label)
        self.background_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        """连接滑块预览事件"""
        if self.processing_handler is not None:
            for slider in [self.line_strength_slider, self.contrast_slider, self.background_slider]:
                slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
                slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_line_strength_label(self):
        """更新线条强度标签"""
        value = self.line_strength_slider.value() / 10.0
        self.line_strength_label.setText(f"{value:.1f}")
    
    @pyqtSlot()
    def _update_contrast_label(self):
        """更新对比度标签"""
        value = self.contrast_slider.value() / 10.0
        self.contrast_label.setText(f"{value:.1f}")
    
    @pyqtSlot()
    def _update_background_label(self):
        """更新背景色标签"""
        value = self.background_slider.value()
        self.background_label.setText(str(value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        """发出参数变化信号"""
        params = SketchParams(
            line_strength=self.line_strength_slider.value() / 10.0,
            contrast=self.contrast_slider.value() / 10.0,
            background_color=self.background_slider.value()
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        """重置所有参数到默认值"""
        self.line_strength_slider.setValue(10)  # 1.0
        self.contrast_slider.setValue(10)       # 1.0
        self.background_slider.setValue(255)    # 白色背景
    
    def get_final_parameters(self) -> SketchParams:
        """获取最终参数设置"""
        return SketchParams(
            line_strength=self.line_strength_slider.value() / 10.0,
            contrast=self.contrast_slider.value() / 10.0,
            background_color=self.background_slider.value()
        )
    
    def set_initial_parameters(self, params: Dict):
        """设置初始参数"""
        if params is None:
            return
        
        # 设置线条强度
        line_strength = params.get('line_strength', 1.0)
        self.line_strength_slider.setValue(int(line_strength * 10))
        
        # 设置对比度
        contrast = params.get('contrast', 1.0)
        self.contrast_slider.setValue(int(contrast * 10))
        
        # 设置背景色
        background_color = params.get('background_color', 255)
        self.background_slider.setValue(background_color)