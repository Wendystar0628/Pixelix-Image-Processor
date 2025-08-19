"""
业务层图像处理器接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import numpy as np

from app.core.operations.base_operation import ImageOperation


class BusinessImageProcessorInterface(ABC):
    """
    业务层图像处理器接口
    
    定义了纯业务逻辑的图像处理能力，完全无状态，不依赖任何上层组件。
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
    
    @abstractmethod
    def apply_single_operation(
        self,
        image: np.ndarray,
        operation: ImageOperation,
        scale_factor: float = 1.0
    ) -> np.ndarray:
        """
        应用单个图像操作
        
        Args:
            image: 输入图像
            operation: 要应用的操作
            scale_factor: 缩放因子
            
        Returns:
            处理后的图像
        """
        pass