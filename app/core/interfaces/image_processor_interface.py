"""
图像处理服务接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import numpy as np

from ..operations.base_operation import ImageOperation


class ImageProcessorInterface(ABC):
    """
    图像处理服务的抽象接口
    
    定义了图像处理的核心能力，包括操作流水线渲染等功能。
    实现类负责具体的图像处理逻辑。
    """
    
    @abstractmethod
    def render_pipeline(
        self,
        base_image: Optional[np.ndarray],
        pipeline: List[ImageOperation],
        preview_op_params: Optional[Dict] = None,
        scale_factor: float = 1.0,
    ) -> np.ndarray:
        """
        渲染图像操作流水线
        
        Args:
            base_image: 基础图像数组
            pipeline: 操作流水线列表
            preview_op_params: 预览操作参数
            scale_factor: 缩放因子
            
        Returns:
            处理后的图像数组
        """
        pass