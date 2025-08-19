"""
matplotlib图表导出工具
"""

import os
import logging
from typing import Optional
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from app.core.models.analysis_export_config import AnalysisChartFormat

logger = logging.getLogger(__name__)


class MatplotlibExportUtils:
    """matplotlib图表导出工具类"""
    
    @staticmethod
    def save_figure_to_file(figure: Figure, file_path: str, 
                          format_type: AnalysisChartFormat, 
                          quality: int = 95) -> bool:
        """
        保存matplotlib图表到文件
        
        Args:
            figure: matplotlib图表对象
            file_path: 输出文件路径
            format_type: 图表格式
            quality: JPEG质量(1-100)
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 设置保存参数
            save_kwargs = {
                'bbox_inches': 'tight',
                'pad_inches': 0.1,
                'facecolor': 'white',
                'edgecolor': 'none'
            }
            
            if format_type == AnalysisChartFormat.PNG:
                save_kwargs['dpi'] = 100
                save_kwargs['format'] = 'png'
            elif format_type == AnalysisChartFormat.JPEG:
                save_kwargs['dpi'] = 100
                save_kwargs['format'] = 'jpeg'
                # matplotlib的JPEG保存不支持quality参数，使用pil_kwargs
                save_kwargs['pil_kwargs'] = {'quality': quality}
            elif format_type == AnalysisChartFormat.SVG:
                save_kwargs['format'] = 'svg'
                
            # 保存图表
            figure.savefig(file_path, **save_kwargs)
            logger.debug(f"图表已保存到: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存图表失败: {e}")
            return False
    
    @staticmethod
    def get_figure_from_widget(widget) -> Optional[Figure]:
        """
        从matplotlib控件获取Figure对象
        
        Args:
            widget: matplotlib控件
            
        Returns:
            Optional[Figure]: Figure对象，如果获取失败返回None
        """
        try:
            if hasattr(widget, 'canvas') and isinstance(widget.canvas, FigureCanvasQTAgg):
                return widget.canvas.figure
            elif hasattr(widget, 'fig'):
                return widget.fig
            elif hasattr(widget, 'figure'):
                return widget.figure
            else:
                logger.warning(f"无法从控件获取Figure对象: {type(widget)}")
                return None
                
        except Exception as e:
            logger.error(f"获取Figure对象失败: {e}")
            return None
    
    @staticmethod
    def optimize_figure_for_export(figure: Figure):
        """
        优化图表用于导出
        
        Args:
            figure: matplotlib图表对象
        """
        try:
            # 使用默认英文字体，避免中文字体警告
            import matplotlib.pyplot as plt
            
            # 设置为默认英文字体
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 调整布局
            figure.tight_layout()
            
        except Exception as e:
            logger.warning(f"优化图表失败: {e}")
    
    @staticmethod
    def get_file_extension(format_type: AnalysisChartFormat) -> str:
        """
        获取格式对应的文件扩展名
        
        Args:
            format_type: 图表格式
            
        Returns:
            str: 文件扩展名
        """
        format_map = {
            AnalysisChartFormat.PNG: '.png',
            AnalysisChartFormat.JPEG: '.jpg',
            AnalysisChartFormat.SVG: '.svg'
        }
        return format_map.get(format_type, '.png')