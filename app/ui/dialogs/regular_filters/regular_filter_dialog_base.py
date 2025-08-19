"""
常规滤镜对话框基类模块
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QLabel,
    QPushButton,
    QGroupBox,
    QCheckBox,
    QComboBox
)

from ..base_dialog import BaseOperationDialog
from ....handlers.processing_handler import ProcessingHandler


class RegularFilterDialog(BaseOperationDialog):
    """
    常规滤镜对话框抽象基类
    
    提供常规滤镜参数调节界面的通用布局和功能
    """
    
    # 参数变化信号
    params_changed = pyqtSignal(object)
    # 应用操作信号
    apply_operation = pyqtSignal(object)
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        """
        初始化常规滤镜对话框
        
        Args:
            parent: 父窗口部件
            initial_params: 初始参数字典
            processing_handler: 处理程序实例
        """
        super().__init__(parent, initial_params)
        
        self.processing_handler = processing_handler
        self._slider_events_connected = False
        
        # 设置对话框基本属性
        self.setMinimumWidth(350)
        
        # 创建UI和连接信号
        self._setup_ui()
        self._connect_signals()
        self.set_initial_parameters(self.initial_params)
        self._connect_slider_events()
    
    def _setup_ui(self):
        """创建UI布局"""
        main_layout = QVBoxLayout()
        
        # 创建参数控制组
        self._create_parameter_groups(main_layout)
        
        # 创建按钮布局
        button_layout = self._create_button_layout()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    @abstractmethod
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        """创建参数控制组 - 子类实现"""
        pass
    
    def _create_button_layout(self) -> QHBoxLayout:
        """创建按钮布局"""
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("重置")
        self.cancel_button = QPushButton("取消")
        self.ok_button = QPushButton("确定")
        self.ok_button.setDefault(True)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        return button_layout
    
    def _create_slider_group(self, title: str, min_val: int, max_val: int, 
                           default_val: int) -> tuple:
        """
        创建滑块控制组
        
        Returns:
            tuple: (group_widget, slider, label)
        """
        group = QGroupBox(title)
        layout = QVBoxLayout()
        
        slider_layout = QHBoxLayout()
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setTracking(True)
        
        label = QLabel(str(default_val))
        label.setMinimumWidth(30)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        slider_layout.addWidget(slider)
        slider_layout.addWidget(label)
        
        layout.addLayout(slider_layout)
        group.setLayout(layout)
        
        return group, slider, label
    
    def _create_checkbox_group(self, title: str, checked: bool = False) -> tuple:
        """
        创建复选框控制组
        
        Returns:
            tuple: (group_widget, checkbox)
        """
        group = QGroupBox(title)
        layout = QVBoxLayout()
        
        checkbox = QCheckBox("启用")
        checkbox.setChecked(checked)
        
        layout.addWidget(checkbox)
        group.setLayout(layout)
        
        return group, checkbox
    
    def _create_combo_group(self, title: str, items: list, default_index: int = 0) -> tuple:
        """
        创建下拉框控制组
        
        Returns:
            tuple: (group_widget, combobox)
        """
        group = QGroupBox(title)
        layout = QVBoxLayout()
        
        combo = QComboBox()
        combo.addItems(items)
        combo.setCurrentIndex(default_index)
        
        layout.addWidget(combo)
        group.setLayout(layout)
        
        return group, combo
    
    def _connect_signals(self):
        """连接信号和槽"""
        self.reset_button.clicked.connect(self._reset_values)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self._apply_and_close)
    
    def _connect_slider_events(self):
        """连接滑块事件以支持预览降采样"""
        if self.processing_handler is not None and not self._slider_events_connected:
            self._connect_slider_preview_events()
            self._slider_events_connected = True
    
    @abstractmethod
    def _connect_slider_preview_events(self):
        """连接滑块预览事件 - 子类实现"""
        pass
    
    @pyqtSlot()
    def _apply_and_close(self):
        """应用参数并关闭对话框"""
        params = self.get_final_parameters()
        self.apply_operation.emit(params)
        self.accept()
    
    @abstractmethod
    def _reset_values(self):
        """重置所有参数到默认值 - 子类实现"""
        pass
    
    @abstractmethod
    def get_final_parameters(self):
        """获取最终参数设置 - 子类实现"""
        pass
    
    @abstractmethod
    def set_initial_parameters(self, params: Dict):
        """设置初始参数 - 子类实现"""
        pass