"""
批处理作业管理器模块

此模块定义了JobManager类，它是批处理作业的唯一管理者。
它作为一个数据模型层，完全独立于UI，负责存储和管理所有批处理作业及其状态。
"""
import os
from typing import List, Dict, Optional, Any, Type

from PyQt6.QtCore import QObject, pyqtSignal

from ..batch_job_models import BatchJob, BatchJobStatus
from app.core.operations.base_operation import ImageOperation
from app.core.models.export_config import ExportConfig
import numpy as np


class JobManager(QObject):
    """
    批处理作业管理器，是批处理作业队列的唯一管理者。
    
    职责：
    - 管理批处理作业列表
    - 提供添加、删除、更新作业的方法
    - 发出作业列表变更和作业状态更新的信号
    """
    
    # 信号：当作业列表发生变化时发出（添加、删除、清空等）
    job_list_changed = pyqtSignal()
    
    # 信号：当某个作业的状态或进度发生变化时发出，参数为job_id
    job_updated = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._jobs: List[BatchJob] = []
        self._default_export_config = ExportConfig()
    
    # --- 作业管理方法 ---
    
    def add_job(self, name: str, operations: Optional[List[ImageOperation]] = None) -> BatchJob:
        """
        添加新的批处理作业
        
        Args:
            name: 作业名称
            operations: 操作流水线，可选
            
        Returns:
            BatchJob: 创建的作业对象
        """
        # 生成唯一的作业ID
        job_id = self._generate_job_id(name)
        
        # 创建新作业
        job = BatchJob(
            job_id=job_id,
            name=name,
            operations=operations if operations is not None else []
        )
        
        # 添加到作业列表
        self._jobs.append(job)
        
        # 发出信号
        self.job_list_changed.emit()
        
        return job
    
    def remove_job(self, job_id: str) -> bool:
        """
        移除批处理作业
        
        Args:
            job_id: 作业ID
            
        Returns:
            bool: 如果作业存在并被成功移除则返回True，否则返回False
        """
        # 查找作业
        job = self.get_job(job_id)
        if job is None:
            return False
        
        # 从列表中移除
        self._jobs.remove(job)
        
        # 发出信号
        self.job_list_changed.emit()
        
        return True
    
    def clear_jobs(self) -> int:
        """
        清空所有批处理作业
        
        Returns:
            int: 清除的作业数量
        """
        count = len(self._jobs)
        
        if count > 0:
            self._jobs.clear()
            # 发出信号
            self.job_list_changed.emit()
        
        return count
    
    def clear_completed_jobs(self) -> int:
        """
        清除所有已完成的作业
        
        Returns:
            int: 清除的作业数量
        """
        completed_jobs = [job for job in self._jobs 
                        if job.status in (BatchJobStatus.COMPLETED, BatchJobStatus.FAILED)]
        count = len(completed_jobs)
        
        if count > 0:
            for job in completed_jobs:
                self._jobs.remove(job)
            # 发出信号
            self.job_list_changed.emit()
        
        return count
    
    def get_job(self, job_id: str) -> Optional[BatchJob]:
        """
        根据ID获取作业
        
        Args:
            job_id: 作业ID
            
        Returns:
            Optional[BatchJob]: 如果找到则返回作业对象，否则返回None
        """
        for job in self._jobs:
            if job.job_id == job_id:
                return job
        return None
    
    def get_job_by_name(self, name: str) -> Optional[BatchJob]:
        """
        根据名称获取作业
        
        Args:
            name: 作业名称
            
        Returns:
            Optional[BatchJob]: 如果找到则返回作业对象，否则返回None
        """
        for job in self._jobs:
            if job.name == name:
                return job
        return None
    
    def get_all_jobs(self) -> List[BatchJob]:
        """
        获取所有作业的副本
        
        Returns:
            List[BatchJob]: 所有作业的列表副本
        """
        return self._jobs.copy()
    
    def get_pending_jobs(self) -> List[BatchJob]:
        """
        获取所有待处理的作业
        
        Returns:
            List[BatchJob]: 待处理作业的列表
        """
        return [job for job in self._jobs if job.status == BatchJobStatus.PENDING]
    
    def rename_job(self, job_id: str, new_name: str) -> bool:
        """
        重命名作业
        
        Args:
            job_id: 作业ID
            new_name: 新名称
            
        Returns:
            bool: 如果作业存在并且重命名成功则返回True，否则返回False
        """
        job = self.get_job(job_id)
        if job is None:
            return False
        
        # 检查新名称是否已存在
        if any(j.name == new_name and j.job_id != job_id for j in self._jobs):
            return False
        
        # 重命名
        job.name = new_name
        
        # 发出信号
        self.job_updated.emit(job_id)
        self.job_list_changed.emit()
        
        return True
    
    # --- 作业源文件管理 ---
    
    def notify_job_updated(self, job_id: str) -> bool:
        """
        手动通知作业已更新
        
        Args:
            job_id: 作业ID
            
        Returns:
            bool: 如果作业存在则返回True，否则返回False
        """
        job = self.get_job(job_id)
        if job is None:
            return False
            
        # 发出信号
        self.job_updated.emit(job_id)
        return True
        
    def add_sources_to_job(self, job_id: str, file_paths: List[str]) -> int:
        """
        向作业添加源文件
        
        Args:
            job_id: 作业ID
            file_paths: 源文件路径列表
            
        Returns:
            int: 成功添加的文件数量
        """
        job = self.get_job(job_id)
        if job is None:
            return 0
        
        added_count = 0
        for path in file_paths:
            if path not in job.source_paths:
                job.source_paths.append(path)
                added_count += 1
        
        return added_count
    
    def remove_sources_from_job(self, job_id: str, indices: List[int]) -> int:
        """
        从作业中移除源文件
        
        Args:
            job_id: 作业ID
            indices: 要移除的源文件索引列表
            
        Returns:
            int: 成功移除的文件数量
        """
        job = self.get_job(job_id)
        if job is None or not indices:
            return 0
        
        # 按照索引从大到小排序，以避免删除时索引变化问题
        sorted_indices = sorted(indices, reverse=True)
        
        removed_count = 0
        for idx in sorted_indices:
            if 0 <= idx < len(job.source_paths):
                job.source_paths.pop(idx)
                removed_count += 1
        
        if removed_count > 0:
            # 发出信号
            self.job_updated.emit(job_id)
        
        return removed_count
    
    def clear_job_sources(self, job_id: str) -> int:
        """
        清空作业的所有源文件
        
        Args:
            job_id: 作业ID
            
        Returns:
            int: 清除的源文件数量
        """
        job = self.get_job(job_id)
        if job is None:
            return 0
        
        count = len(job.source_paths)
        
        if count > 0:
            job.source_paths.clear()
            # 发出信号
            self.job_updated.emit(job_id)
        
        return count
    
    # --- 作业状态管理 ---
    
    def update_job_status(self, job_id: str, status: BatchJobStatus, 
                         progress: Optional[int] = None,
                         message: Optional[str] = None) -> bool:
        """
        更新作业状态
        
        Args:
            job_id: 作业ID
            status: 新状态
            progress: 新进度，可选
            message: 结果消息，可选
            
        Returns:
            bool: 如果作业存在并且更新成功则返回True，否则返回False
        """
        job = self.get_job(job_id)
        if job is None:
            return False
        
        # 更新状态
        job.status = status
        
        # 更新进度（如果提供）
        if progress is not None:
            job.progress = max(0, min(100, progress))  # 确保在0-100范围内
        
        # 更新消息（如果提供）
        if message is not None:
            job.result_message = message
        
        # 发出信号
        self.job_updated.emit(job_id)
        
        return True
    
    # --- 缩略图管理 ---
    
    def add_thumbnail(self, job_id: str, file_path: str, thumbnail: np.ndarray) -> bool:
        """
        添加或更新作业中源文件的缩略图
        
        Args:
            job_id: 作业ID
            file_path: 源文件路径
            thumbnail: 缩略图数据
            
        Returns:
            bool: 如果成功则返回True，否则返回False
        """
        job = self.get_job(job_id)
        if job is None or file_path not in job.source_paths:
            return False
        
        # 添加或更新缩略图
        job.thumbnails[file_path] = thumbnail
        
        return True
    
    # --- 操作管理 ---
    
    def set_job_operations(self, job_id: str, operations: List[ImageOperation]) -> bool:
        """
        设置作业的操作流水线
        
        Args:
            job_id: 作业ID
            operations: 操作流水线
            
        Returns:
            bool: 如果作业存在并且设置成功则返回True，否则返回False
        """
        job = self.get_job(job_id)
        if job is None:
            return False
        
        # 设置操作流水线
        job.operations = operations.copy() if operations else []
        
        # 发出信号
        self.job_updated.emit(job_id)
        
        return True
    
    # --- 导出配置管理 ---
    
    def set_job_export_config(self, job_id: str, export_config: ExportConfig) -> bool:
        """
        设置作业的导出配置
        
        Args:
            job_id: 作业ID
            export_config: 导出配置
            
        Returns:
            bool: 如果作业存在并且设置成功则返回True，否则返回False
        """
        job = self.get_job(job_id)
        if job is None:
            return False
        
        # 设置导出配置
        job.export_config = export_config
        
        # 发出信号
        self.job_updated.emit(job_id)
        
        return True
    
    def set_default_export_config(self, export_config: ExportConfig) -> None:
        """
        设置默认导出配置
        
        Args:
            export_config: 导出配置
        """
        self._default_export_config = export_config
    
    def get_default_export_config(self) -> ExportConfig:
        """
        获取默认导出配置的副本
        
        Returns:
            ExportConfig: 默认导出配置的副本
        """
        return self._default_export_config
    

    
    def get_job_analysis_data(self, job_id: str) -> Optional[Dict]:
        """
        获取作业的分析数据
        
        Args:
            job_id: 作业ID
            
        Returns:
            Optional[Dict]: 分析数据，如果作业不存在则返回None
        """
        job = self.get_job(job_id)
        if job is None:
            return None
        
        return job.get_analysis_results()
    
    # --- 其他方法 ---
    
    def _generate_job_id(self, name: str) -> str:
        """
        根据作业名称生成唯一的作业ID
        
        Args:
            name: 作业名称
            
        Returns:
            str: 唯一的作业ID
        """
        import uuid
        import re
        
        # 将名称转换为安全的字符串
        safe_name = re.sub(r'[^\w\-_]', '_', name)
        
        # 结合UUID生成唯一ID
        return f"{safe_name}_{uuid.uuid4().hex[:8]}"