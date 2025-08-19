import numpy as np
import cv2
from typing import Dict, Any
from .spatial_filter_base import SpatialFilterOperation


class GaussianBlurFilterOp(SpatialFilterOperation):
    """高斯模糊滤波操作"""
    
    def __init__(self, sigma_x: float = 1.0, sigma_y: float = 1.0, kernel_size: int = 5):
        """初始化高斯模糊滤波
        
        Args:
            sigma_x: X方向标准差
            sigma_y: Y方向标准差  
            kernel_size: 核大小
        """
        super().__init__()
        self.sigma_x = max(0.1, sigma_x)
        self.sigma_y = max(0.1, sigma_y)
        self.kernel_size = kernel_size
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用高斯模糊滤波"""
        image = self._ensure_valid_image(image)
        kernel_size = self._validate_kernel_size(self.kernel_size, image.shape)
        
        # 应用高斯模糊
        blurred = cv2.GaussianBlur(
            image, 
            (kernel_size, kernel_size), 
            sigmaX=self.sigma_x,
            sigmaY=self.sigma_y
        )
        
        return blurred
    
    def get_params(self) -> Dict[str, Any]:
        """获取操作参数"""
        return {
            "sigma_x": self.sigma_x,
            "sigma_y": self.sigma_y,
            "kernel_size": self.kernel_size
        }
    
    def serialize(self) -> Dict[str, Any]:
        """序列化操作"""
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }