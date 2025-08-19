import numpy as np
import cv2
from typing import Dict, Any
from .spatial_filter_base import SpatialFilterOperation


class MeanFilterOp(SpatialFilterOperation):
    """均值滤波操作"""
    
    def __init__(self, kernel_size: int = 5):
        """初始化均值滤波
        
        Args:
            kernel_size: 核大小
        """
        super().__init__()
        self.kernel_size = kernel_size
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用均值滤波"""
        image = self._ensure_valid_image(image)
        kernel_size = self._validate_kernel_size(self.kernel_size, image.shape)
        
        # 应用均值滤波
        filtered = cv2.blur(image, (kernel_size, kernel_size))
        
        return filtered
    
    def get_params(self) -> Dict[str, Any]:
        """获取操作参数"""
        return {
            "kernel_size": self.kernel_size
        }
    
    def serialize(self) -> Dict[str, Any]:
        """序列化操作"""
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }