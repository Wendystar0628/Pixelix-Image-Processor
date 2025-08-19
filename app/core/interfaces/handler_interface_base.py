"""
Handler接口基础设施模块

提供Handler接口的基础元类和通用结构。
"""

from abc import ABC, ABCMeta
from PyQt6.QtCore import QObject, pyqtSignal


class HandlerInterfaceMeta(type(QObject), ABCMeta):
    """
    处理QObject和ABC多重继承的元类
    
    解决QObject和ABC的元类冲突问题，使Handler接口能够同时继承两者。
    """
    pass


class BaseHandlerInterface(QObject, ABC, metaclass=HandlerInterfaceMeta):
    """
    Handler接口基类
    
    包含Handler层服务的通用信号定义。
    """
    
    # 通用错误和信息信号
    show_error_message = pyqtSignal(str)
    show_info_message = pyqtSignal(str)