"""
输出色阶控件模块
处理输出黑场和输出白场的UI界面和逻辑
"""

from typing import Callable, Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QLabel,
    QSlider,
    QSpinBox,
    QWidget,
)

from app.ui.dialogs.levels.models.levels_data_model import LevelsDataModel


class OutputLevelsWidget(QWidget):
    """
    输出色阶控件
    管理输出黑场和白场滑块/数值框
    """
    
    # 定义信号
    values_changed = pyqtSignal()  # 当任何值发生变化时发出
    
    def __init__(self, levels_data: LevelsDataModel, parent: Optional[QWidget] = None):
        """
        初始化输出色阶控件
        
        Args:
            levels_data: 色阶数据模型
            parent: 父窗口部件
        """
        super().__init__(parent)
        self._levels_data = levels_data
        
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """初始化UI布局"""
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 输出黑场
        main_layout.addWidget(QLabel("输出黑场 (0 ~ 255):"), 0, 0)
        
        self.output_black_slider = self._create_slider(0, 255)
        self.output_black_slider.setValue(self._levels_data.output_black)
        main_layout.addWidget(self.output_black_slider, 0, 1)
        
        self.output_black_spin = QSpinBox()
        self.output_black_spin.setRange(0, 255)
        self.output_black_spin.setValue(self._levels_data.output_black)
        main_layout.addWidget(self.output_black_spin, 0, 2)
        
        # 输出白场
        main_layout.addWidget(QLabel("输出白场 (0 ~ 255):"), 1, 0)
        
        self.output_white_slider = self._create_slider(0, 255)
        self.output_white_slider.setValue(self._levels_data.output_white)
        main_layout.addWidget(self.output_white_slider, 1, 1)
        
        self.output_white_spin = QSpinBox()
        self.output_white_spin.setRange(0, 255)
        self.output_white_spin.setValue(self._levels_data.output_white)
        main_layout.addWidget(self.output_white_spin, 1, 2)
        
    def _create_slider(self, min_val: int, max_val: int) -> QSlider:
        """
        创建水平滑块
        
        Args:
            min_val: 最小值
            max_val: 最大值
            
        Returns:
            创建的滑块
        """
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        return slider
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 同步滑块和数值框
        self.output_black_slider.valueChanged.connect(self.output_black_spin.setValue)
        self.output_black_spin.valueChanged.connect(self.output_black_slider.setValue)
        
        self.output_white_slider.valueChanged.connect(self.output_white_spin.setValue)
        self.output_white_spin.valueChanged.connect(self.output_white_slider.setValue)
        
        # 更新数据模型并发出信号
        self.output_black_spin.valueChanged.connect(self._on_black_changed)
        self.output_white_spin.valueChanged.connect(self._on_white_changed)
        
    def _on_black_changed(self, value: int):
        """
        当输出黑场值变化时
        
        Args:
            value: 新的黑场值
        """
        # 更新数据模型
        self._levels_data.output_black = value
        
        # 如果黑场大于白场，将白场设置为黑场
        if value > self.output_white_slider.value():
            self.output_white_slider.setValue(value)
            self.output_white_spin.setValue(value)
            
        # 发出信号
        self.values_changed.emit()
        
    def _on_white_changed(self, value: int):
        """
        当输出白场值变化时
        
        Args:
            value: 新的白场值
        """
        # 更新数据模型
        self._levels_data.output_white = value
        
        # 如果白场小于黑场，将黑场设置为白场
        if value < self.output_black_slider.value():
            self.output_black_slider.setValue(value)
            self.output_black_spin.setValue(value)
            
        # 发出信号
        self.values_changed.emit()
        
    def update_from_model(self):
        """从数据模型更新UI控件"""
        # 阻止信号循环
        self.output_black_slider.blockSignals(True)
        self.output_black_spin.blockSignals(True)
        self.output_white_slider.blockSignals(True)
        self.output_white_spin.blockSignals(True)
        
        # 更新控件值
        self.output_black_slider.setValue(self._levels_data.output_black)
        self.output_black_spin.setValue(self._levels_data.output_black)
        self.output_white_slider.setValue(self._levels_data.output_white)
        self.output_white_spin.setValue(self._levels_data.output_white)
        
        # 恢复信号
        self.output_black_slider.blockSignals(False)
        self.output_black_spin.blockSignals(False)
        self.output_white_slider.blockSignals(False)
        self.output_white_spin.blockSignals(False) 