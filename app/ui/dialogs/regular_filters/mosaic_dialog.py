"""
马赛克滤镜对话框模块
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout

from .regular_filter_dialog_base import RegularFilterDialog
from ....handlers.processing_handler import ProcessingHandler
from ....core.models.regular_filter_params import MosaicParams


class MosaicDialog(RegularFilterDialog):
    """
    马赛克滤镜参数调整对话框
    
    允许用户调整马赛克块大小和边缘保持选项
    """
    
    def __init__(self, parent=None, initial_params: Optional[Dict] = None, 
                 processing_handler: Optional[ProcessingHandler] = None):
        """初始化马赛克滤镜对话框"""
        super().__init__(parent, initial_params, processing_handler)
        self.setWindowTitle("马赛克滤镜")
    
    def _create_parameter_groups(self, main_layout: QVBoxLayout):
        """创建参数控制组"""
        # 块大小控制组
        block_size_group, self.block_size_slider, self.block_size_label = self._create_slider_group(
            "块大小", 2, 50, 10
        )
        main_layout.addWidget(block_size_group)
        
        # 边缘保持选项
        preserve_edges_group, self.preserve_edges_checkbox = self._create_checkbox_group(
            "边缘保持", False
        )
        main_layout.addWidget(preserve_edges_group)
        
        # 连接信号
        self.block_size_slider.valueChanged.connect(self._update_block_size_label)
        self.block_size_slider.valueChanged.connect(self._emit_params_changed)
        self.preserve_edges_checkbox.toggled.connect(self._emit_params_changed)
    
    def _connect_slider_preview_events(self):
        """连接滑块预览事件"""
        if self.processing_handler is not None:
            self.block_size_slider.sliderPressed.connect(self.processing_handler.on_slider_pressed)
            self.block_size_slider.sliderReleased.connect(self.processing_handler.on_slider_released)
    
    @pyqtSlot()
    def _update_block_size_label(self):
        """更新块大小标签"""
        value = self.block_size_slider.value()
        self.block_size_label.setText(str(value))
    
    @pyqtSlot()
    def _emit_params_changed(self):
        """发出参数变化信号"""
        params = MosaicParams(
            block_size=self.block_size_slider.value(),
            preserve_edges=self.preserve_edges_checkbox.isChecked()
        )
        self.params_changed.emit(params)
    
    @pyqtSlot()
    def _reset_values(self):
        """重置所有参数到默认值"""
        self.block_size_slider.setValue(10)
        self.preserve_edges_checkbox.setChecked(False)
    
    def get_final_parameters(self) -> MosaicParams:
        """获取最终参数设置"""
        return MosaicParams(
            block_size=self.block_size_slider.value(),
            preserve_edges=self.preserve_edges_checkbox.isChecked()
        )
    
    def set_initial_parameters(self, params: Dict):
        """设置初始参数"""
        if params is None:
            return
        
        # 设置块大小
        block_size = params.get('block_size', 10)
        self.block_size_slider.setValue(block_size)
        
        # 设置边缘保持选项
        preserve_edges = params.get('preserve_edges', False)
        self.preserve_edges_checkbox.setChecked(preserve_edges)