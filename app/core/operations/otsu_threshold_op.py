import cv2
import numpy as np
from typing import Dict, Any
from .base_operation import ImageOperation


class OtsuThresholdOp(ImageOperation):
    """
    使用Otsu方法自动计算阈值并应用阈值处理。
    """

    def __init__(self):
        """
        初始化大津法自动阈值操作。
        """
        pass

    def apply(self, image: np.ndarray) -> np.ndarray:
        """
        应用Otsu阈值处理。

        Args:
            image: 输入图像。

        Returns:
            阈值处理后的图像。
        """
        # 如果是彩色图像，先转换为灰度
        if len(image.shape) > 2:
            gray = np.dot(image[..., :3], [0.114, 0.587, 0.299])
            gray = gray.astype(np.uint8)
        else:
            gray = image

        # 应用Otsu阈值
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 如果原始图像是彩色的，则将结果转换回彩色格式
        if len(image.shape) > 2:
            binary = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

        return binary
        
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