"""
批处理进度管理器模块

负责管理批处理的进度显示、状态跟踪和进度对话框的生命周期。
"""
from typing import Dict, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget

from .batch_execution_manager import ExecutionManager
from .batch_job_manager import JobManager
from app.core.models.progress_models import BatchProgressState
from app.ui.dialogs.batch_progress_dialog import BatchProgressDialog


class ProgressManager(QObject):
    """
    批处理进度管理器
    
    职责：
    - 管理进度状态和计算
    - 处理进度对话框的生命周期
    - 协调进度相关的信号处理
    """
    
    # 定义信号
    show_info_message = pyqtSignal(str)
    
    def __init__(self, job_execution_manager: ExecutionManager, 
                 job_manager: JobManager, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.job_execution_manager = job_execution_manager
        self.job_manager = job_manager
        
        # 进度状态管理
        self.progress_state = BatchProgressState()
        self.job_progress_map: Dict[str, int] = {}  # job_id -> percentage
        self.job_file_counts: Dict[str, int] = {}  # job_id -> total_files
        
        # 进度对话框
        self.progress_dialog: Optional[BatchProgressDialog] = None
    
    def start_processing_with_progress(self, parent_widget: Optional[QWidget] = None) -> bool:
        """
        启动带进度显示的批处理
        
        Args:
            parent_widget: 父窗口部件，用于进度对话框的父窗口
            
        Returns:
            bool: 是否成功启动处理
        """
        # 初始化进度状态
        self._initialize_progress_state()
        
        # 创建并显示进度对话框
        self.progress_dialog = self._create_and_show_progress_dialog(parent_widget)
        
        # 连接进度信号
        self._connect_progress_signals(self.progress_dialog)
        
        # 启动批处理
        if not self.job_execution_manager.start_processing():
            # 如果启动失败，清理对话框和状态
            self._cleanup_progress_dialog()
            self._reset_progress_state()
            return False
        
        # 以模态方式显示对话框
        try:
            self.progress_dialog.exec()
        finally:
            # 确保在对话框关闭后清理资源
            self._cleanup_progress_dialog()
            self._reset_progress_state()
        
        return True
    
    def _create_and_show_progress_dialog(self, parent_widget: Optional[QWidget]) -> BatchProgressDialog:
        """
        创建并显示进度对话框
        
        Args:
            parent_widget: 父窗口部件
            
        Returns:
            BatchProgressDialog: 创建的进度对话框实例
        """
        # 创建进度对话框
        dialog = BatchProgressDialog(parent_widget)
        
        # 连接取消信号
        dialog.cancel_requested.connect(self._on_progress_cancel_requested)
        
        return dialog
    
    def _connect_progress_signals(self, dialog: BatchProgressDialog) -> None:
        """
        连接进度相关信号
        
        Args:
            dialog: 进度对话框实例
        """
        # 连接JobExecutionManager的信号到进度状态管理
        self.job_execution_manager.job_processing_started.connect(self._on_job_started_for_progress)
        self.job_execution_manager.job_processing_finished.connect(self._on_job_finished_for_progress)
        self.job_execution_manager.job_file_progress.connect(self._on_file_progress_for_state)
        self.job_execution_manager.job_progress_updated.connect(self._on_job_progress_for_state)
        
        # 连接取消相关信号
        self.job_execution_manager.job_cancelled.connect(self._on_job_cancelled)
        self.job_execution_manager.all_jobs_cancelled.connect(self._on_all_jobs_cancelled)
        
        # 连接JobExecutionManager的信号到进度对话框
        self.job_execution_manager.job_processing_finished.connect(dialog.on_job_finished)
        self.job_execution_manager.job_file_progress.connect(dialog.update_file_progress)
        self.job_execution_manager.job_progress_updated.connect(dialog.update_job_progress)
        self.job_execution_manager.processing_info.connect(self._on_processing_info_for_dialog)
    
    def _on_job_started_for_progress(self, job_id: str) -> None:
        """
        处理作业开始事件，用于进度显示
        
        Args:
            job_id: 作业ID
        """
        # 更新进度状态
        self._update_job_progress_state(job_id, 0)
        
        if self.progress_dialog:
            # 初始化作业进度为0%
            self.progress_dialog.update_job_progress(job_id, 0)
    
    def _on_job_progress_for_state(self, job_id: str, percentage: int) -> None:
        """
        处理作业进度更新，用于状态管理
        
        Args:
            job_id: 作业ID
            percentage: 进度百分比
        """
        self._update_job_progress_state(job_id, percentage)
    
    def _on_file_progress_for_state(self, job_id: str, file_name: str, current: int, total: int) -> None:
        """
        处理文件进度更新，用于状态管理
        
        Args:
            job_id: 作业ID
            file_name: 当前处理的文件名
            current: 当前文件索引
            total: 总文件数
        """
        self._update_file_progress_state(job_id, file_name, current, total)
    
    def _on_processing_info_for_dialog(self, job_id: str, info: str) -> None:
        """
        处理处理信息，转发给进度对话框
        
        Args:
            job_id: 作业ID
            info: 信息内容
        """
        # 如果是错误信息，添加到进度对话框
        if self.progress_dialog and ("失败" in info or "错误" in info or "异常" in info):
            self.progress_dialog.add_processing_error(f"{job_id}: {info}")
    
    def _on_job_cancelled(self, job_id: str) -> None:
        """
        处理单个作业取消事件
        
        Args:
            job_id: 被取消的作业ID
        """
        # 更新进度状态中的取消标记
        self.progress_state.is_cancelled = True
        
        # 设置作业进度为100%（表示处理完成，虽然是取消）
        if job_id in self.job_progress_map:
            self.job_progress_map[job_id] = 100
        
        # 重新计算整体进度
        self._calculate_overall_progress()
    
    def _on_all_jobs_cancelled(self) -> None:
        """
        处理所有作业取消事件
        """
        # 更新进度状态
        self.progress_state.is_cancelled = True
        self.progress_state.overall_percentage = 100
        
        # 更新对话框状态
        if self.progress_dialog:
            self.progress_dialog.is_processing = False
            self.progress_dialog.is_cancelling = True
            self.progress_dialog.status_label.setText("批处理已取消")
            self.progress_dialog.close_button.setEnabled(True)
            self.progress_dialog.cancel_button.setEnabled(False)
    
    def _on_progress_cancel_requested(self) -> None:
        """
        处理进度对话框的取消请求
        """
        # 检查是否已经在取消中
        if self.progress_state.is_cancelled:
            return
        
        # 更新进度状态
        self.progress_state.is_cancelled = True
        
        # 更新对话框状态为取消中
        if self.progress_dialog:
            self.progress_dialog.is_cancelling = True
            self.progress_dialog.status_label.setText("正在取消...")
            self.progress_dialog.cancel_button.setEnabled(False)
            self.progress_dialog.detail_label.setText("正在安全停止所有处理任务...")
        
        # 取消所有正在处理的作业
        self.job_execution_manager.cancel_all_processing()
        
        # 发出信息消息
        self.show_info_message.emit("正在取消批处理任务...")
    
    def _cleanup_progress_dialog(self) -> None:
        """
        清理进度对话框资源
        """
        if self.progress_dialog:
            # 断开信号连接
            try:
                # 断开状态管理相关信号
                self.job_execution_manager.job_processing_started.disconnect(self._on_job_started_for_progress)
                self.job_execution_manager.job_processing_finished.disconnect(self._on_job_finished_for_progress)
                self.job_execution_manager.job_file_progress.disconnect(self._on_file_progress_for_state)
                self.job_execution_manager.job_progress_updated.disconnect(self._on_job_progress_for_state)
                
                # 断开取消相关信号
                self.job_execution_manager.job_cancelled.disconnect(self._on_job_cancelled)
                self.job_execution_manager.all_jobs_cancelled.disconnect(self._on_all_jobs_cancelled)
                
                # 断开对话框相关信号
                self.job_execution_manager.job_processing_finished.disconnect(self.progress_dialog.on_job_finished)
                self.job_execution_manager.job_file_progress.disconnect(self.progress_dialog.update_file_progress)
                self.job_execution_manager.job_progress_updated.disconnect(self.progress_dialog.update_job_progress)
                self.job_execution_manager.processing_info.disconnect(self._on_processing_info_for_dialog)
            except TypeError:
                # 信号可能已经断开，忽略错误
                pass
            
            # 清空引用
            self.progress_dialog = None
    
    # --- 进度状态管理和汇总逻辑 ---
    
    def _initialize_progress_state(self) -> None:
        """初始化进度状态"""
        # 获取所有待处理的作业
        pending_jobs = self.job_manager.get_pending_jobs()
        
        # 重置进度状态
        self.progress_state.reset()
        self.job_progress_map.clear()
        self.job_file_counts.clear()
        
        # 设置总作业数
        self.progress_state.total_jobs = len(pending_jobs)
        
        # 初始化每个作业的进度和文件数
        for job in pending_jobs:
            self.job_progress_map[job.job_id] = 0
            self.job_file_counts[job.job_id] = len(job.source_paths) if job.source_paths else 0
    
    def _update_job_progress_state(self, job_id: str, percentage: int) -> None:
        """
        更新单个作业的进度状态
        
        Args:
            job_id: 作业ID
            percentage: 进度百分比
        """
        # 更新作业进度
        self.job_progress_map[job_id] = percentage
        
        # 更新当前作业信息
        job = self.job_manager.get_job(job_id)
        if job:
            self.progress_state.current_job_id = job_id
            self.progress_state.current_job_name = job.name
        
        # 计算整体进度
        self._calculate_overall_progress()
    
    def _update_file_progress_state(self, job_id: str, file_name: str, current: int, total: int) -> None:
        """
        更新文件处理进度状态
        
        Args:
            job_id: 作业ID
            file_name: 当前处理的文件名
            current: 当前文件索引
            total: 总文件数
        """
        # 更新当前文件信息
        self.progress_state.current_file = file_name
        self.progress_state.current_file_index = current
        self.progress_state.total_files_in_job = total
        
        # 更新作业的文件总数（如果不一致）
        if job_id in self.job_file_counts and self.job_file_counts[job_id] != total:
            self.job_file_counts[job_id] = total
    
    def _on_job_finished_for_progress(self, job_id: str, success: bool, message: str) -> None:
        """
        处理作业完成事件，更新进度状态
        
        Args:
            job_id: 作业ID
            success: 是否成功
            message: 结果消息
        """
        # 设置作业进度为100%
        self.job_progress_map[job_id] = 100
        
        # 更新完成作业计数
        if success:
            self.progress_state.completed_jobs += 1
        
        # 计算整体进度
        self._calculate_overall_progress()
        
        # 检查是否所有作业都已完成
        if self._is_all_jobs_finished():
            self._on_all_jobs_finished()
    
    def _calculate_overall_progress(self) -> None:
        """计算整体进度百分比"""
        if not self.job_progress_map:
            self.progress_state.overall_percentage = 0
            return
        
        # 计算所有作业的平均进度
        total_progress = sum(self.job_progress_map.values())
        self.progress_state.overall_percentage = total_progress // len(self.job_progress_map)
    
    def _is_all_jobs_finished(self) -> bool:
        """检查是否所有作业都已完成"""
        return all(progress >= 100 for progress in self.job_progress_map.values())
    
    def _on_all_jobs_finished(self) -> None:
        """所有作业完成时的处理"""
        self.progress_state.overall_percentage = 100
        
        # 清空当前处理信息
        self.progress_state.current_job_id = None
        self.progress_state.current_job_name = None
        self.progress_state.current_file = None
    
    def _reset_progress_state(self) -> None:
        """重置进度状态"""
        self.progress_state.reset()
        self.job_progress_map.clear()
        self.job_file_counts.clear()
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """
        获取进度摘要信息
        
        Returns:
            Dict[str, Any]: 包含进度摘要的字典
        """
        return {
            'total_jobs': self.progress_state.total_jobs,
            'completed_jobs': self.progress_state.completed_jobs,
            'overall_percentage': self.progress_state.overall_percentage,
            'current_job_name': self.progress_state.current_job_name,
            'current_file': self.progress_state.current_file,
            'current_file_progress': f"{self.progress_state.current_file_index}/{self.progress_state.total_files_in_job}" if self.progress_state.total_files_in_job > 0 else "",
            'is_cancelled': self.progress_state.is_cancelled
        }
    
    def is_processing_cancelled(self) -> bool:
        """
        检查批处理是否已被取消
        
        Returns:
            bool: 如果已取消返回True，否则返回False
        """
        return self.progress_state.is_cancelled