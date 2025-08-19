"""
Sobel边缘检测对话框模块
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup, QGroupBox

from .spatial_filter_dialog_base import SpatialFilterDialog
from ....handlers.processing_handler import ProcessingHandler
from ....core.models.spatial_filter_params import SobelEdgeParams


class SobelEdgeDialog(SpatialFilterDialog):
    """
    Sobel边缘检测参数调整对话框
    
    允许用户调整Sobel算子的方向选择和阈值参数
    """
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        """初始化Sobel边缘检测对话框"""
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("Sobel边缘检测")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        """创建参数控制组"""
        # 方向选择控制组
        direction_group = self._create_direction_group()
        main_layout.addWidget(direction_group)
        
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
        
        # 连接信号
        self._connect_parameter_signals()
    
    def _create_direction_group(self) -> QGroupBox:
        """创建方向选择控制组"""
        group = QGroupBox("检测方向")
        layout = QVBoxLayout()
        
        # 创建单选按钮组
        self.direction_group = QButtonGroup()
        
        self.horizontal_radio = QRadioButton("水平方向 (dx=1, dy=0)")
        self.vertical_radio = QRadioButton("垂直方向 (dx=0, dy=1)")
        self.both_radio = QRadioButton("两个方向 (dx=1, dy=1)")
        
        # 默认选择两个方向
        self.both_radio.setChecked(True)
        
        # 添加到按钮组
        self.direction_group.addButton(self.horizontal_radio, 0)
        self.direction_group.addButton(self.vertical_radio, 1)
        self.direction_group.addButton(self.both_radio, 2)
        
        # 添加到布局
        layout.addWidget(self.horizontal_radio)
        layout.addWidget(self.vertical_radio)
        layout.addWidget(self.both_radio)
        
        group.setLayout(layout)
        return group
    
    def _connect_parameter_signals(self):
        """连接参数变化信号"""
        # 方向选择信号
        self.direction_group.buttonClicked.connect(self._emit_params_changed)
        
        # 滑块信号
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
    
    def _get_direction_values(self) -> tuple:
        """获取当前选择的方向值"""
        selected_id = self.direction_group.checkedId()
        if selected_id == 0:  # 水平
            return (1, 0)
        elif selected_id == 1:  # 垂直
            return (0, 1)
        else:  # 两个方向
            return (1, 1)
    
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
        dx, dy = self._get_direction_values()
        params = SobelEdgeParams(
            dx=dx,
            dy=dy,
            kernel_size=self.kernel_slider.value(),
            scale=self.scale_slider.value() / 10.0,
            delta=float(self.delta_slider.value())
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        """重置所有参数到默认值"""
        self.both_radio.setChecked(True)
        self.kernel_slider.setValue(3)
        self.scale_slider.setValue(10)  # 1.0
        self.delta_slider.setValue(0)
    
    def get_final_parameters(self) -> SobelEdgeParams:
        """获取最终参数设置"""
        dx, dy = self._get_direction_values()
        return SobelEdgeParams(
            dx=dx,
            dy=dy,
            kernel_size=self.kernel_slider.value(),
            scale=self.scale_slider.value() / 10.0,
            delta=float(self.delta_slider.value())
        )
    
    def set_initial_parameters(self, params: Dict):
        """设置初始参数"""
        if params is None:
            return
        
        # 设置方向
        dx = params.get('dx', 1)
        dy = params.get('dy', 1)
        if dx == 1 and dy == 0:
            self.horizontal_radio.setChecked(True)
        elif dx == 0 and dy == 1:
            self.vertical_radio.setChecked(True)
        else:
            self.both_radio.setChecked(True)
        
        # 设置核大小
        kernel_size = params.get('kernel_size', 3)
        self.kernel_slider.setValue(kernel_size)
        
        # 设置缩放因子
        scale = params.get('scale', 1.0)
        self.scale_slider.setValue(int(scale * 10))
        
        # 设置偏移量
        delta = params.get('delta', 0.0)
        self.delta_slider.setValue(int(delta))