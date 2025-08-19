import numpy as np
import cv2
from typing import Dict, Any
from .spatial_filter_base import SpatialFilterOperation


class SharpenFilterOp(SpatialFilterOperation):
    """锐化滤波操作"""
    
    def __init__(self, strength: float = 1.0, radius: float = 1.0, threshold: float = 0.0):
        """初始化锐化滤波
        
        Args:
            strength: 锐化强度
            radius: 锐化半径
            threshold: 锐化阈值
        """
        super().__init__()
        self.strength = max(0.0, strength)
        self.radius = max(0.1, radius)
        self.threshold = max(0.0, threshold)
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用锐化滤波"""
        image = self._ensure_valid_image(image)
        
        if self.strength == 0.0:
            return image
        
        # 创建高斯模糊版本
        kernel_size = int(self.radius * 6) + 1
        if kernel_size % 2 == 0:
            kernel_size += 1
        kernel_size = self._validate_kernel_size(kernel_size, image.shape)
        
        blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), self.radius)
        
        # 计算锐化掩码
        mask = image.astype(np.float32) - blurred.astype(np.float32)
        
        # 应用阈值
        if self.threshold > 0:
            mask = np.where(np.abs(mask) < self.threshold, 0, mask)
        
        # 应用锐化
        sharpened = image.astype(np.float32) + self.strength * mask
        
        # 裁剪到有效范围
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
        
        return sharpened
    
    def get_params(self) -> Dict[str, Any]:
        """获取操作参数"""
        return {
            "strength": self.strength,
            "radius": self.radius,
            "threshold": self.threshold
        }
    
    def serialize(self) -> Dict[str, Any]:
        """序列化操作"""
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }