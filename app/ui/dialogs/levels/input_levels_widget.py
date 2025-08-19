"""
输入色阶控件模块
处理输入黑场和输入白场的UI界面和逻辑
"""

from typing import Callable, Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QSlider,
    QSpinBox,
    QWidget,
)

from app.ui.dialogs.levels.models.levels_data_model import LevelsDataModel


class InputLevelsWidget(QWidget):
    """
    输入色阶控件
    管理输入黑场和白场滑块/数值框
    """
    
    # 定义信号
    values_changed = pyqtSignal()  # 当任何值发生变化时发出
    
    def __init__(self, levels_data: LevelsDataModel, parent: Optional[QWidget] = None):
        """
        初始化输入色阶控件
        
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
        
        # 输入黑场
        main_layout.addWidget(QLabel("输入黑场 (0 ~ 254):"), 0, 0)
        
        self.input_black_slider = self._create_slider(0, 254)
        self.input_black_slider.setValue(self._levels_data.input_black)
        main_layout.addWidget(self.input_black_slider, 0, 1)
        
        self.input_black_spin = QSpinBox()
        self.input_black_spin.setRange(0, 254)
        self.input_black_spin.setValue(self._levels_data.input_black)
        main_layout.addWidget(self.input_black_spin, 0, 2)
        
        # 输入白场
        main_layout.addWidget(QLabel("输入白场 (1 ~ 255):"), 1, 0)
        
        self.input_white_slider = self._create_slider(1, 255)
        self.input_white_slider.setValue(self._levels_data.input_white)
        main_layout.addWidget(self.input_white_slider, 1, 1)
        
        self.input_white_spin = QSpinBox()
        self.input_white_spin.setRange(1, 255)
        self.input_white_spin.setValue(self._levels_data.input_white)
        main_layout.addWidget(self.input_white_spin, 1, 2)
        
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
        self.input_black_slider.valueChanged.connect(self.input_black_spin.setValue)
        self.input_black_spin.valueChanged.connect(self.input_black_slider.setValue)
        
        self.input_white_slider.valueChanged.connect(self.input_white_spin.setValue)
        self.input_white_spin.valueChanged.connect(self.input_white_slider.setValue)
        
        # 更新数据模型并发出信号
        self.input_black_spin.valueChanged.connect(self._on_black_changed)
        self.input_white_spin.valueChanged.connect(self._on_white_changed)
        
    def _on_black_changed(self, value: int):
        """
        当输入黑场值变化时
        
        Args:
            value: 新的黑场值
        """
        # 更新数据模型
        self._levels_data.input_black = value
        
        # 强制更新白场控件的最小值
        min_white = value + 1
        if self.input_white_slider.value() < min_white:
            self.input_white_slider.setValue(min_white)
            self.input_white_spin.setValue(min_white)
        
        # 发出信号
        self.values_changed.emit()
        
    def _on_white_changed(self, value: int):
        """
        当输入白场值变化时
        
        Args:
            value: 新的白场值
        """
        # 更新数据模型
        self._levels_data.input_white = value
        
        # 强制更新黑场控件的最大值
        max_black = value - 1
        if self.input_black_slider.value() > max_black:
            self.input_black_slider.setValue(max_black)
            self.input_black_spin.setValue(max_black)
            
        # 发出信号
        self.values_changed.emit()
        
    def update_from_model(self):
        """从数据模型更新UI控件"""
        # 阻止信号循环
        self.input_black_slider.blockSignals(True)
        self.input_black_spin.blockSignals(True)
        self.input_white_slider.blockSignals(True)
        self.input_white_spin.blockSignals(True)
        
        # 更新控件值
        self.input_black_slider.setValue(self._levels_data.input_black)
        self.input_black_spin.setValue(self._levels_data.input_black)
        self.input_white_slider.setValue(self._levels_data.input_white)
        self.input_white_spin.setValue(self._levels_data.input_white)
        
        # 恢复信号
        self.input_black_slider.blockSignals(False)
        self.input_black_spin.blockSignals(False)
        self.input_white_slider.blockSignals(False)
        self.input_white_spin.blockSignals(False) 