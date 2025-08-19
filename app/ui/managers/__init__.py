"""
UI管理器模块

包含各种UI组件的管理器类 - 职责分离重构版本。

主要管理器：
- AnalysisComponentsManager: 协调器（门面模式）
- AnalysisUpdateManager: 智能更新逻辑
- AnalysisWidgetManager: UI组件管理
- AnalysisDataProcessor: 数据处理协调
"""

from app.ui.managers.analysis_components_manager import AnalysisComponentsManager
from app.ui.managers.analysis_update_manager import AnalysisUpdateManager
from app.ui.managers.analysis_widget_manager import AnalysisWidgetManager
from app.ui.managers.analysis_data_processor import AnalysisDataProcessor

__all__ = [
    'AnalysisComponentsManager',  # 主要协调器
    'AnalysisUpdateManager',      # 智能更新管理
    'AnalysisWidgetManager',      # UI组件管理
    'AnalysisDataProcessor'       # 数据处理协调
]