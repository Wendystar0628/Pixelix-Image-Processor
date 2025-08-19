#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQtGraph版本的色相/饱和度控件  
使用PyQtGraph库提供高性能渲染
"""

import cv2
import numpy as np
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel
import pyqtgraph as pg
from pyqtgraph import PlotWidget, BarGraphItem

from app.core import ImageAnalysisEngine
from .pyqtgraph_base_widget import PyQtGraphBaseWidget
from .pyqtgraph_utils import create_hue_colors, create_gradient_colors


class PyQtGraphHueSaturationWidget(PyQtGraphBaseWidget):
    """
    基于PyQtGraph的色相/饱和度控件，提供高性能渲染
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 获取主布局
        main_layout = self.layout()
        
        # 创建垂直布局用于放置两个直方图（保持与原版一致的上下排布）
        plots_layout = QVBoxLayout()
        main_layout.addLayout(plots_layout)
        
        # 创建两个绘图控件（色相和饱和度）
        self.hue_plot = PlotWidget()
        self.saturation_plot = PlotWidget()
        
        # 配置绘图控件
        self._setup_plot_widgets()
        
        # 添加到布局
        plots_layout.addWidget(self.hue_plot)
        plots_layout.addWidget(self.saturation_plot)
        
        # 创建柱状图项目
        self.hue_bars = BarGraphItem(x=[], height=[], width=1.0, brush='r')
        self.saturation_bars = BarGraphItem(x=[], height=[], width=1.0, brush='g')
        
        # 添加柱状图项目到绘图控件
        self.hue_plot.addItem(self.hue_bars)
        self.saturation_plot.addItem(self.saturation_bars)
        
    def _setup_plot_widgets(self):
        """配置两个绘图控件的基本属性"""
        # 使用基类方法配置色相直方图
        self._configure_plot_widget(
            self.hue_plot,
            title='色相分布',
            y_label='像素数量',
            x_label='色相值'
        )
        self.hue_plot.setXRange(0, 180)  # 色相范围0-180
        
        # 使用基类方法配置饱和度直方图
        self._configure_plot_widget(
            self.saturation_plot,
            title='饱和度分布',
            y_label='像素数量',
            x_label='饱和度值'
        )
        self.saturation_plot.setXRange(0, 255)  # 饱和度范围0-255
        
    def update_histograms(self, image: np.ndarray | None) -> None:
        """
        根据输入图像更新色相和饱和度直方图。
        
        注意: 此方法在主线程中计算直方图数据，可能会导致UI阻塞。
        推荐使用update_histograms_with_data方法，它接受预先计算好的直方图数据。

        Args:
            image: 输入的图像 (NumPy 数组) 或 None。
        """
        if image is None:
            self.clear_histograms()
            return
            
        hue_hist, sat_hist = ImageAnalysisEngine.get_hue_saturation_histograms(image)
        self._plot_histograms(hue_hist, sat_hist)
        
    def update_histograms_with_data(self, results: dict):
        """
        使用预先计算好的色相和饱和度直方图数据更新显示，并存储原始数据。
        保持与Matplotlib版本的接口一致。
        
        Args:
            results: 包含分析结果的字典，期望包含'hue_histogram'和'sat_histogram'键
        """
        if results is None:
            self.clear_histograms()
            return
            
        # 存储完整的分析数据
        self.store_analysis_data(results.copy())
        
        # 从结果字典中提取所需的数据
        if 'hue_histogram' in results and 'sat_histogram' in results:
            hue_hist = results['hue_histogram']
            sat_hist = results['sat_histogram']
            
            self._plot_histograms(hue_hist, sat_hist)
        else:
            self.clear_histograms()
            
    def _plot_histograms(self, hue_hist, sat_hist):
        """
        绘制色相和饱和度直方图的内部方法
        
        Args:
            hue_hist: 色相直方图数据
            sat_hist: 饱和度直方图数据
        """
        if hue_hist is not None and sat_hist is not None:
            # 绘制色相直方图
            hue_x = np.arange(len(hue_hist))
            hue_colors = create_hue_colors(len(hue_hist))
            
            self.hue_bars.setOpts(
                x=hue_x,
                height=hue_hist,
                width=1.0,
                brushes=hue_colors
            )
            
            # 绘制饱和度直方图
            saturation_x = np.arange(len(sat_hist))
            saturation_colors = create_gradient_colors(len(sat_hist), (0, 0, 255))  # 蓝色渐变
            
            self.saturation_bars.setOpts(
                x=saturation_x,
                height=sat_hist,
                width=1.0,
                brushes=saturation_colors
            )
        
    def clear_histograms(self):
        """清除直方图数据"""
        # 清除柱状图数据
        self.hue_bars.setOpts(x=[], height=[], width=1.0)
        self.saturation_bars.setOpts(x=[], height=[], width=1.0)
        
        # 使用基类方法设置无数据标题
        self._set_no_data_title(self.hue_plot, '色相分布')
        self._set_no_data_title(self.saturation_plot, '饱和度分布')
        
        # 清除分析数据
        self.clear_analysis_data()