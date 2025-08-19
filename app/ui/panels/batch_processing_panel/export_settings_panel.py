"""
导出设置面板模块
"""
import os
from typing import Dict, Any, Optional

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QLabel, QPushButton, QComboBox, QLineEdit,
    QFileDialog
)

from app.features.batch_processing.batch_coordinator import BatchProcessingHandler
from app.core.models.export_config import ExportConfig, OutputDirectoryMode, ConflictResolution
from app.ui.dialogs.export_options import ExportOptionsDialog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.configuration.config_data_accessor import ConfigDataAccessor



class ExportSettingsPanel(QWidget):
    """
    管理批处理导出设置的面板
    
    职责：
    1. 显示和更新导出设置
    2. 处理导出相关的用户操作
    3. 发出处理请求的信号
    """
    
    # 定义信号
    process_requested = pyqtSignal()
    
    def __init__(self, handler: BatchProcessingHandler, config_accessor: Optional['ConfigDataAccessor'] = None, app_controller=None, parent=None):
        super().__init__(parent)
        self.handler = handler
        self.config_accessor = config_accessor
        self.app_controller = app_controller
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """初始化UI组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 导出设置组
        export_settings_group = QGroupBox("导出设置")
        export_settings_layout = QVBoxLayout(export_settings_group)
        
        # 输出目录模式
        dir_mode_layout = QHBoxLayout()
        dir_mode_layout.addWidget(QLabel("输出位置:"))
        self.dir_mode_combo = QComboBox()
        self.dir_mode_combo.addItem("保存到指定文件夹", OutputDirectoryMode.SAVE_TO_SINGLE_FOLDER.value)
        self.dir_mode_combo.addItem("在原图位置保存", OutputDirectoryMode.SAVE_IN_PLACE.value)
        self.dir_mode_combo.addItem("保持原始目录结构", OutputDirectoryMode.MAINTAIN_DIRECTORY_STRUCTURE.value)
        dir_mode_layout.addWidget(self.dir_mode_combo)
        export_settings_layout.addLayout(dir_mode_layout)
        
        # 输出目录选择
        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(QLabel("输出目录:"))
        self.output_dir_edit = QLineEdit()
        
        # 加载上次的导出路径
        if self.config_accessor:
            last_path = self.config_accessor.get_last_batch_export_path()
            if last_path:
                self.output_dir_edit.setText(last_path)
        
        self.browse_output_dir_button = QPushButton("浏览...")
        output_dir_layout.addWidget(self.output_dir_edit)
        output_dir_layout.addWidget(self.browse_output_dir_button)
        export_settings_layout.addLayout(output_dir_layout)
        
        # 文件冲突解决
        conflict_layout = QHBoxLayout()
        conflict_layout.addWidget(QLabel("文件冲突时:"))
        self.conflict_combo = QComboBox()
        self.conflict_combo.addItem("覆盖", ConflictResolution.OVERWRITE.value)
        self.conflict_combo.addItem("跳过", ConflictResolution.SKIP.value)
        self.conflict_combo.addItem("重命名", ConflictResolution.RENAME.value)
        conflict_layout.addWidget(self.conflict_combo)
        export_settings_layout.addLayout(conflict_layout)
        
        # 高级选项按钮
        self.advanced_options_button = QPushButton("高级导出选项...")
        export_settings_layout.addWidget(self.advanced_options_button)
        
        export_settings_layout.addStretch()
        
        # 处理与导出按钮
        self.process_button = QPushButton("处理并导出")
        self.process_button.setStyleSheet("font-weight: bold; background-color: #4CAF50; color: white;")
        self.process_button.setMinimumHeight(40)
        export_settings_layout.addWidget(self.process_button)
        
        layout.addWidget(export_settings_group)
        
        # 初始化UI状态
        self._update_output_dir_ui()
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 连接按钮点击信号
        self.browse_output_dir_button.clicked.connect(self._on_browse_output_dir_clicked)
        self.advanced_options_button.clicked.connect(self._on_advanced_options_clicked)
        self.process_button.clicked.connect(self._on_process_clicked)
        
        # 连接下拉框变更信号
        self.dir_mode_combo.currentIndexChanged.connect(self._update_output_dir_ui)
        
    def _update_output_dir_ui(self):
        """根据输出目录模式更新UI"""
        mode = self.dir_mode_combo.currentData()
        is_single_folder = mode == OutputDirectoryMode.SAVE_TO_SINGLE_FOLDER.value
        self.output_dir_edit.setEnabled(is_single_folder)
        self.browse_output_dir_button.setEnabled(is_single_folder)
        if not is_single_folder:
            self.output_dir_edit.clear()
    
    def update_export_config(self):
        """从UI更新导出配置"""
        config_updates = {
            "output_directory": self.output_dir_edit.text(),
            "output_directory_mode": self.dir_mode_combo.currentData(),
            "conflict_resolution": self.conflict_combo.currentData()
        }
        self.handler.update_export_config(config_updates)
        
    def set_processing_state(self, is_processing: bool):
        """设置处理状态"""
        self.process_button.setEnabled(not is_processing)
        if is_processing:
            self.process_button.setText("处理中...")
        else:
            self.process_button.setText("处理并导出")
    
    # --- 槽函数 ---
    
    @pyqtSlot()
    def _on_browse_output_dir_clicked(self):
        """浏览输出目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录", self.output_dir_edit.text())
        if directory:
            self.output_dir_edit.setText(directory)
            # 保存导出路径到配置
            self._save_export_path(directory)
    
    @pyqtSlot()
    def _on_advanced_options_clicked(self):
        """打开高级导出选项对话框"""
        # 获取当前配置
        current_config = self.handler.get_export_config()
        
        # 获取配置访问器和应用控制器
        config_accessor = None
        app_controller = None
        if hasattr(self.handler, 'get_config_accessor'):
            config_accessor = self.handler.get_config_accessor()
        if hasattr(self.handler, 'get_app_controller'):
            app_controller = self.handler.get_app_controller()
        
        # 创建并显示对话框
        dialog = ExportOptionsDialog(current_config, config_accessor, app_controller, self)
        dialog.config_updated.connect(self._on_config_updated)
        
        if dialog.exec() == ExportOptionsDialog.DialogCode.Accepted:
            # 对话框已通过信号更新配置
            pass
    
    @pyqtSlot(dict)
    def _on_config_updated(self, config_updates):
        """处理配置更新
        
        Args:
            config_updates: 配置更新字典
        """
        self.handler.update_export_config(config_updates)
    
    @pyqtSlot()
    def _on_process_clicked(self):
        """处理并导出所有作业"""
        # 更新导出配置
        self.update_export_config()
        
        # 检查输出目录
        config = self.handler.get_export_config()
        if config.output_directory_mode == OutputDirectoryMode.SAVE_TO_SINGLE_FOLDER and not config.output_directory:
            directory = QFileDialog.getExistingDirectory(self, "选择输出目录", "")
            if not directory:
                return
            self.output_dir_edit.setText(directory)
            self.update_export_config()
            # 保存导出路径到配置
            self._save_export_path(directory)
        else:
            # 如果已有路径，也保存到配置
            if self.output_dir_edit.text():
                self._save_export_path(self.output_dir_edit.text())
        
        # 发出处理请求信号
        self.process_requested.emit()
    
    def _save_export_path(self, path: str) -> None:
        """保存导出路径到配置
        
        Args:
            path: 要保存的导出路径
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