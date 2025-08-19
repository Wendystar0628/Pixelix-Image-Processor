from dataclasses import dataclass


@dataclass
class RegularFilterParams:
    """常规滤镜操作参数基类"""
    pass


@dataclass
class EmbossParams(RegularFilterParams):
    """浮雕滤镜参数"""
    direction: int = 0  # 0-7: 8个方向
    depth: float = 1.0


@dataclass
class MosaicParams(RegularFilterParams):
    """马赛克滤镜参数"""
    block_size: int = 10
    preserve_edges: bool = False


@dataclass
class OilPaintingParams(RegularFilterParams):
    """油画滤镜参数"""
    brush_size: int = 5
    detail_level: int = 3
    saturation: float = 1.0


@dataclass
class SketchParams(RegularFilterParams):
    """素描滤镜参数"""
    line_strength: float = 1.0
    contrast: float = 1.0
    background_color: int = 255  # 0-255 灰度值


@dataclass
class VintageParams(RegularFilterParams):
    """怀旧滤镜参数"""
    intensity: float = 0.5
    temperature: float = 0.0  # -1.0 to 1.0
    vignette: float = 0.3


# 新增滤镜参数类

@dataclass
class WatercolorParams(RegularFilterParams):
    """水彩画滤镜参数"""
    flow_intensity: float = 0.5  # 流动强度 0.0-1.0
    penetration: float = 0.3     # 渗透程度 0.0-1.0


@dataclass
class PencilSketchParams(RegularFilterParams):
    """铅笔画滤镜参数"""
    line_thickness: float = 1.0   # 线条粗细 0.1-3.0
    shadow_intensity: float = 0.5 # 阴影强度 0.0-1.0


@dataclass
class CartoonParams(RegularFilterParams):
    """卡通化滤镜参数"""
    color_simplification: float = 0.7  # 色彩简化程度 0.0-1.0
    edge_enhancement: float = 0.8       # 边缘增强强度 0.0-1.0


@dataclass
class WarmToneParams(RegularFilterParams):
    """暖色调滤镜参数"""
    warmth_intensity: float = 0.5  # 暖色强度 0.0-1.0
    temperature_shift: float = 0.3 # 色温偏移 0.0-1.0


@dataclass
class CoolToneParams(RegularFilterParams):
    """冷色调滤镜参数"""
    coolness_intensity: float = 0.5  # 冷色强度 0.0-1.0
    temperature_shift: float = 0.3   # 色温偏移 0.0-1.0


@dataclass
class FilmGrainParams(RegularFilterParams):
    """黑白胶片滤镜参数"""
    grain_intensity: float = 0.5  # 颗粒强度 0.0-1.0
    contrast_boost: float = 0.3   # 对比度增强 0.0-1.0


@dataclass
class NoiseParams(RegularFilterParams):
    """噪点滤镜参数"""
    noise_type: int = 0        # 噪点类型 0:高斯 1:椒盐 2:泊松
    noise_intensity: float = 0.1  # 噪点强度 0.0-1.0


@dataclass
class FrostedGlassParams(RegularFilterParams):
    """磨砂玻璃滤镜参数"""
    blur_amount: float = 0.5     # 模糊程度 0.0-1.0
    distortion_strength: float = 0.3  # 扭曲强度 0.0-1.0


@dataclass
class FabricTextureParams(RegularFilterParams):
    """织物纹理滤镜参数"""
    fabric_type: int = 0         # 织物类型 0:帆布 1:丝绸 2:麻布
    texture_intensity: float = 0.5  # 纹理强度 0.0-1.0


@dataclass
class VignetteParams(RegularFilterParams):
    """暗角滤镜参数"""
    vignette_strength: float = 0.5  # 暗角强度 0.0-1.0
    gradient_range: float = 0.7     # 渐变范围 0.1-1.0