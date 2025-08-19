from dataclasses import dataclass


@dataclass
class SpatialFilterParams:
    """空间滤波操作参数基类"""
    pass


@dataclass
class GaussianBlurParams(SpatialFilterParams):
    """高斯模糊滤波参数"""
    sigma_x: float = 1.0
    sigma_y: float = 1.0
    kernel_size: int = 5


@dataclass
class LaplacianEdgeParams(SpatialFilterParams):
    """拉普拉斯边缘检测参数"""
    kernel_size: int = 3
    scale: float = 1.0
    delta: float = 0.0


@dataclass
class SobelEdgeParams(SpatialFilterParams):
    """Sobel边缘检测参数"""
    dx: int = 1
    dy: int = 1
    kernel_size: int = 3
    scale: float = 1.0
    delta: float = 0.0


@dataclass
class SharpenParams(SpatialFilterParams):
    """锐化滤波参数"""
    strength: float = 1.0
    radius: float = 1.0
    threshold: float = 0.0


@dataclass
class MeanFilterParams(SpatialFilterParams):
    """均值滤波参数"""
    kernel_size: int = 5