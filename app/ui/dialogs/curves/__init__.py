"""
曲线对话框包
提供向外部模块暴露的接口，确保与现有代码的兼容性
"""

# 导出主对话框类，保持与原接口一致
from app.ui.dialogs.curves.curves_dialog import CurvesDialog

__all__ = ['CurvesDialog']
