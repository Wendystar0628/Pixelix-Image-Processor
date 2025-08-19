#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQtGraph控件基类
提供所有PyQtGraph控件的通用功能，减少代码重复
"""

import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
from pyqtgraph import PlotWidget


class PyQtGraphBaseWidget(QWidget):
    """
    PyQtGraph控件的基类，提供通用功能
    
    所有基于PyQtGraph的分析控件都应该继承此类，以获得：
    - 统一的布局设置
    - 通用的绘图控件配置
    - 标准化的数据存储
    - 一致的清除方法
    """
    
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        
        # 存储最新的分析数据
        self.latest_analysis_data = {}
        
        # 设置基本布局
        self._setup_layout()
        
    def _setup_layout(self) -> QVBoxLayout:
        """
        设置基本布局
        
        Returns:
            QVBoxLayout: 创建的布局对象
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        return layout
        
    def _configure_plot_widget(self, plot_widget: PlotWidget, 
                             title: str = "", 
                             y_label: str = "", 
                             x_label: str = "") -> None:
        """
        配置绘图控件的通用属性
        
        Args:
            plot_widget: 要配置的绘图控件
            title: 图表标题
            y_label: Y轴标签
            x_label: X轴标签
        """
        if title:
            plot_widget.setTitle(title)
        if y_label:
            plot_widget.setLabel('left', y_label)
        if x_label:
            plot_widget.setLabel('bottom', x_label)
            
        # 设置通用样式
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        plot_widget.setBackground('w')  # 白色背景
        
    def _configure_image_plot_widget(self, plot_widget: PlotWidget, 
                                    title: str = "", 
                                    y_label: str = "", 
                                    x_label: str = "") -> None:
        """
        配置用于图像显示的绘图控件
        
        这个方法专门用于显示图像数据的绘图控件，
        会设置0-255的Y轴范围和标准刻度
        
        Args:
            plot_widget: 要配置的绘图控件
            title: 图表标题
            y_label: Y轴标签
            x_label: X轴标签
        """
        # 应用基本配置
        self._configure_plot_widget(plot_widget, title, y_label, x_label)
        
        # 设置图像特定的配置
        plot_widget.setYRange(0, 255)
        
        # 设置Y轴刻度
        y_ticks = [0, 64, 128, 192, 255]
        y_axis = plot_widget.getAxis('left')
        y_axis.setTicks([[(v, str(v)) for v in y_ticks]])
        
    def _setup_image_item(self, image_item, data: np.ndarray, 
                         width: int | None = None, 
                         height: int | None = None) -> None:
        """
        设置图像项目的通用属性
        
        Args:
            image_item: PyQtGraph的ImageItem对象
            data: 图像数据
            width: 图像宽度（如果为None，从data.shape推断）
            height: 图像高度（如果为None，从data.shape推断）
        """
        # 对数缩放以增强低强度值的可见性
        log_data = np.log1p(data)
        
        # 设置图像数据
        image_item.setImage(
            log_data,
            autoLevels=True,  # 自动调整颜色范围
            autoDownsample=True  # 自动降采样以提高性能
        )
        
        # 设置图像矩形
        if width is None or height is None:
            height, width = data.shape
        image_item.setRect(0, 0, width, 255)
        
    def store_analysis_data(self, results: dict | None) -> None:
        """
        存储分析数据
        
        Args:
            results: 分析结果字典
        """
        self.latest_analysis_data = results.copy() if results else {}
        
    def clear_analysis_data(self) -> None:
        """
        清除存储的分析数据
        """
        self.latest_analysis_data = {}
        
    def _set_no_data_title(self, plot_widget: PlotWidget, base_title: str) -> None:
        """
        设置无数据状态的标题
        
        Args:
            plot_widget: 绘图控件
            base_title: 基础标题
        """
        plot_widget.setTitle(f"{base_title} - 无数据")
        
    def _clear_plot_items(self, plot_widget: PlotWidget, items: list) -> None:
        """
        清除绘图项目
        
        Args:
            plot_widget: 绘图控件
            items: 要清除的绘图项目列表
        """
        for item in items:
            if item is not None:
                plot_widget.removeItem(item)
        items.clear()
        
    def _clear_legend(self, plot_widget: PlotWidget) -> None:
        """
        清除图例
        
        Args:
            plot_widget: 绘图控件
        """
        legend = plot_widget.plotItem.legend
        if legend is not None:
            legend.scene().removeItem(legend)
            plot_widget.plotItem.legend = None