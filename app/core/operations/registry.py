"""
操作注册表模块

提供一个中央注册表，将操作名称映射到操作类，用于动态创建操作实例。
"""
from typing import Dict, Type

from .base_operation import ImageOperation
from .brightness_contrast_op import BrightnessContrastOp
from .color_balance_op import ColorBalanceOp
from .curves_op import CurvesOp
from .grayscale_op import GrayscaleOp
from .histogram_equalization_op import HistogramEqualizationOp
from .hue_saturation_op import HueSaturationOp
from .invert_op import InvertOp
from .levels_op import LevelsOp
from .otsu_threshold_op import OtsuThresholdOp
from .threshold_op import ThresholdOp

# 空间滤波操作
from .spatial_filtering import (
    GaussianBlurFilterOp,
    LaplacianEdgeFilterOp,
    SobelEdgeFilterOp,
    SharpenFilterOp,
    MeanFilterOp
)

# 常规滤镜操作
from .regular_filters import (
    EmbossFilterOp,
    MosaicFilterOp,
    OilPaintingFilterOp,
    SketchFilterOp,
    VintageFilterOp,
    # 新增滤镜操作
    WatercolorFilterOp,
    PencilSketchFilterOp,
    CartoonFilterOp,
    WarmToneFilterOp,
    CoolToneFilterOp,
    FilmGrainFilterOp,
    NoiseFilterOp,
    FrostedGlassFilterOp,
    FabricTextureFilterOp,
    VignetteFilterOp
)

# 图像缩放操作
from .image_scaling import (
    NearestScaleUpOp,
    BilinearScaleUpOp,
    BicubicScaleUpOp,
    LanczosScaleUpOp,
    EdgePreservingScaleUpOp,
    NearestScaleDownOp,
    BilinearScaleDownOp,
    AreaAverageScaleDownOp,
    GaussianScaleDownOp,
    AntiAliasScaleDownOp
)

# 图像压缩操作
from .image_compression import (
    JpegCompressionOp,
    PngCompressionOp,
    WebpCompressionOp,
    ColorQuantizationOp,
    LossyOptimizationOp
)


# 操作注册表：将操作类名称映射到操作类
OPERATION_REGISTRY: Dict[str, Type[ImageOperation]] = {
    "BrightnessContrastOp": BrightnessContrastOp,
    "ColorBalanceOp": ColorBalanceOp,
    "CurvesOp": CurvesOp,
    "GrayscaleOp": GrayscaleOp,
    "HistogramEqualizationOp": HistogramEqualizationOp,
    "HueSaturationOp": HueSaturationOp,
    "InvertOp": InvertOp,
    "LevelsOp": LevelsOp,
    "OtsuThresholdOp": OtsuThresholdOp,
    "ThresholdOp": ThresholdOp,
    # 空间滤波操作
    "GaussianBlurFilterOp": GaussianBlurFilterOp,
    "LaplacianEdgeFilterOp": LaplacianEdgeFilterOp,
    "SobelEdgeFilterOp": SobelEdgeFilterOp,
    "SharpenFilterOp": SharpenFilterOp,
    "MeanFilterOp": MeanFilterOp,
    # 常规滤镜操作
    "EmbossFilterOp": EmbossFilterOp,
    "MosaicFilterOp": MosaicFilterOp,
    "OilPaintingFilterOp": OilPaintingFilterOp,
    "SketchFilterOp": SketchFilterOp,
    "VintageFilterOp": VintageFilterOp,
    # 新增滤镜操作
    "WatercolorFilterOp": WatercolorFilterOp,
    "PencilSketchFilterOp": PencilSketchFilterOp,
    "CartoonFilterOp": CartoonFilterOp,
    "WarmToneFilterOp": WarmToneFilterOp,
    "CoolToneFilterOp": CoolToneFilterOp,
    "FilmGrainFilterOp": FilmGrainFilterOp,
    "NoiseFilterOp": NoiseFilterOp,
    "FrostedGlassFilterOp": FrostedGlassFilterOp,
    "FabricTextureFilterOp": FabricTextureFilterOp,
    "VignetteFilterOp": VignetteFilterOp,
    # 图像放大操作
    "NearestScaleUpOp": NearestScaleUpOp,
    "BilinearScaleUpOp": BilinearScaleUpOp,
    "BicubicScaleUpOp": BicubicScaleUpOp,
    "LanczosScaleUpOp": LanczosScaleUpOp,
    "EdgePreservingScaleUpOp": EdgePreservingScaleUpOp,
    # 图像缩小操作
    "NearestScaleDownOp": NearestScaleDownOp,
    "BilinearScaleDownOp": BilinearScaleDownOp,
    "AreaAverageScaleDownOp": AreaAverageScaleDownOp,
    "GaussianScaleDownOp": GaussianScaleDownOp,
    "AntiAliasScaleDownOp": AntiAliasScaleDownOp,
    # 图像压缩操作
    "JpegCompressionOp": JpegCompressionOp,
    "PngCompressionOp": PngCompressionOp,
    "WebpCompressionOp": WebpCompressionOp,
    "ColorQuantizationOp": ColorQuantizationOp,
    "LossyOptimizationOp": LossyOptimizationOp,
}


def register_operation(name: str, op_class: Type[ImageOperation]) -> None:
    """
    注册一个新的操作类。
    
    Args:
        name: 操作类名称
        op_class: 操作类
    """
    OPERATION_REGISTRY[name] = op_class
    
    
def get_operation_class(name: str) -> Type[ImageOperation]:
    """
    根据名称获取操作类。
    
    Args:
        name: 操作类名称
        
    Returns:
        Type[ImageOperation]: 操作类
        
    Raises:
        KeyError: 如果找不到对应的操作类
    """
    if name not in OPERATION_REGISTRY:
        raise KeyError(f"未知的操作类: {name}")
    
    return OPERATION_REGISTRY[name] 