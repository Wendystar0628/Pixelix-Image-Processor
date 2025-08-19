"""
分析组件工厂模块

负责创建不同渲染引擎对应的UI组件
"""

import logging
from typing import Dict, List, Optional
from PyQt6.QtWidgets import QWidget

from app.ui.widgets.combined_analysis_widget import CombinedAnalysisWidget
from app.ui.widgets.rgb_parade_widget import RGBParadeWidget
from app.ui.widgets.hue_saturation_widget import HueSaturationWidget
from app.ui.widgets.lab_analysis_widget import LabAnalysisWidget
# PyQtGraph版本的控件
from app.ui.widgets.pyqtgraph_combined_analysis_widget import PyQtGraphCombinedAnalysisWidget
from app.ui.widgets.pyqtgraph_rgb_parade_widget import PyQtGraphRGBParadeWidget
from app.ui.widgets.pyqtgraph_hue_saturation_widget import PyQtGraphHueSaturationWidget
from app.ui.widgets.pyqtgraph_lab_analysis_widget import PyQtGraphLabAnalysisWidget

# 设置日志记录器
logger = logging.getLogger(__name__)


class AnalysisWidgetFactory:
    """
    分析组件工厂类
    
    负责根据渲染引擎名称创建对应的UI组件，
    提供统一的组件创建接口，便于扩展新的渲染引擎。
    """
    
    # 支持的渲染引擎
    SUPPORTED_ENGINES = ["matplotlib", "pyqtgraph"]
    
    @staticmethod
    def create_widgets(engine_name: str) -> Optional[Dict[str, QWidget]]:
        """
        根据引擎名称创建对应的UI组件
        
        Args:
            engine_name: 渲染引擎名称 ("matplotlib" 或 "pyqtgraph")
            
        Returns:
            Dict[str, QWidget]: 包含组件的字典，创建失败时返回None
            字典包含以下键：
            - 'combined': 组合分析组件（直方图与波形）
            - 'rgb_parade': RGB Parade组件
            - 'hue_saturation': 色相/饱和度组件
            - 'lab_analysis': Lab色彩空间分析组件
        """
        if engine_name not in AnalysisWidgetFactory.SUPPORTED_ENGINES:
            logger.error(f"不支持的渲染引擎: {engine_name}")
            return None
            
        try:
            logger.debug(f"开始创建 {engine_name} 引擎的UI组件")
            
            if engine_name == "pyqtgraph":
                widgets = AnalysisWidgetFactory._create_pyqtgraph_widgets()
            elif engine_name == "matplotlib":
                widgets = AnalysisWidgetFactory._create_matplotlib_widgets()
            else:
                # 这个分支理论上不会执行，因为上面已经检查过
                logger.error(f"未实现的渲染引擎: {engine_name}")
                return None
                
            logger.debug(f"成功创建 {engine_name} 引擎的所有UI组件")
            return widgets
            
        except Exception as e:
            logger.error(f"创建 {engine_name} 引擎组件时发生错误: {e}")
            return None
    
    @staticmethod
    def _create_matplotlib_widgets() -> Dict[str, QWidget]:
        """
        创建Matplotlib引擎的UI组件
        
        Returns:
            Dict[str, QWidget]: Matplotlib组件字典
        """
        return {
            'combined': CombinedAnalysisWidget(),
            'rgb_parade': RGBParadeWidget(),
            'hue_saturation': HueSaturationWidget(),
            'lab_analysis': LabAnalysisWidget()
        }
    
    @staticmethod
    def _create_pyqtgraph_widgets() -> Dict[str, QWidget]:
        """
        创建PyQtGraph引擎的UI组件
        
        Returns:
            Dict[str, QWidget]: PyQtGraph组件字典
        """
        return {
            'combined': PyQtGraphCombinedAnalysisWidget(),
            'rgb_parade': PyQtGraphRGBParadeWidget(),
            'hue_saturation': PyQtGraphHueSaturationWidget(),
            'lab_analysis': PyQtGraphLabAnalysisWidget()
        }
    
    @staticmethod
    def get_supported_engines() -> List[str]:
        """
        获取支持的渲染引擎列表
        
        Returns:
            List[str]: 支持的引擎名称列表
        """
        return AnalysisWidgetFactory.SUPPORTED_ENGINES.copy()
    
    @staticmethod
    def is_engine_supported(engine_name: str) -> bool:
        """
        检查指定的引擎是否被支持
        
        Args:
            engine_name: 引擎名称
            
        Returns:
            bool: 如果引擎被支持返回True，否则返回False
        """
        return engine_name in AnalysisWidgetFactory.SUPPORTED_ENGINES