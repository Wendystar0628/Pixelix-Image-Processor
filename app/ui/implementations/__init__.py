"""
UI接口实现模块

此模块包含核心层定义的UI抽象接口的具体实现。
通过这些实现类，UI层向核心层提供所需的UI功能，
同时保持分层架构的清晰边界。
"""

from .widget_implementation import WidgetImplementation
from .dialog_implementation import DialogImplementation
from .ui_factory_implementation import UIFactoryImplementation

__all__ = [
    'WidgetImplementation',
    'DialogImplementation', 
    'UIFactoryImplementation',
]