"""
高斯模糊滤波对话框模块
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout

from .spatial_filter_dialog_base import SpatialFilterDialog
from ....handlers.processing_handler import ProcessingHandler
from ....core.models.spatial_filter_params import GaussianBlurParams


class GaussianBlurDialog(SpatialFilterDialog):
    """
    高斯模糊滤波参数调整对话框
    
    允许用户调整高斯模糊的标准差和核大小参数
    """
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        """初始化高斯模糊对话框"""
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("高斯模糊滤波")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        """创建参数控制组"""
        # 标准差X控制组
        sigma_x_group, self.sigma_x_slider, self.sigma_x_label = self._create_slider_group(
            "标准差 X", 1, 100, 10  # 1.0对应10，便于滑块控制
        )
        main_layout.addWidget(sigma_x_group)
        
        # 标准差Y控制组
        sigma_y_group, self.sigma_y_slider, self.sigma_y_label = self._create_slider_group(
            "标准差 Y", 1, 100, 10
        )
        main_layout.addWidget(sigma_y_group)
        
        # 核大小控制组
        kernel_group, self.kernel_slider, self.kernel_label = self._create_slider_group(
            "核大小", 3, 21, 5
        )
        main_layout.addWidget(kernel_group)
        
        # 连接滑块值变化信号
        self.sigma_x_slider.valueChanged.connect(self._update_sigma_x_label)
        self.sigma_x_slider.valueChanged.connect(self._emit_params_changed)
        
        self.sigma_y_slider.valueChanged.connect(self._update_sigma_y_label)
        self.sigma_y_slider.valueChanged.connect(self._emit_params_changed)
        
        self.kernel_slider.valueChanged.connect(self._update_kernel_label)
        self.kernel_slider.valueChanged.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        """连接滑块预览事件"""
        if self.processing_handler is not None:
            # 连接所有滑块的按下和释放事件
            for slider in [self.sigma_x_slider, self.sigma_y_slider, self.kernel_slider]:
                slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
                slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_sigma_x_label(self):
        """更新标准差X标签"""
        value = self.sigma_x_slider.value() / 10.0  # 转换为实际值
        self.sigma_x_label.setText(f"{value:.1f}")
    
    @pyqtSlot()
    def _update_sigma_y_label(self):
        """更新标准差Y标签"""
        value = self.sigma_y_slider.value() / 10.0
        self.sigma_y_label.setText(f"{value:.1f}")
    
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
        params = GaussianBlurParams(
            sigma_x=self.sigma_x_slider.value() / 10.0,
            sigma_y=self.sigma_y_slider.value() / 10.0,
            kernel_size=self.kernel_slider.value()
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        """重置所有参数到默认值"""
        self.sigma_x_slider.setValue(10)  # 1.0
        self.sigma_y_slider.setValue(10)  # 1.0
        self.kernel_slider.setValue(5)
    
    def get_final_parameters(self) -> GaussianBlurParams:
        """获取最终参数设置"""
        return GaussianBlurParams(
            sigma_x=self.sigma_x_slider.value() / 10.0,
            sigma_y=self.sigma_y_slider.value() / 10.0,
            kernel_size=self.kernel_slider.value()
        )
    
    def set_initial_parameters(self, params: Dict):
        """设置初始参数"""
        if params is None:
            return
        
        # 设置标准差X
        sigma_x = params.get('sigma_x', 1.0)
        self.sigma_x_slider.setValue(int(sigma_x * 10))
        
        # 设置标准差Y
        sigma_y = params.get('sigma_y', 1.0)
        self.sigma_y_slider.setValue(int(sigma_y * 10))
        
        # 设置核大小
        kernel_size = params.get('kernel_size', 5)
        self.kernel_slider.setValue(kernel_size)