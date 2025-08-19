"""
批处理功能模块数据模型

定义了批处理相关的数据模型类，包括作业管理和分析导出功能。
"""
from dataclasses import dataclass, field
from enum import Enum
import os
from typing import List, Dict, Optional, Any, Union
import time

import numpy as np

from app.core.operations.base_operation import ImageOperation
from app.core.models.export_config import ExportConfig
# JobInfo 应该在本地定义或从其他地方导入


class BatchJobStatus(Enum):
    """批处理作业状态枚举"""
    PENDING = "pending"        # 等待处理
    PROCESSING = "processing"  # 正在处理
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败
    CANCELLED = "cancelled"    # 已取消











class BatchItem:
    """
    批处理项类，表示一个需要处理的文件项。
    """
    def __init__(self, file_path: str):
        """
        初始化批处理项
        
        Args:
            file_path: 文件路径
        """
        self.file_path = file_path
        self.thumbnail = None
        self.analysis_data: Optional[Dict[str, Any]] = None
        
    def load_thumbnail(self, max_size: int = 100) -> Optional[np.ndarray]:
        """
        加载缩略图
        
        Args:
            max_size: 缩略图最大尺寸
            
        Returns:
            Optional[np.ndarray]: 缩略图数据，如果加载失败则返回None
        """
        from app.utils.image_utils import load_image_safely
        
        if not os.path.exists(self.file_path):
            return None
            
        try:
            # 加载图像
            image = load_image_safely(self.file_path)
            if image is None:
                return None
                
            # 计算缩放比例
            h, w = image.shape[:2]
            scale = min(max_size / w, max_size / h)
            
            # 如果图像已经小于最大尺寸，不需要缩放
            if scale >= 1:
                self.thumbnail = image
                return image
                
            # 缩放图像
            import cv2
            new_w = int(w * scale)
            new_h = int(h * scale)
            self.thumbnail = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            
            return self.thumbnail
        except Exception as e:
            print(f"加载缩略图失败: {e}")
            return None
    
    def set_analysis_data(self, analysis_data: Dict[str, Any]):
        """设置分析数据"""
        self.analysis_data = analysis_data
    
    def get_analysis_data(self) -> Optional[Dict[str, Any]]:
        """获取分析数据"""
        return self.analysis_data


@dataclass
class BatchJob:
    """
    批处理作业数据类，表示一个需要处理的批处理作业。
    """
    job_id: str                                # 作业的唯一标识符
    name: str                                  # 作业名称
    status: BatchJobStatus = BatchJobStatus.PENDING  # 作业状态
    progress: int = 0                          # 作业进度(0-100)
    source_paths: List[str] = field(default_factory=list)  # 源文件路径列表
    operations: List[ImageOperation] = field(default_factory=list)  # 操作流水线
    export_config: Optional[ExportConfig] = None  # 导出配置
    result_message: str = ""                   # 结果消息
    thumbnails: Dict[str, np.ndarray] = field(default_factory=dict)  # 源文件缩略图
    

    
    # 时间戳
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    # 资源需求（实现JobInfo接口）
    estimated_memory_mb: int = 512
    estimated_cpu_cores: int = 1
    estimated_duration_seconds: float = 60.0
    
    def get_resource_requirements(self) -> Dict[str, Any]:
        """获取资源需求（实现JobInfo接口）"""
        # 根据文件数量和操作复杂度估算资源需求
        file_count = len(self.source_paths)
        operation_count = len(self.operations)
        
        # 基础内存需求
        base_memory = 256
        # 每个文件大约需要50MB内存
        file_memory = file_count * 50
        # 每个操作大约需要额外20MB内存
        operation_memory = operation_count * 20
        
        estimated_memory = base_memory + file_memory + operation_memory
        
        # CPU需求基于并发处理能力
        estimated_cpu = min(4, max(1, file_count // 10))
        
        # 时间估算：每个文件每个操作大约1秒
        estimated_time = file_count * operation_count * 1.0
        
        return {
            'memory_mb': estimated_memory,
            'cpu_cores': estimated_cpu,
            'duration_seconds': estimated_time,
            'disk_mb': file_count * 100  # 估算输出文件大小
        }
    

    
    def start_processing(self):
        """开始处理"""
        self.status = BatchJobStatus.PROCESSING
        self.started_at = time.time()
        self.progress = 0
    
    def complete_processing(self, success: bool = True, message: str = ""):
        """完成处理"""
        self.status = BatchJobStatus.COMPLETED if success else BatchJobStatus.FAILED
        self.completed_at = time.time()
        self.progress = 100 if success else self.progress
        self.result_message = message
    
    def cancel_processing(self):
        """取消处理"""
        self.status = BatchJobStatus.CANCELLED
        self.completed_at = time.time()
        self.result_message = "作业已取消"
    
    def update_progress(self, progress: int):
        """更新进度"""
        self.progress = max(0, min(100, progress))
    
    def get_duration(self) -> Optional[float]:
        """获取处理时长"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return time.time() - self.started_at
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'job_id': self.job_id,
            'name': self.name,
            'status': self.status.value,
            'progress': self.progress,
            'source_paths': self.source_paths,
            'operations': [str(op) for op in self.operations],  # 简化操作序列化
            'export_config': self.export_config.to_dict() if self.export_config else None,
            'result_message': self.result_message,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'estimated_memory_mb': self.estimated_memory_mb,
            'estimated_cpu_cores': self.estimated_cpu_cores,
            'estimated_duration_seconds': self.estimated_duration_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatchJob':
        """从字典创建作业"""
        job = cls(
            job_id=data['job_id'],
            name=data['name'],
            status=BatchJobStatus(data.get('status', BatchJobStatus.PENDING.value)),
            progress=data.get('progress', 0),
            source_paths=data.get('source_paths', []),
            result_message=data.get('result_message', ''),
            created_at=data.get('created_at', time.time()),
            started_at=data.get('started_at'),
            completed_at=data.get('completed_at'),
            estimated_memory_mb=data.get('estimated_memory_mb', 512),
            estimated_cpu_cores=data.get('estimated_cpu_cores', 1),
            estimated_duration_seconds=data.get('estimated_duration_seconds', 60.0)
        )
        
        # 恢复导出配置
        if data.get('export_config'):
            job.export_config = ExportConfig.from_dict(data['export_config'])
        

        
        return job


@dataclass
class BatchProcessingStats:
    """批处理统计信息"""
    total_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    cancelled_jobs: int = 0
    total_files_processed: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    
    def add_job_result(self, job: BatchJob):
        """添加作业结果到统计"""
        self.total_jobs += 1
        
        if job.status == BatchJobStatus.COMPLETED:
            self.completed_jobs += 1
            self.total_files_processed += len(job.source_paths)
            
            duration = job.get_duration()
            if duration:
                self.total_processing_time += duration
                self.average_processing_time = self.total_processing_time / self.completed_jobs
                
        elif job.status == BatchJobStatus.FAILED:
            self.failed_jobs += 1
        elif job.status == BatchJobStatus.CANCELLED:
            self.cancelled_jobs += 1
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_jobs == 0:
            return 0.0
        return (self.completed_jobs / self.total_jobs) * 100
    
    @property
    def failure_rate(self) -> float:
        """失败率"""
        if self.total_jobs == 0:
            return 0.0
        return (self.failed_jobs / self.total_jobs) * 100