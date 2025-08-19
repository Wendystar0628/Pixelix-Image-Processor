"""
配置管理模块
"""

from .config_data_transfer import ConfigDataTransferObject
from .config_data_accessor import ConfigDataAccessor

# 向后兼容
ConfigDataRegistry = ConfigDataAccessor

__all__ = ['ConfigDataTransferObject', 'ConfigDataAccessor', 'ConfigDataRegistry']