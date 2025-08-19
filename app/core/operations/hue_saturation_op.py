import cv2
import numpy as np
from typing import Dict, Any
from .base_operation import ImageOperation


class HueSaturationOp(ImageOperation):
    """
    色相/饱和度调整操作。
    
    允许用户调整图像的色相、饱和度和明度。
    """

    def __init__(
        self,
        hue: int = 0,
        saturation: int = 0,
        lightness: int = 0,
        colorize: bool = False,
        colorize_hue: int = 0,
        colorize_saturation: int = 50,
    ):
        """
        初始化色相/饱和度调整操作。

        Args:
            hue: 色相调整值，范围[-180, 180]，表示色相环上的偏移量。
            saturation: 饱和度调整值，范围[-100, 100]，正值增加饱和度，负值减少饱和度。
            lightness: 明度调整值，范围[-100, 100]，正值增加明度，负值减少明度。
            colorize: 是否启用着色模式，True表示启用。
            colorize_hue: 着色模式下的色相值，范围[0, 360]。
            colorize_saturation: 着色模式下的饱和度值，范围[0, 100]。
        """
        self.hue = max(-180, min(180, hue))
        self.saturation = max(-100, min(100, saturation))
        self.lightness = max(-100, min(100, lightness))
        self.colorize = colorize
        self.colorize_hue = max(0, min(360, colorize_hue))
        self.colorize_saturation = max(0, min(100, colorize_saturation))

    def apply(self, image: np.ndarray) -> np.ndarray:
        """
        应用色相/饱和度调整。

        Args:
            image: 输入图像。

        Returns:
            调整后的图像。
        """
        # 确保输入图像是BGR格式
        if image.ndim != 3 or image.shape[2] != 3:
            # 如果是灰度图像，转换为BGR
            if image.ndim == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            else:
                # 不支持的格式，直接返回原图
                return image

        # 将图像转换为HSV颜色空间
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)

        if self.colorize:
            # 着色模式：替换所有像素的色相，并应用指定的饱和度
            hsv_image[:, :, 0] = self.colorize_hue / 2.0  # OpenCV的H通道范围是[0, 180]
            hsv_image[:, :, 1] = self.colorize_saturation * 2.55  # 转换为[0, 255]范围
        else:
            # 调整色相
            hsv_image[:, :, 0] = (hsv_image[:, :, 0] + self.hue / 2.0) % 180  # 色相是循环的

            # 调整饱和度
            if self.saturation > 0:
                # 增加饱和度
                factor = 1 + self.saturation / 100.0
                hsv_image[:, :, 1] = hsv_image[:, :, 1] * factor
            else:
                # 减少饱和度
                factor = 1 + self.saturation / 100.0  # factor < 1
                hsv_image[:, :, 1] = hsv_image[:, :, 1] * factor

        # 调整明度（值）
        if self.lightness > 0:
            # 增加明度
            factor = 1 + self.lightness / 100.0
            hsv_image[:, :, 2] = hsv_image[:, :, 2] * factor
        else:
            # 减少明度
            factor = 1 + self.lightness / 100.0  # factor < 1
            hsv_image[:, :, 2] = hsv_image[:, :, 2] * factor

        # 裁剪值到有效范围
        hsv_image[:, :, 0] = np.clip(hsv_image[:, :, 0], 0, 179)  # H: [0, 179]
        hsv_image[:, :, 1] = np.clip(hsv_image[:, :, 1], 0, 255)  # S: [0, 255]
        hsv_image[:, :, 2] = np.clip(hsv_image[:, :, 2], 0, 255)  # V: [0, 255]

        # 转换回BGR颜色空间
        result = cv2.cvtColor(hsv_image.astype(np.uint8), cv2.COLOR_HSV2BGR)

        return result 
        
    def get_params(self) -> Dict[str, Any]:
        """
        获取此操作的参数。
        
        Returns:
            Dict[str, Any]: 包含操作参数的字典。
        """
        return {
            "hue": self.hue,
            "saturation": self.saturation,
            "lightness": self.lightness,
            "colorize": self.colorize,
            "colorize_hue": self.colorize_hue,
            "colorize_saturation": self.colorize_saturation
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