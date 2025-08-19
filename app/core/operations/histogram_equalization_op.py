import cv2
import numpy as np
from typing import Dict, Any
from .base_operation import ImageOperation


class HistogramEqualizationOp(ImageOperation):
    """
    直方图均衡化操作，增强图像对比度。
    """

    def __init__(self):
        """
        初始化直方图均衡化操作。
        """
        pass

    def apply(self, image: np.ndarray) -> np.ndarray:
        """
        应用直方图均衡化。

        Args:
            image: 输入图像。

        Returns:
            直方图均衡化后的图像。
        """
        # 如果是彩色图像，在HSV空间中只对V通道进行均衡化
        if len(image.shape) == 3 and image.shape[2] == 3:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            hsv[..., 2] = cv2.equalizeHist(hsv[..., 2])
            return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        else:
            # 灰度图像直接均衡化
            return cv2.equalizeHist(image)
            
    def get_params(self) -> Dict[str, Any]:
        """
        获取此操作的参数。
        
        Returns:
            Dict[str, Any]: 包含操作参数的字典。
        """
        return {}
        
    def serialize(self) -> Dict[str, Any]:
        """
        将此操作序列化为字典，用于保存到预设中。
        
        Returns:
            Dict[str, Any]: 包含操作类型和参数的字典。
        """
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }