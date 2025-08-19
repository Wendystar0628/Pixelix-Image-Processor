import cv2
import numpy as np
from typing import Dict, Any
from .base_operation import ImageOperation


class GrayscaleOp(ImageOperation):
    """
    将图像转换为灰度图像。
    """

    def __init__(self):
        """
        初始化灰度转换操作。
        """
        pass

    def apply(self, image: np.ndarray) -> np.ndarray:
        """
        将图像转换为灰度图像。

        Args:
            image (np.ndarray): 输入的彩色图像。

        Returns:
            np.ndarray: 转换后的灰度图像。
        """
        # 检查图像是否已经是灰度的
        if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
            return image

        # 使用OpenCV的灰度转换公式: Y = 0.299*R + 0.587*G + 0.114*B
        gray = np.dot(image[..., :3], [0.114, 0.587, 0.299])
        return gray.astype(np.uint8)
        
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