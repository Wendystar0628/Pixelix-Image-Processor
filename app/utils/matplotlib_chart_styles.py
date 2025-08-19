#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Matplotlib图表样式配置
提供与主界面Matplotlib控件一致的样式配置
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Any


class MatplotlibChartStyles:
    """Matplotlib图表样式配置类"""
    
    # RGB通道标准颜色
    RGB_COLORS = {
        'red': '#FF0000',
        'green': '#00FF00', 
        'blue': '#0000FF'
    }
    
    # BGR顺序的颜色列表（对应OpenCV格式）
    BGR_COLORS = ['b', 'g', 'r']  # 蓝、绿、红
    BGR_NAMES = ['蓝色通道', '绿色通道', '红色通道']
    
    # 散状波形参数
    SCATTER_PARAMS = {
        'alpha': 0.1,
        'size': 1,
        'marker': ','
    }
    
    # 色相圆环参数
    HUE_RING_PARAMS = {
        'alpha': 0.8,
        'width_factor': 1.0
    }
    
    # 饱和度直方图参数
    SATURATION_PARAMS = {
        'color': 'blue',
        'alpha': 0.7
    }
    
    # Lab散点图参数
    LAB_SCATTER_PARAMS = {
        'alpha': 0.6,
        'size': 1,
        'cmap': 'viridis'
    }
    
    @staticmethod
    def setup_matplotlib_defaults():
        """设置Matplotlib默认参数"""
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
    @staticmethod
    def get_color_histogram_style() -> Dict[str, Any]:
        """获取色彩直方图样式配置"""
        return {
            'colors': MatplotlibChartStyles.BGR_COLORS,
            'labels': MatplotlibChartStyles.BGR_NAMES,
            'alpha': 0.7,
            'linewidth': 1.5
        }
    
    @staticmethod
    def get_rgb_parade_style() -> Dict[str, Any]:
        """获取RGB波形图样式配置"""
        return {
            'cmaps': ['Reds', 'Greens', 'Blues'],
            'aspect': 'auto',
            'origin': 'lower',
            'log_scale': True  # 使用对数缩放增强低强度值可见性
        }
    
    @staticmethod
    def get_luma_waveform_style() -> Dict[str, Any]:
        """获取亮度波形图样式配置"""
        return {
            'cmap': 'viridis',
            'aspect': 'auto',
            'origin': 'lower',
            'log_scale': True
        }
    
    @staticmethod
    def get_hue_histogram_style() -> Dict[str, Any]:
        """获取色相直方图样式配置"""
        return {
            'colormap': 'hsv',
            'alpha': MatplotlibChartStyles.HUE_RING_PARAMS['alpha'],
            'polar': True
        }
    
    @staticmethod
    def get_saturation_histogram_style() -> Dict[str, Any]:
        """获取饱和度直方图样式配置"""
        return {
            'color': MatplotlibChartStyles.SATURATION_PARAMS['color'],
            'alpha': MatplotlibChartStyles.SATURATION_PARAMS['alpha']
        }
    
    @staticmethod
    def get_lab_chromaticity_style() -> Dict[str, Any]:
        """获取Lab色度图样式配置"""
        return {
            'cmap': MatplotlibChartStyles.LAB_SCATTER_PARAMS['cmap'],
            'alpha': MatplotlibChartStyles.LAB_SCATTER_PARAMS['alpha'],
            'size': MatplotlibChartStyles.LAB_SCATTER_PARAMS['size']
        }
    
    @staticmethod
    def create_hue_colors(num_bins: int) -> List[Tuple[float, float, float, float]]:
        """创建色相圆环的颜色映射"""
        colors = plt.get_cmap("hsv")(np.linspace(0, 1, num_bins))
        return colors
    
    @staticmethod
    def apply_log_scaling(data: np.ndarray) -> np.ndarray:
        """应用对数缩放以增强低强度值的可见性"""
        return np.log1p(data)
    
    @staticmethod
    def setup_common_axis_properties(ax, title: str, xlabel: str = '', ylabel: str = ''):
        """设置通用的坐标轴属性"""
        ax.set_title(title)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)