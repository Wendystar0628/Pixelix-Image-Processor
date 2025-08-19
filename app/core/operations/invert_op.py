import cv2
import numpy as np
from typing import Dict, Any
from .base_operation import ImageOperation


class InvertOp(ImageOperation):
    """反转图像颜色。"""

    def __init__(self):
        """
        初始化反相操作。
        """
        pass

    def apply(self, image: np.ndarray) -> np.ndarray:
        """
        反转图像颜色。

        Args:
            image: 输入图像。

        Returns:
            反转颜色后的图像。
        """
        return 255 - image
        
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