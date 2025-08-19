"""
Lab色彩空间分析控件 - matplotlib版本
"""

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QVBoxLayout, QWidget
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class LabAnalysisWidget(QWidget):
    """
    Lab色彩空间分析控件，显示a*b*色度散点图和3D可视化
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建matplotlib图形画布
        self.canvas = FigureCanvas(Figure(figsize=(10, 8)))
        layout.addWidget(self.canvas)

        # 创建子图布局
        self.fig = self.canvas.figure
        self.ax_2d = None
        self.ax_3d = None
        self.colorbar_2d = None  # 存储2D散点图的颜色条引用
        self._setup_subplots()

    def _setup_subplots(self):
        """设置子图布局"""
        self.fig.clear()
        
        # 创建2D散点图子图（上方）
        self.ax_2d = self.fig.add_subplot(211)
        self.ax_2d.set_title("a*b* Chromaticity")
        self.ax_2d.set_xlabel("a* (Green <- -> Red)")
        self.ax_2d.set_ylabel("b* (Blue <- -> Yellow)")
        self.ax_2d.grid(True, alpha=0.3)
        self.ax_2d.set_xlim(-128, 127)
        self.ax_2d.set_ylim(-128, 127)
        
        # 创建3D可视化子图（下方）
        self.ax_3d = self.fig.add_subplot(212, projection='3d')
        self.ax_3d.set_title("Lab 3D Color Space")
        self.ax_3d.set_xlabel("a*")
        self.ax_3d.set_ylabel("b*")
        self.ax_3d.set_zlabel("L*")
        
        self.fig.tight_layout()
        self.canvas.draw()

    def update_lab_analysis_with_data(self, lab_data):
        """
        使用预计算的Lab分析数据更新显示
        
        Args:
            lab_data: 包含chromaticity和3d数据的字典
        """
        if not lab_data or ('lab_chromaticity' not in lab_data and 'lab_3d' not in lab_data):
            self._clear_plots()
            return
            
        # 更新2D色度散点图
        if 'lab_chromaticity' in lab_data:
            self._plot_chromaticity_scatter(lab_data['lab_chromaticity'])
            
        # 更新3D可视化
        if 'lab_3d' in lab_data:
            self._plot_3d_visualization(lab_data['lab_3d'])
            
        self.canvas.draw()

    def _plot_chromaticity_scatter(self, chromaticity_data):
        """
        绘制a*b*色度散点图
        
        Args:
            chromaticity_data: 色度数据字典
        """
        if not chromaticity_data or len(chromaticity_data) == 0:
            return
        
        # 清除旧的颜色条
        if self.colorbar_2d is not None:
            self.colorbar_2d.remove()
            self.colorbar_2d = None
            
        self.ax_2d.clear()
        self.ax_2d.set_title("a*b* Chromaticity")
        self.ax_2d.set_xlabel("a* (Green <- -> Red)")
        self.ax_2d.set_ylabel("b* (Blue <- -> Yellow)")
        self.ax_2d.grid(True, alpha=0.3)
        self.ax_2d.set_xlim(-128, 127)
        self.ax_2d.set_ylim(-128, 127)
        
        a_values = chromaticity_data.get('a_star', [])
        b_values = chromaticity_data.get('b_star', [])
        l_values = chromaticity_data.get('l_values', [])
        
        if len(a_values) > 0 and len(b_values) > 0:
            # 使用L值作为颜色映射
            scatter = self.ax_2d.scatter(
                a_values, b_values, 
                c=l_values if len(l_values) > 0 else 'blue',
                cmap='viridis', 
                alpha=0.6, 
                s=1
            )
            
            # 添加颜色条并保存引用
            if len(l_values) > 0:
                self.colorbar_2d = self.fig.colorbar(scatter, ax=self.ax_2d)
                self.colorbar_2d.set_label('L* (Lightness)')

    def _plot_3d_visualization(self, lab_3d_data):
        """
        绘制Lab 3D可视化
        
        Args:
            lab_3d_data: 3D数据字典
        """
        if not lab_3d_data or len(lab_3d_data) == 0:
            return
            
        self.ax_3d.clear()
        self.ax_3d.set_title("Lab 3D Color Space")
        self.ax_3d.set_xlabel("a*")
        self.ax_3d.set_ylabel("b*")
        self.ax_3d.set_zlabel("L*")
        
        l_coords = lab_3d_data.get('l_coords', [])
        a_coords = lab_3d_data.get('a_coords', [])
        b_coords = lab_3d_data.get('b_coords', [])
        
        if len(l_coords) > 0 and len(a_coords) > 0 and len(b_coords) > 0:
            # 3D散点图
            self.ax_3d.scatter(
                a_coords, b_coords, l_coords,
                c=l_coords,
                cmap='viridis',
                alpha=0.6,
                s=1
            )
            
            # 设置坐标轴范围
            self.ax_3d.set_xlim(-128, 127)
            self.ax_3d.set_ylim(-128, 127)
            self.ax_3d.set_zlim(0, 100)

    def _clear_plots(self):
        """清除所有图表"""
        # 清除颜色条引用
        if self.colorbar_2d is not None:
            self.colorbar_2d.remove()
            self.colorbar_2d = None
        
        self._setup_subplots()
        self.canvas.draw()
    
    def clear_lab_analysis(self):
        """清除所有Lab分析数据"""
        self._clear_plots()
    
    def get_figure(self):
        """获取matplotlib Figure对象"""
        return self.fig
    
    def export_to_file(self, file_path: str, format_type: str = 'png', quality: int = 95) -> bool:
        """
        导出图表到文件
        
        Args:
            file_path: 输出文件路径
            format_type: 文件格式 ('png', 'jpeg', 'svg')
            quality: JPEG质量(1-100)
            
        Returns:
            bool: 是否导出成功
        """
        try:
            from app.utils.matplotlib_export_utils import MatplotlibExportUtils
            from app.core.models.analysis_export_config import AnalysisChartFormat
            
            # 转换格式类型
            format_map = {
                'png': AnalysisChartFormat.PNG,
                'jpeg': AnalysisChartFormat.JPEG,
                'svg': AnalysisChartFormat.SVG
            }
            chart_format = format_map.get(format_type.lower(), AnalysisChartFormat.PNG)
            
            return MatplotlibExportUtils.save_figure_to_file(
                self.fig, file_path, chart_format, quality
            )
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"导出Lab分析图表失败: {e}")
            return False