"""
图像压缩参数数据模型
"""

from dataclasses import dataclass


@dataclass
class CompressionParams:
    """图像压缩参数基类"""
    quality: int = 85
    format: str = "JPEG"
    algorithm: str = "jpeg"


@dataclass
class JpegCompressionParams(CompressionParams):
    """JPEG质量压缩参数"""
    format: str = "JPEG"
    algorithm: str = "jpeg"
    optimize: bool = True


@dataclass
class PngCompressionParams(CompressionParams):
    """PNG压缩级别参数"""
    format: str = "PNG"
    algorithm: str = "png"
    compress_level: int = 6


@dataclass
class WebpCompressionParams(CompressionParams):
    """WebP压缩参数"""
    format: str = "WEBP"
    algorithm: str = "webp"
    lossless: bool = False


@dataclass
class ColorQuantizationParams(CompressionParams):
    """颜色量化压缩参数"""
    algorithm: str = "color_quantization"
    colors: int = 256
    dither: bool = True


@dataclass
class LossyOptimizationParams(CompressionParams):
    """有损压缩优化参数"""
    algorithm: str = "lossy_optimization"
    target_size_kb: int = 100
    max_iterations: int = 10