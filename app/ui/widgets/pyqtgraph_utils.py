#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQtGraph工具函数模块
提供PyQtGraph控件使用的通用工具函数
"""

import colorsys
from typing import List, Tuple


def create_hue_colors(num_bins: int) -> List[Tuple[int, int, int, int]]:
    """
    创建色相颜色数组，模拟HSV色轮
    
    Args:
        num_bins: 颜色数量
        
    Returns:
        List[Tuple[int, int, int, int]]: RGBA颜色元组列表
    """
    colors = []
    for i in range(num_bins):
        hue_angle = i / num_bins  # 0-1范围
        # 将HSV转换为RGB（饱和度和明度设为最大）
        r, g, b = colorsys.hsv_to_rgb(hue_angle, 1.0, 1.0)
        colors.append((int(r*255), int(g*255), int(b*255), 180))  # 添加透明度
    return colors


def create_gradient_colors(num_bins: int, 
                         base_color: Tuple[int, int, int] = (0, 0, 255)) -> List[Tuple[int, int, int, int]]:
    """
    创建渐变颜色数组
    
    Args:
        num_bins: 颜色数量
        base_color: 基础颜色 (R, G, B)
        
    Returns:
        List[Tuple[int, int, int, int]]: RGBA颜色元组列表
    """
    colors = []
    r_base, g_base, b_base = base_color
    
    for i in range(num_bins):
        intensity = 0.3 + 0.7 * (i / num_bins)  # 从30%到100%的强度
        colors.append((
            int(r_base * intensity), 
            int(g_base * intensity), 
            int(b_base * intensity), 
            180  # 透明度
        ))
    return colors


def create_channel_colors() -> List[Tuple[str, str]]:
    """
    创建RGB通道的颜色和名称映射
    
    Returns:
        List[Tuple[str, str]]: (颜色名称, 显示名称) 元组列表
    """
    return [
        ('red', '红色'),
        ('green', '绿色'), 
        ('blue', '蓝色')
    ]


def create_histogram_colors() -> List[str]:
    """
    创建直方图的标准颜色列表（BGR顺序，对应OpenCV格式）
    
    Returns:
        List[str]: 颜色名称列表
    """
    return ['blue', 'green', 'red']


def create_histogram_names() -> List[str]:
    """
    创建直方图的标准名称列表
    
    Returns:
        List[str]: 通道名称列表
    """
    return ['蓝色', '绿色', '红色']


def get_standard_y_ticks() -> List[int]:
    """
    获取标准的Y轴刻度（用于0-255范围的图表）
    
    Returns:
        List[int]: Y轴刻度值列表
    """
    return [0, 64, 128, 192, 255]


def get_colormap_name(channel_type: str) -> str:
    """
    根据通道类型获取合适的颜色映射名称
    
    Args:
        channel_type: 通道类型 ('red', 'green', 'blue', 'gray', 'viridis')
        
    Returns:
        str: PyQtGraph颜色映射名称
    """
    colormap_mapping = {
        'red': 'Reds',
        'green': 'Greens', 
        'blue': 'Blues',
        'gray': 'viridis',
        'viridis': 'viridis'
    }
    return colormap_mapping.get(channel_type, 'viridis')


def create_lab_colormap(l_values):
    """
    为a*b*散点图创建基于L值的色彩映射
    
    Args:
        l_values: L通道值数组
        
    Returns:
        颜色数组
    """
    import numpy as np
    
    if len(l_values) == 0:
        return []
        
    # 归一化L值到0-1范围
    min_val = np.min(l_values)
    max_val = np.max(l_values)
    
    if max_val == min_val:
        return [(128, 128, 128, 100)] * len(l_values)
        
    normalized = (l_values - min_val) / (max_val - min_val)
    
    # 创建从暗到亮的颜色映射
    colors = []
    for norm_val in normalized:
        intensity = int(norm_val * 255)
        colors.append((intensity, intensity, intensity, 150))
        
    return colors


def create_chromaticity_grid():
    """创建a*b*色度空间的网格线配置"""
    return {
        'x_range': (-128, 127),
        'y_range': (-128, 127),
        'grid_spacing': 32,
        'alpha': 0.3
    }


def optimize_lab_data_for_rendering(data, max_points=10000):
    """
    优化Lab数据以提高渲染性能
    
    Args:
        data: 原始数据字典
        max_points: 最大数据点数量
        
    Returns:
        优化后的数据字典
    """
    import numpy as np
    
    if not data or len(data) == 0:
        return data
        
    # 获取数据长度
    data_length = len(next(iter(data.values())))
    
    if data_length <= max_points:
        return data
        
    # 计算采样步长
    step = max(1, data_length // max_points)
    
    # 对所有数据进行采样
    optimized_data = {}
    for key, values in data.items():
        if isinstance(values, np.ndarray):
            optimized_data[key] = values[::step]
        else:
            optimized_data[key] = values
            
    return optimized_data