#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQtGraph版本的RGB Parade控件
使用PyQtGraph库提供高性能渲染
"""

import cv2
import numpy as np
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel
import pyqtgraph as pg
from pyqtgraph import PlotWidget

from app.core import ImageAnalysisEngine
from .pyqtgraph_base_widget import PyQtGraphBaseWidget
from .pyqtgraph_utils import create_channel_colors


class PyQtGraphRGBParadeWidget(PyQtGraphBaseWidget):
    """
    基于PyQtGraph的RGB Parade控件，提供高性能渲染
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 获取主布局
        main_layout = self.layout()
        
        # 创建垂直布局用于放置三个通道的波形图（保持与原版一致的上下排布）
        plots_layout = QVBoxLayout()
        main_layout.addLayout(plots_layout)
        
        # 创建三个绘图控件（R、G、B）
        self.r_plot = PlotWidget()
        self.g_plot = PlotWidget()
        self.b_plot = PlotWidget()
        
        # 添加到布局
        plots_layout.addWidget(self.r_plot)
        plots_layout.addWidget(self.g_plot)
        plots_layout.addWidget(self.b_plot)
        
        # 配置绘图控件
        self._setup_plot_widgets()
        
        # 创建图像项目用于显示波形数据
        self.r_image = pg.ImageItem()
        self.g_image = pg.ImageItem()
        self.b_image = pg.ImageItem()
        
        # 添加图像项目到绘图控件
        self.r_plot.addItem(self.r_image)
        self.g_plot.addItem(self.g_image)
        self.b_plot.addItem(self.b_image)
        
        # 使用工具函数获取通道颜色
        self.channel_colors = create_channel_colors()
        
    def _setup_plot_widgets(self):
        """配置三个绘图控件的基本属性"""
        plots = [self.r_plot, self.g_plot, self.b_plot]
        titles = ['红色通道', '绿色通道', '蓝色通道']
        
        for plot, title in zip(plots, titles):
            # 使用基类方法配置图像绘图控件
            self._configure_image_plot_widget(
                plot,
                title=title,
                y_label='强度值',
                x_label='水平位置'
            )
        
    def _setup_single_plot_widget(self, plot_widget: PlotWidget, title: str, color: str):
        """配置单个绘图控件"""
        # 设置标题和标签
        plot_widget.setLabel('left', title)
        plot_widget.setLabel('bottom', '水平位置')
        plot_widget.setTitle(title)
        
        # 设置Y轴范围（像素值0-255）
        plot_widget.setYRange(0, 255)
        
        # 启用网格
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # 设置背景颜色
        plot_widget.setBackground('w')  # 白色背景
        
        # 设置Y轴刻度
        y_ticks = [0, 64, 128, 192, 255]
        y_axis = plot_widget.getAxis('left')
        y_axis.setTicks([[(v, str(v)) for v in y_ticks]])
        
    def update_rgb_parade_with_data(self, rgb_parade_data):
        """
        使用预先计算好的RGB Parade数据绘制波形图。
        
        Args:
            rgb_parade_data: 预先计算好的RGB Parade数据，包含三个通道的波形数据（彩色图像）或一个通道的波形数据（灰度图像）
        """
        if rgb_parade_data is None or len(rgb_parade_data) == 0:
            self.clear_rgb_parade()
            return
            
        # 检查是否为灰度图像（只有一个通道）
        if len(rgb_parade_data) == 1:
            # 灰度图像：将同一数据显示在所有三个通道中
            grayscale_data = rgb_parade_data[0]
            data_to_plot = [grayscale_data, grayscale_data, grayscale_data]  # R, G, B都使用相同数据
        elif len(rgb_parade_data) >= 3:
            # 彩色图像：获取三个通道的数据
            # OpenCV的split返回的是B, G, R，我们需要正确映射到R, G, B显示
            data_to_plot = [rgb_parade_data[2], rgb_parade_data[1], rgb_parade_data[0]]  # R, G, B
        else:
            # 处理异常情况：数据不完整
            self.clear_rgb_parade()
            return
        
        # 使用基类方法设置图像项目，应用对数缩放以增强低强度值的可见性
        images = [self.r_image, self.g_image, self.b_image]
        
        for image, data in zip(images, data_to_plot):
            # 对数据进行对数缩放以增强低强度值的可见性（与matplotlib版本一致）
            log_data = np.log1p(data)
            self._setup_image_item(image, log_data)
        
        # 设置X轴范围以匹配图像宽度
        width = rgb_parade_data[0].shape[1]
        for plot in [self.r_plot, self.g_plot, self.b_plot]:
            plot.setXRange(0, width)
        
        # 设置颜色映射
        self._setup_colormaps()
        
        # 存储分析数据
        self.store_analysis_data({'rgb_parade': rgb_parade_data})
        
    def update_parade(self, analysis_results: dict):
        """
        使用预先计算好的分析结果更新RGB波形图。
        保持与Matplotlib版本的接口一致。
        
        Args:
            analysis_results: 包含分析结果的字典，期望包含'rgb_parade'键
        """
        # 存储最新的完整分析数据，以备将来使用（如导出）
        self.store_analysis_data(analysis_results.copy())
        
        # 从结果字典中提取所需的数据
        parade_data = analysis_results.get('rgb_parade')
        
        if parade_data is None or len(parade_data) == 0:
            self.clear_rgb_parade()
            return
            
        self.update_rgb_parade_with_data(parade_data)
        
    def clear_view(self):
        """
        清空视图并显示无图像状态。
        保持与Matplotlib版本的接口一致。
        """
        self.clear_rgb_parade()
        
    def clear_rgb_parade(self):
        """清除RGB Parade数据"""
        # 清除图像数据
        self.r_image.clear()
        self.g_image.clear()
        self.b_image.clear()
        
        # 使用基类方法设置无数据标题
        plots = [self.r_plot, self.g_plot, self.b_plot]
        titles = ['红色通道', '绿色通道', '蓝色通道']
        
        for plot, title in zip(plots, titles):
            self._set_no_data_title(plot, title)
        
        # 清除分析数据
        self.clear_analysis_data()
        
    def _setup_colormaps(self):
        """设置颜色映射"""
        try:
            # 为每个通道设置对应的颜色映射
            r_colormap = pg.colormap.get('Reds')
            g_colormap = pg.colormap.get('Greens')
            b_colormap = pg.colormap.get('Blues')
            
            self.r_image.setColorMap(r_colormap)
            self.g_image.setColorMap(g_colormap)
            self.b_image.setColorMap(b_colormap)
        except:
            # 如果指定的颜色映射不存在，使用默认的viridis
            default_colormap = pg.colormap.get('viridis')
            self.r_image.setColorMap(default_colormap)
            self.g_image.setColorMap(default_colormap)
            self.b_image.setColorMap(default_colormap)