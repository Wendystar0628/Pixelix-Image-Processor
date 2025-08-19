"""
数据分析导出配置对话框
"""

import os
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QCheckBox, QComboBox, QSpinBox, QGroupBox,
    QFileDialog, QMessageBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt

from app.core.models.analysis_export_config import (
    AnalysisExportConfig, AnalysisExportType, 
    AnalysisChartFormat, AnalysisDataFormat
)
from app.ui.widgets.job_selection_widget import JobSelectionWidget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.configuration.config_data_accessor import ConfigDataAccessor


class AnalysisExportDialog(QDialog):
    """数据分析导出配置对话框"""
    
    def __init__(self, parent=None, batch_coordinator=None, config_accessor: Optional['ConfigDataAccessor'] = None, app_controller=None):
        super().__init__(parent)
        self.setWindowTitle("导出数据分析")
        self.setModal(True)
        self.resize(500, 700)  # 增加高度以容纳新组件
        
        self.batch_coordinator = batch_coordinator
        self.config_accessor = config_accessor
        self.app_controller = app_controller
        self.config = AnalysisExportConfig()
        self.jobs_data = {}  # 作业数据缓存
        
        self._load_jobs_data()
        self._init_ui()
        
    def _load_jobs_data(self):
        """加载作业数据"""
        if self.batch_coordinator:
            try:
                jobs = self.batch_coordinator.get_all_jobs()
                for job in jobs:
                    self.jobs_data[job.job_id] = {
                        "name": job.name,
                        "image_count": len(job.source_paths)
                    }
            except Exception as e:
                # 如果获取作业失败，使用空数据
                self.jobs_data = {}
                print(f"加载作业数据失败: {e}")
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 导出路径选择
        self._create_path_section(layout)
        
        # 导出模式选择
        self._create_export_mode_section(layout)
        
        # 分析类型选择
        self._create_analysis_types_section(layout)
        
        # 格式选择
        self._create_formats_section(layout)
        
        # 导出说明
        self._create_export_info_section(layout)
        
        # 按钮区域
        self._create_buttons_section(layout)
        
    def _create_path_section(self, layout):
        """创建路径选择区域"""
        group = QGroupBox("导出路径")
        group_layout = QVBoxLayout(group)
        
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("选择导出文件夹...")
        
        # 加载上次的导出路径
        if self.config_accessor:
            last_path = self.config_accessor.get_last_analysis_export_path()
            if last_path:
                self.path_edit.setText(last_path)
        
        path_layout.addWidget(self.path_edit)
        
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(browse_btn)
        
        group_layout.addLayout(path_layout)
        layout.addWidget(group)
        
    def _create_export_mode_section(self, layout):
        """创建导出模式选择区域"""
        group = QGroupBox("选择要导出的作业")
        group_layout = QVBoxLayout(group)
        
        # 作业选择组件
        self.job_selection_widget = JobSelectionWidget()
        self.job_selection_widget.set_jobs_data(self.jobs_data)
        self.job_selection_widget.selection_changed.connect(self._on_job_selection_changed)
        group_layout.addWidget(self.job_selection_widget)
        
        # 如果没有作业数据，显示提示信息
        if not self.jobs_data:
            info_label = QLabel("⚠️ 当前没有可用的作业，请先创建作业后再进行导出。")
            info_label.setStyleSheet("""
                QLabel {
                    color: #ff6b35;
                    font-size: 12px;
                    padding: 8px;
                    background-color: #fff3e0;
                    border-radius: 4px;
                    border: 1px solid #ffcc80;
                }
            """)
            info_label.setWordWrap(True)
            group_layout.addWidget(info_label)
        
        layout.addWidget(group)
        
    def _create_analysis_types_section(self, layout):
        """创建分析类型选择区域"""
        group = QGroupBox("选择分析类型")
        group_layout = QVBoxLayout(group)
        
        self.analysis_checkboxes = {}
        display_names = self.config.get_analysis_type_display_names()
        
        for analysis_type in AnalysisExportType:
            checkbox = QCheckBox(display_names[analysis_type])
            checkbox.setChecked(True)
            self.analysis_checkboxes[analysis_type] = checkbox
            group_layout.addWidget(checkbox)
            
        layout.addWidget(group)
        
    def _create_formats_section(self, layout):
        """创建格式选择区域"""
        group = QGroupBox("导出格式")
        group_layout = QVBoxLayout(group)
        
        # 图表格式
        chart_layout = QHBoxLayout()
        chart_layout.addWidget(QLabel("图表格式:"))
        self.chart_format_combo = QComboBox()
        self.chart_format_combo.addItem("PNG", AnalysisChartFormat.PNG)
        self.chart_format_combo.addItem("JPEG", AnalysisChartFormat.JPEG)
        self.chart_format_combo.addItem("SVG", AnalysisChartFormat.SVG)
        chart_layout.addWidget(self.chart_format_combo)
        chart_layout.addStretch()
        group_layout.addLayout(chart_layout)
        
        # JPEG质量
        quality_layout = QHBoxLayout()
        self.quality_label = QLabel("JPEG质量:")
        quality_layout.addWidget(self.quality_label)
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(95)
        self.quality_spin.setMinimumWidth(80)  # 增加宽度以显示数字
        self.quality_spin.setSuffix("%")  # 添加百分号后缀
        quality_layout.addWidget(self.quality_spin)
        quality_layout.addStretch()
        group_layout.addLayout(quality_layout)
        
        # 连接图表格式变化信号
        self.chart_format_combo.currentIndexChanged.connect(self._on_chart_format_changed)
        
        # 数据格式
        data_layout = QHBoxLayout()
        self.include_data_checkbox = QCheckBox("导出原始数据")
        self.include_data_checkbox.setChecked(True)
        data_layout.addWidget(self.include_data_checkbox)
        
        self.data_format_combo = QComboBox()
        self.data_format_combo.addItem("CSV", AnalysisDataFormat.CSV)
        self.data_format_combo.addItem("JSON", AnalysisDataFormat.JSON)
        self.data_format_combo.addItem("Excel", AnalysisDataFormat.XLSX)
        data_layout.addWidget(self.data_format_combo)
        data_layout.addStretch()
        group_layout.addLayout(data_layout)
        
        layout.addWidget(group)
        
        # 初始化JPEG质量控件状态
        self._on_chart_format_changed()
        

            
    def _on_job_selection_changed(self, selected_job_ids: List[str]):
        """作业选择改变处理"""
        # 这里可以添加额外的逻辑，比如更新预估导出时间等
        pass
        
    def _create_export_info_section(self, layout):
        """创建导出说明区域"""
        info_label = QLabel("💡 导出将使用Matplotlib引擎以确保最佳兼容性")
        info_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 8px;
                background-color: #f0f0f0;
                border-radius: 4px;
                border: 1px solid #d0d0d0;
            }
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
    def _on_chart_format_changed(self):
        """图表格式变化处理"""
        current_format = self.chart_format_combo.currentData()
        is_jpeg = current_format == AnalysisChartFormat.JPEG
        
        # 只有选择JPEG时才启用质量设置
        self.quality_label.setEnabled(is_jpeg)
        self.quality_spin.setEnabled(is_jpeg)
        
    def _create_buttons_section(self, layout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        export_btn = QPushButton("开始导出")
        export_btn.clicked.connect(self._on_export_clicked)
        export_btn.setDefault(True)
        button_layout.addWidget(export_btn)
        
        layout.addLayout(button_layout)
        
    def _browse_path(self):
        """浏览选择路径"""
        path = QFileDialog.getExistingDirectory(
            self, "选择导出文件夹", self.path_edit.text()
        )
        if path:
            self.path_edit.setText(path)
            
    def _on_export_clicked(self):
        """导出按钮点击处理"""
        if not self._validate_config():
            return
            
        self._update_config()
        
        # 保存导出路径到配置
        if self.path_edit.text():
            self._save_export_path(self.path_edit.text())
        
        self.accept()
        
    def _validate_config(self) -> bool:
        """验证配置"""
        if not self.path_edit.text().strip():
            QMessageBox.warning(self, "警告", "请选择导出路径")
            return False
            
        if not os.path.exists(self.path_edit.text()):
            QMessageBox.warning(self, "警告", "导出路径不存在")
            return False
            
        selected_types = [
            analysis_type for analysis_type, checkbox in self.analysis_checkboxes.items()
            if checkbox.isChecked()
        ]
        
        if not selected_types:
            QMessageBox.warning(self, "警告", "请至少选择一种分析类型")
            return False
            
        # 验证是否选择了作业
        selected_job_ids = self.job_selection_widget.get_selected_job_ids()
        if not selected_job_ids:
            QMessageBox.warning(self, "警告", "请至少选择一个作业进行导出")
            return False
            
        return True
        
    def _update_config(self):
        """更新配置对象"""
        self.config.export_path = self.path_edit.text().strip()
        
        self.config.selected_analysis_types = [
            analysis_type for analysis_type, checkbox in self.analysis_checkboxes.items()
            if checkbox.isChecked()
        ]
        
        self.config.chart_format = self.chart_format_combo.currentData()
        self.config.chart_quality = self.quality_spin.value()
        self.config.include_raw_data = self.include_data_checkbox.isChecked()
        self.config.data_format = self.data_format_combo.currentData()
        
        # 设置导出模式和选中的作业
        self.config.export_mode = "selected"
        self.config.selected_job_ids = self.job_selection_widget.get_selected_job_ids()
        
    def get_config(self) -> AnalysisExportConfig:
        """获取配置"""
        return self.config
    
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
                    config_service.update_config(last_analysis_export_path=path)
        except Exception as e:
            # 配置保存失败不应影响主要功能
            print(f"保存分析导出路径失败: {e}")