#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQtGraph版本的亮度波形图控件
使用PyQtGraph库提供高性能渲染
"""

import cv2
import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget, ImageItem

from app.core import ImageAnalysisEngine
from .pyqtgraph_base_widget import PyQtGraphBaseWidget
from .pyqtgraph_utils import get_colormap_name


class PyQtGraphLumaWaveformWidget(PyQtGraphBaseWidget):
    """
    基于PyQtGraph的亮度波形图控件，提供高性能渲染
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
        
        # 创建图像项目用于显示波形数据
        self.image_item = ImageItem()
        self.plot_widget.addItem(self.image_item)
        
    def _setup_plot_widget(self):
        """配置绘图控件的基本属性"""
        # 使用基类方法配置图像绘图控件
        self._configure_image_plot_widget(
            self.plot_widget,
            title='亮度波形图',
            y_label='亮度值',
            x_label='水平位置'
        )
        
    def update_waveform(self, image: np.ndarray | None):
        """
        计算并绘制亮度波形图。
        
        注意: 此方法在主线程中计算波形图数据，可能会导致UI阻塞。
        推荐使用update_waveform_with_data方法，它接受预先计算好的波形数据。
        
        Args:
            image: 输入图像数据(NumPy数组)或None
        """
        if image is None:
            self.clear_waveform()
            return
            
        if image.ndim == 3:
            # 使用 cv2 转换为灰度图
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image
            
        parade_data = ImageAnalysisEngine.get_rgb_parade_efficient(gray_image)
        self.update_waveform_with_data(parade_data[0] if parade_data else None)
        
    def update_waveform_with_data(self, waveform_data):
        """
        使用预先计算好的波形数据绘制亮度波形图。
        
        Args:
            waveform_data: 预先计算好的亮度波形数据，通常是RGB波形数据的第一个通道
        """
        if waveform_data is None:
            self.clear_waveform()
            return
            
        # 使用基类方法设置图像项目
        self._setup_image_item(self.image_item, waveform_data)
        
        # 设置X轴范围以匹配图像宽度
        height, width = waveform_data.shape
        self.plot_widget.setXRange(0, width)
        
        # 设置颜色映射
        self._setup_colormap()
        
    def _setup_colormap(self):
        """设置颜色映射"""
        # 使用工具函数获取颜色映射名称
        colormap_name = get_colormap_name('viridis')
        colormap = pg.colormap.get(colormap_name)
        self.image_item.setColorMap(colormap)
        
    def clear_waveform(self):
        """清除波形图数据"""
        # 清除图像数据
        self.image_item.clear()
        
        # 使用基类方法设置无数据标题
        self._set_no_data_title(self.plot_widget, '亮度波形图')
        
        # 清除分析数据
        self.clear_analysis_data()