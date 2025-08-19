"""
图像缩放对话框模块

导出所有图像缩放参数调整对话框。
"""

from .scale_up_dialog import ScaleUpDialog
from .scale_down_dialog import ScaleDownDialog

__all__ = [
    'ScaleUpDialog',
    'ScaleDownDialog'
]