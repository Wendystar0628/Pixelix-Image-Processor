import numpy as np
import cv2
from typing import Dict, Any
from .regular_filter_base import RegularFilterOperation


class EmbossFilterOp(RegularFilterOperation):
    """浮雕滤镜操作"""
    
    # 8个方向的浮雕核
    EMBOSS_KERNELS = [
        np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]]),    # 0: 右下
        np.array([[-1, 0, 1], [-2, 1, 2], [-1, 0, 1]]),    # 1: 右
        np.array([[0, 1, 2], [-1, 1, 1], [-2, -1, 0]]),    # 2: 右上
        np.array([[1, 2, 1], [0, 1, 0], [-1, -2, -1]]),    # 3: 上
        np.array([[2, 1, 0], [1, 1, -1], [0, -1, -2]]),    # 4: 左上
        np.array([[1, 0, -1], [2, 1, -2], [1, 0, -1]]),    # 5: 左
        np.array([[0, -1, -2], [1, 1, -1], [2, 1, 0]]),    # 6: 左下
        np.array([[-1, -2, -1], [0, 1, 0], [1, 2, 1]])     # 7: 下
    ]
    
    def __init__(self, direction: int = 0, depth: float = 1.0):
        """初始化浮雕滤镜
        
        Args:
            direction: 浮雕方向 (0-7)
            depth: 浮雕深度
        """
        super().__init__()
        self.direction = max(0, min(7, direction))
        self.depth = max(0.1, depth)
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用浮雕滤镜"""
        image = self._ensure_valid_image(image)
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 应用浮雕核
        kernel = self.EMBOSS_KERNELS[self.direction] * self.depth
        embossed = cv2.filter2D(gray, cv2.CV_32F, kernel)
        
        # 添加偏移并归一化
        embossed = embossed + 128
        embossed = np.clip(embossed, 0, 255).astype(np.uint8)
        
        # 转换回3通道
        result = np.stack([embossed] * 3, axis=-1)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        """获取操作参数"""
        return {
            "direction": self.direction,
            "depth": self.depth
        }
    
    def serialize(self) -> Dict[str, Any]:
        """序列化操作"""
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }