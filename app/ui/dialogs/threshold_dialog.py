"""
阈值对话框模块。
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
from ...core.models.operation_params import ThresholdParams


class ThresholdDialog(BaseOperationDialog[ThresholdParams]):
    """
    手动阈值调整对话框。
    
    允许用户调整图像的阈值。
    """
    
    # 定义参数变化的信号
    params_changed = pyqtSignal(ThresholdParams)
    # 定义应用操作的信号
    apply_operation = pyqtSignal(ThresholdParams)
    
    def __init__(self, parent=None, initial_params=None, processing_handler: Optional[ProcessingHandler] = None):
        """
        初始化手动阈值对话框。
        
        Args:
            parent: 父窗口部件
            initial_params: 初始参数字典 (向后兼容的字典格式)
            processing_handler: 处理程序实例，用于连接滑块事件以支持预览降采样
        """
        super().__init__(parent, initial_params)
        
        # 保存对处理程序的引用
        self.processing_handler = processing_handler
        
        # 设置对话框属性
        self.setWindowTitle("手动阈值")
        self.threshold_value = 127
        
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
        
        # 阈值组
        threshold_group = QGroupBox("阈值")
        threshold_layout = QVBoxLayout(threshold_group)
        
        # 阈值滑块和标签水平布局
        threshold_slider_layout = QHBoxLayout()
        self.threshold_value_label = QLabel(str(self.threshold_value))
        self.threshold_value_label.setMinimumWidth(40)
        self.threshold_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(0, 255)
        self.threshold_slider.setValue(self.threshold_value)
        self.threshold_slider.setTickInterval(25)
        self.threshold_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(0, 255)
        self.threshold_spin.setValue(self.threshold_value)
        
        threshold_slider_layout.addWidget(QLabel("0"))
        threshold_slider_layout.addWidget(self.threshold_slider)
        threshold_slider_layout.addWidget(QLabel("255"))
        threshold_slider_layout.addWidget(self.threshold_spin)
        
        threshold_layout.addLayout(threshold_slider_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        self.reset_button = QPushButton("重置")
        self.cancel_button = QPushButton("取消")
        self.ok_button = QPushButton("确定")
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        # 添加组件到主布局
        main_layout.addWidget(threshold_group)
        main_layout.addLayout(button_layout)
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 连接滑块和数值框
        self.threshold_slider.valueChanged.connect(self.threshold_spin.setValue)
        self.threshold_spin.valueChanged.connect(self.threshold_slider.setValue)
        
        # 更新标签并发送预览信号
        self.threshold_slider.valueChanged.connect(self._update_threshold_label)
        self.threshold_slider.valueChanged.connect(self._emit_params_changed)
        
        # 连接按钮
        self.reset_button.clicked.connect(self._reset_values)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self._apply_and_close)
    
    def _connect_slider_events(self):
        """
        连接滑块的按下事件以支持预览降采样
        """
        if self.processing_handler is not None and not self._slider_events_connected:
            # 连接阈值滑块事件
            self.threshold_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.threshold_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            
            self._slider_events_connected = True
    
    @pyqtSlot()
    def _update_threshold_label(self):
        """更新阈值标签"""
        self.threshold_value = self.threshold_slider.value()
        self.threshold_value_label.setText(str(self.threshold_value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        """当参数变化时发出信号"""
        params = ThresholdParams(
            threshold=self.threshold_value
        )
        self.params_changed.emit(params)
        
    @pyqtSlot()
    def _reset_values(self):
        """重置阈值到默认值"""
        self.threshold_slider.setValue(127)
        
    @pyqtSlot()
    def _apply_and_close(self):
        """应用参数并关闭对话框"""
        params = self.get_final_parameters()
        self.apply_operation.emit(params)
        self.accept()
        
    def get_final_parameters(self) -> ThresholdParams:
        """
        获取最终的参数设置
        
        Returns:
            ThresholdParams: 包含最终参数的数据类
        """
        return ThresholdParams(
            threshold=self.threshold_value
        )
        
    def set_initial_parameters(self, params: Dict):
        """
        设置对话框的初始参数
        
        Args:
            params: 包含初始参数的字典
        """
        if params is None:
            return
            
        threshold = params.get("threshold", 127)
        self.threshold_slider.setValue(threshold)
        self.threshold_spin.setValue(threshold)
