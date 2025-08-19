"""
PyQtGraph版本的Lab色彩空间分析控件
"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget, GraphicsLayoutWidget
from PyQt6.QtWidgets import QHBoxLayout, QLabel

from .pyqtgraph_base_widget import PyQtGraphBaseWidget

# 尝试导入OpenGL，如果失败则使用2D替代方案
try:
    import pyqtgraph.opengl as gl
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False


class PyQtGraphLabAnalysisWidget(PyQtGraphBaseWidget):
    """
    基于PyQtGraph的Lab色彩空间分析控件
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 获取布局
        layout = self.layout()
        
        # 创建垂直布局容器
        from PyQt6.QtWidgets import QVBoxLayout
        container_layout = QVBoxLayout()
        
        # 创建2D散点图控件
        self.plot_2d = PlotWidget()
        self._setup_2d_plot()
        container_layout.addWidget(self.plot_2d, 1)  # 添加拉伸因子
        
        # 创建3D可视化控件（如果OpenGL可用）
        if OPENGL_AVAILABLE:
            self.plot_3d = gl.GLViewWidget()
            self._setup_3d_plot()
            container_layout.addWidget(self.plot_3d, 1)  # 添加拉伸因子，确保两个控件平分空间
        else:
            # 如果OpenGL不可用，显示提示信息
            self.plot_3d = QLabel("3D visualization requires OpenGL\nPlease install PyOpenGL")
            self.plot_3d.setStyleSheet("QLabel { color: gray; text-align: center; }")
            container_layout.addWidget(self.plot_3d, 1)  # 添加拉伸因子
        
        # 添加到主布局
        from PyQt6.QtWidgets import QWidget
        container = QWidget()
        container.setLayout(container_layout)
        layout.addWidget(container)
        
        # 存储绘图项目引用
        self.scatter_2d = None
        self.scatter_3d = None

    def _setup_2d_plot(self):
        """配置2D散点图"""
        self._configure_plot_widget(
            self.plot_2d,
            title='a*b* Chromaticity',
            x_label='a* (Green <- -> Red)',
            y_label='b* (Blue <- -> Yellow)'
        )
        
        # 设置坐标轴范围
        self.plot_2d.setXRange(-128, 127)
        self.plot_2d.setYRange(-128, 127)
        
        # 添加网格
        self.plot_2d.showGrid(x=True, y=True, alpha=0.3)

    def _setup_3d_plot(self):
        """配置3D可视化"""
        if not OPENGL_AVAILABLE:
            return
            
        # 设置3D视图的基本属性
        self.plot_3d.setCameraPosition(distance=300)
        
        # 添加坐标轴
        axis = gl.GLAxisItem()
        axis.setSize(x=256, y=256, z=100)
        self.plot_3d.addItem(axis)

    def update_lab_analysis_with_data(self, lab_data):
        """
        使用预计算的Lab分析数据更新显示
        
        Args:
            lab_data: 包含chromaticity和3d数据的字典
        """
        if not lab_data:
            self.clear_lab_analysis()
            return
            
        # 更新2D色度散点图
        if 'lab_chromaticity' in lab_data:
            self._plot_chromaticity_scatter(lab_data['lab_chromaticity'])
            
        # 更新3D可视化
        if 'lab_3d' in lab_data:
            self._plot_3d_visualization(lab_data['lab_3d'])

    def _plot_chromaticity_scatter(self, chromaticity_data):
        """
        绘制a*b*色度散点图
        
        Args:
            chromaticity_data: 色度数据字典
        """
        # 清除旧的散点图
        if self.scatter_2d is not None:
            self.plot_2d.removeItem(self.scatter_2d)
            self.scatter_2d = None
            
        if not chromaticity_data:
            return
            
        a_values = chromaticity_data.get('a_star', [])
        b_values = chromaticity_data.get('b_star', [])
        l_values = chromaticity_data.get('l_values', [])
        
        if len(a_values) > 0 and len(b_values) > 0:
            # 创建颜色映射
            if len(l_values) > 0:
                # 根据L值创建颜色
                colors = self._create_color_map(l_values)
            else:
                colors = [(0, 0, 255, 100)] * len(a_values)  # 默认蓝色
            
            # 创建散点图
            self.scatter_2d = pg.ScatterPlotItem(
                x=a_values,
                y=b_values,
                brush=colors,
                size=3,
                pen=None
            )
            
            self.plot_2d.addItem(self.scatter_2d)

    def _plot_3d_visualization(self, lab_3d_data):
        """
        绘制Lab 3D可视化
        
        Args:
            lab_3d_data: 3D数据字典
        """
        if not OPENGL_AVAILABLE:
            return
            
        # 清除旧的3D散点图
        if self.scatter_3d is not None:
            self.plot_3d.removeItem(self.scatter_3d)
            
        if not lab_3d_data:
            return
            
        l_coords = lab_3d_data.get('l_coords', [])
        a_coords = lab_3d_data.get('a_coords', [])
        b_coords = lab_3d_data.get('b_coords', [])
        
        if len(l_coords) > 0 and len(a_coords) > 0 and len(b_coords) > 0:
            # 准备3D坐标数据
            pos = np.column_stack((a_coords, b_coords, l_coords))
            
            # 创建颜色映射
            colors = self._create_color_map(l_coords)
            
            # 创建3D散点图 - 使用单一颜色避免颜色映射问题
            self.scatter_3d = gl.GLScatterPlotItem(
                pos=pos,
                color=(0.5, 0.8, 1.0, 0.6),  # 单一颜色：浅蓝色
                size=2,
                pxMode=True
            )
            
            self.plot_3d.addItem(self.scatter_3d)

    def _create_color_map(self, values):
        """
        根据数值创建颜色映射
        
        Args:
            values: 数值数组
            
        Returns:
            颜色数组
        """
        if len(values) == 0:
            return []
            
        # 归一化值到0-1范围
        min_val = np.min(values)
        max_val = np.max(values)
        
        if max_val == min_val:
            # 所有值相同，使用单一颜色
            return [(0, 0, 255, 100)] * len(values)
            
        normalized = (values - min_val) / (max_val - min_val)
        
        # 创建颜色映射（从蓝色到黄色）
        colors = []
        for norm_val in normalized:
            r = int(norm_val * 255)  # 0-255范围
            g = int(norm_val * 255)  # 0-255范围
            b = int((1 - norm_val) * 255)  # 0-255范围
            colors.append((r, g, b, 150))  # RGBA格式，0-255范围
            
        return colors

    def clear_lab_analysis(self):
        """清除所有Lab分析数据"""
        # 清除2D散点图
        if self.scatter_2d is not None:
            self.plot_2d.removeItem(self.scatter_2d)
            self.scatter_2d = None
            
        # 清除3D散点图
        if OPENGL_AVAILABLE and self.scatter_3d is not None:
            self.plot_3d.removeItem(self.scatter_3d)
            self.scatter_3d = None
            
        # 重置标题
        self.plot_2d.setTitle('a*b* Chromaticity')
        
        # 清除分析数据
        self.clear_analysis_data()