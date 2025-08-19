"""
图像缩小操作类
"""

import numpy as np
import cv2
from typing import Dict, Any
from scipy import ndimage

from ..base_operation import ImageOperation


class NearestScaleDownOp(ImageOperation):
    """最近邻下采样操作"""
    
    def __init__(self, scale_factor: float = 0.5, algorithm: str = "nearest", **kwargs):
        self.scale_factor = scale_factor
        self.algorithm = algorithm
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用最近邻下采样"""
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


class BilinearScaleDownOp(ImageOperation):
    """双线性下采样操作"""
    
    def __init__(self, scale_factor: float = 0.5, algorithm: str = "bilinear", **kwargs):
        self.scale_factor = scale_factor
        self.algorithm = algorithm
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用双线性下采样"""
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


class AreaAverageScaleDownOp(ImageOperation):
    """区域平均下采样操作"""
    
    def __init__(self, scale_factor: float = 0.5, algorithm: str = "area_average", **kwargs):
        self.scale_factor = scale_factor
        self.algorithm = algorithm
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用区域平均下采样"""
        height, width = image.shape[:2]
        new_width = int(width * self.scale_factor)
        new_height = int(height * self.scale_factor)
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    def get_params(self) -> Dict[str, Any]:
        return {"scale_factor": self.scale_factor, "algorithm": "area_average"}
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class GaussianScaleDownOp(ImageOperation):
    """高斯下采样操作"""
    
    def __init__(self, scale_factor: float = 0.5, algorithm: str = "gaussian", sigma: float = 1.0, **kwargs):
        self.scale_factor = scale_factor
        self.algorithm = algorithm
        self.sigma = sigma
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用高斯下采样"""
        # 先应用高斯模糊
        blurred = cv2.GaussianBlur(image, (0, 0), self.sigma)
        
        # 然后进行下采样
        height, width = blurred.shape[:2]
        new_width = int(width * self.scale_factor)
        new_height = int(height * self.scale_factor)
        
        return cv2.resize(blurred, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "scale_factor": self.scale_factor,
            "algorithm": "gaussian",
            "sigma": self.sigma
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class AntiAliasScaleDownOp(ImageOperation):
    """抗锯齿下采样操作"""
    
    def __init__(self, scale_factor: float = 0.5, algorithm: str = "anti_alias", filter_size: int = 3, **kwargs):
        self.scale_factor = scale_factor
        self.algorithm = algorithm
        self.filter_size = filter_size
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用抗锯齿下采样"""
        # 计算抗锯齿滤波器
        filter_sigma = 1.0 / self.scale_factor
        
        # 应用抗锯齿滤波
        if len(image.shape) == 3:
            filtered = np.zeros_like(image)
            for i in range(image.shape[2]):
                filtered[:, :, i] = ndimage.gaussian_filter(image[:, :, i], filter_sigma)
        else:
            filtered = ndimage.gaussian_filter(image, filter_sigma)
        
        # 进行下采样
        height, width = filtered.shape[:2]
        new_width = int(width * self.scale_factor)
        new_height = int(height * self.scale_factor)
        
        return cv2.resize(filtered, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "scale_factor": self.scale_factor,
            "algorithm": "anti_alias",
            "filter_size": self.filter_size
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }