"""
分析标签页类型工具

简化的标签页类型管理，只保留实际使用的功能。
"""

from enum import Enum, auto
from typing import Optional


class TabType(Enum):
    """分析标签页类型枚举"""
    INFO = auto()           # 信息标签页
    HISTOGRAM = auto()      # 直方图标签页
    RGB_PARADE = auto()     # RGB Parade标签页
    HUE_SATURATION = auto() # 色相饱和度标签页
    LUMA_WAVEFORM = auto()  # 亮度波形标签页
    LAB_CHROMATICITY = auto()  # Lab色度分析标签页


class TabConfigManager:
    """标签页配置管理器 - 简化版本"""
    
    # 标签页索引到类型的简单映射
    TAB_TYPE_MAPPING = {
        0: TabType.INFO,
        1: TabType.HISTOGRAM,
        2: TabType.RGB_PARADE,
        3: TabType.HUE_SATURATION,
        4: TabType.LAB_CHROMATICITY,
    }
    
    def get_tab_type(self, tab_index: int) -> Optional[TabType]:
        """获取标签页类型"""
        return self.TAB_TYPE_MAPPING.get(tab_index)
    
    def is_valid_tab_index(self, tab_index: int) -> bool:
        """检查标签页索引是否有效"""
        return tab_index in self.TAB_TYPE_MAPPING