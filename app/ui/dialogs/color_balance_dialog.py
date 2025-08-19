"""
色彩平衡对话框模块。
"""

from typing import Dict, Any, Optional, Tuple

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
    QCheckBox,
)

from .base_dialog import BaseOperationDialog
from ...handlers.processing_handler import ProcessingHandler
from ...core.models.operation_params import ColorBalanceParams


class ColorBalanceDialog(BaseOperationDialog[ColorBalanceParams]):
    """
    色彩平衡调整对话框。
    
    允许用户调整图像的色彩平衡。
    """
    
    # 定义参数变化的信号
    params_changed = pyqtSignal(ColorBalanceParams)
    # 定义应用操作的信号
    apply_operation = pyqtSignal(ColorBalanceParams)
    
    def __init__(self, parent=None, initial_params=None, processing_handler: Optional[ProcessingHandler] = None):
        """
        初始化色彩平衡对话框。
        
        Args:
            parent: 父窗口部件
            initial_params: 初始参数字典 (向后兼容的字典格式)
            processing_handler: 处理程序实例，用于连接滑块事件以支持预览降采样
        """
        super().__init__(parent, initial_params)
        
        # 保存对处理程序的引用
        self.processing_handler = processing_handler
        
        # 设置对话框属性
        self.setWindowTitle("色彩平衡")
        
        # 颜色范围定义
        self.color_ranges = {
            "cyan_red": ("青色", "红色"),
            "magenta_green": ("洋红", "绿色"),
            "yellow_blue": ("黄色", "蓝色"),
        }
        
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
        
        # 创建滑块组
        self.cyan_red_slider, self.cyan_red_spin = self._create_slider_group(
            "cyan_red", main_layout
        )
        
        self.magenta_green_slider, self.magenta_green_spin = self._create_slider_group(
            "magenta_green", main_layout
        )
        
        self.yellow_blue_slider, self.yellow_blue_spin = self._create_slider_group(
            "yellow_blue", main_layout
        )
        
        # 保留亮度复选框
        self.preserve_luminosity_checkbox = QCheckBox("保留亮度")
        self.preserve_luminosity_checkbox.setChecked(True)
        main_layout.addWidget(self.preserve_luminosity_checkbox)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        self.reset_button = QPushButton("重置")
        self.cancel_button = QPushButton("取消")
        self.ok_button = QPushButton("确定")
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        # 添加按钮布局到主布局
        main_layout.addLayout(button_layout)
        
    def _create_slider_group(
        self, key: str, layout: QVBoxLayout
    ) -> tuple[QSlider, QSpinBox]:
        """创建一个滑块组，包含滑块和数值框。"""
        group_box = QGroupBox(f"{self.color_ranges[key][0]} - {self.color_ranges[key][1]}")
        group_layout = QVBoxLayout(group_box)
        
        slider_layout = QHBoxLayout()
        
        # 创建左侧标签、滑块、右侧标签和数值框
        left_label = QLabel(self.color_ranges[key][0])
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(-100, 100)
        slider.setValue(0)
        slider.setTickInterval(20)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        right_label = QLabel(self.color_ranges[key][1])
        
        spin = QSpinBox()
        spin.setRange(-100, 100)
        spin.setValue(0)
        
        # 添加到滑块布局
        slider_layout.addWidget(left_label)
        slider_layout.addWidget(slider)
        slider_layout.addWidget(right_label)
        slider_layout.addWidget(spin)
        
        group_layout.addLayout(slider_layout)
        layout.addWidget(group_box)
        
        return slider, spin
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 连接滑块和数值框
        self.cyan_red_slider.valueChanged.connect(self.cyan_red_spin.setValue)
        self.cyan_red_spin.valueChanged.connect(self.cyan_red_slider.setValue)
        
        self.magenta_green_slider.valueChanged.connect(self.magenta_green_spin.setValue)
        self.magenta_green_spin.valueChanged.connect(self.magenta_green_slider.setValue)
        
        self.yellow_blue_slider.valueChanged.connect(self.yellow_blue_spin.setValue)
        self.yellow_blue_spin.valueChanged.connect(self.yellow_blue_slider.setValue)
        
        # 触发参数变化
        self.cyan_red_slider.valueChanged.connect(self._emit_params_changed)
        self.magenta_green_slider.valueChanged.connect(self._emit_params_changed)
        self.yellow_blue_slider.valueChanged.connect(self._emit_params_changed)
        self.preserve_luminosity_checkbox.stateChanged.connect(self._emit_params_changed)
        
        # 连接按钮
        self.reset_button.clicked.connect(self._reset_values)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self._apply_and_close)
    
    def _connect_slider_events(self):
        """
        连接滑块的按下事件以支持预览降采样
        """
        if self.processing_handler is not None and not self._slider_events_connected:
            # 连接滑块事件
            self.cyan_red_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.cyan_red_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            
            self.magenta_green_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.magenta_green_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            
            self.yellow_blue_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.yellow_blue_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
            
            self._slider_events_connected = True
    
    @pyqtSlot()
    def _emit_params_changed(self):
        """当参数变化时发出信号"""
        params = ColorBalanceParams(
            midtones_cyan_red=float(self.cyan_red_slider.value()),
            midtones_magenta_green=float(self.magenta_green_slider.value()),
            midtones_yellow_blue=float(self.yellow_blue_slider.value()),
            preserve_luminosity=self.preserve_luminosity_checkbox.isChecked()
        )
        self.params_changed.emit(params)
        
    @pyqtSlot()
    def _reset_values(self):
        """重置所有滑块到默认值"""
        self.cyan_red_slider.setValue(0)
        self.magenta_green_slider.setValue(0)
        self.yellow_blue_slider.setValue(0)
        self.preserve_luminosity_checkbox.setChecked(True)
        
    @pyqtSlot()
    def _apply_and_close(self):
        """应用参数并关闭对话框"""
        params = self.get_final_parameters()
        self.apply_operation.emit(params)
        self.accept()
        
    def get_final_parameters(self) -> ColorBalanceParams:
        """
        获取最终的参数设置
        
        Returns:
            ColorBalanceParams: 包含最终参数的数据类
        """
        return ColorBalanceParams(
            midtones_cyan_red=float(self.cyan_red_slider.value()),
            midtones_magenta_green=float(self.magenta_green_slider.value()),
            midtones_yellow_blue=float(self.yellow_blue_slider.value()),
            preserve_luminosity=self.preserve_luminosity_checkbox.isChecked()
        )
        
    def set_initial_parameters(self, params: Dict):
        """
        设置对话框的初始参数
        
        Args:
            params: 包含初始参数的字典
        """
        if params is None:
            return
            
        # 设置青/红值 (兼容旧版本参数命名)
        cyan_red = params.get("cyan_red", params.get("midtones_cyan_red", 0))
        self.cyan_red_slider.setValue(int(cyan_red))
        self.cyan_red_spin.setValue(int(cyan_red))
        
        # 设置洋红/绿值
        magenta_green = params.get("magenta_green", params.get("midtones_magenta_green", 0))
        self.magenta_green_slider.setValue(int(magenta_green))
        self.magenta_green_spin.setValue(int(magenta_green))
        
        # 设置黄/蓝值
        yellow_blue = params.get("yellow_blue", params.get("midtones_yellow_blue", 0))
        self.yellow_blue_slider.setValue(int(yellow_blue))
        self.yellow_blue_spin.setValue(int(yellow_blue))
        
        # 设置保留亮度
        preserve_luminosity = params.get("preserve_luminosity", True)
        self.preserve_luminosity_checkbox.setChecked(preserve_luminosity)
