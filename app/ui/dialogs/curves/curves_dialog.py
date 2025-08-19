"""
曲线对话框模块
使用模块化组件实现曲线调整对话框
"""

from typing import Dict, Any, Optional, List, Tuple

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.ui.dialogs.base_dialog import BaseOperationDialog
from app.ui.dialogs.curves.curve_edit_widget import CurveEditWidget
from app.ui.dialogs.curves.models.curve_data_model import CurveDataModel
from app.ui.dialogs.curves.models.curve_preset_model import CurvePresetModel
from app.ui.dialogs.curves.curve_channel_manager import CurveChannelManager
from app.ui.dialogs.curves.curve_preset_manager import CurvePresetManager
from app.ui.widgets.histogram_widget import HistogramWidget
from app.core.models.operation_params import CurvesParams


class CurvesDialog(BaseOperationDialog[CurvesParams]):
    """
    曲线调整对话框
    允许用户通过控制点精确调整图像的色调曲线
    使用模块化组件和MVC架构重构后的版本
    """

    def __init__(self, parent=None, initial_params: Optional[Dict[str, Any]] = None):
        """
        初始化曲线对话框
        
        Args:
            parent: 父窗口
            initial_params: 初始参数字典 (向后兼容的字典格式)
        """
        super().__init__(parent, initial_params)
        self.setWindowTitle("曲线")
        self.setMinimumSize(800, 600)
        
        # 初始化数据模型和管理器
        self._curve_data = CurveDataModel()
        self._preset_model = CurvePresetModel()
        self._channel_manager = CurveChannelManager(self._curve_data)
        self._preset_manager = CurvePresetManager(self._preset_model, self._curve_data)
        
        # 获取处理处理器引用以支持代理模式
        # 注意：已重构为不依赖全局上下文，使用备用方案
        try:
            # 使用默认处理方式
            self._processing_handler = None
        except ImportError:
            self._processing_handler = None
        
        # 用于直方图的图像引用
        self._image = None
        
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
        
        # 创建水平分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # --- 左侧：曲线编辑器 ---
        self._curve_widget = CurveEditWidget()
        splitter.addWidget(self._curve_widget)
        
        # --- 右侧：控制面板 ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        splitter.addWidget(right_panel)
        
        # 隐藏的直方图组件（保留以避免后续代码引用错误）
        self._histogram_widget = HistogramWidget()
        self._histogram_widget.setVisible(False)
        
        # 通道选择
        channel_layout = QHBoxLayout()
        self._channel_combo = self._channel_manager.setup_channel_selector(channel_layout)
        right_layout.addLayout(channel_layout)
        
        # 预设
        preset_group = self._preset_manager.setup_preset_ui(right_panel)
        right_layout.addLayout(channel_layout)
        right_layout.addWidget(preset_group)
        right_layout.addStretch()
        
        # --- 底部按钮 ---
        self._preview_checkbox = QCheckBox("实时预览")
        self._preview_checkbox.setChecked(True)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        # 添加重置按钮
        reset_button = QPushButton("重置")
        button_box.addButton(reset_button, QDialogButtonBox.ButtonRole.ResetRole)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self._preview_checkbox)
        bottom_layout.addStretch()
        bottom_layout.addWidget(button_box)
        main_layout.addLayout(bottom_layout)
        
        # --- 连接信号 ---
        self._connect_signals(button_box, reset_button)
        
        # 设置分割器比例
        splitter.setSizes([500, 300])

    def _connect_signals(self, button_box, reset_button):
        """连接所有信号和槽"""
        # 曲线编辑控件
        self._curve_widget.curve_changed.connect(self._on_curve_changed)
        
        # 添加交互开始和结束的事件处理
        # 这些事件用于触发代理工作流
        self._curve_widget.drag_started.connect(self._on_drag_started)
        self._curve_widget.drag_finished.connect(self._on_drag_finished)
        
        # 通道管理器
        self._channel_manager.connect_channel_changed(
            self._channel_combo, 
            self._on_channel_changed
        )
        
        # 预设管理器
        self._preset_manager.connect_preset_changed(self._on_preset_changed)
        
        # 预览复选框
        self._preview_checkbox.toggled.connect(self._on_preview_toggled)
        
        # 按钮
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        reset_button.clicked.connect(self._reset_curve)
    
    def _on_drag_started(self):
        """
        处理曲线拖拽开始事件
        
        触发代理模式启动，创建低分辨率预览
        """
        # 防止重复进入交互模式
        if not self._is_interacting and self._processing_handler:
            self._is_interacting = True
            # 调用处理处理器的方法启动代理模式
            self._processing_handler.on_slider_pressed()
    
    def _on_drag_finished(self):
        """
        处理曲线拖拽结束事件
        
        结束交互模式，切换到全分辨率渲染（保留预览效果）
        """
        # 只在正在交互时处理
        if self._is_interacting and self._processing_handler:
            self._is_interacting = False
            # 结束交互模式，ProxyWorkflowManager会自动切换到全分辨率渲染并保留预览效果
            self._processing_handler.on_slider_released()

    def _on_curve_changed(self, points: List[Tuple[int, int]]):
        """
        曲线控制点变化回调
        
        Args:
            points: 新的控制点列表
        """
        # 更新数据模型
        self._curve_data.set_current_points(points)
        
        # 如果当前是RGB通道，同步到所有通道
        if self._curve_data.current_channel == "RGB":
            self._curve_data.sync_all_channels_from_rgb()
        
        # 检查是否需要切换到自定义预设
        self._preset_manager.check_and_update_preset_status(points)
        
        # 触发参数变化
        self._emit_params_changed()

    def _on_channel_changed(self, channel_code: str):
        """
        通道变更回调
        
        Args:
            channel_code: 新的通道代码
        """
        # 更新曲线编辑控件
        self._curve_widget.set_curve_points(self._curve_data.get_current_points())
        
        # 更新直方图（如果有图像）
        self._update_histogram()
        
        # 触发参数变化
        self._emit_params_changed()

    def _on_preset_changed(self, preset_name: str):
        """
        预设变更回调
        
        Args:
            preset_name: 预设名称
        """
        # 更新曲线编辑控件
        self._curve_widget.set_curve_points(self._curve_data.get_current_points())
        
        # 触发参数变化
        self._emit_params_changed()

    def _on_preview_toggled(self, checked: bool):
        """
        预览切换回调
        
        Args:
            checked: 是否选中
        """
        self._emit_params_changed()

    def _reset_curve(self):
        """重置曲线为线性"""
        self._preset_manager.reset_to_linear()
        
    def _emit_params_changed(self):
        """
        发送参数变化信号，触发实时预览
        """
        # 只有在勾选了实时预览时才发送信号
        if self._preview_checkbox.isChecked():
            params = self.get_final_parameters()
            self.params_changed.emit(params)

    def set_image(self, image: np.ndarray):
        """
        设置要处理的图像，用于直方图显示
        
        Args:
            image: 图像数据
        """
        self._image = image
        self._update_histogram()

    def _update_histogram(self):
        """更新直方图数据"""
        if self._image is None:
            return
            
        # 从当前通道提取数据
        channel_data = self._channel_manager.extract_channel_data(self._image)
        
        # 更新直方图控件
        self._histogram_widget.update_histogram(channel_data)

    def get_final_parameters(self) -> CurvesParams:
        """
        获取对话框的最终参数
        
        Returns:
            CurvesParams: 包含曲线调整参数的数据类
        """
        data = self._curve_data.get_serializable_data()
        return CurvesParams(
            points_rgb=data["points_rgb"],
            points_r=data["points_r"],
            points_g=data["points_g"],
            points_b=data["points_b"]
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
        self._curve_data.load_from_params(params)
        
        # 更新UI
        self._curve_widget.set_curve_points(self._curve_data.get_current_points())
        
        # 预设将根据当前点自动更新
        # 通过_on_curve_changed的调用来处理 