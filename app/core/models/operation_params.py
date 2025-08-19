from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class BaseOperationParams:
    """所有操作参数的基类"""
    pass


@dataclass
class BrightnessContrastParams(BaseOperationParams):
    """亮度/对比度操作的参数"""
    brightness: int = 0
    contrast: int = 0


@dataclass
class ColorBalanceParams(BaseOperationParams):
    """色彩平衡操作的参数"""
    shadows_cyan_red: float = 0.0
    shadows_magenta_green: float = 0.0
    shadows_yellow_blue: float = 0.0
    midtones_cyan_red: float = 0.0
    midtones_magenta_green: float = 0.0
    midtones_yellow_blue: float = 0.0
    highlights_cyan_red: float = 0.0
    highlights_magenta_green: float = 0.0
    highlights_yellow_blue: float = 0.0
    preserve_luminosity: bool = True


@dataclass
class LevelsParams(BaseOperationParams):
    """色阶调整操作的参数"""
    channel: int = 0  # 0: RGB, 1: R, 2: G, 3: B
    input_black: int = 0
    input_gamma: float = 1.0
    input_white: int = 255
    output_black: int = 0
    output_white: int = 255


@dataclass
class CurvesParams(BaseOperationParams):
    """曲线调整操作的参数"""
    points_rgb: List[Tuple[int, int]]
    points_r: Optional[List[Tuple[int, int]]] = None
    points_g: Optional[List[Tuple[int, int]]] = None
    points_b: Optional[List[Tuple[int, int]]] = None


@dataclass
class HueSaturationParams(BaseOperationParams):
    """色相/饱和度操作的参数"""
    hue: int = 0
    saturation: int = 0
    lightness: int = 0
    colorize: bool = False
    colorize_hue: int = 0
    colorize_saturation: int = 50


@dataclass
class ThresholdParams(BaseOperationParams):
    """阈值操作的参数"""
    threshold: int = 128


# 导入滤波参数类
from .spatial_filter_params import (
    SpatialFilterParams,
    GaussianBlurParams,
    LaplacianEdgeParams,
    SobelEdgeParams,
    SharpenParams,
    MeanFilterParams
)

from .regular_filter_params import (
    RegularFilterParams,
    EmbossParams,
    MosaicParams,
    OilPaintingParams,
    SketchParams,
    VintageParams
)