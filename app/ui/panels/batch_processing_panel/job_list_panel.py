"""
作业列表面板模块
"""
import os
from typing import Optional, List, Dict, Any

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QListWidget, QListWidgetItem, QPushButton, 
    QInputDialog, QGridLayout
)

from app.core.models.batch_models import BatchJob
from app.features.batch_processing.batch_coordinator import BatchProcessingHandler


class JobListPanel(QWidget):
    """
    管理批处理作业列表的面板
    
    职责：
    1. 显示作业列表
    2. 处理作业的添加、删除、重命名等操作
    3. 发出作业选择变更的信号
    """
    
    # 注意：job_selected信号已移除，统一使用JobSelectionManager管理选择状态
    
    def __init__(self, handler: BatchProcessingHandler, parent=None):
        super().__init__(parent)
        self.handler = handler
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """初始化UI组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 作业列表组
        jobs_group = QGroupBox("批处理作业")
        jobs_layout = QVBoxLayout(jobs_group)
        
        # 作业列表
        self.jobs_list = QListWidget()
        self.jobs_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        jobs_layout.addWidget(self.jobs_list)
        
        # 按钮布局
        buttons_layout = QGridLayout()
        self.add_job_button = QPushButton("新建作业")
        self.quick_create_button = QPushButton("快速新建")
        self.remove_job_button = QPushButton("删除作业")
        self.rename_job_button = QPushButton("重命名")
        
        buttons_layout.addWidget(self.add_job_button, 0, 0)
        buttons_layout.addWidget(self.quick_create_button, 0, 1)
        buttons_layout.addWidget(self.remove_job_button, 1, 0)
        buttons_layout.addWidget(self.rename_job_button, 1, 1)
        
        jobs_layout.addLayout(buttons_layout)
        layout.addWidget(jobs_group)
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 连接作业列表选择变更信号
        self.jobs_list.currentItemChanged.connect(self._on_job_selection_changed)
        
        # 连接按钮点击信号
        self.add_job_button.clicked.connect(self._on_add_job_clicked)
        self.quick_create_button.clicked.connect(self._on_quick_create_clicked)
        self.remove_job_button.clicked.connect(self._on_remove_job_clicked)
        self.rename_job_button.clicked.connect(self._on_rename_job_clicked)
        
        # 连接作业管理器的信号
        self.handler.job_manager.job_list_changed.connect(self.update_jobs_display)
        
        # 连接作业选择管理器的信号
        self.handler.job_selection_manager.selection_update_requested.connect(self._on_selection_update_requested)
        
    def update_jobs_display(self):
        """更新作业列表显示"""
        self.jobs_list.clear()
        
        # 获取所有作业并添加到列表（不再需要过滤图像池作业）
        all_jobs = self.handler.job_manager.get_all_jobs()
        for job in all_jobs:
            self.jobs_list.addItem(job.name)
        
        # 让JobSelectionManager处理选择一致性
        self.handler.job_selection_manager.ensure_selection_consistency()
    
    def get_current_job(self) -> Optional[BatchJob]:
        """获取当前选中的作业"""
        current_item = self.jobs_list.currentItem()
        if current_item:
            job_name = current_item.text()
            return self.handler.job_manager.get_job_by_name(job_name)
        return None
    
    def select_job_by_name(self, job_name: str) -> bool:
        """根据作业名称选中作业"""
        for i in range(self.jobs_list.count()):
            item = self.jobs_list.item(i)
            if item and item.text() == job_name:
                self.jobs_list.setCurrentRow(i)
                return True
        return False
    
    # --- 槽函数 ---
    
    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def _on_job_selection_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        """当选择的作业改变时通过JobSelectionManager统一管理"""
        job = self.get_current_job()
        if job:
            # 通过JobSelectionManager设置选择，统一管理选择状态
            self.handler.job_selection_manager.set_selected_job(job.job_id)
    
    @pyqtSlot(str)
    def _on_selection_update_requested(self, job_id: str):
        """处理JobSelectionManager请求的选择更新，同步UI选中状态"""
        if job_id:
            job = self.handler.job_manager.get_job(job_id)
            if job:
                self.select_job_by_name(job.name)
        else:
            # 清除选择
            self.jobs_list.setCurrentRow(-1)
    
    @pyqtSlot()
    def _on_add_job_clicked(self):
        """添加新作业"""
        name, ok = QInputDialog.getText(self, "新建作业", "请输入作业名称:")
        if ok and name:
            job = self.handler.add_job(name)
            if job:
                self.select_job_by_name(job.name)
    
    @pyqtSlot()
    def _on_quick_create_clicked(self):
        """快速创建多个作业"""
        from app.ui.dialogs.quick_create_jobs_dialog import QuickCreateJobsDialog
        
        dialog = QuickCreateJobsDialog(self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            job_count = dialog.get_job_count()
            created_jobs = self.handler.quick_create_jobs(job_count)
            if created_jobs:
                # 选中第一个新创建的作业
                self.select_job_by_name(created_jobs[0].name)
    
    @pyqtSlot()
    def _on_remove_job_clicked(self):
        """删除选中的作业"""
        job = self.get_current_job()
        if job:
            self.handler.remove_job(job.job_id)
    
    @pyqtSlot()
    def _on_rename_job_clicked(self):
        """重命名选中的作业"""
        job = self.get_current_job()
        if job:
            new_name, ok = QInputDialog.getText(
                self, "重命名作业", "请输入新的作业名称:", 
                text=job.name
            )
            if ok and new_name and new_name != job.name:
                self.handler.rename_job(job.job_id, new_name)