"""
图像缩小参数数据模型
"""

from dataclasses import dataclass


@dataclass
class ScaleDownParams:
    """图像缩小参数基类"""
    scale_factor: float = 0.5
    algorithm: str = "bilinear"
    
    def __post_init__(self):
        """参数验证"""
        if self.scale_factor >= 1.0:
            raise ValueError("缩小倍数必须小于1.0")
        if self.scale_factor <= 0.1:
            raise ValueError("缩小倍数不能小于0.1")


@dataclass
class NearestScaleDownParams(ScaleDownParams):
    """最近邻下采样参数"""
    algorithm: str = "nearest"


@dataclass
class BilinearScaleDownParams(ScaleDownParams):
    """双线性下采样参数"""
    algorithm: str = "bilinear"


@dataclass
class AreaAverageScaleDownParams(ScaleDownParams):
    """区域平均下采样参数"""
    algorithm: str = "area_average"


@dataclass
class GaussianScaleDownParams(ScaleDownParams):
    """高斯下采样参数"""
    algorithm: str = "gaussian"
    sigma: float = 1.0


@dataclass
class AntiAliasScaleDownParams(ScaleDownParams):
    """抗锯齿下采样参数"""
    algorithm: str = "anti_alias"
    filter_size: int = 3