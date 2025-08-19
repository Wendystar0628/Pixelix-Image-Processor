"""
色阶对话框模块
使用模块化组件实现色阶调整对话框
"""

from typing import Dict, Any, Optional

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.dialogs.base_dialog import BaseOperationDialog
from app.ui.widgets.histogram_widget import HistogramWidget
from app.ui.dialogs.levels.models.levels_data_model import LevelsDataModel
from app.ui.dialogs.levels.input_levels_widget import InputLevelsWidget
from app.ui.dialogs.levels.output_levels_widget import OutputLevelsWidget
from app.ui.dialogs.levels.gamma_controller import GammaController
from app.core.models.operation_params import LevelsParams


class LevelsDialog(BaseOperationDialog[LevelsParams]):
    """
    色阶调整对话框
    允许用户调整图像的输入/输出色阶和伽马值
    使用模块化组件重构后的版本
    """

    def __init__(self, parent=None, initial_params: Optional[Dict[str, Any]] = None):
        """
        初始化色阶对话框
        
        Args:
            parent: 父窗口
            initial_params: 初始参数字典 (向后兼容的字典格式)
        """
        super().__init__(parent, initial_params)
        self.setWindowTitle("色阶")
        self.setMinimumWidth(450)
        
        # 初始化数据模型
        self._levels_data = LevelsDataModel()
        
        # 获取处理处理器引用以支持代理模式
        # 注意：已重构为不依赖全局上下文，使用备用方案
        try:
            # 使用默认处理方式
            self._processing_handler = None
        except ImportError:
            self._processing_handler = None
        
        # 是否正在交互标志，用于管理代理状态
        self._is_interacting = False
        
        # 初始化UI
        self._init_ui()
        
        # 如果有初始参数，应用它们
        if initial_params:
            self.set_initial_parameters(initial_params)
            
        # 初始预览
        self._emit_params_changed()

    def _init_ui(self):
        """初始化UI布局"""
        main_layout = QVBoxLayout(self)
        
        # 隐藏的直方图控件（保留以避免后续代码引用错误）
        self.histogram_widget = HistogramWidget()
        self.histogram_widget.setVisible(False)

        # 色阶控件组
        controls_group = QGroupBox("色阶调整")
        controls_layout = QVBoxLayout(controls_group)
        
        # 创建子组件
        self._input_levels = InputLevelsWidget(self._levels_data)
        self._gamma_controller = GammaController(self._levels_data)
        self._output_levels = OutputLevelsWidget(self._levels_data)
        
        # 添加到布局
        controls_layout.addWidget(self._input_levels)
        controls_layout.addWidget(self._gamma_controller)
        controls_layout.addWidget(self._output_levels)
        
        main_layout.addWidget(controls_group)
        
        # 预览复选框
        self._preview_checkbox = QCheckBox("实时预览")
        self._preview_checkbox.setChecked(True)
        main_layout.addWidget(self._preview_checkbox)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        # 添加重置按钮
        reset_button = QPushButton("重置")
        button_box.addButton(reset_button, QDialogButtonBox.ButtonRole.ResetRole)
        
        main_layout.addWidget(button_box)
        
        # 连接信号
        self._connect_signals(button_box, reset_button)

    def _connect_signals(self, button_box, reset_button):
        """连接所有信号和槽"""
        # 子组件的值变化信号
        self._input_levels.values_changed.connect(self._emit_params_changed)
        self._gamma_controller.value_changed.connect(self._emit_params_changed)
        self._output_levels.values_changed.connect(self._emit_params_changed)
        
        # 连接交互事件，用于触发代理模式
        self._connect_slider_events(self._input_levels.input_black_slider)
        self._connect_slider_events(self._input_levels.input_white_slider)
        self._connect_slider_events(self._gamma_controller.gamma_slider)
        self._connect_slider_events(self._output_levels.output_black_slider)
        self._connect_slider_events(self._output_levels.output_white_slider)
        
        # 预览复选框
        self._preview_checkbox.toggled.connect(self._emit_params_changed)
        
        # 按钮
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        reset_button.clicked.connect(self._reset_levels)
        
    def _connect_slider_events(self, slider):
        """
        连接滑块的按下和释放事件
        
        Args:
            slider: 要连接事件的滑块控件
        """
        slider.sliderPressed.connect(self._on_slider_pressed)
        slider.sliderReleased.connect(self._on_slider_released)
        
    def _on_slider_pressed(self):
        """
        处理滑块按下事件
        
        触发代理模式启动，创建低分辨率预览
        """
        # 防止重复进入交互模式
        if not self._is_interacting and self._processing_handler:
            self._is_interacting = True
            # 调用处理处理器的方法启动代理模式
            self._processing_handler.on_slider_pressed()
            
    def _on_slider_released(self):
        """
        处理滑块释放事件
        
        结束交互模式，切换到全分辨率渲染（保留预览效果）
        """
        # 只在正在交互时处理
        if self._is_interacting and self._processing_handler:
            self._is_interacting = False
            # 结束交互模式，StateManager会自动切换到全分辨率渲染并保留预览效果
            self._processing_handler.on_slider_released()

    def _reset_levels(self):
        """重置所有色阶参数为默认值"""
        # 创建一个新的数据模型（使用默认值）
        self._levels_data = LevelsDataModel()
        
        # 更新所有控件
        self._input_levels._levels_data = self._levels_data
        self._gamma_controller._levels_data = self._levels_data
        self._output_levels._levels_data = self._levels_data
        
        self._input_levels.update_from_model()
        self._gamma_controller.update_from_model()
        self._output_levels.update_from_model()
        
        # 触发更新
        self._emit_params_changed()
        
    def _emit_params_changed(self):
        """
        发送参数变化信号，触发实时预览
        """
        # 只有在勾选了实时预览时才发送信号
        if self._preview_checkbox.isChecked():
            params = self.get_final_parameters()
            self.params_changed.emit(params)

    def get_final_parameters(self) -> LevelsParams:
        """
        获取对话框的最终参数
        
        Returns:
            LevelsParams: 包含色阶调整参数的数据类
        """
        data = self._levels_data.get_serializable_data()
        return LevelsParams(
            channel=0,  # 当前默认为0 (RGB通道)
            input_black=data["input_black"],
            input_gamma=data["input_gamma"],
            input_white=data["input_white"],
            output_black=data["output_black"],
            output_white=data["output_white"]
        )

    def set_initial_parameters(self, params: Dict[str, Any]):
        """
        设置对话框的初始参数
        
        Args:
            params: 参数字典 (向后兼容的字典格式)
        """
        if params is None:
            return
            
        # 加载参数到数据模型
        self._levels_data.load_from_params(params)
        
        # 更新UI控件
        self._input_levels.update_from_model()
        self._gamma_controller.update_from_model()
        self._output_levels.update_from_model() 