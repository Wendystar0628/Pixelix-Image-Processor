"""常规滤镜操作模块"""

from .emboss_filter_op import EmbossFilterOp
from .mosaic_filter_op import MosaicFilterOp
from .oil_painting_filter_op import OilPaintingFilterOp
from .sketch_filter_op import SketchFilterOp
from .vintage_filter_op import VintageFilterOp

# 新增滤镜操作
from .additional_filters_ops import (
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

__all__ = [
    # 原有滤镜
    'EmbossFilterOp',
    'MosaicFilterOp',
    'OilPaintingFilterOp',
    'SketchFilterOp',
    'VintageFilterOp',
    # 新增滤镜
    'WatercolorFilterOp',
    'PencilSketchFilterOp',
    'CartoonFilterOp',
    'WarmToneFilterOp',
    'CoolToneFilterOp',
    'FilmGrainFilterOp',
    'NoiseFilterOp',
    'FrostedGlassFilterOp',
    'FabricTextureFilterOp',
    'VignetteFilterOp'
]