"""
亮度/对比度对话框模块。
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
)

from .base_dialog import BaseOperationDialog
from ...handlers.processing_handler import ProcessingHandler
from ...core.models.operation_params import BrightnessContrastParams


class BrightnessContrastDialog(BaseOperationDialog):
    """
    亮度/对比度调整对话框。
    
    允许用户调整图像的亮度和对比度。
    """
    
    # 定义参数变化的信号
    params_changed = pyqtSignal(BrightnessContrastParams)
    # 定义应用操作的信号
    apply_operation = pyqtSignal(BrightnessContrastParams)
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, processing_handler: Optional[ProcessingHandler] = None):
        """
        初始化亮度/对比度对话框。
        
        Args:
            parent: 父窗口部件
            initial_params: 初始参数字典 (向后兼容的字典格式)
            processing_handler: 处理程序实例，用于连接滑块事件以支持预览降采样
        """
        super().__init__(parent, initial_params)
        
        # 保存对处理程序的引用
        self.processing_handler = processing_handler
        
        # 设置对话框属性
        self.setWindowTitle("亮度/对比度")
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
        """创建和设置UI控件"""
        main_layout = QVBoxLayout()
        
        # === 亮度组 ===
        brightness_group = QGroupBox("亮度")
        brightness_layout = QVBoxLayout()
        
        # 亮度滑块和标签布局
        brightness_slider_layout = QHBoxLayout()
        
        # 亮度值标签
        self.brightness_value_label = QLabel("0")
        self.brightness_value_label.setMinimumWidth(30)
        self.brightness_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # 亮度滑块
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(-255)
        self.brightness_slider.setMaximum(255)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setTracking(True)  # 实时更新
        
        brightness_slider_layout.addWidget(self.brightness_slider)
        brightness_slider_layout.addWidget(self.brightness_value_label)
        
        brightness_layout.addLayout(brightness_slider_layout)
        brightness_group.setLayout(brightness_layout)
        
        # === 对比度组 ===
        contrast_group = QGroupBox("对比度")
        contrast_layout = QVBoxLayout()
        
        # 对比度滑块和标签布局
        contrast_slider_layout = QHBoxLayout()
        
        # 对比度值标签
        self.contrast_value_label = QLabel("0")
        self.contrast_value_label.setMinimumWidth(30)
        self.contrast_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # 对比度滑块
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setMinimum(-255)
        self.contrast_slider.setMaximum(255)
        self.contrast_slider.setValue(0)
        self.contrast_slider.setTracking(True)  # 实时更新
        
        contrast_slider_layout.addWidget(self.contrast_slider)
        contrast_slider_layout.addWidget(self.contrast_value_label)
        
        contrast_layout.addLayout(contrast_slider_layout)
        contrast_group.setLayout(contrast_layout)
        
        # === 按钮布局 ===
        button_layout = QHBoxLayout()
        
        # 重置按钮
        self.reset_button = QPushButton("重置")
        
        # 取消按钮
        self.cancel_button = QPushButton("取消")
        
        # 确定按钮
        self.ok_button = QPushButton("确定")
        self.ok_button.setDefault(True)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        # 添加所有组件到主布局
        main_layout.addWidget(brightness_group)
        main_layout.addWidget(contrast_group)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 亮度滑块值变化连接到更新标签
        self.brightness_slider.valueChanged.connect(self._update_brightness_label)
        # 当亮度变化时发送参数变化信号
        self.brightness_slider.valueChanged.connect(self._emit_params_changed)
        
        # 对比度滑块值变化连接到更新标签
        self.contrast_slider.valueChanged.connect(self._update_contrast_label)
        # 当对比度变化时发送参数变化信号
        self.contrast_slider.valueChanged.connect(self._emit_params_changed)
        
        # 重置按钮
        self.reset_button.clicked.connect(self._reset_values)
        
        # 取消按钮
        self.cancel_button.clicked.connect(self.reject)
        
        # 确定按钮
        self.ok_button.clicked.connect(self._apply_and_close)
    
    def _connect_slider_events(self):
        """
        连接滑块的按下事件以支持预览降采样
        """
        if self.processing_handler is not None and not self._slider_events_connected:
            # 连接亮度滑块事件
            self.brightness_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.brightness_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            
            # 连接对比度滑块事件
            self.contrast_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.contrast_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            
            self._slider_events_connected = True
    
    @pyqtSlot()
    def _update_brightness_label(self):
        """更新亮度值标签"""
        self.brightness_value_label.setText(str(self.brightness_slider.value()))
        
    @pyqtSlot()
    def _update_contrast_label(self):
        """更新对比度值标签"""
        self.contrast_value_label.setText(str(self.contrast_slider.value()))
        
    @pyqtSlot()
    def _emit_params_changed(self):
        """当参数变化时发出信号"""
        params = BrightnessContrastParams(
            brightness=self.brightness_slider.value(),
            contrast=self.contrast_slider.value()
        )
        self.params_changed.emit(params)
        
    @pyqtSlot()
    def _reset_values(self):
        """重置所有滑块到默认值"""
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        
    @pyqtSlot()
    def _apply_and_close(self):
        """应用参数并关闭对话框"""
        params = self.get_final_parameters()
        self.apply_operation.emit(params)
        self.accept()
        
    def get_final_parameters(self) -> BrightnessContrastParams:
        """
        获取最终的参数设置
        
        Returns:
            BrightnessContrastParams: 包含最终参数的数据类
        """
        return BrightnessContrastParams(
            brightness=self.brightness_slider.value(),
            contrast=self.contrast_slider.value()
        )
        
    def set_initial_parameters(self, params: Dict):
        """
        设置对话框的初始参数
        
        Args:
            params: 包含初始参数的字典
        """
        if params is None:
            return
            
        # 设置亮度值
        brightness = params.get('brightness', 0)
        self.brightness_slider.setValue(brightness)
        
        # 设置对比度值
        contrast = params.get('contrast', 0)
        self.contrast_slider.setValue(contrast)
