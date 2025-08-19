"""
分析组件UI管理器

专门负责UI组件管理：widget引用管理、widget更新、widget清理等。
职责单一：只处理"UI组件管理"的逻辑。
"""

import logging
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject

logger = logging.getLogger(__name__)


class AnalysisWidgetManager(QObject):
    """
    分析组件UI管理器
    
    专门负责UI组件管理，包括：
    - UI widget引用管理
    - widget更新方法
    - widget清理方法
    - widget间协调逻辑
    """
    
    def __init__(self, analysis_tabs, image_info_widget, combined_analysis_widget, 
                 rgb_parade_widget, hue_saturation_widget, lab_analysis_widget=None, parent=None):
        super().__init__(parent)
        
        # UI Widget引用
        self.analysis_tabs = analysis_tabs
        self.image_info_widget = image_info_widget
        self.combined_analysis_widget = combined_analysis_widget
        self.rgb_parade_widget = rgb_parade_widget
        self.hue_saturation_widget = hue_saturation_widget
        self.lab_analysis_widget = lab_analysis_widget
        
        logger.debug("分析组件UI管理器初始化完成")
    
    def update_widgets_with_results(self, results: Optional[Dict[str, Any]]):
        """
        使用预先计算好的结果更新分析组件
        
        Args:
            results: 分析结果字典，包含各种分析数据
        """
        try:
            if not results:
                self._clear_all_widget_views()
                return
                
            # 更新组合分析组件（直方图和波形图）
            if 'histogram' in results and 'rgb_parade' in results:
                self.combined_analysis_widget.update_views(results)
                logger.debug("已更新组合分析组件")
                
            # 更新RGB Parade组件
            if 'rgb_parade' in results:
                self.rgb_parade_widget.update_parade(results)
                logger.debug("已更新RGB Parade组件")
                
            # 更新色相饱和度组件
            if 'hue_histogram' in results and 'sat_histogram' in results:
                self.hue_saturation_widget.update_histograms_with_data(results)
                logger.debug("已更新色相饱和度组件")
                
            # 更新Lab分析组件
            if self.lab_analysis_widget and ('lab_chromaticity' in results or 'lab_3d' in results):
                self.lab_analysis_widget.update_lab_analysis_with_data(results)
                logger.debug("已更新Lab分析组件")
                
        except Exception as e:
            logger.error(f"更新UI组件时发生错误: {e}")
            # 出错时清空所有组件以避免显示错误数据
            self._clear_all_widget_views()
    
    def update_image_info(self, image, file_path, operations):
        """
        更新图像信息组件
        
        Args:
            image: 图像数据
            file_path: 文件路径
            operations: 操作管道
        """
        try:
            self.image_info_widget.update_info(image, file_path, operations)
            logger.debug("已更新图像信息组件")
        except Exception as e:
            logger.error(f"更新图像信息组件时发生错误: {e}")
    
    def clear_all_analyses(self):
        """清空所有分析组件的内容"""
        try:
            # 清空图像信息组件
            self.image_info_widget.update_info(None, None, None)
            
            # 清空其他分析组件
            self._clear_all_widget_views()
            
            logger.debug("已清空所有分析组件")
            
        except Exception as e:
            logger.error(f"清空分析组件时发生错误: {e}")
    
    def _clear_all_widget_views(self):
        """清空所有widget的视图内容"""
        try:
            self.combined_analysis_widget.clear_views()
            self.rgb_parade_widget.clear_view()
            self.hue_saturation_widget.update_histograms(None)
            if self.lab_analysis_widget:
                self.lab_analysis_widget.clear_lab_analysis()
            logger.debug("已清空所有widget视图")
        except Exception as e:
            logger.error(f"清空widget视图时发生错误: {e}")
    
    def get_current_tab_index(self) -> int:
        """
        获取当前选中的标签页索引
        
        Returns:
            int: 当前标签页索引
        """
        return self.analysis_tabs.currentIndex()
    
    def get_total_tabs_count(self) -> int:
        """
        获取标签页总数
        
        Returns:
            int: 标签页总数
        """
        return self.analysis_tabs.count()
    
    def is_widget_visible(self, widget_name: str) -> bool:
        """
        检查指定的widget是否可见
        
        Args:
            widget_name: widget名称 ('info', 'histogram', 'rgb_parade', 'hue_saturation')
            
        Returns:
            bool: widget是否可见
        """
        try:
            widget_map = {
                'info': self.image_info_widget,
                'histogram': self.combined_analysis_widget, 
                'rgb_parade': self.rgb_parade_widget,
                'hue_saturation': self.hue_saturation_widget,
                'lab_analysis': self.lab_analysis_widget
            }
            
            widget = widget_map.get(widget_name)
            if widget:
                return widget.isVisible()
            else:
                logger.warning(f"未知的widget名称: {widget_name}")
                return False
                
        except Exception as e:
            logger.error(f"检查widget可见性时发生错误: {e}")
            return False
    
    def get_widget_status(self) -> Dict[str, Any]:
        """
        获取所有widget的状态信息
        
        Returns:
            dict: 包含widget状态的字典
        """
        try:
            status = {
                'current_tab': self.get_current_tab_index(),
                'total_tabs': self.get_total_tabs_count(),
                'widgets': {
                    'image_info': {
                        'visible': self.is_widget_visible('info'),
                        'type': type(self.image_info_widget).__name__
                    },
                    'combined_analysis': {
                        'visible': self.is_widget_visible('histogram'),
                        'type': type(self.combined_analysis_widget).__name__
                    },
                    'rgb_parade': {
                        'visible': self.is_widget_visible('rgb_parade'),
                        'type': type(self.rgb_parade_widget).__name__
                    },
                    'hue_saturation': {
                        'visible': self.is_widget_visible('hue_saturation'),
                        'type': type(self.hue_saturation_widget).__name__
                    },
                    'lab_analysis': {
                        'visible': self.is_widget_visible('lab_analysis') if self.lab_analysis_widget else False,
                        'type': type(self.lab_analysis_widget).__name__ if self.lab_analysis_widget else None
                    }
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"获取widget状态时发生错误: {e}")
            return {'error': str(e)}
    
    def refresh_all_widgets(self):
        """
        刷新所有widget的显示状态
        """
        try:
            # 强制刷新所有widget
            widgets = [
                self.image_info_widget,
                self.combined_analysis_widget,
                self.rgb_parade_widget,
                self.hue_saturation_widget
            ]
            
            if self.lab_analysis_widget:
                widgets.append(self.lab_analysis_widget)
            
            for widget in widgets:
                if hasattr(widget, 'update'):
                    widget.update()
                if hasattr(widget, 'repaint'):
                    widget.repaint()
            
            logger.debug("已刷新所有widget显示")
            
        except Exception as e:
            logger.error(f"刷新widget显示时发生错误: {e}")