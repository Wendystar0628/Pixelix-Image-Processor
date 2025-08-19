"""
常规滤镜对话框模块

导出所有常规滤镜参数调整对话框。
"""

from .emboss_dialog import EmbossDialog
from .mosaic_dialog import MosaicDialog
from .oil_painting_dialog import OilPaintingDialog
from .sketch_dialog import SketchDialog
from .vintage_dialog import VintageDialog

# 新增滤镜对话框
from .additional_filters_dialogs import (
    WatercolorDialog,
    PencilSketchDialog,
    CartoonDialog,
    WarmToneDialog,
    CoolToneDialog,
    FilmGrainDialog,
    NoiseDialog,
    FrostedGlassDialog,
    FabricTextureDialog,
    VignetteDialog
)

__all__ = [
    # 原有对话框
    'EmbossDialog',
    'MosaicDialog',
    'OilPaintingDialog',
    'SketchDialog',
    'VintageDialog',
    # 新增对话框
    'WatercolorDialog',
    'PencilSketchDialog',
    'CartoonDialog',
    'WarmToneDialog',
    'CoolToneDialog',
    'FilmGrainDialog',
    'NoiseDialog',
    'FrostedGlassDialog',
    'FabricTextureDialog',
    'VignetteDialog'
]