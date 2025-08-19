"""
图像池存储组件模块

此模块定义了ImagePoolStorage类，负责独立管理图像文件的存储和检索，
不依赖于作业系统，只承担文件IO和图像存储的职责。
"""
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, field

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

from app.handlers.file_handler import FileHandler


@dataclass
class ImagePoolData:
    """图像池数据结构"""
    images: List[str] = field(default_factory=list)
    thumbnails: Dict[str, np.ndarray] = field(default_factory=dict)
    
    def add_image(self, file_path: str) -> bool:
        """添加图像到池中"""
        if file_path not in self.images:
            self.images.append(file_path)
            return True
        return False
    
    def remove_image(self, index: int) -> bool:
        """根据索引移除图像"""
        if 0 <= index < len(self.images):
            file_path = self.images.pop(index)
            # 同时移除缩略图
            if file_path in self.thumbnails:
                del self.thumbnails[file_path]
            return True
        return False
    
    def clear(self) -> None:
        """清空所有图像和缩略图"""
        self.images.clear()
        self.thumbnails.clear()


class ImagePoolStorage(QObject):
    """
    图像池存储组件
    
    职责：
    - 管理图像文件的存储和检索
    - 提供图像的缩略图生成和缓存
    - 处理图像的添加、删除、清空操作
    - 完全独立于作业系统
    """
    
    # 信号：当图像池内容发生变化时发出
    pool_changed = pyqtSignal()
    
    def __init__(self, file_handler: FileHandler):
        """
        初始化图像池存储组件
        
        Args:
            file_handler: 文件处理器实例
        """
        super().__init__()
        self.file_handler = file_handler
        self._data = ImagePoolData()
    
    def add_images(self, file_paths: List[str]) -> int:
        """
        向图像池添加图像
        
        Args:
            file_paths: 图像文件路径列表
            
        Returns:
            int: 成功添加的图像数量
        """
        if not file_paths:
            return 0
        
        # 过滤有效的图像文件
        valid_paths = []
        for path in file_paths:
            if os.path.exists(path) and self.file_handler.is_supported_image_file(path):
                valid_paths.append(path)
        
        if not valid_paths:
            return 0
        
        # 添加到图像池
        added_count = 0
        for path in valid_paths:
            if self._data.add_image(path):
                added_count += 1
                # 异步生成缩略图
                self._generate_thumbnail(path)
        
        if added_count > 0:
            self.pool_changed.emit()
        
        return added_count
    
    def remove_images(self, indices: List[int]) -> int:
        """
        从图像池中移除图像
        
        Args:
            indices: 要移除的索引列表
            
        Returns:
            int: 成功移除的图像数量
        """
        if not indices:
            return 0
        
        # 按照索引从大到小排序，以避免删除时索引变化问题
        sorted_indices = sorted(indices, reverse=True)
        
        removed_count = 0
        for idx in sorted_indices:
            if self._data.remove_image(idx):
                removed_count += 1
        
        if removed_count > 0:
            self.pool_changed.emit()
        
        return removed_count
    
    def clear_images(self) -> int:
        """
        清空图像池
        
        Returns:
            int: 清除的图像数量
        """
        count = len(self._data.images)
        
        if count > 0:
            self._data.clear()
            self.pool_changed.emit()
        
        return count
    
    def get_all_images(self) -> List[str]:
        """
        获取所有图像路径
        
        Returns:
            List[str]: 图像路径列表的副本
        """
        return self._data.images.copy()
    
    def get_image_count(self) -> int:
        """
        获取图像数量
        
        Returns:
            int: 图像数量
        """
        return len(self._data.images)
    
    def is_empty(self) -> bool:
        """
        检查图像池是否为空
        
        Returns:
            bool: 如果图像池为空则返回True，否则返回False
        """
        return len(self._data.images) == 0
    
    def get_thumbnail(self, file_path: str) -> Optional[np.ndarray]:
        """
        获取图像的缩略图
        
        Args:
            file_path: 图像文件路径
            
        Returns:
            Optional[np.ndarray]: 缩略图数据，如果不存在则返回None
        """
        return self._data.thumbnails.get(file_path)
    
    def get_all_thumbnails(self) -> Dict[str, np.ndarray]:
        """
        获取所有缩略图
        
        Returns:
            Dict[str, np.ndarray]: 文件路径到缩略图的映射
        """
        return self._data.thumbnails.copy()
    
    def _generate_thumbnail(self, file_path: str, max_size: int = 100) -> bool:
        """
        生成图像缩略图
        
        Args:
            file_path: 图像文件路径
            max_size: 缩略图最大尺寸
            
        Returns:
            bool: 是否成功生成缩略图
        """
        try:
            from app.utils.image_utils import load_image_safely
            
            # 加载图像
            image = load_image_safely(file_path)
            if image is None:
                return False
            
            # 计算缩放比例
            h, w = image.shape[:2]
            scale = min(max_size / w, max_size / h)
            
            # 如果图像已经小于最大尺寸，不需要缩放
            if scale >= 1:
                self._data.thumbnails[file_path] = image
                return True
            
            # 缩放图像
            import cv2
            new_w = int(w * scale)
            new_h = int(h * scale)
            thumbnail = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            
            self._data.thumbnails[file_path] = thumbnail
            return True
            
        except Exception as e:
            print(f"生成缩略图失败 {file_path}: {e}")
            return False
    
    def import_folder(self, folder_path: str, recursive: bool = False, 
                     file_types: Optional[List[str]] = None) -> int:
        """
        从文件夹导入图像到图像池
        
        Args:
            folder_path: 文件夹路径
            recursive: 是否递归搜索子文件夹
            file_types: 要导入的文件类型列表，如 [".jpg", ".png"]
            
        Returns:
            int: 成功导入的图像数量
        """
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return 0
        
        # 收集图像文件
        image_files = []
        
        if recursive:
            # 递归搜索
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self._is_valid_image_file(file_path, file_types):
                        image_files.append(file_path)
        else:
            # 只搜索当前目录
            try:
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    if os.path.isfile(file_path) and self._is_valid_image_file(file_path, file_types):
                        image_files.append(file_path)
            except PermissionError:
                return 0
        
        # 添加到图像池
        return self.add_images(image_files)
    
    def _is_valid_image_file(self, file_path: str, file_types: Optional[List[str]] = None) -> bool:
        """
        检查文件是否为有效的图像文件
        
        Args:
            file_path: 文件路径
            file_types: 允许的文件类型列表
            
        Returns:
            bool: 如果是有效的图像文件则返回True
        """
        if not self.file_handler.is_supported_image_file(file_path):
            return False
        
        if file_types:
            file_ext = os.path.splitext(file_path)[1].lower()
            return file_ext in [ft.lower() for ft in file_types]
        
        return True