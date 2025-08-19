"""
作业效果管理器模块

此模块定义了JobEffectsManager类，负责管理每个作业的独立效果配置，
提供效果的应用、清除、隔离功能，处理作业删除时的效果清理。
"""
from typing import List, Dict, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from app.core.operations.base_operation import ImageOperation
from app.core.managers.state_manager import StateManager
from ..batch_job_models import BatchJob, BatchJobStatus
from .batch_job_manager import JobManager


class JobEffectsManager(QObject):
    """
    作业效果管理器
    
    职责：
    - 管理每个作业的独立效果配置
    - 提供效果的应用、清除、隔离功能
    - 处理作业删除时的效果清理
    - 从StateManager获取当前效果并应用到作业
    """
    
    # 信号：当作业效果发生变化时发出
    job_effects_changed = pyqtSignal(str)  # job_id
    
    # 信号：当效果被清除时发出
    job_effects_cleared = pyqtSignal(str)  # job_id
    
    def __init__(self, job_manager: JobManager, state_manager: StateManager):
        """
        初始化作业效果管理器
        
        Args:
            job_manager: 作业管理器实例
            state_manager: 状态管理器实例
        """
        super().__init__()
        self.job_manager = job_manager
        self.state_manager = state_manager
        
        # 连接作业管理器的信号
        self.job_manager.job_list_changed.connect(self._on_job_list_changed)
    
    def apply_current_effects_to_job(self, job_id: str) -> int:
        """
        将当前主视图的效果应用到指定作业
        
        Args:
            job_id: 目标作业ID
            
        Returns:
            int: 应用的效果数量
        """
        # 验证作业是否存在
        job = self.job_manager.get_job(job_id)
        if job is None:
            return 0
        
        # 从StateManager获取当前操作流水线的副本
        current_operations = self.state_manager.pipeline_manager.clone_pipeline()
        if not current_operations:
            return 0
        
        # 设置作业的操作流水线
        if self.job_manager.set_job_operations(job_id, current_operations):
            # 更新作业状态为待处理
            self.job_manager.update_job_status(job_id, BatchJobStatus.PENDING, 0)
            
            # 发出信号
            self.job_effects_changed.emit(job_id)
            
            return len(current_operations)
        
        return 0
    
    def clear_job_effects(self, job_id: str) -> bool:
        """
        清除指定作业的所有效果
        
        Args:
            job_id: 目标作业ID
            
        Returns:
            bool: 是否成功清除
        """
        # 验证作业是否存在
        job = self.job_manager.get_job(job_id)
        if job is None:
            return False
        
        # 清除作业的操作流水线
        if self.job_manager.set_job_operations(job_id, []):
            # 重置作业状态
            self.job_manager.update_job_status(job_id, BatchJobStatus.PENDING, 0, "")
            
            # 发出信号
            self.job_effects_cleared.emit(job_id)
            
            return True
        
        return False
    
    def get_job_effects(self, job_id: str) -> List[ImageOperation]:
        """
        获取指定作业的效果列表
        
        Args:
            job_id: 作业ID
            
        Returns:
            List[ImageOperation]: 效果列表的副本
        """
        job = self.job_manager.get_job(job_id)
        if job is None:
            return []
        
        return job.operations.copy() if job.operations else []
    
    def get_job_effects_count(self, job_id: str) -> int:
        """
        获取指定作业的效果数量
        
        Args:
            job_id: 作业ID
            
        Returns:
            int: 效果数量
        """
        job = self.job_manager.get_job(job_id)
        if job is None:
            return 0
        
        return len(job.operations) if job.operations else 0
    
    def has_job_effects(self, job_id: str) -> bool:
        """
        检查指定作业是否有效果
        
        Args:
            job_id: 作业ID
            
        Returns:
            bool: 如果作业有效果则返回True
        """
        return self.get_job_effects_count(job_id) > 0
    
    def copy_effects_between_jobs(self, source_job_id: str, target_job_id: str) -> bool:
        """
        在作业之间复制效果
        
        Args:
            source_job_id: 源作业ID
            target_job_id: 目标作业ID
            
        Returns:
            bool: 是否成功复制
        """
        # 获取源作业的效果
        source_effects = self.get_job_effects(source_job_id)
        if not source_effects:
            return False
        
        # 验证目标作业是否存在
        target_job = self.job_manager.get_job(target_job_id)
        if target_job is None:
            return False
        
        # 设置目标作业的操作流水线
        if self.job_manager.set_job_operations(target_job_id, source_effects):
            # 更新目标作业状态为待处理
            self.job_manager.update_job_status(target_job_id, BatchJobStatus.PENDING, 0)
            
            # 发出信号
            self.job_effects_changed.emit(target_job_id)
            
            return True
        
        return False
    
    def cleanup_job_effects(self, job_id: str) -> None:
        """
        清理指定作业的效果资源
        
        Args:
            job_id: 作业ID
        """
        # 这个方法在作业删除时被调用，确保效果相关的资源被清理
        # 由于效果存储在作业对象中，作业删除时会自动清理
        # 这里主要是为了扩展性，可以在未来添加额外的清理逻辑
        
        # 发出清理信号（如果需要的话）
        self.job_effects_cleared.emit(job_id)
    
    def get_all_jobs_with_effects(self) -> List[str]:
        """
        获取所有有效果的作业ID列表
        
        Returns:
            List[str]: 有效果的作业ID列表
        """
        jobs_with_effects = []
        
        for job in self.job_manager.get_all_jobs():
            if self.has_job_effects(job.job_id):
                jobs_with_effects.append(job.job_id)
        
        return jobs_with_effects
    
    def get_effects_summary(self) -> Dict[str, int]:
        """
        获取所有作业的效果摘要
        
        Returns:
            Dict[str, int]: 作业ID到效果数量的映射
        """
        summary = {}
        
        for job in self.job_manager.get_all_jobs():
            effects_count = self.get_job_effects_count(job.job_id)
            if effects_count > 0:
                summary[job.job_id] = effects_count
        
        return summary
    
    def validate_job_effects(self, job_id: str) -> bool:
        """
        验证作业效果的有效性
        
        Args:
            job_id: 作业ID
            
        Returns:
            bool: 如果效果有效则返回True
        """
        effects = self.get_job_effects(job_id)
        
        # 检查每个效果是否有效
        for effect in effects:
            if not isinstance(effect, ImageOperation):
                return False
            
            # 可以添加更多的验证逻辑
            # 例如检查效果的参数是否有效等
        
        return True
    
    def _on_job_list_changed(self) -> None:
        """
        处理作业列表变化事件
        
        当作业被删除时，相关的效果会自动清理
        """
        # 获取当前所有作业的ID
        current_job_ids = {job.job_id for job in self.job_manager.get_all_jobs()}
        
        # 这里可以添加额外的清理逻辑，比如清理孤立的效果数据
        # 但由于效果存储在作业对象中，作业删除时会自动清理
        pass
    
    def reset_all_effects(self) -> int:
        """
        重置所有作业的效果
        
        Returns:
            int: 被重置的作业数量
        """
        reset_count = 0
        
        for job in self.job_manager.get_all_jobs():
            if self.clear_job_effects(job.job_id):
                reset_count += 1
        
        return reset_count