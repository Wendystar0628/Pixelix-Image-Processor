#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQtGraph版本的组合分析控件
将直方图和亮度波形图组合在一起
"""

import numpy as np

from .pyqtgraph_histogram_widget import PyQtGraphHistogramWidget
from .pyqtgraph_luma_waveform_widget import PyQtGraphLumaWaveformWidget
from .pyqtgraph_base_widget import PyQtGraphBaseWidget


class PyQtGraphCombinedAnalysisWidget(PyQtGraphBaseWidget):
    """
    基于PyQtGraph的组合分析控件，包含直方图和亮度波形
    使用PyQtGraph库提供高性能渲染
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 获取主布局
        layout = self.layout()
        
        # 创建直方图控件
        self.histogram_widget = PyQtGraphHistogramWidget()
        layout.addWidget(self.histogram_widget)
        
        # 创建亮度波形图控件
        self.waveform_widget = PyQtGraphLumaWaveformWidget()
        layout.addWidget(self.waveform_widget)

    def update_views(self, analysis_data):
        """
        使用预先计算好的分析数据更新直方图和波形图。
        
        Args:
            analysis_data: 包含直方图和波形图数据的字典
        """
        # 存储分析数据
        self.store_analysis_data(analysis_data)
        
        # 更新直方图
        histogram_data = analysis_data.get('histogram')
        if histogram_data is not None:
            self.histogram_widget.update_histogram_with_data(histogram_data)
        else:
            self.histogram_widget.clear_histogram()
        
        # 更新波形图
        waveform_data = analysis_data.get('rgb_parade')
        if waveform_data is not None and len(waveform_data) > 0:
            # 使用第一个通道作为亮度波形（通常是红色通道）
            luma_waveform = waveform_data[0]
            self.waveform_widget.update_waveform_with_data(luma_waveform)
        else:
            self.waveform_widget.clear_waveform()

    def clear_views(self):
        """清除所有视图"""
        self.histogram_widget.clear_histogram()
        self.waveform_widget.clear_waveform()
        
        # 清除分析数据
        self.clear_analysis_data()