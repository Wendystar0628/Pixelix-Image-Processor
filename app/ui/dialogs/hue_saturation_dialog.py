"""
色相饱和度对话框模块。
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QLabel,
    QPushButton,
    QGroupBox,
    QSpinBox,
)

from .base_dialog import BaseOperationDialog
from ...handlers.processing_handler import ProcessingHandler
from ...core.models.operation_params import HueSaturationParams


class HueSaturationDialog(BaseOperationDialog[HueSaturationParams]):
    """
    色相/饱和度调整对话框。
    
    允许用户调整图像的色相、饱和度和明度。
    """
    
    # 定义参数变化的信号
    params_changed = pyqtSignal(HueSaturationParams)
    # 定义应用操作的信号
    apply_operation = pyqtSignal(HueSaturationParams)
    
    def __init__(self, parent=None, initial_params=None, processing_handler: Optional[ProcessingHandler] = None):
        """
        初始化色相/饱和度对话框。
        
        Args:
            parent: 父窗口部件
            initial_params: 初始参数字典 (向后兼容的字典格式)
            processing_handler: 处理程序实例，用于连接滑块事件以支持预览降采样
        """
        super().__init__(parent, initial_params)
        
        # 保存对处理程序的引用
        self.processing_handler = processing_handler
        
        # 设置对话框属性
        self.setWindowTitle("色相/饱和度")
        self.setMinimumWidth(350)
        
        # 创建UI控件
        self._setup_ui()
        
        # 连接信号和槽
        self._connect_signals()
        
        # 设置初始参数
        self.set_initial_parameters(self.initial_params)
        
        # 标记是否已连接滑块事件
        self._slider_events_connected = False
        
        # 连接滑块事件
        self._connect_slider_events()
        
    def _setup_ui(self):
        """创建和布局UI控件。"""
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 色相部分
        hue_group = QGroupBox("色相")
        hue_layout = QVBoxLayout(hue_group)
        
        # 色相滑块和标签水平布局
        hue_slider_layout = QHBoxLayout()
        self.hue_value_label = QLabel("0")
        self.hue_value_label.setMinimumWidth(40)
        self.hue_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.hue_slider = QSlider(Qt.Orientation.Horizontal)
        self.hue_slider.setRange(-180, 180)
        self.hue_slider.setValue(0)
        self.hue_slider.setTickInterval(30)
        self.hue_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        
        self.hue_spin = QSpinBox()
        self.hue_spin.setRange(-180, 180)
        self.hue_spin.setValue(0)
        
        hue_slider_layout.addWidget(QLabel("-"))
        hue_slider_layout.addWidget(self.hue_slider)
        hue_slider_layout.addWidget(QLabel("+"))
        hue_slider_layout.addWidget(self.hue_spin)
        
        hue_layout.addLayout(hue_slider_layout)
        
        # 饱和度部分
        saturation_group = QGroupBox("饱和度")
        saturation_layout = QVBoxLayout(saturation_group)
        
        # 饱和度滑块和标签水平布局
        saturation_slider_layout = QHBoxLayout()
        self.saturation_value_label = QLabel("0")
        self.saturation_value_label.setMinimumWidth(40)
        self.saturation_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setRange(-100, 100)
        self.saturation_slider.setValue(0)
        self.saturation_slider.setTickInterval(20)
        self.saturation_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        
        self.saturation_spin = QSpinBox()
        self.saturation_spin.setRange(-100, 100)
        self.saturation_spin.setValue(0)
        
        saturation_slider_layout.addWidget(QLabel("-"))
        saturation_slider_layout.addWidget(self.saturation_slider)
        saturation_slider_layout.addWidget(QLabel("+"))
        saturation_slider_layout.addWidget(self.saturation_spin)
        
        saturation_layout.addLayout(saturation_slider_layout)
        
        # 明度部分
        lightness_group = QGroupBox("明度")
        lightness_layout = QVBoxLayout(lightness_group)
        
        # 明度滑块和标签水平布局
        lightness_slider_layout = QHBoxLayout()
        self.lightness_value_label = QLabel("0")
        self.lightness_value_label.setMinimumWidth(40)
        self.lightness_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.lightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.lightness_slider.setRange(-100, 100)
        self.lightness_slider.setValue(0)
        self.lightness_slider.setTickInterval(20)
        self.lightness_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        
        self.lightness_spin = QSpinBox()
        self.lightness_spin.setRange(-100, 100)
        self.lightness_spin.setValue(0)
        
        lightness_slider_layout.addWidget(QLabel("-"))
        lightness_slider_layout.addWidget(self.lightness_slider)
        lightness_slider_layout.addWidget(QLabel("+"))
        lightness_slider_layout.addWidget(self.lightness_spin)
        
        lightness_layout.addLayout(lightness_slider_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        self.reset_button = QPushButton("重置")
        self.cancel_button = QPushButton("取消")
        self.ok_button = QPushButton("确定")
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        # 添加所有组件到主布局
        main_layout.addWidget(hue_group)
        main_layout.addWidget(saturation_group)
        main_layout.addWidget(lightness_group)
        main_layout.addLayout(button_layout)
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 连接滑块和数值框
        self.hue_slider.valueChanged.connect(self.hue_spin.setValue)
        self.hue_spin.valueChanged.connect(self.hue_slider.setValue)
        
        self.saturation_slider.valueChanged.connect(self.saturation_spin.setValue)
        self.saturation_spin.valueChanged.connect(self.saturation_slider.setValue)
        
        self.lightness_slider.valueChanged.connect(self.lightness_spin.setValue)
        self.lightness_spin.valueChanged.connect(self.lightness_slider.setValue)
        
        # 触发参数变化
        self.hue_slider.valueChanged.connect(self._emit_params_changed)
        self.saturation_slider.valueChanged.connect(self._emit_params_changed)
        self.lightness_slider.valueChanged.connect(self._emit_params_changed)
        
        # 连接按钮
        self.reset_button.clicked.connect(self._reset_values)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self._apply_and_close)
    
    def _connect_slider_events(self):
        """
        连接滑块的按下事件以支持预览降采样
        """
        if self.processing_handler is not None and not self._slider_events_connected:
            # 连接色相滑块事件
            self.hue_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.hue_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            
            # 连接饱和度滑块事件
            self.saturation_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.saturation_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            
            # 连接明度滑块事件
            self.lightness_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.lightness_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            
            self._slider_events_connected = True
    
    @pyqtSlot()
    def _emit_params_changed(self):
        """当参数变化时发出信号"""
        params = HueSaturationParams(
            hue=self.hue_slider.value(),
            saturation=self.saturation_slider.value(),
            lightness=self.lightness_slider.value()
        )
        self.params_changed.emit(params)
        
    @pyqtSlot()
    def _reset_values(self):
        """重置所有滑块到默认值"""
        self.hue_slider.setValue(0)
        self.saturation_slider.setValue(0)
        self.lightness_slider.setValue(0)
        
    @pyqtSlot()
    def _apply_and_close(self):
        """应用参数并关闭对话框"""
        params = self.get_final_parameters()
        self.apply_operation.emit(params)
        self.accept()
        
    def get_final_parameters(self) -> HueSaturationParams:
        """
        获取最终的参数设置
        
        Returns:
            HueSaturationParams: 包含最终参数的数据类
        """
        return HueSaturationParams(
            hue=self.hue_slider.value(),
            saturation=self.saturation_slider.value(),
            lightness=self.lightness_slider.value()
        )
        
    def set_initial_parameters(self, params: Dict):
        """
        设置对话框的初始参数
        
        Args:
            params: 包含初始参数的字典
        """
        if params is None:
            return
            
        # 设置色相值
        hue = params.get('hue', 0)
        self.hue_slider.setValue(hue)
        self.hue_spin.setValue(hue)
        
        # 设置饱和度值
        saturation = params.get('saturation', 0)
        self.saturation_slider.setValue(saturation)
        self.saturation_spin.setValue(saturation)
        
        # 设置明度值
        lightness = params.get('lightness', 0)
        self.lightness_slider.setValue(lightness)
        self.lightness_spin.setValue(lightness)
