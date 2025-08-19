#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQtGraph版本的直方图控件
使用PyQtGraph库提供高性能渲染
"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget, PlotDataItem

from app.core import ImageAnalysisEngine
from .pyqtgraph_base_widget import PyQtGraphBaseWidget
from .pyqtgraph_utils import create_histogram_colors, create_histogram_names


class PyQtGraphHistogramWidget(PyQtGraphBaseWidget):
    """
    基于PyQtGraph的直方图控件，提供高性能渲染
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 获取布局
        layout = self.layout()
        
        # 创建PyQtGraph绘图控件
        self.plot_widget = PlotWidget()
        layout.addWidget(self.plot_widget)
        
        # 配置绘图区域
        self._setup_plot_widget()
        
        # 存储绘图项目引用
        self.plot_items = []
        
    def _setup_plot_widget(self):
        """配置绘图控件的基本属性"""
        # 使用基类方法配置通用属性
        self._configure_plot_widget(
            self.plot_widget, 
            title='直方图',
            y_label='频率',
            x_label='像素值'
        )
        
        # 设置坐标轴范围
        self.plot_widget.setXRange(0, 255)
        
        # 禁用自动范围调整的某些功能以提高性能
        self.plot_widget.enableAutoRange(axis='y')
        self.plot_widget.setAutoVisible(y=True)
        
    def update_histogram(self, image: np.ndarray | None):
        """
        计算并绘制直方图。
        
        注意: 此方法在主线程中计算直方图，可能会导致UI阻塞。
        推荐使用update_histogram_with_data方法，它接受预先计算好的直方图数据。
        """
        if image is None:
            self.clear_histogram()
            return
            
        hist_data = ImageAnalysisEngine.calculate_histogram(image)
        self.update_histogram_with_data(hist_data)
        
    def update_histogram_with_data(self, hist_data):
        """
        使用预先计算好的直方图数据绘制直方图。
        
        Args:
            hist_data: 预先计算好的直方图数据，格式与ImageAnalysisEngine.calculate_histogram返回值相同
        """
        # 清除旧的绘图项目
        self.clear_histogram()
        
        if hist_data is None or len(hist_data) == 0:
            self.plot_widget.setTitle('无直方图数据')
            return
            
        # 生成x轴数据（0-255的像素值）
        x = np.arange(256)
        
        if len(hist_data) == 1:  # 灰度图
            self._plot_grayscale_histogram(x, hist_data[0])
        elif len(hist_data) == 3:  # 彩色图
            self._plot_color_histogram(x, hist_data)
        else:
            self.plot_widget.setTitle('不支持的直方图格式')
            
    def _plot_grayscale_histogram(self, x: np.ndarray, hist: np.ndarray):
        """绘制灰度直方图"""
        self.plot_widget.setTitle('灰度直方图')
        
        # 创建灰度直方图绘图项目
        plot_item = self.plot_widget.plot(
            x, hist,
            pen=pg.mkPen(color='gray', width=1),
            brush=pg.mkBrush(color=(128, 128, 128, 100)),  # 半透明填充
            fillLevel=0,
            name='灰度'
        )
        self.plot_items.append(plot_item)
        
    def _plot_color_histogram(self, x: np.ndarray, hist_data: list):
        """绘制彩色直方图"""
        self.plot_widget.setTitle('彩色直方图')
        
        # 使用工具函数获取颜色和名称
        colors = create_histogram_colors()
        names = create_histogram_names()
        
        # 绘制每个颜色通道
        for i, (hist, color, name) in enumerate(zip(hist_data, colors, names)):
            plot_item = self.plot_widget.plot(
                x, hist,
                pen=pg.mkPen(color=color, width=2),
                name=name
            )
            self.plot_items.append(plot_item)
            
        # 添加图例
        self.plot_widget.addLegend()
        
    def clear_histogram(self):
        """清除所有直方图数据"""
        # 使用基类方法清除绘图项目
        self._clear_plot_items(self.plot_widget, self.plot_items)
        
        # 使用基类方法清除图例
        self._clear_legend(self.plot_widget)
            
        # 重置标题
        self.plot_widget.setTitle('直方图')
        
        # 清除分析数据
        self.clear_analysis_data()