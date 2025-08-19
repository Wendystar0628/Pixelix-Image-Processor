"""
进度相关的数据模型

定义批处理进度跟踪相关的数据结构。
"""
from typing import Optional
from dataclasses import dataclass


@dataclass
class BatchProgressState:
    """
    批处理进度状态
    
    用于跟踪批处理任务的整体进度和当前状态信息。
    """
    total_jobs: int = 0
    completed_jobs: int = 0
    current_job_id: Optional[str] = None
    current_job_name: Optional[str] = None
    current_file: Optional[str] = None
    current_file_index: int = 0
    total_files_in_job: int = 0
    overall_percentage: int = 0
    is_cancelled: bool = False
    
    def reset(self) -> None:
        """重置进度状态到初始值"""
        self.total_jobs = 0
        self.completed_jobs = 0
        self.current_job_id = None
        self.current_job_name = None
        self.current_file = None
        self.current_file_index = 0
        self.total_files_in_job = 0
        self.overall_percentage = 0
        self.is_cancelled = False
    
    def is_completed(self) -> bool:
        """检查是否所有作业都已完成"""
        return self.completed_jobs >= self.total_jobs and self.total_jobs > 0
    
    def get_completion_rate(self) -> float:
        """获取完成率 (0.0 - 1.0)"""
        if self.total_jobs == 0:
            return 0.0
        return self.completed_jobs / self.total_jobs