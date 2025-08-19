import numpy as np
import cv2
from typing import Dict, Any
from .spatial_filter_base import SpatialFilterOperation


class SobelEdgeFilterOp(SpatialFilterOperation):
    """Sobel边缘检测操作"""
    
    def __init__(self, dx: int = 1, dy: int = 1, kernel_size: int = 3, 
                 scale: float = 1.0, delta: float = 0.0):
        """初始化Sobel边缘检测
        
        Args:
            dx: X方向导数阶数
            dy: Y方向导数阶数
            kernel_size: 核大小
            scale: 缩放因子
            delta: 偏移量
        """
        super().__init__()
        self.dx = max(0, dx)
        self.dy = max(0, dy)
        self.kernel_size = kernel_size
        self.scale = scale
        self.delta = delta
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用Sobel边缘检测"""
        image = self._ensure_valid_image(image)
        kernel_size = self._validate_kernel_size(self.kernel_size, image.shape)
        
        # 转换为灰度图进行边缘检测
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 应用Sobel算子
        sobel = cv2.Sobel(
            gray,
            cv2.CV_64F,
            dx=self.dx,
            dy=self.dy,
            ksize=kernel_size,
            scale=self.scale,
            delta=self.delta
        )
        
        # 转换为绝对值并归一化
        sobel = np.absolute(sobel)
        sobel = np.clip(sobel, 0, 255).astype(np.uint8)
        
        # 转换回3通道
        result = np.stack([sobel] * 3, axis=-1)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        """获取操作参数"""
        return {
            "dx": self.dx,
            "dy": self.dy,
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