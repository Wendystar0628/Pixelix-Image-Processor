"""
图像加载工作器模块

提供在后台线程中加载和处理图像的功能，避免阻塞UI线程。
"""

import cv2
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
from app.utils.image_utils import load_image_safely

class ImageLoadingWorker(QObject):
    """
    后台图像加载与处理工作器
    
    负责在不阻塞UI的情况下加载和处理图像
    """
    
    # 定义信号
    loading_complete = pyqtSignal(np.ndarray, str)  # 图像加载/渲染完成信号(图像, 文件路径)
    loading_failed = pyqtSignal(str)  # 加载失败信号(错误信息)
    
    def __init__(self):
        super().__init__()
    
    def load_and_process(self, file_path):
        """
        在后台线程中加载和处理图像
        
        Args:
            file_path: 图像文件路径
        """
        try:
            # 使用安全的图像加载函数，它已经处理了BGR到RGB的转换
            image = load_image_safely(file_path)
                
            # 发出加载完成信号
            self.loading_complete.emit(image, file_path)
                
        except Exception as e:
            self.loading_failed.emit(f"图像加载出错: {str(e)}") 