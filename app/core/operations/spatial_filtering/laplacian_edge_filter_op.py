import numpy as np
import cv2
from typing import Dict, Any
from .spatial_filter_base import SpatialFilterOperation


class LaplacianEdgeFilterOp(SpatialFilterOperation):
    """拉普拉斯边缘检测操作"""
    
    def __init__(self, kernel_size: int = 3, scale: float = 1.0, delta: float = 0.0):
        """初始化拉普拉斯边缘检测
        
        Args:
            kernel_size: 核大小
            scale: 缩放因子
            delta: 偏移量
        """
        super().__init__()
        self.kernel_size = kernel_size
        self.scale = scale
        self.delta = delta
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用拉普拉斯边缘检测"""
        image = self._ensure_valid_image(image)
        kernel_size = self._validate_kernel_size(self.kernel_size, image.shape)
        
        # 转换为灰度图进行边缘检测
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 应用拉普拉斯算子
        laplacian = cv2.Laplacian(
            gray, 
            cv2.CV_64F, 
            ksize=kernel_size,
            scale=self.scale,
            delta=self.delta
        )
        
        # 转换为绝对值并归一化
        laplacian = np.absolute(laplacian)
        laplacian = np.clip(laplacian, 0, 255).astype(np.uint8)
        
        # 转换回3通道
        result = np.stack([laplacian] * 3, axis=-1)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        """获取操作参数"""
        return {
            "kernel_size": self.kernel_size,
            "scale": self.scale,
            "delta": self.delta
        }
    
    def serialize(self) -> Dict[str, Any]:
        """序列化操作"""
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }