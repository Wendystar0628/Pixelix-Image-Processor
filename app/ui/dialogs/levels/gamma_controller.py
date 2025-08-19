"""
伽马控制器模块
处理伽马调整的UI界面和逻辑
"""

from typing import Callable, Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QLabel,
    QSlider,
    QDoubleSpinBox,
    QWidget,
)

from app.ui.dialogs.levels.models.levels_data_model import LevelsDataModel


class GammaController(QWidget):
    """
    伽马控制器
    管理伽马值的滑块和数值框
    """
    
    # 定义信号
    value_changed = pyqtSignal()  # 当伽马值发生变化时发出
    
    def __init__(self, levels_data: LevelsDataModel, parent: Optional[QWidget] = None):
        """
        初始化伽马控制器
        
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
        
        # 伽马值控件
        main_layout.addWidget(QLabel("伽马 (0.10 ~ 9.99):"), 0, 0)
        
        # 滑块使用0.01为单位的整数值（10-999）
        self.gamma_slider = QSlider(Qt.Orientation.Horizontal)
        self.gamma_slider.setRange(10, 999)  # 10 -> 0.10
        gamma_int = int(self._levels_data.gamma * 100)
        self.gamma_slider.setValue(gamma_int)
        main_layout.addWidget(self.gamma_slider, 0, 1)
        
        # 数值框显示实际伽马值（0.10-9.99）
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setRange(0.10, 9.99)
        self.gamma_spin.setSingleStep(0.01)
        self.gamma_spin.setDecimals(2)
        self.gamma_spin.setValue(self._levels_data.gamma)
        main_layout.addWidget(self.gamma_spin, 0, 2)
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 同步滑块和数值框的特殊映射关系
        self.gamma_slider.valueChanged.connect(
            lambda v: self.gamma_spin.setValue(v / 100.0)
        )
        self.gamma_spin.valueChanged.connect(
            lambda d: self.gamma_slider.setValue(int(d * 100))
        )
        
        # 更新数据模型并发出信号
        self.gamma_spin.valueChanged.connect(self._on_gamma_changed)
        
    def _on_gamma_changed(self, value: float):
        """
        当伽马值变化时
        
        Args:
            value: 新的伽马值
        """
        # 更新数据模型
        self._levels_data.gamma = value
        
        # 发出信号
        self.value_changed.emit()
        
    def update_from_model(self):
        """从数据模型更新UI控件"""
        # 阻止信号循环
        self.gamma_slider.blockSignals(True)
        self.gamma_spin.blockSignals(True)
        
        # 更新控件值
        gamma_int = int(self._levels_data.gamma * 100)
        self.gamma_slider.setValue(gamma_int)
        self.gamma_spin.setValue(self._levels_data.gamma)
        
        # 恢复信号
        self.gamma_slider.blockSignals(False)
        self.gamma_spin.blockSignals(False) 