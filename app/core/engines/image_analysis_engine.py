"""
图像分析引擎 - 负责执行所有耗时的图像分析计算

此模块提供一个运行在后台线程中的引擎，用于处理所有耗时的分析计算，
从而避免阻塞GUI主线程并提高应用程序的响应性。
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

class ImageAnalysisEngine(QObject):
    """
    图像分析引擎 - 在后台线程中运行
    
    这个类负责执行所有耗时的分析计算，如直方图、RGB波形等，
    从而避免阻塞GUI主线程并提高应用程序的响应性。
    """
    
    # 信号：当所有分析计算完成时发出
    analysis_finished = pyqtSignal(dict)
    
    # 信号：请求进行分析计算
    request_analysis = pyqtSignal(np.ndarray)
    
    # 信号：请求进行选择性分析计算
    request_selective_analysis = pyqtSignal(np.ndarray, str)
    
    def __init__(self):
        super().__init__()
        # 连接请求分析信号到计算槽
        self.request_analysis.connect(self.calculate_analyses)
        self.request_selective_analysis.connect(self.calculate_selective_analysis)
        
        # 创建线程池以并行计算分析
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
    def _downsample_image(self, image, max_size=480):
        """
        对图像进行降采样以加快分析计算
        
        Args:
            image: 原始图像
            max_size: 处理后图像的最大宽度或高度
            
        Returns:
            降采样后的图像
        """
        h, w = image.shape[:2]
        # 计算缩放比例
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            new_size = (int(w * scale), int(h * scale))
            return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
        return image
    
    @pyqtSlot(np.ndarray, str)
    def calculate_selective_analysis(self, image: np.ndarray, analysis_type: str):
        """
        只计算指定类型的分析，用于快速更新特定分析面板
        
        Args:
            image: 要分析的图像(NumPy数组)
            analysis_type: 分析类型名称，如'histogram', 'rgb_parade', 'hue_saturation', 'lab_analysis'
        """
        if image is None:
            # 如果没有图像，发送一个空结果字典
            self.analysis_finished.emit({})
            return
            
        # 创建一个字典来存储分析结果
        results = {}
        
        # 对图像进行降采样以加快分析计算
        downsampled_image = self._downsample_image(image)
        
        # 只计算请求的分析类型
        if analysis_type == 'histogram':
            results['histogram'] = self.calculate_histogram(downsampled_image)
        elif analysis_type == 'rgb_parade':
            results['rgb_parade'] = self.get_rgb_parade_efficient(downsampled_image)
        elif analysis_type == 'hue_saturation':
            hue_hist, sat_hist = self.get_hue_saturation_histograms(downsampled_image)
            results['hue_histogram'] = hue_hist
            results['sat_histogram'] = sat_hist
        elif analysis_type == 'lab_analysis':
            # Lab色彩空间分析
            chromaticity_data, lab_3d_data = self.calculate_lab_analysis(downsampled_image)
            results['lab_chromaticity'] = chromaticity_data
            results['lab_3d'] = lab_3d_data
        elif analysis_type == 'luma_waveform':
            # 亮度波形分析（使用RGB波形的第一个通道）
            results['rgb_parade'] = self.get_rgb_parade_efficient(downsampled_image)
        elif analysis_type == 'histogram_and_waveform':
            # 组合类型：同时计算直方图和RGB波形（用于亮度波形）
            results['histogram'] = self.calculate_histogram(downsampled_image)
            results['rgb_parade'] = self.get_rgb_parade_efficient(downsampled_image)
        elif analysis_type == 'all':
            # 全部计算（但使用并行方式）
            self.calculate_analyses(image)
            return
        
        # 通过信号发送结果
        self.analysis_finished.emit(results)
        
    @pyqtSlot(np.ndarray)
    def calculate_analyses(self, image: np.ndarray):
        """
        执行所有分析计算并通过信号发送结果
        
        Args:
            image: 要分析的图像(NumPy数组)
        """
        if image is None:
            # 如果没有图像，发送一个空结果字典
            self.analysis_finished.emit({})
            return
            
        # 创建一个字典来存储所有分析结果
        results = {}
        
        # 对图像进行降采样以加快分析计算
        downsampled_image = self._downsample_image(image)
        
        # 并行计算各种分析
        futures = []
        
        # 计算直方图数据
        futures.append(self.thread_pool.submit(
            self.calculate_histogram, downsampled_image))
        
        # 计算RGB波形数据 - 使用高效版本
        futures.append(self.thread_pool.submit(
            self.get_rgb_parade_efficient, downsampled_image))
        
        # 计算色相/饱和度直方图数据
        futures.append(self.thread_pool.submit(
            self.get_hue_saturation_histograms, downsampled_image))
        
        # 计算Lab色彩空间分析数据
        futures.append(self.thread_pool.submit(
            self.calculate_lab_analysis, downsampled_image))
        
        # 收集计算结果
        results['histogram'] = futures[0].result()
        results['rgb_parade'] = futures[1].result()
        hue_hist, sat_hist = futures[2].result()
        results['hue_histogram'] = hue_hist
        results['sat_histogram'] = sat_hist
        chromaticity_data, lab_3d_data = futures[3].result()
        results['lab_chromaticity'] = chromaticity_data
        results['lab_3d'] = lab_3d_data
        
        # 通过信号发送结果
        self.analysis_finished.emit(results)

    @staticmethod
    def calculate_histogram(image: np.ndarray) -> List[np.ndarray]:
        """
        计算图像的直方图。

        Args:
            image (np.ndarray): 输入图像。

        Returns:
            List[np.ndarray]: 图像的直方图数据。对于灰度图像，返回一个元素；对于彩色图像，返回三个元素（B, G, R）。
        """
        # 检查图像是否为彩色
        if image.ndim == 3:
            # 对于彩色图像，计算每个通道的直方图
            hist_data = []
            for i in range(3):  # BGR 通道
                hist = cv2.calcHist([image], [i], None, [256], [0, 256])
                hist_data.append(hist.flatten())
            return hist_data
        else:
            # 对于灰度图像，计算单通道直方图
            hist = cv2.calcHist([image], [0], None, [256], [0, 256])
            return [hist.flatten()]

    @staticmethod
    def get_rgb_parade_efficient(image: np.ndarray) -> List[np.ndarray]:
        """
        计算图像的RGB波形图数据，使用高效的向量化操作。

        Args:
            image (np.ndarray): 输入图像。

        Returns:
            List[np.ndarray]: 图像的RGB波形图数据。对于灰度图像，返回一个元素；对于彩色图像，返回三个元素（B, G, R）。
        """
        if image is None:
            return []

        # 检查图像是否为彩色
        if image.ndim == 3:
            height, width = image.shape[:2]
            parade_data = []
            
            # 对每个通道单独计算
            for c in range(3):  # BGR通道
                # 创建波形数据存储空间
                parade = np.zeros((256, width), dtype=np.float32)
                
                # 获取当前通道
                channel = image[:, :, c]
                
                # 使用NumPy批量操作，一次处理整个图像
                # 这个方法避免了使用Python循环，大大提高了性能
                # 特别是对于大图像
                for x in range(width):
                    col_values = channel[:, x]
                    parade[:, x] = np.bincount(col_values, minlength=256)
                
                parade_data.append(parade)

            return parade_data
        else:
            # 对于灰度图像，只计算一个通道
            height, width = image.shape
            parade = np.zeros((256, width), dtype=np.float32)
            
            # 对灰度图像直接计算
            for x in range(width):
                col_values = image[:, x]
                parade[:, x] = np.bincount(col_values, minlength=256)

            return [parade]

    @staticmethod
    def get_hue_saturation_histograms(
        image: np.ndarray,
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        计算图像的色相和饱和度直方图。
        使用向量化操作提高性能。

        Args:
            image (np.ndarray): 输入图像。

        Returns:
            Tuple[Optional[np.ndarray], Optional[np.ndarray]]: 色相和饱和度直方图。如果是灰度图像，则返回(None, None)。
        """
        if image is None:
            return None, None

        # 检查图像是否为彩色
        if image.ndim == 3:
            # 转换为HSV颜色空间
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # 提取H和S通道
            h_channel = hsv_image[:, :, 0].flatten()  # 色相通道
            s_channel = hsv_image[:, :, 1].flatten()  # 饱和度通道
            
            # 使用numpy的向量化操作高效计算直方图
            h_hist = np.bincount(h_channel, minlength=180)
            s_hist = np.bincount(s_channel, minlength=256)
            
            # 确保返回一维数组（PyQtGraph需要一维数组）
            h_hist = h_hist.flatten()
            s_hist = s_hist.flatten()

            return h_hist, s_hist
        else:
            # 灰度图像没有色相和饱和度
            return None, None

    @staticmethod
    def get_image_properties(
        image: np.ndarray, file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取图像的基本属性和（如果可用）EXIF元数据。

        Args:
            image (np.ndarray): 输入图像。
            file_path (Optional[str]): 图像文件路径，用于读取EXIF数据。

        Returns:
            Dict[str, Any]: 包含图像属性和元数据的字典。
        """
        properties = {}
        
        # 文件信息
        if file_path:
            try:
                file_stats = os.stat(file_path)
                file_size = file_stats.st_size
                created_time = datetime.fromtimestamp(file_stats.st_ctime)
                modified_time = datetime.fromtimestamp(file_stats.st_mtime)
                
                properties["文件名称"] = os.path.basename(file_path)
                properties["文件路径"] = file_path
                properties["文件大小"] = f"{file_size / 1024:.2f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.2f} MB"
                properties["格式"] = os.path.splitext(file_path)[1].upper().replace('.', '')
                properties["创建时间"] = created_time.strftime("%Y-%m-%d %H:%M:%S")
                properties["修改时间"] = modified_time.strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(f"读取文件信息错误: {e}")
        
        # 图像尺寸信息
        if image is not None:
            height, width = image.shape[:2]
            total_pixels = width * height
            
            # 计算宽高比
            gcd = lambda a, b: a if b == 0 else gcd(b, a % b)
            divisor = gcd(width, height)
            aspect_ratio = f"{width // divisor}:{height // divisor}"
            
            properties["分辨率"] = f"{width} × {height} 像素"
            properties["宽高比"] = aspect_ratio
            properties["总像素数"] = f"{total_pixels:,} 像素"
            
            # 色彩信息
            if image.ndim == 3:
                channels = image.shape[2]
                color_space = "RGB" if channels == 3 else "RGBA" if channels == 4 else f"{channels}通道"
                has_alpha = channels == 4
            else:
                channels = 1
                color_space = "灰度"
                has_alpha = False
                
            bit_depth = 8  # 默认为8位
            if image.dtype == np.uint16:
                bit_depth = 16
            elif image.dtype == np.float32:
                bit_depth = 32
                
            properties["色彩空间"] = color_space
            properties["通道数"] = channels
            properties["透明通道"] = "是" if has_alpha else "否"
            properties["数据类型"] = str(image.dtype)
            properties["位深度"] = f"{bit_depth} 位/通道"
            
            # 内存使用
            memory_usage = image.nbytes
            properties["内存占用"] = f"{memory_usage / (1024 * 1024):.2f} MB"
            
            # 像素值范围
            min_val = image.min()
            max_val = image.max()
            properties["数值范围"] = f"{min_val} - {max_val}"

        # 尝试从文件路径读取并解析EXIF数据
        if file_path:
            from PIL import Image
            from PIL.ExifTags import GPSTAGS, TAGS
            
            try:
                with Image.open(file_path) as img:
                    exif_data = img.getexif()
                    if exif_data:
                        # 解码基本EXIF标签
                        for tag, value in exif_data.items():
                            tag_name = TAGS.get(tag, tag)
                            if isinstance(tag_name, str):
                                # 对特定的EXIF标签进行分类
                                if tag_name in ["Make", "Model"]:
                                    # 相机制造商和型号
                                    cn_tag = "制造商" if tag_name == "Make" else "型号"
                                    properties[f"相机{cn_tag}"] = value
                                elif tag_name in ["ExposureTime", "FNumber", "ISOSpeedRatings", "FocalLength"]:
                                    # 拍摄参数
                                    cn_tag = {"ExposureTime": "曝光时间", 
                                             "FNumber": "光圈值", 
                                             "ISOSpeedRatings": "ISO感光度", 
                                             "FocalLength": "焦距"}
                                    properties[f"拍摄{cn_tag.get(tag_name, tag_name)}"] = value
                                elif "Date" in tag_name or "Time" in tag_name:
                                    # 日期和时间信息
                                    properties[f"EXIF {tag_name}"] = value
                                else:
                                    properties[f"EXIF {tag_name}"] = value

                        # 解码GPS标签
                        if 34853 in exif_data:  # GPSInfo tag
                            gps_info = exif_data[34853]
                            for gps_tag, value in gps_info.items():
                                tag_name = GPSTAGS.get(gps_tag, gps_tag)
                                properties[f"GPS {tag_name}"] = value
            except Exception as e:
                # 某些图像可能没有EXIF数据或格式不支持
                print(f"无法读取 {file_path} 的EXIF数据: {e}")
                pass

        return properties

    @staticmethod
    def calculate_lab_analysis(image: np.ndarray) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
        """
        计算Lab色彩空间分析数据
        
        Args:
            image: 输入图像
            
        Returns:
            Tuple: (色度散点数据, 3D可视化数据)
        """
        if image is None:
            return {}, {}
            
        # 检查图像是否为彩色
        if image.ndim != 3:
            # 灰度图像转换为3通道
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            
        # 转换为Lab色彩空间
        lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # 计算色度散点数据
        chromaticity_data = ImageAnalysisEngine._calculate_lab_chromaticity_data(lab_image)
        
        # 计算3D可视化数据
        lab_3d_data = ImageAnalysisEngine._calculate_lab_3d_data(lab_image)
        
        return chromaticity_data, lab_3d_data
    
    @staticmethod
    def _calculate_lab_chromaticity_data(lab_image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        计算a*b*色度散点图数据
        
        Args:
            lab_image: Lab色彩空间图像
            
        Returns:
            Dict: 包含a*, b*, L值的字典
        """
        height, width = lab_image.shape[:2]
        
        # 提取Lab通道
        l_channel = lab_image[:, :, 0].flatten()
        a_channel = lab_image[:, :, 1].flatten() 
        b_channel = lab_image[:, :, 2].flatten()
        
        # 数据降采样以提高性能（每16个像素取一个）
        sample_step = max(1, len(l_channel) // 10000)  # 最多10000个点
        
        sampled_l = l_channel[::sample_step]
        sampled_a = a_channel[::sample_step]
        sampled_b = b_channel[::sample_step]
        
        # 转换Lab通道到正确范围
        # OpenCV Lab: L范围0-255(对应0-100), a,b范围0-255(对应-128到127)
        sampled_l = sampled_l.astype(np.float32) * 100.0 / 255.0  # 转换L到0-100
        sampled_a = sampled_a.astype(np.float32) - 128  # 转换a*到-128到127
        sampled_b = sampled_b.astype(np.float32) - 128  # 转换b*到-128到127
        
        return {
            'a_star': sampled_a,
            'b_star': sampled_b,
            'l_values': sampled_l
        }
    
    @staticmethod
    def _calculate_lab_3d_data(lab_image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        计算Lab 3D可视化数据
        
        Args:
            lab_image: Lab色彩空间图像
            
        Returns:
            Dict: 包含L, a*, b*三维坐标的字典
        """
        height, width = lab_image.shape[:2]
        
        # 提取Lab通道
        l_channel = lab_image[:, :, 0].flatten()
        a_channel = lab_image[:, :, 1].flatten()
        b_channel = lab_image[:, :, 2].flatten()
        
        # 更大的降采样以控制3D渲染性能（最多5000个点）
        sample_step = max(1, len(l_channel) // 5000)
        
        sampled_l = l_channel[::sample_step]
        sampled_a = a_channel[::sample_step]
        sampled_b = b_channel[::sample_step]
        
        # 转换Lab通道到正确范围
        sampled_l = sampled_l.astype(np.float32) * 100.0 / 255.0  # 转换L到0-100
        sampled_a = sampled_a.astype(np.float32) - 128  # 转换a*到-128到127
        sampled_b = sampled_b.astype(np.float32) - 128  # 转换b*到-128到127
        
        return {
            'l_coords': sampled_l,
            'a_coords': sampled_a,
            'b_coords': sampled_b
        }