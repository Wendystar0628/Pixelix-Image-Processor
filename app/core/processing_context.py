"""
Processing Context Module

这个模块定义了ProcessingContext类，封装了图像处理会话的状态，
特别是与预览降采样工作流相关的状态。
"""

from typing import Optional, Dict, Any
import numpy as np
from .configuration.config_data_accessor import ConfigDataAccessor




class ProcessingContext:
    """
    封装了图像处理会话的状态，特别是与代理工作流相关的状态。
    
    这是一个简单的数据容器，用于存储代理质量设置。
    该类已大幅简化，仅保留必要的功能。
    """
    def __init__(self, config_registry: Optional[ConfigDataAccessor] = None):
        # 从配置注册表获取代理质量设置
        if config_registry is None:
            # 使用默认值
            self.proxy_quality_factor: float = 0.75
        else:
            self.proxy_quality_factor: float = config_registry.get_proxy_quality_factor()
        
    def reset(self) -> None:
        """
        重置所有状态，用于加载新图像。
        保留此方法仅为兼容现有代码。
        """
        # 保留当前的代理质量设置
        pass 