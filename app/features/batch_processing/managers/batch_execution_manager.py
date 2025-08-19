"""
作业执行管理器模块

此模块定义了ExecutionManager类，负责管理批处理作业的执行。
"""
from typing import List, Dict, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from .batch_job_manager import JobManager
from ..batch_job_models import BatchJob, BatchJobStatus
from ..batch_processing_worker import BatchProcessingWorker
from app.handlers.file_handler import FileHandler
from app.layers.business.processing.image_processor import ImageProcessor


class ExecutionManager(QObject):
    """
    作业执行管理器
    
    职责：
    - 管理作业的执行
    - 协调工作线程
    - 处理作业状态更新
    """
    
    # 信号：作业处理开始
    job_processing_started = pyqtSignal(str)  # job_id
    
    # 信号：作业处理完成
    job_processing_finished = pyqtSignal(str, bool, str)  # job_id, success, message
    
    # 信号：文件处理进度
    job_file_progress = pyqtSignal(str, str, int, int)  # job_id, file_name, current, total
    
    # 信号：处理信息
    processing_info = pyqtSignal(str, str)  # job_id, info
    
    # 信号：作业进度更新
    job_progress_updated = pyqtSignal(str, int)  # job_id, percentage
    
    # 信号：作业已取消
    job_cancelled = pyqtSignal(str)  # job_id
    
    # 信号：所有作业已取消
    all_jobs_cancelled = pyqtSignal()
    
    def __init__(self, job_manager: JobManager, file_handler: FileHandler, 
                 image_processor: ImageProcessor):
        """
        初始化执行管理器
        
        Args:
            job_manager: 作业管理器实例
            file_handler: 文件处理器实例
            image_processor: 图像处理器实例
        """
        super().__init__()
        self.job_manager = job_manager
        self.file_handler = file_handler
        self.image_processor = image_processor
        
        # 工作线程管理
        self.workers: Dict[str, BatchProcessingWorker] = {}
        self.worker_threads: Dict[str, QThread] = {}
        self.cancelled_jobs: set = set()
        self.is_cancelling_all = False
    
    def start_processing(self) -> bool:
        """
        开始处理所有待处理作业
        
        Returns:
            bool: 是否成功启动处理
        """
        pending_jobs = self.job_manager.get_pending_jobs()
        
        if not pending_jobs:
            self.processing_info.emit("system", "没有待处理的作业")
            return False
        
        # 启动每个待处理作业
        started_count = 0
        for job in pending_jobs:
            if self._start_job_processing(job):
                started_count += 1
        
        if started_count > 0:
            return True
        else:
            self.processing_info.emit("system", "没有作业可以启动")
            return False
    
    def _start_job_processing(self, job: BatchJob) -> bool:
        """
        启动单个作业的处理
        
        Args:
            job: 要处理的作业
            
        Returns:
            bool: 是否成功启动
        """
        if job.job_id in self.workers:
            return False  # 作业已在处理中
        
        if not job.source_paths:
            self.processing_info.emit(job.job_id, "作业没有源文件，跳过处理")
            return False
        
        if not job.operations:
            self.processing_info.emit(job.job_id, "作业没有操作流水线，跳过处理")
            return False
        
        # 创建工作线程和工作器
        thread = QThread()
        worker = BatchProcessingWorker()
        
        # 移动工作器到线程
        worker.moveToThread(thread)
        
        # 连接信号
        worker.progress_updated.connect(self._on_job_progress_updated)
        worker.job_finished.connect(self._on_job_finished)
        worker.file_progress.connect(self.job_file_progress)
        worker.processing_info.connect(self.processing_info)
        
        # 连接线程信号
        thread.started.connect(lambda: self._process_job_in_thread(worker, job))
        thread.finished.connect(thread.deleteLater)
        
        # 存储引用
        self.workers[job.job_id] = worker
        self.worker_threads[job.job_id] = thread
        
        # 更新作业状态
        self.job_manager.update_job_status(job.job_id, BatchJobStatus.PROCESSING, 0)
        
        # 启动线程
        thread.start()
        
        # 发出开始信号
        self.job_processing_started.emit(job.job_id)
        
        return True
    
    def _process_job_in_thread(self, worker: BatchProcessingWorker, job: BatchJob):
        """
        在线程中处理作业
        
        Args:
            worker: 工作器实例
            job: 要处理的作业
        """
        # 获取导出配置
        export_config = job.export_config or self.job_manager.get_default_export_config()
        
        # 处理作业
        worker.process_job(
            job.job_id,
            job.name,  # 传递作业名称用于创建子文件夹
            job.source_paths,
            job.operations,
            export_config,
            self.file_handler,
            self.image_processor
        )
    
    def _on_job_progress_updated(self, job_id: str, progress: int):
        """
        处理作业进度更新
        
        Args:
            job_id: 作业ID
            progress: 进度百分比
        """
        self.job_manager.update_job_status(job_id, BatchJobStatus.PROCESSING, progress)
        # 发出进度更新信号
        self.job_progress_updated.emit(job_id, progress)
    
    def _on_job_finished(self, job_id: str, success: bool, message: str):
        """
        处理作业完成
        
        Args:
            job_id: 作业ID
            success: 是否成功
            message: 结果消息
        """
        # 更新作业状态
        final_status = BatchJobStatus.COMPLETED if success else BatchJobStatus.FAILED
        self.job_manager.update_job_status(job_id, final_status, 100 if success else None, message)
        
        # 清理资源
        self._cleanup_job_resources(job_id)
        
        # 发出完成信号
        self.job_processing_finished.emit(job_id, success, message)
    
    def _cleanup_job_resources(self, job_id: str):
        """
        清理作业资源
        
        Args:
            job_id: 作业ID
        """
        # 停止并清理线程
        if job_id in self.worker_threads:
            thread = self.worker_threads[job_id]
            if thread.isRunning():
                thread.quit()
                thread.wait(5000)  # 等待最多5秒
            del self.worker_threads[job_id]
        
        # 清理工作器
        if job_id in self.workers:
            del self.workers[job_id]
        
        # 从取消列表中移除
        self.cancelled_jobs.discard(job_id)
    
    def cancel_processing(self, job_id: str) -> None:
        """
        取消处理指定作业
        
        Args:
            job_id: 作业ID
        """
        if job_id not in self.workers:
            return
        
        # 标记为已取消
        self.cancelled_jobs.add(job_id)
        
        # 请求工作器取消
        worker = self.workers[job_id]
        worker.cancel()
        
        # 更新作业状态
        self.job_manager.update_job_status(job_id, BatchJobStatus.CANCELLED, None, "用户取消")
        
        # 发出作业取消信号
        self.job_cancelled.emit(job_id)
        
        self.processing_info.emit(job_id, "正在取消作业...")
    
    def cancel_all_processing(self) -> None:
        """取消所有正在处理的作业"""
        if not self.workers:
            self.all_jobs_cancelled.emit()
            return
        
        self.is_cancelling_all = True
        
        # 取消所有正在运行的作业
        for job_id in list(self.workers.keys()):
            self.cancel_processing(job_id)
        
        self.processing_info.emit("system", "正在取消所有作业...")
        
        # 发出所有作业已取消信号
        self.all_jobs_cancelled.emit()
    
    def get_active_jobs(self) -> List[str]:
        """
        获取当前活跃的作业ID列表
        
        Returns:
            List[str]: 活跃作业ID列表
        """
        return list(self.workers.keys())
    
    def is_job_running(self, job_id: str) -> bool:
        """
        检查作业是否正在运行
        
        Args:
            job_id: 作业ID
            
        Returns:
            bool: 如果作业正在运行则返回True
        """
        return job_id in self.workers
    
    def get_running_jobs_count(self) -> int:
        """
        获取正在运行的作业数量
        
        Returns:
            int: 正在运行的作业数量
        """
        return len(self.workers)