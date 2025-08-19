import numpy as np
from abc import abstractmethod
from typing import Dict, Any
from ..base_operation import ImageOperation


class SpatialFilterOperation(ImageOperation):
    """空间滤波操作抽象基类"""
    
    def __init__(self):
        """初始化空间滤波操作"""
        pass
    
    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用空间滤波操作"""
        pass
    
    def _validate_kernel_size(self, kernel_size: int, image_shape: tuple) -> int:
        """验证并调整核大小"""
        if kernel_size <= 0:
            kernel_size = 3
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # 确保核大小不超过图像尺寸
        min_dim = min(image_shape[:2])
        if kernel_size > min_dim:
            kernel_size = min_dim if min_dim % 2 == 1 else min_dim - 1
            
        return max(kernel_size, 3)
    
    def _ensure_valid_image(self, image: np.ndarray) -> np.ndarray:
        """确保图像格式有效"""
        if image is None or image.size == 0:
            raise ValueError("输入图像无效")
        
        if len(image.shape) == 2:
            # 灰度图像转为3通道
            image = np.stack([image] * 3, axis=-1)
        elif len(image.shape) == 3 and image.shape[2] == 4:
            # RGBA转RGB
            image = image[:, :, :3]
            
        return image.astype(np.uint8)