"""
均值滤波对话框模块
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout

from .spatial_filter_dialog_base import SpatialFilterDialog
from ....handlers.processing_handler import ProcessingHandler
from ....core.models.spatial_filter_params import MeanFilterParams


class MeanFilterDialog(SpatialFilterDialog):
    """
    均值滤波参数调整对话框
    
    允许用户调整均值滤波的核大小参数
    """
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        """初始化均值滤波对话框"""
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("均值滤波")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        """创建参数控制组"""
        # 核大小控制组
        kernel_group, self.kernel_slider, self.kernel_label = self._create_slider_group(
            "核大小", 3, 21, 5
        )
        main_layout.addWidget(kernel_group)
        
        # 连接滑块值变化信号
        self.kernel_slider.valueChanged.connect(self._update_kernel_label)
        self.kernel_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        """连接滑块预览事件"""
        if self.processing_handler is not None:
            self.kernel_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.kernel_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_kernel_label(self):
        """更新核大小标签"""
        # 确保核大小为奇数
        value = self.kernel_slider.value()
        if value % 2 == 0:
            value += 1
            self.kernel_slider.setValue(value)
        self.kernel_label.setText(str(value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        """发出参数变化信号"""
        params = MeanFilterParams(
            kernel_size=self.kernel_slider.value()
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        """重置所有参数到默认值"""
        self.kernel_slider.setValue(5)
    
    def get_final_parameters(self) -> MeanFilterParams:
        """获取最终参数设置"""
        return MeanFilterParams(
            kernel_size=self.kernel_slider.value()
        )
    
    def set_initial_parameters(self, params: Dict):
        """设置初始参数"""
        if params is None:
            return
        
        # 设置核大小
        kernel_size = params.get('kernel_size', 5)
        self.kernel_slider.setValue(kernel_size)