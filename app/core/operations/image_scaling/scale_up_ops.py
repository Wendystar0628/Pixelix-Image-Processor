"""
图像放大操作类
"""

import numpy as np
import cv2
from typing import Dict, Any

from ..base_operation import ImageOperation


class NearestScaleUpOp(ImageOperation):
    """最近邻插值放大操作"""
    
    def __init__(self, scale_factor: float = 2.0, algorithm: str = "nearest", **kwargs):
        self.scale_factor = scale_factor
        self.algorithm = algorithm
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用最近邻插值放大"""
        height, width = image.shape[:2]
        new_width = int(width * self.scale_factor)
        new_height = int(height * self.scale_factor)
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_NEAREST)
    
    def get_params(self) -> Dict[str, Any]:
        return {"scale_factor": self.scale_factor, "algorithm": "nearest"}
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class BilinearScaleUpOp(ImageOperation):
    """双线性插值放大操作"""
    
    def __init__(self, scale_factor: float = 2.0, algorithm: str = "bilinear", **kwargs):
        self.scale_factor = scale_factor
        self.algorithm = algorithm
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用双线性插值放大"""
        height, width = image.shape[:2]
        new_width = int(width * self.scale_factor)
        new_height = int(height * self.scale_factor)
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    
    def get_params(self) -> Dict[str, Any]:
        return {"scale_factor": self.scale_factor, "algorithm": "bilinear"}
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class BicubicScaleUpOp(ImageOperation):
    """双三次插值放大操作"""
    
    def __init__(self, scale_factor: float = 2.0, algorithm: str = "bicubic", **kwargs):
        self.scale_factor = scale_factor
        self.algorithm = algorithm
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用双三次插值放大"""
        height, width = image.shape[:2]
        new_width = int(width * self.scale_factor)
        new_height = int(height * self.scale_factor)
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    
    def get_params(self) -> Dict[str, Any]:
        return {"scale_factor": self.scale_factor, "algorithm": "bicubic"}
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class LanczosScaleUpOp(ImageOperation):
    """Lanczos插值放大操作"""
    
    def __init__(self, scale_factor: float = 2.0, algorithm: str = "lanczos", **kwargs):
        self.scale_factor = scale_factor
        self.algorithm = algorithm
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用Lanczos插值放大"""
        height, width = image.shape[:2]
        new_width = int(width * self.scale_factor)
        new_height = int(height * self.scale_factor)
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
    
    def get_params(self) -> Dict[str, Any]:
        return {"scale_factor": self.scale_factor, "algorithm": "lanczos"}
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class EdgePreservingScaleUpOp(ImageOperation):
    """边缘保持插值放大操作"""
    
    def __init__(self, scale_factor: float = 2.0, edge_threshold: float = 0.1):
        self.scale_factor = scale_factor
        self.edge_threshold = edge_threshold
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用边缘保持插值放大"""
        height, width = image.shape[:2]
        new_width = int(width * self.scale_factor)
        new_height = int(height * self.scale_factor)
        
        # 先用双三次插值作为基础
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # 检测边缘并进行锐化处理
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 检测边缘
        edges = cv2.Canny(gray, 50, 150)
        edges_resized = cv2.resize(edges, (new_width, new_height), interpolation=cv2.INTER_NEAREST)
        
        # 在边缘区域应用锐化
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(resized, -1, kernel)
        
        # 根据边缘强度混合结果
        if len(resized.shape) == 3:
            edges_mask = np.stack([edges_resized] * 3, axis=2) / 255.0
        else:
            edges_mask = edges_resized / 255.0
        
        result = resized * (1 - edges_mask * self.edge_threshold) + sharpened * (edges_mask * self.edge_threshold)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "scale_factor": self.scale_factor,
            "algorithm": "edge_preserving",
            "edge_threshold": self.edge_threshold
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }