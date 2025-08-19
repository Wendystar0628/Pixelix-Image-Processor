"""
图像模型模块

定义了图像的数据模型，用于表示图像数据和元数据。
"""
from typing import Dict, Any, Optional, Tuple
import os
import numpy as np


class ImageModel:
    """
    图像模型，表示一个图像及其元数据。
    
    包含图像数据、文件路径、尺寸、通道数等信息。
    """
    
    def __init__(self, image_data: Optional[np.ndarray] = None, file_path: Optional[str] = None):
        """
        初始化一个图像模型。
        
        Args:
            image_data: 图像数据，NumPy数组格式
            file_path: 图像文件路径
        """
        self.image_data = image_data
        self.file_path = file_path
        self.metadata: Dict[str, Any] = {}
        
        # 如果提供了图像数据，计算基本属性
        if image_data is not None:
            self._calculate_properties()
    
    def _calculate_properties(self) -> None:
        """
        计算图像的基本属性。
        """
        if self.image_data is None:
            return
            
        # 计算尺寸和通道数
        if len(self.image_data.shape) == 2:
            # 灰度图像
            height, width = self.image_data.shape
            channels = 1
        elif len(self.image_data.shape) == 3:
            # 彩色图像
            height, width, channels = self.image_data.shape
        else:
            # 未知格式
            height, width, channels = 0, 0, 0
            
        # 存储属性
        self.metadata["width"] = width
        self.metadata["height"] = height
        self.metadata["channels"] = channels
        self.metadata["dtype"] = str(self.image_data.dtype)
        
        # 如果有文件路径，添加文件相关信息
        if self.file_path:
            self.metadata["filename"] = os.path.basename(self.file_path)
            self.metadata["directory"] = os.path.dirname(self.file_path)
            self.metadata["extension"] = os.path.splitext(self.file_path)[1]
            
            # 获取文件大小
            try:
                self.metadata["file_size"] = os.path.getsize(self.file_path)
            except:
                self.metadata["file_size"] = 0
    
    @property
    def width(self) -> int:
        """获取图像宽度。"""
        return self.metadata.get("width", 0)
    
    @property
    def height(self) -> int:
        """获取图像高度。"""
        return self.metadata.get("height", 0)
    
    @property
    def channels(self) -> int:
        """获取图像通道数。"""
        return self.metadata.get("channels", 0)
    
    @property
    def shape(self) -> Tuple[int, int, int]:
        """获取图像形状（高度、宽度、通道数）。"""
        return (self.height, self.width, self.channels)
    
    @property
    def is_valid(self) -> bool:
        """检查图像是否有效。"""
        return self.image_data is not None and self.width > 0 and self.height > 0
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取图像元数据的副本。
        
        Returns:
            Dict[str, Any]: 图像元数据
        """
        return self.metadata.copy()
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        设置图像元数据。
        
        Args:
            key: 元数据键
            value: 元数据值
        """
        self.metadata[key] = value 