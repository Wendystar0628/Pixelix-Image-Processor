import numpy as np
from abc import abstractmethod
from typing import Dict, Any
from ..base_operation import ImageOperation


class RegularFilterOperation(ImageOperation):
    """常规滤镜操作抽象基类"""
    
    def __init__(self):
        """初始化常规滤镜操作"""
        pass
    
    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用常规滤镜操作"""
        pass
    
    def _ensure_valid_image(self, image: np.ndarray) -> np.ndarray:
        """确保图像格式有效"""
        if image is None or image.size == 0:
            raise ValueError("输入图像无效")
        
        if len(image.shape) == 2:
            # 灰度图像转为3通道
            image = np.stack([image] * 3, axis=-1)
        elif len(image.shape) == 3 and image.shape[2] == 4:
            # RGBA转RGB
            image = image[:, :, :3]
            
        return image.astype(np.uint8)
    
    def _apply_intensity(self, original: np.ndarray, filtered: np.ndarray, 
                        intensity: float) -> np.ndarray:
        """应用滤镜强度混合"""
        intensity = np.clip(intensity, 0.0, 1.0)
        if intensity == 0.0:
            return original
        elif intensity == 1.0:
            return filtered
        else:
            return (original * (1 - intensity) + filtered * intensity).astype(np.uint8)