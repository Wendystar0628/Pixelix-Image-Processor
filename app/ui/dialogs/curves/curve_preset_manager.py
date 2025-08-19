"""
曲线预设管理器模块
管理曲线预设的UI交互和应用
"""

from typing import Callable, Optional, List, Tuple
from PyQt6.QtWidgets import QComboBox, QLabel, QGridLayout, QGroupBox

from app.ui.dialogs.curves.models.curve_preset_model import CurvePresetModel
from app.ui.dialogs.curves.models.curve_data_model import CurveDataModel


class CurvePresetManager:
    """
    曲线预设管理器
    处理预设的UI交互和应用逻辑
    """
    
    def __init__(self, preset_model: CurvePresetModel, curve_data_model: CurveDataModel):
        """
        初始化预设管理器
        
        Args:
            preset_model: 预设数据模型
            curve_data_model: 曲线数据模型
        """
        self._preset_model = preset_model
        self._curve_data = curve_data_model
        self._preset_combo = None
        self._preset_description = None
        
    def setup_preset_ui(self, parent) -> QGroupBox:
        """
        设置预设UI组件
        
        Args:
            parent: 父窗口
            
        Returns:
            创建的预设组框
        """
        # 创建组框
        preset_group = QGroupBox("预设")
        preset_layout = QGridLayout(preset_group)
        
        # 添加预设标签和下拉框
        preset_layout.addWidget(QLabel("预设:"), 0, 0)
        self._preset_combo = QComboBox()
        self._preset_combo.addItems(self._preset_model.preset_names)
        self._preset_combo.setCurrentText(self._preset_model.current_preset_name)
        preset_layout.addWidget(self._preset_combo, 0, 1)
        
        # 添加预设描述标签
        self._preset_description = QLabel(self._get_current_description())
        self._preset_description.setWordWrap(True)
        preset_layout.addWidget(self._preset_description, 1, 0, 1, 2)
        
        return preset_group
    
    def connect_preset_changed(self, on_preset_changed: Optional[Callable] = None):
        """
        连接预设变更事件
        
        Args:
            on_preset_changed: 当预设改变时调用的回调
        """
        if not self._preset_combo:
            return
            
        def _on_preset_changed(index: int):
            preset_name = self._preset_combo.itemText(index)
            
            # 如果是"自定义"，不执行任何操作
            if preset_name == "自定义":
                return
                
            # 更新预设模型
            self._preset_model.current_preset_name = preset_name
            
            # 更新描述
            self._update_description(preset_name)
            
            # 获取并应用预设点
            points = self._preset_model.get_preset_points(preset_name)
            if points:
                self._curve_data.apply_preset(points)
                
            # 调用外部回调
            if on_preset_changed:
                on_preset_changed(preset_name)
        
        self._preset_combo.currentIndexChanged.connect(_on_preset_changed)
    
    def _update_description(self, preset_name: str):
        """
        更新预设描述
        
        Args:
            preset_name: 预设名称
        """
        if self._preset_description:
            desc = self._preset_model.get_preset_description(preset_name)
            self._preset_description.setText(desc)
    
    def _get_current_description(self) -> str:
        """
        获取当前预设的描述
        
        Returns:
            预设描述
        """
        name = self._preset_model.current_preset_name
        return self._preset_model.get_preset_description(name)
    
    def switch_to_custom_preset(self):
        """切换到自定义预设"""
        if self._preset_combo and self._preset_combo.currentText() != "自定义":
            self._preset_model.set_to_custom()
            self._preset_combo.blockSignals(True)  # 防止触发事件
            self._preset_combo.setCurrentText("自定义")
            self._preset_combo.blockSignals(False)
            self._update_description("自定义")
    
    def check_and_update_preset_status(self, points: List[Tuple[int, int]]):
        """
        检查点是否匹配预设，如果不匹配则切换到自定义模式
        
        Args:
            points: 当前曲线点
        """
        current_preset = self._preset_model.current_preset_name
        if current_preset != "自定义":
            # 检查点是否匹配当前预设
            if not self._preset_model.compare_points_with_preset(points, current_preset):
                self.switch_to_custom_preset()
    
    def reset_to_linear(self):
        """重置为线性预设"""
        if self._preset_combo:
            self._preset_combo.setCurrentText("线性") 