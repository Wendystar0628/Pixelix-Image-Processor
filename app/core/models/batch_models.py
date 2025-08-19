"""
批处理模型模块

定义了批处理相关的数据模型类。
"""
from dataclasses import dataclass, field
from enum import Enum
import os
from typing import List, Dict, Optional, Any

import numpy as np

from app.core.operations.base_operation import ImageOperation
from app.core.models.export_config import ExportConfig


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