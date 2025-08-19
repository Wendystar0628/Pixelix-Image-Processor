"""
绘图渲染器模块

提供用于将分析数据渲染为图像的工具。
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Optional, Tuple, Any


class PlotRenderer:
    """
    绘图渲染器类，用于将分析数据渲染为图像。
    """
    
    def __init__(self):
        """
        初始化绘图渲染器
        """
        # 设置非交互式后端，避免线程问题
        import matplotlib
        matplotlib.use('Agg')
        
        # 设置全局字体，支持中文
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
    def _ensure_output_directory(self, output_path: str) -> bool:
        """
        确保输出文件的目录存在
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            bool: 目录是否存在或成功创建
        """
        try:
            directory = os.path.dirname(output_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建目录失败: {os.path.dirname(output_path)}, 错误: {str(e)}")
            return False
            
    def render_histogram(self, hist_data: List[np.ndarray], output_path: str) -> None:
        """
        渲染亮度直方图
        
        Args:
            hist_data: 直方图数据
            output_path: 输出文件路径
        """
        # 确保输出目录存在
        if not self._ensure_output_directory(output_path):
            return
            
        # 创建一个新的图形
        plt.figure(figsize=(10, 6))
        
        # 绘制直方图
        if len(hist_data) == 1:  # 灰度图
            plt.plot(hist_data[0], color='gray', label='亮度')
            plt.fill_between(range(256), hist_data[0], alpha=0.3, color='gray')
        else:  # 彩色图
            # 只绘制亮度直方图，使用Y = 0.299R + 0.587G + 0.114B计算亮度
            luma = 0.299 * hist_data[2] + 0.587 * hist_data[1] + 0.114 * hist_data[0]
            plt.plot(luma, color='black', label='亮度')
            plt.fill_between(range(256), luma, alpha=0.3, color='gray')
            
        # 设置图表属性
        plt.title('亮度直方图')
        plt.xlabel('像素值 (0-255)')
        plt.ylabel('频率')
        plt.xlim([0, 255])
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # 保存图像
        plt.tight_layout()
        plt.savefig(output_path, dpi=100)
        plt.close()
        
    def render_rgb_histogram(self, hist_data: List[np.ndarray], output_path: str) -> None:
        """
        渲染RGB直方图
        
        Args:
            hist_data: 直方图数据
            output_path: 输出文件路径
        """
        # 确保输出目录存在
        if not self._ensure_output_directory(output_path):
            return
            
        # 创建一个新的图形
        plt.figure(figsize=(10, 6))
        
        # 绘制直方图
        if len(hist_data) >= 3:  # 彩色图
            colors = ['blue', 'green', 'red']
            labels = ['蓝色', '绿色', '红色']
            
            for i, (color, label) in enumerate(zip(colors, labels)):
                plt.plot(hist_data[i], color=color, label=label)
                plt.fill_between(range(256), hist_data[i], alpha=0.1, color=color)
        else:  # 灰度图
            plt.plot(hist_data[0], color='gray', label='灰度')
            plt.fill_between(range(256), hist_data[0], alpha=0.3, color='gray')
            
        # 设置图表属性
        plt.title('RGB直方图')
        plt.xlabel('像素值 (0-255)')
        plt.ylabel('频率')
        plt.xlim([0, 255])
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # 保存图像
        plt.tight_layout()
        plt.savefig(output_path, dpi=100)
        plt.close()
        
    def render_luma_waveform(self, parade_data: List[np.ndarray], output_path: str) -> None:
        """
        渲染亮度波形图
        
        Args:
            parade_data: 波形图数据
            output_path: 输出文件路径
        """
        # 确保输出目录存在
        if not self._ensure_output_directory(output_path):
            return
            
        # 创建一个新的图形
        plt.figure(figsize=(10, 6))
        
        # 绘制波形图
        if len(parade_data) >= 3:  # 彩色图
            # 使用Y = 0.299R + 0.587G + 0.114B计算亮度
            r_data = parade_data[2]
            g_data = parade_data[1]
            b_data = parade_data[0]
            
            # 计算亮度波形
            luma_data = 0.299 * r_data + 0.587 * g_data + 0.114 * b_data
            
            # 对数缩放以增强低强度值的可见性
            log_data = np.log1p(luma_data)
            
            # 绘制波形图
            plt.imshow(
                log_data,
                aspect='auto',
                cmap='viridis',
                origin='lower',
                extent=(0, luma_data.shape[1], 0, 255),  # 使用元组而不是列表
                interpolation='nearest'
            )
        else:  # 灰度图
            # 对数缩放以增强低强度值的可见性
            log_data = np.log1p(parade_data[0])
            
            # 绘制波形图
            plt.imshow(
                log_data,
                aspect='auto',
                cmap='viridis',
                origin='lower',
                extent=(0, parade_data[0].shape[1], 0, 255),  # 使用元组而不是列表
                interpolation='nearest'
            )
            
        # 设置图表属性
        plt.title('亮度波形图')
        plt.xlabel('图像宽度 (像素)')
        plt.ylabel('亮度值 (0-255)')
        plt.colorbar(label='像素密度 (对数刻度)')
        
        # 保存图像
        plt.tight_layout()
        plt.savefig(output_path, dpi=100)
        plt.close()
        
    def render_rgb_parade(self, parade_data: List[np.ndarray], output_path: str) -> None:
        """
        渲染RGB Parade
        
        Args:
            parade_data: 波形图数据
            output_path: 输出文件路径
        """
        # 确保输出目录存在
        if not self._ensure_output_directory(output_path):
            return
            
        # 创建一个新的图形，包含3个子图
        fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
        
        # 设置标题
        fig.suptitle('RGB Parade')
        
        if len(parade_data) >= 3:  # 彩色图
            # 绘制RGB Parade
            cmaps = ['Reds', 'Greens', 'Blues']
            titles = ['红色通道', '绿色通道', '蓝色通道']
            
            # OpenCV的split返回的是B, G, R，我们需要正确映射到R, G, B显示
            data_to_plot = [parade_data[2], parade_data[1], parade_data[0]]  # R, G, B
            
            for ax, data, cmap, title in zip(axes, data_to_plot, cmaps, titles):
                # 对数缩放以增强低强度值的可见性
                log_data = np.log1p(data)
                
                # 绘制波形图
                im = ax.imshow(
                    log_data,
                    aspect='auto',
                    cmap=cmap,
                    origin='lower',
                    extent=(0, data.shape[1], 0, 255),  # 使用元组而不是列表
                    interpolation='nearest'
                )
                
                # 设置子图属性
                ax.set_ylabel('像素值 (0-255)')
                ax.set_title(title)
                ax.grid(True, linestyle=':', alpha=0.6)
                
                # 添加颜色条
                plt.colorbar(im, ax=ax, label='像素密度 (对数刻度)')
        else:  # 灰度图
            # 只使用第一个子图
            axes[0].set_visible(True)
            axes[1].set_visible(False)
            axes[2].set_visible(False)
            
            # 对数缩放以增强低强度值的可见性
            log_data = np.log1p(parade_data[0])
            
            # 绘制波形图
            im = axes[0].imshow(
                log_data,
                aspect='auto',
                cmap='viridis',
                origin='lower',
                extent=(0, parade_data[0].shape[1], 0, 255),  # 使用元组而不是列表
                interpolation='nearest'
            )
            
            # 设置子图属性
            axes[0].set_ylabel('像素值 (0-255)')
            axes[0].set_title('灰度通道')
            axes[0].grid(True, linestyle=':', alpha=0.6)
            
            # 添加颜色条
            plt.colorbar(im, ax=axes[0], label='像素密度 (对数刻度)')
            
        # 设置最后一个子图的x轴标签
        axes[-1].set_xlabel('图像宽度 (像素)')
        
        # 保存图像
        plt.tight_layout(rect=(0, 0.03, 1, 0.95))
        plt.savefig(output_path, dpi=100)
        plt.close()
        
    def render_hue_saturation(self, hue_hist: Optional[np.ndarray], 
                              sat_hist: Optional[np.ndarray], 
                              output_path: str) -> None:
        """
        渲染色相/饱和度直方图
        
        Args:
            hue_hist: 色相直方图数据
            sat_hist: 饱和度直方图数据
            output_path: 输出文件路径
        """
        # 确保输出目录存在
        if not self._ensure_output_directory(output_path):
            return
            
        # 创建一个新的图形，包含2个子图
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # 设置标题
        fig.suptitle('色相/饱和度直方图')
        
        if hue_hist is not None and sat_hist is not None:
            # 绘制色相直方图
            ax1.bar(range(180), hue_hist.flatten(), color='purple', alpha=0.7)
            ax1.set_title('色相直方图')
            ax1.set_xlabel('色相值 (0-179)')
            ax1.set_ylabel('频率')
            ax1.set_xlim([0, 179])
            ax1.grid(True, linestyle='--', alpha=0.7)
            
            # 绘制饱和度直方图
            ax2.bar(range(256), sat_hist.flatten(), color='teal', alpha=0.7)
            ax2.set_title('饱和度直方图')
            ax2.set_xlabel('饱和度值 (0-255)')
            ax2.set_ylabel('频率')
            ax2.set_xlim([0, 255])
            ax2.grid(True, linestyle='--', alpha=0.7)
        else:
            # 显示无数据信息
            ax1.text(0.5, 0.5, '灰度图像没有色相数据', horizontalalignment='center', 
                     verticalalignment='center', transform=ax1.transAxes)
            ax2.text(0.5, 0.5, '灰度图像没有饱和度数据', horizontalalignment='center', 
                     verticalalignment='center', transform=ax2.transAxes)
            
        # 保存图像
        plt.tight_layout(rect=(0, 0, 1, 0.95))
        plt.savefig(output_path, dpi=100)
        plt.close() 