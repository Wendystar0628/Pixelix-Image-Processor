import cv2
import numpy as np
from typing import Dict, Any
from .base_operation import ImageOperation


class ColorBalanceOp(ImageOperation):
    """
    色彩平衡操作。
    
    允许用户调整图像的色彩平衡，包括阴影、中间调、高光的独立调整。
    """

    def __init__(
        self,
        shadows_cyan_red: float = 0.0,
        shadows_magenta_green: float = 0.0,
        shadows_yellow_blue: float = 0.0,
        midtones_cyan_red: float = 0.0,
        midtones_magenta_green: float = 0.0,
        midtones_yellow_blue: float = 0.0,
        highlights_cyan_red: float = 0.0,
        highlights_magenta_green: float = 0.0,
        highlights_yellow_blue: float = 0.0,
        preserve_luminosity: bool = True,
    ):
        """
        初始化色彩平衡操作。

        Args:
            shadows_cyan_red: 阴影区域的青-红平衡，范围 [-100.0, 100.0]，正值增加红色，负值增加青色。
            shadows_magenta_green: 阴影区域的洋红-绿平衡，范围 [-100.0, 100.0]，正值增加绿色，负值增加洋红色。
            shadows_yellow_blue: 阴影区域的黄-蓝平衡，范围 [-100.0, 100.0]，正值增加蓝色，负值增加黄色。
            midtones_cyan_red: 中间调区域的青-红平衡，范围同上。
            midtones_magenta_green: 中间调区域的洋红-绿平衡，范围同上。
            midtones_yellow_blue: 中间调区域的黄-蓝平衡，范围同上。
            highlights_cyan_red: 高光区域的青-红平衡，范围同上。
            highlights_magenta_green: 高光区域的洋红-绿平衡，范围同上。
            highlights_yellow_blue: 高光区域的黄-蓝平衡，范围同上。
            preserve_luminosity: 是否保持亮度不变，True表示保持亮度。
        """
        # 将调整参数映射到[-1.0, 1.0]范围，以便于计算
        self.shadows_cyan_red = shadows_cyan_red / 100.0
        self.shadows_magenta_green = shadows_magenta_green / 100.0
        self.shadows_yellow_blue = shadows_yellow_blue / 100.0
        self.midtones_cyan_red = midtones_cyan_red / 100.0
        self.midtones_magenta_green = midtones_magenta_green / 100.0
        self.midtones_yellow_blue = midtones_yellow_blue / 100.0
        self.highlights_cyan_red = highlights_cyan_red / 100.0
        self.highlights_magenta_green = highlights_magenta_green / 100.0
        self.highlights_yellow_blue = highlights_yellow_blue / 100.0
        self.preserve_luminosity = preserve_luminosity
        
        # 预计算查找表
        self.lut_b = self._create_lut_for_channel(0)  # 蓝色通道
        self.lut_g = self._create_lut_for_channel(1)  # 绿色通道
        self.lut_r = self._create_lut_for_channel(2)  # 红色通道
        
        # 如果所有通道的所有调整参数都为零，标记为无需处理
        self.no_adjustments = (
            shadows_cyan_red == 0.0 and
            shadows_magenta_green == 0.0 and
            shadows_yellow_blue == 0.0 and
            midtones_cyan_red == 0.0 and
            midtones_magenta_green == 0.0 and
            midtones_yellow_blue == 0.0 and
            highlights_cyan_red == 0.0 and
            highlights_magenta_green == 0.0 and
            highlights_yellow_blue == 0.0
        )

    def apply(self, image: np.ndarray) -> np.ndarray:
        """
        应用色彩平衡调整。

        Args:
            image: 输入图像。

        Returns:
            调整后的图像。
        """
        # 如果没有任何调整，直接返回原图
        if self.no_adjustments:
            return image.copy()
        
        # 确保输入图像是BGR格式
        if image.ndim != 3 or image.shape[2] != 3:
            # 如果是灰度图像，转换为BGR
            if image.ndim == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            else:
                # 不支持的格式，直接返回原图
                return image

        # 保存原始图像以计算亮度
        original_l = None
        if self.preserve_luminosity:
            original_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            original_l = original_lab[:, :, 0].copy()  # 原始亮度通道

        # 使用OpenCV的LUT函数应用查找表 - 一次性处理整个图像
        result = cv2.LUT(image, np.dstack([self.lut_b, self.lut_g, self.lut_r]))
        
        # 如果需要保持亮度
        if self.preserve_luminosity and original_l is not None:
            # 计算新图像的LAB表示
            new_lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
            # 替换亮度通道
            new_lab[:, :, 0] = original_l
            # 转换回BGR
            result = cv2.cvtColor(new_lab, cv2.COLOR_LAB2BGR)
            
        return result
        
    def _create_lut_for_channel(self, channel_idx):
        """
        为特定颜色通道创建查找表
        
        Args:
            channel_idx: 通道索引 (0=B, 1=G, 2=R)
            
        Returns:
            查找表，一个长度为256的uint8数组
        """
        # 选择对应通道的调整参数
        if channel_idx == 0:  # 蓝色通道 (对应黄-蓝调整)
            shadows_adjust = self.shadows_yellow_blue
            midtones_adjust = self.midtones_yellow_blue
            highlights_adjust = self.highlights_yellow_blue
        elif channel_idx == 1:  # 绿色通道 (对应洋红-绿调整)
            shadows_adjust = self.shadows_magenta_green
            midtones_adjust = self.midtones_magenta_green
            highlights_adjust = self.highlights_magenta_green
        else:  # 红色通道 (对应青-红调整)
            shadows_adjust = self.shadows_cyan_red
            midtones_adjust = self.midtones_cyan_red
            highlights_adjust = self.highlights_cyan_red
            
        # 创建查找表数组
        x = np.arange(256, dtype=np.float32)
        
        # 计算阴影、中间调和高光的权重 (一次性向量化计算)
        shadows_weight = np.clip(1.0 - x * (3.0/255.0), 0.0, 1.0)
        highlights_weight = np.clip((x/255.0 - 0.67) * 3.0, 0.0, 1.0)
        midtones_weight = 1.0 - shadows_weight - highlights_weight
        
        # 应用调整 (一次性向量化计算)
        adjustments = (
            shadows_adjust * shadows_weight + 
            midtones_adjust * midtones_weight + 
            highlights_adjust * highlights_weight
        )
        
        # 调整后的值（调整值以255为单位）
        x = x + (adjustments * 255.0)
        
        # 裁剪到[0, 255]范围
        return np.clip(x, 0, 255).astype(np.uint8) 
        
    def get_params(self) -> Dict[str, Any]:
        """
        获取此操作的参数。
        
        Returns:
            Dict[str, Any]: 包含操作参数的字典。
        """
        return {
            "shadows_cyan_red": self.shadows_cyan_red * 100.0,
            "shadows_magenta_green": self.shadows_magenta_green * 100.0,
            "shadows_yellow_blue": self.shadows_yellow_blue * 100.0,
            "midtones_cyan_red": self.midtones_cyan_red * 100.0,
            "midtones_magenta_green": self.midtones_magenta_green * 100.0,
            "midtones_yellow_blue": self.midtones_yellow_blue * 100.0,
            "highlights_cyan_red": self.highlights_cyan_red * 100.0,
            "highlights_magenta_green": self.highlights_magenta_green * 100.0,
            "highlights_yellow_blue": self.highlights_yellow_blue * 100.0,
            "preserve_luminosity": self.preserve_luminosity
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