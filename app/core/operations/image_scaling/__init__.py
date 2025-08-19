"""
图像缩放操作模块

导出所有图像缩放操作类。
"""

from .scale_up_ops import (
    NearestScaleUpOp,
    BilinearScaleUpOp,
    BicubicScaleUpOp,
    LanczosScaleUpOp,
    EdgePreservingScaleUpOp
)

from .scale_down_ops import (
    NearestScaleDownOp,
    BilinearScaleDownOp,
    AreaAverageScaleDownOp,
    GaussianScaleDownOp,
    AntiAliasScaleDownOp
)

__all__ = [
    # 放大操作
    'NearestScaleUpOp',
    'BilinearScaleUpOp',
    'BicubicScaleUpOp',
    'LanczosScaleUpOp',
    'EdgePreservingScaleUpOp',
    # 缩小操作
    'NearestScaleDownOp',
    'BilinearScaleDownOp',
    'AreaAverageScaleDownOp',
    'GaussianScaleDownOp',
    'AntiAliasScaleDownOp'
]