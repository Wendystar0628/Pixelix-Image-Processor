"""
拉普拉斯边缘检测对话框模块
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout

from .spatial_filter_dialog_base import SpatialFilterDialog
from ....handlers.processing_handler import ProcessingHandler
from ....core.models.spatial_filter_params import LaplacianEdgeParams


class LaplacianEdgeDialog(SpatialFilterDialog):
    """
    拉普拉斯边缘检测参数调整对话框
    
    允许用户调整拉普拉斯算子的核大小和缩放参数
    """
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        """初始化拉普拉斯边缘检测对话框"""
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("拉普拉斯边缘检测")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        """创建参数控制组"""
        # 核大小控制组
        kernel_group, self.kernel_slider, self.kernel_label = self._create_slider_group(
            "核大小", 1, 7, 3
        )
        main_layout.addWidget(kernel_group)
        
        # 缩放因子控制组
        scale_group, self.scale_slider, self.scale_label = self._create_slider_group(
            "缩放因子", 1, 50, 10  # 1.0对应10
        )
        main_layout.addWidget(scale_group)
        
        # 偏移量控制组
        delta_group, self.delta_slider, self.delta_label = self._create_slider_group(
            "偏移量", 0, 100, 0
        )
        main_layout.addWidget(delta_group)
        
        # 连接滑块值变化信号
        self.kernel_slider.valueChanged.connect(self._update_kernel_label)
        self.kernel_slider.valueChanged.connect(self._emit_params_changed)
        
        self.scale_slider.valueChanged.connect(self._update_scale_label)
        self.scale_slider.valueChanged.connect(self._emit_params_changed)
        
        self.delta_slider.valueChanged.connect(self._update_delta_label)
        self.delta_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        """连接滑块预览事件"""
        if self.processing_handler is not None:
            for slider in [self.kernel_slider, self.scale_slider, self.delta_slider]:
                slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
                slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
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
    def _update_scale_label(self):
        """更新缩放因子标签"""
        value = self.scale_slider.value() / 10.0
        self.scale_label.setText(f"{value:.1f}")
    
    @pyqtSlot()
    def _update_delta_label(self):
        """更新偏移量标签"""
        value = self.delta_slider.value()
        self.delta_label.setText(str(value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        """发出参数变化信号"""
        params = LaplacianEdgeParams(
            kernel_size=self.kernel_slider.value(),
            scale=self.scale_slider.value() / 10.0,
            delta=float(self.delta_slider.value())
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        """重置所有参数到默认值"""
        self.kernel_slider.setValue(3)
        self.scale_slider.setValue(10)  # 1.0
        self.delta_slider.setValue(0)
    
    def get_final_parameters(self) -> LaplacianEdgeParams:
        """获取最终参数设置"""
        return LaplacianEdgeParams(
            kernel_size=self.kernel_slider.value(),
            scale=self.scale_slider.value() / 10.0,
            delta=float(self.delta_slider.value())
        )
    
    def set_initial_parameters(self, params: Dict):
        """设置初始参数"""
        if params is None:
            return
        
        # 设置核大小
        kernel_size = params.get('kernel_size', 3)
        self.kernel_slider.setValue(kernel_size)
        
        # 设置缩放因子
        scale = params.get('scale', 1.0)
        self.scale_slider.setValue(int(scale * 10))
        
        # 设置偏移量
        delta = params.get('delta', 0.0)
        self.delta_slider.setValue(int(delta))