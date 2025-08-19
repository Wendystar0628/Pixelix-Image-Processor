"""
图像压缩操作模块

导出所有图像压缩操作类。
"""

from .compression_ops import (
    JpegCompressionOp,
    PngCompressionOp,
    WebpCompressionOp,
    ColorQuantizationOp,
    LossyOptimizationOp
)

__all__ = [
    'JpegCompressionOp',
    'PngCompressionOp',
    'WebpCompressionOp',
    'ColorQuantizationOp',
    'LossyOptimizationOp'
]