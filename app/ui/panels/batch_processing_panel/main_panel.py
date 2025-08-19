"""
批处理面板模块
"""
import os
from typing import Optional, List, Dict, Any

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMessageBox
)

from app.core.models.batch_models import BatchJob, BatchJobStatus
from app.features.batch_processing.batch_coordinator import BatchProcessingHandler
from app.ui.panels.batch_processing_panel.job_list_panel import JobListPanel
from app.ui.panels.batch_processing_panel.job_detail_panel import JobDetailPanel
from app.ui.panels.batch_processing_panel.image_pool_panel import ImagePoolPanel
from app.ui.panels.batch_processing_panel.export_settings_panel import ExportSettingsPanel


class BatchProcessingPanel(QWidget):
    """
    管理批处理UI的面板。
    
    职责：
    1. 组织和布局子面板
    2. 协调子面板之间的交互
    3. 处理批处理相关的全局事件
    """

    def __init__(self, handler: BatchProcessingHandler, app_controller=None, parent=None):
        super().__init__(parent)
        self.handler = handler
        self.app_controller = app_controller
        self._processing_started = False  # 跟踪处理状态
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """设置批处理UI组件"""
        # 创建子组件，但不添加到布局中
        # 这些组件将由MainWindow直接使用
        
        # 创建作业列表面板
        self.job_list_panel = JobListPanel(self.handler)
        
        # 创建作业详情面板
        self.job_detail_panel = JobDetailPanel(self.handler)
        
        # 创建图像池面板
        self.image_pool_panel = ImagePoolPanel(self.handler)
        
        # 创建导出设置面板
        # 尝试从app_controller获取配置访问器
        config_accessor = None
        if self.app_controller and hasattr(self.app_controller, 'get_core_service_adapter'):
            core_adapter = self.app_controller.get_core_service_adapter()
            if core_adapter and hasattr(core_adapter, 'get_config_accessor'):
                config_accessor = core_adapter.get_config_accessor()
        
        self.export_settings_panel = ExportSettingsPanel(self.handler, config_accessor, self.app_controller)
        self.export_settings_panel.setMaximumWidth(350)  # 限制最大宽度
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 连接JobSelectionManager的信号（统一的选择管理）
        self.handler.job_selection_manager.selection_changed.connect(self._on_job_selected)
        
        # 连接图像池面板的信号
        self.image_pool_panel.add_to_job_requested.connect(self._on_add_to_job_requested)
        self.image_pool_panel.add_all_to_job_requested.connect(self._on_add_all_to_job_requested)
        
        # 连接导出设置面板的信号
        self.export_settings_panel.process_requested.connect(self._on_process_requested)
        
        # 连接处理器的作业处理信号
        self.handler.job_processing_finished.connect(self._on_job_processing_finished)
        
        # 连接JobExecutionManager的信号来管理处理状态
        self.handler.job_execution_manager.job_processing_started.connect(self._on_job_processing_started)
        self.handler.job_execution_manager.all_jobs_cancelled.connect(self._on_all_jobs_cancelled)
        
    # --- 槽函数 ---
    
    @pyqtSlot(str)
    def _on_job_selected(self, job_id: str):
        """处理作业选择变更"""
        if job_id:
            self.job_detail_panel.set_job(job_id)
        else:
            self.job_detail_panel.clear_display()
    
    @pyqtSlot(list)
    def _on_add_to_job_requested(self, indices: List[int]):
        """将选中的图像添加到当前作业"""
        selected_job = self.handler.get_selected_job()
        if selected_job:
            count = self.handler.add_pool_items_to_job(selected_job.job_id, indices)
            if count > 0:
                self.job_detail_panel.update_display()
    
        else:
            self.handler.show_error_message.emit("请先选择一个作业")
    
    @pyqtSlot()
    def _on_add_all_to_job_requested(self):
        """将所有图像添加到作业"""
        # 检查是否可以添加到作业
        if not self.handler.can_add_to_job():
            if self.handler.is_pool_empty():
                self.handler.show_error_message.emit("图像池为空，无法添加到作业")
            else:
                self.handler.show_error_message.emit("请先选择一个作业")
            return
        
        # 调用处理器的方法
        job = self.handler.add_all_pool_items_to_selected_job()
        
        # 如果成功添加，更新UI
        if job:
            # 确保作业详情面板更新
            self.job_detail_panel.update_display()
    
    @pyqtSlot()
    def _on_process_requested(self):
        """处理并导出所有作业"""
        try:
            # 使用带进度显示的批处理方法
            success = self.handler.start_processing_with_progress(self)
            if not success:
                # 如果启动失败，确保UI状态正确
                self._processing_started = False
                self.export_settings_panel.set_processing_state(False)
        except Exception as e:
            # 处理异常情况
            self._processing_started = False
            self.export_settings_panel.set_processing_state(False)
            QMessageBox.critical(self, "错误", f"启动批处理时发生错误: {str(e)}")
    
    @pyqtSlot(str)
    def _on_job_processing_started(self, job_id: str):
        """处理作业开始处理事件"""
        # 只在第一个作业开始时设置处理状态
        if not hasattr(self, '_processing_started') or not self._processing_started:
            self._processing_started = True
            self.export_settings_panel.set_processing_state(True)
    
    @pyqtSlot(str, bool, str)
    def _on_job_processing_finished(self, job_id: str, success: bool, message: str):
        """处理作业完成事件"""
        # 检查是否还有其他作业在处理
        active_jobs_count = self.handler.get_active_jobs_count()
        if active_jobs_count == 0:
            # 所有作业都已完成
            self._processing_started = False
            self.export_settings_panel.set_processing_state(False)
        
        # 更新作业列表和详情显示
        self.job_list_panel.update_jobs_display()
    

    
    @pyqtSlot()
    def _on_all_jobs_cancelled(self):
        """处理所有作业取消事件"""
        self._processing_started = False
        self.export_settings_panel.set_processing_state(False)
        
        # 更新作业列表和详情显示
        self.job_list_panel.update_jobs_display()
        self.job_detail_panel.update_display()