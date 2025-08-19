import numpy as np
from typing import Dict, Any
from .base_operation import ImageOperation


class BrightnessContrastOp(ImageOperation):
    """
    调整图像的亮度和对比度。
    """

    def __init__(self, brightness: int = 0, contrast: int = 0):
        """
        初始化亮度/对比度操作。

        Args:
            brightness (int): 亮度调整值，范围通常为 -255 到 255。
            contrast (int): 对比度调整值，范围通常为 -255 到 255。
        """
        self.brightness = brightness
        self.contrast = contrast

    def apply(self, image: np.ndarray) -> np.ndarray:
        """
        应用亮度和对比度调整。

        算法参考自 GIMP/Photoshop 的亮度-对比度工具。
        公式: new_value = (old_value - 128) * factor + 128 + brightness
        """
        # 使用浮点数进行计算以保持精度
        img_float = image.astype(np.float32)

        # 调整对比度
        # 将对比度值从 [-255, 255] 映射到更合适的乘数因子
        if self.contrast > 0:
            factor = 259 * (self.contrast + 259) / (259 * (259 - self.contrast))
        else:
            factor = (self.contrast + 259) / 259
        
        adjusted_contrast = (img_float - 128) * factor + 128

        # 调整亮度
        adjusted_brightness = adjusted_contrast + self.brightness

        # 将像素值裁剪到 [0, 255] 范围，并转换回8位无符号整数
        adjusted_image = np.clip(adjusted_brightness, 0, 255).astype(np.uint8)

        return adjusted_image
        
    def get_params(self) -> Dict[str, Any]:
        """
        获取此操作的参数。
        
        Returns:
            Dict[str, Any]: 包含操作参数的字典。
        """
        return {
            "brightness": self.brightness,
            "contrast": self.contrast
        } 
        
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