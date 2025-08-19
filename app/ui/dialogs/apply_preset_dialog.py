"""
应用预设对话框模块
"""
from typing import List, Optional, Tuple, Dict, Any
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QDialogButtonBox, QWidget,
    QMessageBox, QRadioButton, QGroupBox
)

from app.handlers.preset_handler import PresetHandler
from app.core.models.batch_models import BatchJob


class ApplyPresetDialog(QDialog):
    """
    应用预设对话框，用于选择预设和目标作业。
    """
    
    def __init__(self, parent: Optional[QWidget] = None, preset_handler: Optional[PresetHandler] = None):
        """
        初始化应用预设对话框。
        
        Args:
            parent: 父窗口部件
            preset_handler: 预设处理器
        """
        super().__init__(parent)
        self.preset_handler = preset_handler
        self.selected_preset = ""
        self.apply_to_current = True
        self.selected_jobs = []
        
        # 获取批处理作业列表
        self.jobs = []
        self._get_batch_jobs()
        
        self._setup_ui()
        self._populate_presets()
        
    def _get_batch_jobs(self) -> None:
        """
        获取批处理作业列表
        """
        if self.preset_handler is None:
            return
            
        try:
            if hasattr(self.preset_handler, 'context'):
                context = self.preset_handler.context
                if hasattr(context, 'batch_processor') and context.batch_processor is not None:
                    batch_processor = context.batch_processor
                    if hasattr(batch_processor, 'jobs'):
                        # 如果是方法，调用它
                        if callable(getattr(batch_processor, 'jobs')):
                            jobs = batch_processor.jobs()
                            if jobs is not None:  # 确保返回的jobs不是None
                                self.jobs = jobs
                        # 如果是属性，直接访问
                        else:
                            jobs = batch_processor.jobs
                            if jobs is not None:  # 确保jobs属性不是None
                                self.jobs = jobs
        except Exception as e:
            print(f"获取批处理作业失败: {e}")
        
    def _setup_ui(self) -> None:
        """
        设置用户界面。
        """
        self.setWindowTitle("快速应用预设")
        self.setMinimumWidth(350)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 预设选择
        preset_layout = QHBoxLayout()
        preset_label = QLabel("选择预设:")
        self.preset_combo = QComboBox()
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.preset_combo, 1)
        layout.addLayout(preset_layout)
        
        # 应用目标选择
        layout.addSpacing(10)
        
        # 创建单选按钮组
        self.target_group = QGroupBox("应用到:")
        target_layout = QVBoxLayout()
        
        # 当前图片选项
        self.current_radio = QRadioButton("当前图片")
        self.current_radio.setChecked(True)
        target_layout.addWidget(self.current_radio)
        
        # 批处理作业选项
        self.jobs_radio = QRadioButton("批处理作业")
        target_layout.addWidget(self.jobs_radio)
        
        # 作业选择区域
        self.jobs_container = QWidget()
        jobs_layout = QVBoxLayout()
        jobs_layout.setContentsMargins(20, 0, 0, 0)
        
        # 如果有作业，显示作业复选框
        if self.jobs:
            self.job_checkboxes = []
            for job in self.jobs:
                if hasattr(job, 'name'):  # 确保job对象有name属性
                    checkbox = QCheckBox(job.name)
                    self.job_checkboxes.append(checkbox)
                    jobs_layout.addWidget(checkbox)
        else:
            # 如果没有作业，显示提示
            no_jobs_label = QLabel("请先新建作业")
            no_jobs_label.setStyleSheet("color: gray; font-style: italic;")
            jobs_layout.addWidget(no_jobs_label)
            # 禁用作业选项
            self.jobs_radio.setEnabled(False)
            
        self.jobs_container.setLayout(jobs_layout)
        target_layout.addWidget(self.jobs_container)
        
        # 设置单选按钮组的布局
        self.target_group.setLayout(target_layout)
        layout.addWidget(self.target_group)
        
        # 连接单选按钮的信号
        self.current_radio.toggled.connect(self._on_target_changed)
        self.jobs_radio.toggled.connect(self._on_target_changed)
        
        # 按钮
        layout.addSpacing(20)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # 初始状态下禁用作业选择区域
        self._on_target_changed()
        
    def _on_target_changed(self) -> None:
        """
        当目标选择改变时更新UI
        """
        # 启用/禁用作业选择区域
        self.jobs_container.setEnabled(self.jobs_radio.isChecked())
        
    def _populate_presets(self) -> None:
        """
        填充预设下拉列表。
        """
        if not self.preset_handler:
            return
            
        # 获取所有预设名称
        preset_names = self.preset_handler.get_all_preset_names()
        
        # 清空下拉列表
        self.preset_combo.clear()
        
        if not preset_names:
            self.preset_combo.addItem("(无可用预设)")
            self.preset_combo.setEnabled(False)
            return
            
        # 添加预设名称
        for name in preset_names:
            self.preset_combo.addItem(name)
            
        # 默认选择第一个预设
        if preset_names:
            self.preset_combo.setCurrentIndex(0)
            
    def get_selected_options(self) -> Tuple[str, bool, List[str]]:
        """
        获取用户选择的预设和目标作业。
        
        Returns:
            Tuple[str, bool, List[str]]: (预设名称, 是否应用到当前图片, 要应用的作业名称列表)
        """
        # 获取选择的预设
        self.selected_preset = self.preset_combo.currentText()
        
        # 获取应用目标
        self.apply_to_current = self.current_radio.isChecked()
        
        # 获取选择的作业
        self.selected_jobs = []
        if self.jobs_radio.isChecked() and hasattr(self, 'job_checkboxes'):
            for i, checkbox in enumerate(self.job_checkboxes):
                if checkbox.isChecked() and i < len(self.jobs):
                    if hasattr(self.jobs[i], 'name'):  # 确保job对象有name属性
                        self.selected_jobs.append(self.jobs[i].name)
        
        return (self.selected_preset, self.apply_to_current, self.selected_jobs) 