"""导出选项对话框模块

提供批量导出的高级选项设置界面。
"""

from typing import Dict, Any, Optional
import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QGroupBox, QLabel, QLineEdit, QSpinBox, QComboBox, 
    QCheckBox, QSlider, QPushButton, QDialogButtonBox,
    QFormLayout, QGridLayout, QFileDialog
)

from app.core.models.export_config import (
    ExportConfig, NamingPattern, ExportFormat
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.configuration.config_data_accessor import ConfigDataAccessor


class ExportOptionsDialog(QDialog):
    """导出选项对话框
    
    提供批量导出的高级选项设置，包括：
    - 文件命名设置
    - 格式和质量设置
    - 其他高级选项
    """
    
    # 定义信号
    config_updated = pyqtSignal(dict)  # 配置更新信号
    
    def __init__(self, config: ExportConfig, config_accessor: Optional['ConfigDataAccessor'] = None, app_controller=None, parent=None):
        """初始化对话框
        
        Args:
            config: 当前的导出配置
            config_accessor: 配置数据访问器实例
            app_controller: 应用控制器实例
            parent: 父窗口
        """
        super().__init__(parent)
        self.config = config
        self.config_accessor = config_accessor
        self.app_controller = app_controller
        self.setWindowTitle("高级导出选项")
        self.setMinimumSize(500, 600)
        self.setModal(True)
        
        self._init_ui()
        self._load_config()
        
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建主内容区域
        main_content = self._create_main_content()
        layout.addWidget(main_content)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
    def _create_main_content(self) -> QWidget:
        """创建主内容区域，包含文件命名和格式设置"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 文件命名组
        naming_group = QGroupBox("文件命名")
        naming_layout = QFormLayout(naming_group)
        
        # 命名模式选择
        self.naming_pattern_combo = QComboBox()
        self.naming_pattern_combo.addItem("保持原始文件名", NamingPattern.ORIGINAL.value)
        self.naming_pattern_combo.addItem("前缀 + 原始文件名", NamingPattern.PREFIX.value)
        self.naming_pattern_combo.addItem("原始文件名 + 后缀", NamingPattern.SUFFIX.value)
        self.naming_pattern_combo.addItem("索引号", NamingPattern.INDEX.value)
        self.naming_pattern_combo.addItem("前缀 + 索引号", NamingPattern.PREFIX_INDEX.value)
        self.naming_pattern_combo.addItem("自定义模式", NamingPattern.CUSTOM.value)
        self.naming_pattern_combo.currentTextChanged.connect(self._on_naming_pattern_changed)
        naming_layout.addRow("命名模式:", self.naming_pattern_combo)
        
        # 前缀
        self.prefix_edit = QLineEdit()
        self.prefix_edit.setPlaceholderText("输入前缀...")
        naming_layout.addRow("前缀:", self.prefix_edit)
        
        # 后缀
        self.suffix_edit = QLineEdit()
        self.suffix_edit.setPlaceholderText("输入后缀...")
        naming_layout.addRow("后缀:", self.suffix_edit)
        
        # 起始索引
        self.start_index_spin = QSpinBox()
        self.start_index_spin.setRange(0, 99999)
        self.start_index_spin.setValue(1)
        naming_layout.addRow("起始索引:", self.start_index_spin)
        
        # 索引位数
        self.index_digits_spin = QSpinBox()
        self.index_digits_spin.setRange(1, 10)
        self.index_digits_spin.setValue(3)
        naming_layout.addRow("索引位数:", self.index_digits_spin)
        
        # 自定义模式
        self.custom_pattern_edit = QLineEdit()
        self.custom_pattern_edit.setPlaceholderText("例如: {prefix}_{filename}_{index}")
        naming_layout.addRow("自定义模式:", self.custom_pattern_edit)
        
        layout.addWidget(naming_group)
        
        # 导出路径组
        path_group = QGroupBox("导出路径")
        path_layout = QHBoxLayout(path_group)
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("选择导出目录...")
        path_layout.addWidget(self.path_edit)
        
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self._browse_export_path)
        path_layout.addWidget(browse_btn)
        
        layout.addWidget(path_group)
        
        # 预览组
        preview_group = QGroupBox("预览")
        preview_layout = QFormLayout(preview_group)
        
        self.preview_label = QLabel("示例: example_image.jpg")
        self.preview_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 8px; border: 1px solid #ccc; }")
        preview_layout.addRow("文件名预览:", self.preview_label)
        
        layout.addWidget(preview_group)
        
        # 导出格式组
        format_group = QGroupBox("导出格式")
        format_layout = QFormLayout(format_group)
        
        # 格式选择
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItem("保持原始格式", ExportFormat.ORIGINAL.value)
        self.export_format_combo.addItem("PNG", ExportFormat.PNG.value)
        self.export_format_combo.addItem("JPEG", ExportFormat.JPEG.value)
        self.export_format_combo.addItem("BMP", ExportFormat.BMP.value)
        self.export_format_combo.addItem("TIFF", ExportFormat.TIFF.value)
        self.export_format_combo.currentTextChanged.connect(self._on_format_changed)
        format_layout.addRow("导出格式:", self.export_format_combo)
        
        layout.addWidget(format_group)
        
        # JPEG质量组
        self.jpeg_group = QGroupBox("JPEG 设置")
        jpeg_layout = QFormLayout(self.jpeg_group)
        
        # JPEG质量滑块
        jpeg_quality_layout = QHBoxLayout()
        self.jpeg_quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.jpeg_quality_slider.setRange(1, 100)
        self.jpeg_quality_slider.setValue(90)
        self.jpeg_quality_slider.valueChanged.connect(self._on_jpeg_quality_changed)
        
        self.jpeg_quality_label = QLabel("90")
        self.jpeg_quality_label.setMinimumWidth(30)
        
        jpeg_quality_layout.addWidget(self.jpeg_quality_slider)
        jpeg_quality_layout.addWidget(self.jpeg_quality_label)
        
        jpeg_layout.addRow("质量 (1-100):", jpeg_quality_layout)
        
        layout.addWidget(self.jpeg_group)
        
        # PNG压缩组
        self.png_group = QGroupBox("PNG 设置")
        png_layout = QFormLayout(self.png_group)
        
        # PNG压缩滑块
        png_compression_layout = QHBoxLayout()
        self.png_compression_slider = QSlider(Qt.Orientation.Horizontal)
        self.png_compression_slider.setRange(0, 9)
        self.png_compression_slider.setValue(9)
        self.png_compression_slider.valueChanged.connect(self._on_png_compression_changed)
        
        self.png_compression_label = QLabel("9")
        self.png_compression_label.setMinimumWidth(30)
        
        png_compression_layout.addWidget(self.png_compression_slider)
        png_compression_layout.addWidget(self.png_compression_label)
        
        png_layout.addRow("压缩级别 (0-9):", png_compression_layout)
        
        layout.addWidget(self.png_group)
        
        return widget
        

        

        

        
    def _load_config(self):
        """从配置加载UI状态"""
        # 命名设置
        self._set_combo_value(self.naming_pattern_combo, self.config.naming_pattern.value)
        self.prefix_edit.setText(self.config.prefix)
        self.suffix_edit.setText(self.config.suffix)
        self.start_index_spin.setValue(self.config.start_index)
        self.index_digits_spin.setValue(self.config.index_digits)
        self.custom_pattern_edit.setText(self.config.custom_pattern)
        
        # 格式设置
        self._set_combo_value(self.export_format_combo, self.config.export_format.value)
        self.jpeg_quality_slider.setValue(self.config.jpeg_quality)
        self.png_compression_slider.setValue(self.config.png_compression)
        
        # 加载上次的导出路径
        if self.config_accessor:
            last_path = self.config_accessor.get_last_batch_export_path()
            if last_path:
                self.path_edit.setText(last_path)
        
        # 更新UI状态
        self._on_naming_pattern_changed()
        self._on_format_changed()
        self._update_preview()
        
    def _set_combo_value(self, combo: QComboBox, value: str):
        """设置下拉框的值"""
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                break
                
    def _on_naming_pattern_changed(self):
        """命名模式改变时的处理"""
        pattern = self.naming_pattern_combo.currentData()
        
        # 根据模式启用/禁用相关控件
        self.prefix_edit.setEnabled(pattern in [NamingPattern.PREFIX.value, NamingPattern.PREFIX_INDEX.value, NamingPattern.CUSTOM.value])
        self.suffix_edit.setEnabled(pattern in [NamingPattern.SUFFIX.value, NamingPattern.CUSTOM.value])
        self.start_index_spin.setEnabled(pattern in [NamingPattern.INDEX.value, NamingPattern.PREFIX_INDEX.value, NamingPattern.CUSTOM.value])
        self.index_digits_spin.setEnabled(pattern in [NamingPattern.INDEX.value, NamingPattern.PREFIX_INDEX.value, NamingPattern.CUSTOM.value])
        self.custom_pattern_edit.setEnabled(pattern == NamingPattern.CUSTOM.value)
        
        self._update_preview()
        
    def _on_format_changed(self):
        """格式改变时的处理"""
        format_value = self.export_format_combo.currentData()
        
        # 根据格式显示/隐藏相关设置组
        self.jpeg_group.setVisible(format_value == ExportFormat.JPEG.value)
        self.png_group.setVisible(format_value == ExportFormat.PNG.value)
        
    def _on_jpeg_quality_changed(self):
        """JPEG质量改变时的处理"""
        value = self.jpeg_quality_slider.value()
        self.jpeg_quality_label.setText(str(value))
        
    def _on_png_compression_changed(self):
        """PNG压缩级别改变时的处理"""
        value = self.png_compression_slider.value()
        self.png_compression_label.setText(str(value))
        
    def _update_preview(self):
        """更新文件名预览"""
        try:
            # 创建临时配置用于预览
            temp_config = ExportConfig(
                naming_pattern=NamingPattern(self.naming_pattern_combo.currentData()),
                prefix=self.prefix_edit.text(),
                suffix=self.suffix_edit.text(),
                start_index=self.start_index_spin.value(),
                index_digits=self.index_digits_spin.value(),
                custom_pattern=self.custom_pattern_edit.text(),
                export_format=ExportFormat(self.export_format_combo.currentData())
            )
            
            # 生成预览文件名
            filename = temp_config.get_output_filename("example_image", 1)
            extension = temp_config.get_output_extension(".jpg")
            preview = f"{filename}{extension}"
            
            self.preview_label.setText(f"示例: {preview}")
        except Exception:
            self.preview_label.setText("预览: 无效配置")
            
    def _on_accept(self):
        """确认按钮点击处理"""
        # 收集所有配置
        config_updates = {
            "naming_pattern": self.naming_pattern_combo.currentData(),
            "prefix": self.prefix_edit.text(),
            "suffix": self.suffix_edit.text(),
            "start_index": self.start_index_spin.value(),
            "index_digits": self.index_digits_spin.value(),
            "custom_pattern": self.custom_pattern_edit.text(),
            "export_format": self.export_format_combo.currentData(),
            "jpeg_quality": self.jpeg_quality_slider.value(),
            "png_compression": self.png_compression_slider.value(),
            "export_path": self.path_edit.text()
        }
        
        # 保存导出路径到配置
        if self.path_edit.text():
            self._save_export_path(self.path_edit.text())
        
        # 发出配置更新信号
        self.config_updated.emit(config_updates)
        
        # 接受对话框
        self.accept()
    
    def _browse_export_path(self):
        """浏览选择导出路径"""
        current_path = self.path_edit.text() or os.path.expanduser("~")
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择导出目录",
            current_path
        )
        
        if directory:
            self.path_edit.setText(directory)
        
    def _save_export_path(self, path: str):
        """保存导出路径到配置
        
        Args:
            path: 导出路径
        """
        try:
            # 通过app_controller获取config_service
            if hasattr(self, 'app_controller') and self.app_controller:
                config_service = self.app_controller.get_config_service()
                if config_service:
                    config_service.update_config(last_batch_export_path=path)
        except Exception as e:
            # 配置保存失败不应影响主要功能
            print(f"保存导出路径失败: {e}")
    
    def get_config_updates(self) -> Dict[str, Any]:
        """获取配置更新
        
        Returns:
            Dict[str, Any]: 配置更新字典
        """
        return {
            "naming_pattern": self.naming_pattern_combo.currentData(),
            "prefix": self.prefix_edit.text(),
            "suffix": self.suffix_edit.text(),
            "start_index": self.start_index_spin.value(),
            "index_digits": self.index_digits_spin.value(),
            "custom_pattern": self.custom_pattern_edit.text(),
            "export_format": self.export_format_combo.currentData(),
            "jpeg_quality": self.jpeg_quality_slider.value(),
            "png_compression": self.png_compression_slider.value()
        }