import cv2
import numpy as np
from typing import Dict, Any
from .base_operation import ImageOperation


class LevelsOp(ImageOperation):
    """
    色阶调整操作。
    
    允许用户调整图像的输入色阶（黑场、灰场、白场）和输出色阶。
    """

    def __init__(
        self,
        channel: int = 0,  # 0: RGB, 1: R, 2: G, 3: B
        input_black: int = 0,
        input_gamma: float = 1.0,
        input_white: int = 255,
        output_black: int = 0,
        output_white: int = 255,
    ):
        """
        初始化色阶调整操作。

        Args:
            channel: 要调整的通道，0表示RGB（所有通道），1表示R，2表示G，3表示B。
            input_black: 输入黑场，范围[0, 254]。
            input_gamma: 输入伽马（中间调），范围通常为[0.1, 9.99]。
            input_white: 输入白场，范围[1, 255]。
            output_black: 输出黑场，范围[0, 255]。
            output_white: 输出白场，范围[0, 255]。
        """
        self.channel = channel
        self.input_black = max(0, min(254, input_black))
        self.input_gamma = max(0.1, min(9.99, input_gamma))
        self.input_white = max(1, min(255, input_white))
        self.output_black = max(0, min(255, output_black))
        self.output_white = max(0, min(255, output_white))

    def apply(self, image: np.ndarray, scale_factor: float = 1.0) -> np.ndarray:
        """
        应用色阶调整。

        Args:
            image: 输入图像。
            scale_factor: 图像缩放因子，用于代理图像处理。
                          由于色阶操作基于查找表，与图像大小无关，因此不需要特别处理。

        Returns:
            调整后的图像。
        """
        # 确保输入图像是BGR格式或灰度图像
        if image.ndim != 3 and image.ndim != 2:
            return image  # 不支持的格式，直接返回原图

        # 创建输出图像
        result = image.copy()

        # 创建查找表 (LUT)，使用向量化操作
        # 生成输入值数组 [0, 1, 2, ..., 255]
        x = np.arange(256, dtype=np.float32)
        
        # 一次性完成所有计算，避免临时数组
        lut = np.clip(
            (np.power(
                np.clip((x - self.input_black) / max(1, self.input_white - self.input_black), 0, 1), 
                1.0 / self.input_gamma)
            ) * (self.output_white - self.output_black) + self.output_black,
            0, 255
        ).astype(np.uint8)

        # 应用查找表
        if image.ndim == 2 or self.channel == 0:  # 灰度图像或RGB所有通道
            if image.ndim == 3:
                # 使用OpenCV的LUT函数一次性处理整个图像
                result = cv2.LUT(image, lut)
            else:
                # 灰度图像
                result = cv2.LUT(image, lut)
        else:
            # 只处理特定通道
            channel_idx = self.channel - 1  # 转换为0-based索引
            result[:, :, channel_idx] = cv2.LUT(image[:, :, channel_idx], lut)

        return result 
        
    def get_params(self) -> Dict[str, Any]:
        """
        获取此操作的参数。
        
        Returns:
            Dict[str, Any]: 包含操作参数的字典。
        """
        return {
            "channel": self.channel,
            "input_black": self.input_black,
            "input_gamma": self.input_gamma,
            "input_white": self.input_white,
            "output_black": self.output_black,
            "output_white": self.output_white
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