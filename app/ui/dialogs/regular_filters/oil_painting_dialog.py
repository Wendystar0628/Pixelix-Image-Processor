"""
油画滤镜对话框模块
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout

from .regular_filter_dialog_base import RegularFilterDialog
from ....handlers.processing_handler import ProcessingHandler
from ....core.models.regular_filter_params import OilPaintingParams


class OilPaintingDialog(RegularFilterDialog):
    """
    油画滤镜参数调整对话框
    
    允许用户调整笔触大小、细节级别和饱和度参数
    """
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        """初始化油画滤镜对话框"""
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("油画滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        """创建参数控制组"""
        # 笔触大小控制组
        brush_size_group, self.brush_size_slider, self.brush_size_label = self._create_slider_group(
            "笔触大小", 1, 20, 5
        )
        main_layout.addWidget(brush_size_group)
        
        # 细节级别控制组
        detail_group, self.detail_slider, self.detail_label = self._create_slider_group(
            "细节级别", 1, 10, 3
        )
        main_layout.addWidget(detail_group)
        
        # 饱和度控制组
        saturation_group, self.saturation_slider, self.saturation_label = self._create_slider_group(
            "饱和度", 1, 30, 10  # 1.0对应10
        )
        main_layout.addWidget(saturation_group)
        
        # 连接信号
        self.brush_size_slider.valueChanged.connect(self._update_brush_size_label)
        self.brush_size_slider.valueChanged.connect(self._emit_params_changed)
        
        self.detail_slider.valueChanged.connect(self._update_detail_label)
        self.detail_slider.valueChanged.connect(self._emit_params_changed)
        
        self.saturation_slider.valueChanged.connect(self._update_saturation_label)
        self.saturation_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        """连接滑块预览事件"""
        if self.processing_handler is not None:
            for slider in [self.brush_size_slider, self.detail_slider, self.saturation_slider]:
                slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
                slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_brush_size_label(self):
        """更新笔触大小标签"""
        value = self.brush_size_slider.value()
        self.brush_size_label.setText(str(value))
    
    @pyqtSlot()
    def _update_detail_label(self):
        """更新细节级别标签"""
        value = self.detail_slider.value()
        self.detail_label.setText(str(value))
    
    @pyqtSlot()
    def _update_saturation_label(self):
        """更新饱和度标签"""
        value = self.saturation_slider.value() / 10.0
        self.saturation_label.setText(f"{value:.1f}")
    
    @pyqtSlot()
    def _emit_params_changed(self):
        """发出参数变化信号"""
        params = OilPaintingParams(
            brush_size=self.brush_size_slider.value(),
            detail_level=self.detail_slider.value(),
            saturation=self.saturation_slider.value() / 10.0
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        """重置所有参数到默认值"""
        self.brush_size_slider.setValue(5)
        self.detail_slider.setValue(3)
        self.saturation_slider.setValue(10)  # 1.0
    
    def get_final_parameters(self) -> OilPaintingParams:
        """获取最终参数设置"""
        return OilPaintingParams(
            brush_size=self.brush_size_slider.value(),
            detail_level=self.detail_slider.value(),
            saturation=self.saturation_slider.value() / 10.0
        )
    
    def set_initial_parameters(self, params: Dict):
        """设置初始参数"""
        if params is None:
            return
        
        # 设置笔触大小
        brush_size = params.get('brush_size', 5)
        self.brush_size_slider.setValue(brush_size)
        
        # 设置细节级别
        detail_level = params.get('detail_level', 3)
        self.detail_slider.setValue(detail_level)
        
        # 设置饱和度
        saturation = params.get('saturation', 1.0)
        self.saturation_slider.setValue(int(saturation * 10))