import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from scipy import interpolate
from .base_operation import ImageOperation


class CurvesOp(ImageOperation):
    """
    曲线调整操作。
    
    允许用户通过控制点精确调整图像的色调曲线。
    """

    def __init__(
        self,
        points_rgb: List[Tuple[int, int]],
        points_r: Optional[List[Tuple[int, int]]] = None,
        points_g: Optional[List[Tuple[int, int]]] = None,
        points_b: Optional[List[Tuple[int, int]]] = None,
    ):
        """
        初始化曲线调整操作。

        Args:
            points_rgb: RGB/亮度通道的控制点列表。
            points_r: 红色通道的控制点列表。
            points_g: 绿色通道的控制点列表。
            points_b: 蓝色通道的控制点列表。
        """
        # 如果单独的通道未提供，则使用RGB通道的设置
        self.points_r = points_r or points_rgb
        self.points_g = points_g or points_rgb
        self.points_b = points_b or points_rgb

        # 预计算查找表
        self.lut_r = self._create_lut(self.points_r)
        self.lut_g = self._create_lut(self.points_g)
        self.lut_b = self._create_lut(self.points_b)

    @staticmethod
    def get_presets() -> Dict[str, Dict]:
        """返回一个包含所有预设曲线的字典。"""
        return {
            "自定义": {
                "description": "自定义曲线。",
                "points": [(0, 0), (255, 255)]  # 初始为线性
            },
            "线性": {
                "description": "线性曲线，保持原始色调分布不变。",
                "points": [(0, 0), (255, 255)]
            },
            "S曲线 (增强对比度)": {
                "description": "S形曲线，增强中间调对比度，同时保持高光和阴影细节。",
                "points": [(0, 0), (64, 32), (192, 224), (255, 255)]
            },
            "反转": {
                "description": "反转色调，创建负片效果。",
                "points": [(0, 255), (255, 0)]
            },
            "明亮化": {
                "description": "提高中间调亮度，保持高光和阴影。",
                "points": [(0, 0), (128, 160), (255, 255)]
            },
            "暗化": {
                "description": "降低中间调亮度，保持高光和阴影。",
                "points": [(0, 0), (128, 96), (255, 255)]
            }
        }

    def _create_lut(self, control_points: List[Tuple[int, int]]) -> np.ndarray:
        """
        根据给定的控制点创建查找表。
        """
        # 确保控制点按x坐标排序
        control_points.sort(key=lambda p: p[0])
        
        x_points = np.array([p[0] for p in control_points])
        y_points = np.array([p[1] for p in control_points])
        
        # 默认使用线性插值
        lut = np.interp(np.arange(256), x_points, y_points)

        if len(control_points) > 2:
            try:
                cs = interpolate.CubicSpline(x_points, y_points)
                smooth_lut = cs(np.arange(256))
                lut = np.clip(smooth_lut, 0, 255)
            except Exception:
                pass  # 插值失败则保留线性结果
                
        return lut.astype(np.uint8)

    def apply(self, image: np.ndarray, scale_factor: float = 1.0) -> np.ndarray:
        """
        应用曲线调整。
        
        Args:
            image: 输入图像
            scale_factor: 图像缩放因子，用于代理图像处理。
                          由于曲线操作基于查找表，与图像大小无关，因此不需要特别处理。
                          
        Returns:
            调整后的图像
        """
        if image.ndim != 3 or image.shape[2] != 3:
            return image

        # 分离通道
        b, g, r = cv2.split(image)
        
        # 应用各自的查找表
        r_new = cv2.LUT(r, self.lut_r)
        g_new = cv2.LUT(g, self.lut_g)
        b_new = cv2.LUT(b, self.lut_b)

        # 合并通道
        return cv2.merge([b_new, g_new, r_new])
        
    def get_params(self) -> Dict:
        """
        获取此操作的参数。
        """
        return {
            "points_rgb": self.points_r, # 在当前实现中，RGB等于R
            "points_r": self.points_r,
            "points_g": self.points_g,
            "points_b": self.points_b,
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