"""
作业选择管理器模块

此模块定义了JobSelectionManager类，负责管理当前选中的作业状态，
确保作业列表中始终有选中项（如果存在作业），处理作业删除时的选择逻辑。
"""
from typing import Optional, List
from dataclasses import dataclass

from PyQt6.QtCore import QObject, pyqtSignal

from ..batch_job_models import BatchJob
from .batch_job_manager import JobManager


@dataclass
class JobSelectionState:
    """作业选择状态数据结构"""
    selected_job_id: Optional[str] = None
    last_selected_job_id: Optional[str] = None
    
    def update_selection(self, job_id: Optional[str]) -> None:
        """更新选择状态"""
        if self.selected_job_id != job_id:
            self.last_selected_job_id = self.selected_job_id
            self.selected_job_id = job_id
    
    def get_fallback_selection(self, available_jobs: List[BatchJob]) -> Optional[str]:
        """获取备选选择"""
        if not available_jobs:
            return None
        
        # 优先选择上次选中的作业
        if self.last_selected_job_id:
            for job in available_jobs:
                if job.job_id == self.last_selected_job_id:
                    return self.last_selected_job_id
        
        # 否则选择第一个作业
        return available_jobs[0].job_id


class JobSelectionManager(QObject):
    """
    作业选择管理器
    
    职责：
    - 管理当前选中的作业状态
    - 确保作业列表中始终有选中项（如果存在作业）
    - 处理作业删除时的自动选择逻辑
    - 提供选择状态的一致性保证
    """
    
    # 信号：当选中的作业发生变化时发出
    selection_changed = pyqtSignal(str)  # job_id
    
    # 信号：当选择状态需要更新时发出（用于UI同步）
    selection_update_requested = pyqtSignal(str)  # job_id
    
    def __init__(self, job_manager: JobManager):
        """
        初始化作业选择管理器
        
        Args:
            job_manager: 作业管理器实例
        """
        super().__init__()
        self.job_manager = job_manager
        self._state = JobSelectionState()
        
        # 连接作业管理器的信号
        self.job_manager.job_list_changed.connect(self._on_job_list_changed)
    
    def set_selected_job(self, job_id: str) -> bool:
        """
        设置选中的作业
        
        Args:
            job_id: 作业ID
            
        Returns:
            bool: 是否成功设置
        """
        # 验证作业是否存在
        job = self.job_manager.get_job(job_id)
        if job is None:
            return False
        
        # 更新选择状态
        old_selection = self._state.selected_job_id
        self._state.update_selection(job_id)
        
        # 如果选择发生变化，发出信号
        if old_selection != job_id:
            self.selection_changed.emit(job_id)
        
        return True
    
    def get_selected_job(self) -> Optional[BatchJob]:
        """
        获取当前选中的作业
        
        Returns:
            Optional[BatchJob]: 当前选中的作业，如果没有选中则返回None
        """
        if self._state.selected_job_id:
            return self.job_manager.get_job(self._state.selected_job_id)
        return None
    
    def get_selected_job_id(self) -> Optional[str]:
        """
        获取当前选中的作业ID
        
        Returns:
            Optional[str]: 当前选中的作业ID，如果没有选中则返回None
        """
        return self._state.selected_job_id
    
    def handle_job_deletion(self, deleted_job_id: str) -> Optional[str]:
        """
        处理作业删除时的选择逻辑
        
        Args:
            deleted_job_id: 被删除的作业ID
            
        Returns:
            Optional[str]: 新选中的作业ID，如果没有可选作业则返回None
        """
        # 如果删除的不是当前选中的作业，不需要处理
        if self._state.selected_job_id != deleted_job_id:
            return self._state.selected_job_id
        
        # 获取剩余的作业列表
        available_jobs = self.job_manager.get_all_jobs()
        
        # 获取备选选择
        new_selection = self._state.get_fallback_selection(available_jobs)
        
        # 更新选择状态
        self._state.update_selection(new_selection)
        
        # 发出信号
        if new_selection:
            self.selection_changed.emit(new_selection)
            self.selection_update_requested.emit(new_selection)
        else:
            # 没有可选作业，发出空字符串信号
            self.selection_changed.emit("")
            self.selection_update_requested.emit("")
        
        return new_selection
    
    def ensure_selection_consistency(self) -> None:
        """
        确保选择状态的一致性
        
        如果当前选中的作业不存在，自动选择一个可用的作业
        """
        current_job = self.get_selected_job()
        
        # 如果当前选中的作业存在，不需要处理
        if current_job is not None:
            return
        
        # 获取可用的作业列表
        available_jobs = self.job_manager.get_all_jobs()
        
        if available_jobs:
            # 选择第一个作业
            new_selection = available_jobs[0].job_id
            self._state.update_selection(new_selection)
            self.selection_changed.emit(new_selection)
            self.selection_update_requested.emit(new_selection)
        else:
            # 没有可用作业，清除选择并发出信号
            old_selection = self._state.selected_job_id
            self._state.update_selection(None)
            if old_selection is not None:
                # 发出空字符串信号表示没有选中作业
                self.selection_changed.emit("")
                self.selection_update_requested.emit("")
    
    def handle_job_creation(self, new_job_id: str) -> bool:
        """
        处理新作业创建时的选择逻辑
        
        Args:
            new_job_id: 新创建的作业ID
            
        Returns:
            bool: 是否自动选中了新作业
        """
        # 验证作业是否存在
        job = self.job_manager.get_job(new_job_id)
        if job is None:
            return False
        
        # 自动选中新创建的作业
        old_selection = self._state.selected_job_id
        self._state.update_selection(new_job_id)
        
        # 发出信号
        if old_selection != new_job_id:
            self.selection_changed.emit(new_job_id)
            self.selection_update_requested.emit(new_job_id)
        
        return True
    
    def clear_selection(self) -> None:
        """清除当前选择"""
        if self._state.selected_job_id:
            self._state.update_selection(None)
    
    def has_selection(self) -> bool:
        """
        检查是否有选中的作业
        
        Returns:
            bool: 如果有选中的作业则返回True
        """
        return self._state.selected_job_id is not None
    
    def _on_job_list_changed(self) -> None:
        """
        处理作业列表变化事件
        
        确保选择状态的一致性
        """
        self.ensure_selection_consistency()
    
    def get_selection_state(self) -> JobSelectionState:
        """
        获取选择状态的副本（用于调试和测试）
        
        Returns:
            JobSelectionState: 选择状态的副本
        """
        return JobSelectionState(
            selected_job_id=self._state.selected_job_id,
            last_selected_job_id=self._state.last_selected_job_id
        )