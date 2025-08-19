"""
核心抽象层
定义核心业务需要的最小基础设施接口
"""

from .config_access_interface import ConfigAccessInterface

__all__ = [
    'ConfigAccessInterface',
]