"""文件系统服务接口"""
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from pathlib import Path
import numpy as np


class FileServiceInterface(ABC):
    """文件系统服务抽象接口"""
    
    @abstractmethod
    def load_image(self, file_path: str) -> Tuple[Optional[np.ndarray], str]:
        """加载图像文件
        
        Args:
            file_path: 图像文件路径
            
        Returns:
            (图像数据, 实际文件路径) 或 (None, 错误信息)
        """
        pass
    
    @abstractmethod
    def save_image(self, image: np.ndarray, file_path: str, quality: int = 85) -> bool:
        """保存图像文件
        
        Args:
            image: 图像数据
            file_path: 保存路径
            quality: 图像质量（用于JPEG）
            
        Returns:
            是否保存成功
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """获取支持的图像格式"""
        pass
    
    @abstractmethod
    def is_image_file(self, file_path: str) -> bool:
        """检查是否为支持的图像文件"""
        pass
    
    @abstractmethod
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """获取文件信息"""
        pass
    
    @abstractmethod
    def ensure_directory(self, dir_path: str) -> bool:
        """确保目录存在"""
        pass