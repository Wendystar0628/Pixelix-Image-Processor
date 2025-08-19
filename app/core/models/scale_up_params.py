"""
图像放大参数数据模型
"""

from dataclasses import dataclass


@dataclass
class ScaleUpParams:
    """图像放大参数基类"""
    scale_factor: float = 2.0
    algorithm: str = "bilinear"
    
    def __post_init__(self):
        """参数验证"""
        if self.scale_factor <= 1.0:
            raise ValueError("放大倍数必须大于1.0")
        if self.scale_factor > 3.0:
            raise ValueError("放大倍数不能超过3.0")


@dataclass
class NearestScaleUpParams(ScaleUpParams):
    """最近邻插值放大参数"""
    algorithm: str = "nearest"


@dataclass
class BilinearScaleUpParams(ScaleUpParams):
    """双线性插值放大参数"""
    algorithm: str = "bilinear"


@dataclass
class BicubicScaleUpParams(ScaleUpParams):
    """双三次插值放大参数"""
    algorithm: str = "bicubic"


@dataclass
class LanczosScaleUpParams(ScaleUpParams):
    """Lanczos插值放大参数"""
    algorithm: str = "lanczos"


@dataclass
class EdgePreservingScaleUpParams(ScaleUpParams):
    """边缘保持插值放大参数"""
    algorithm: str = "edge_preserving"
    edge_threshold: float = 0.1