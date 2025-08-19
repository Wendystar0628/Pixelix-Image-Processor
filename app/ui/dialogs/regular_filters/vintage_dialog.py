"""
怀旧滤镜对话框模块
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout

from .regular_filter_dialog_base import RegularFilterDialog
from ....handlers.processing_handler import ProcessingHandler
from ....core.models.regular_filter_params import VintageParams


class VintageDialog(RegularFilterDialog):
    """
    怀旧滤镜参数调整对话框
    
    允许用户调整怀旧强度、色温和暗角效果参数
    """
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        """初始化怀旧滤镜对话框"""
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("怀旧滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        """创建参数控制组"""
        # 怀旧强度控制组
        intensity_group, self.intensity_slider, self.intensity_label = self._create_slider_group(
            "怀旧强度", 0, 100, 50  # 0.5对应50
        )
        main_layout.addWidget(intensity_group)
        
        # 色温控制组
        temperature_group, self.temperature_slider, self.temperature_label = self._create_slider_group(
            "色温", -100, 100, 0  # -1.0到1.0映射到-100到100
        )
        main_layout.addWidget(temperature_group)
        
        # 暗角效果控制组
        vignette_group, self.vignette_slider, self.vignette_label = self._create_slider_group(
            "暗角效果", 0, 100, 30  # 0.3对应30
        )
        main_layout.addWidget(vignette_group)
        
        # 连接信号
        self.intensity_slider.valueChanged.connect(self._update_intensity_label)
        self.intensity_slider.valueChanged.connect(self._emit_params_changed)
        
        self.temperature_slider.valueChanged.connect(self._update_temperature_label)
        self.temperature_slider.valueChanged.connect(self._emit_params_changed)
        
        self.vignette_slider.valueChanged.connect(self._update_vignette_label)
        self.vignette_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        """连接滑块预览事件"""
        if self.processing_handler is not None:
            for slider in [self.intensity_slider, self.temperature_slider, self.vignette_slider]:
                slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
                slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_intensity_label(self):
        """更新怀旧强度标签"""
        value = self.intensity_slider.value() / 100.0
        self.intensity_label.setText(f"{value:.2f}")
    
    @pyqtSlot()
    def _update_temperature_label(self):
        """更新色温标签"""
        value = self.temperature_slider.value() / 100.0
        self.temperature_label.setText(f"{value:+.2f}")
    
    @pyqtSlot()
    def _update_vignette_label(self):
        """更新暗角效果标签"""
        value = self.vignette_slider.value() / 100.0
        self.vignette_label.setText(f"{value:.2f}")
    
    @pyqtSlot()
    def _emit_params_changed(self):
        """发出参数变化信号"""
        params = VintageParams(
            intensity=self.intensity_slider.value() / 100.0,
            temperature=self.temperature_slider.value() / 100.0,
            vignette=self.vignette_slider.value() / 100.0
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        """重置所有参数到默认值"""
        self.intensity_slider.setValue(50)  # 0.5
        self.temperature_slider.setValue(0)  # 0.0
        self.vignette_slider.setValue(30)   # 0.3
    
    def get_final_parameters(self) -> VintageParams:
        """获取最终参数设置"""
        return VintageParams(
            intensity=self.intensity_slider.value() / 100.0,
            temperature=self.temperature_slider.value() / 100.0,
            vignette=self.vignette_slider.value() / 100.0
        )
    
    def set_initial_parameters(self, params: Dict):
        """设置初始参数"""
        if params is None:
            return
        
        # 设置怀旧强度
        intensity = params.get('intensity', 0.5)
        self.intensity_slider.setValue(int(intensity * 100))
        
        # 设置色温
        temperature = params.get('temperature', 0.0)
        self.temperature_slider.setValue(int(temperature * 100))
        
        # 设置暗角效果
        vignette = params.get('vignette', 0.3)
        self.vignette_slider.setValue(int(vignette * 100))