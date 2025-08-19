"""
导入文件夹对话框模块

提供导入文件夹时的高级选项设置。
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QSpinBox, QDialogButtonBox, QGroupBox,
    QFormLayout
)


class ImportFolderDialog(QDialog):
    """
    导入文件夹对话框，提供导入选项设置。
    """
    
    def __init__(self, parent=None):
        """
        初始化导入文件夹对话框
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.setWindowTitle("导入文件夹选项")
        self.setMinimumWidth(400)
        
        # 初始化选项
        self.recursive = True
        self.filter_by_size = False
        self.min_width = 100
        self.min_height = 100
        
        # 初始化UI
        self._init_ui()
        
    def _init_ui(self):
        """初始化对话框UI"""
        layout = QVBoxLayout(self)
        
        # 搜索选项组
        search_group = QGroupBox("搜索选项")
        search_layout = QVBoxLayout(search_group)
        
        # 递归搜索选项
        self.recursive_checkbox = QCheckBox("递归搜索子文件夹")
        self.recursive_checkbox.setChecked(self.recursive)
        self.recursive_checkbox.stateChanged.connect(self._on_recursive_changed)
        search_layout.addWidget(self.recursive_checkbox)
        
        layout.addWidget(search_group)
        
        # 过滤选项组
        filter_group = QGroupBox("过滤选项")
        filter_layout = QVBoxLayout(filter_group)
        
        # 按尺寸过滤选项
        self.filter_size_checkbox = QCheckBox("过滤小图像")
        self.filter_size_checkbox.setChecked(self.filter_by_size)
        self.filter_size_checkbox.stateChanged.connect(self._on_filter_size_changed)
        filter_layout.addWidget(self.filter_size_checkbox)
        
        # 最小尺寸设置
        size_layout = QFormLayout()
        
        self.min_width_spinbox = QSpinBox()
        self.min_width_spinbox.setRange(1, 9999)
        self.min_width_spinbox.setValue(self.min_width)
        self.min_width_spinbox.setEnabled(self.filter_by_size)
        size_layout.addRow("最小宽度:", self.min_width_spinbox)
        
        self.min_height_spinbox = QSpinBox()
        self.min_height_spinbox.setRange(1, 9999)
        self.min_height_spinbox.setValue(self.min_height)
        self.min_height_spinbox.setEnabled(self.filter_by_size)
        size_layout.addRow("最小高度:", self.min_height_spinbox)
        
        filter_layout.addLayout(size_layout)
        layout.addWidget(filter_group)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def _on_recursive_changed(self, state):
        """递归搜索选项改变时的处理"""
        self.recursive = state == Qt.CheckState.Checked
        
    def _on_filter_size_changed(self, state):
        """按尺寸过滤选项改变时的处理"""
        self.filter_by_size = state == Qt.CheckState.Checked
        self.min_width_spinbox.setEnabled(self.filter_by_size)
        self.min_height_spinbox.setEnabled(self.filter_by_size)
        
    def get_options(self):
        """
        获取用户设置的选项
        
        Returns:
            dict: 包含选项的字典
        """
        return {
            "recursive": self.recursive_checkbox.isChecked(),
            "filter_by_size": self.filter_size_checkbox.isChecked(),
            "min_width": self.min_width_spinbox.value(),
            "min_height": self.min_height_spinbox.value()
        } 
        
    def get_selected_folder(self) -> str:
        """
        获取用户选择的文件夹路径
        
        Returns:
            str: 文件夹路径
        """
        # 这个方法应该返回用户在对话框中选择的文件夹路径
        # 但是当前对话框设计中没有文件夹选择器，所以返回空字符串
        # 实际应用中，这个值应该由调用者设置
        return getattr(self, "_selected_folder", "")
        
    def set_selected_folder(self, folder_path: str) -> None:
        """
        设置选中的文件夹路径
        
        Args:
            folder_path: 文件夹路径
        """
        self._selected_folder = folder_path
        
    def is_recursive_selected(self) -> bool:
        """
        获取是否选中递归搜索子文件夹
        
        Returns:
            bool: 是否递归搜索
        """
        return self.recursive_checkbox.isChecked()
        
    def get_selected_file_types(self) -> list:
        """
        获取选中的文件类型列表
        
        Returns:
            list: 文件类型列表，例如 [".jpg", ".png"]
        """
        # 当前对话框设计中没有文件类型选择器，返回默认图像类型
        return [".jpg", ".jpeg", ".png", ".bmp", ".tiff"] 