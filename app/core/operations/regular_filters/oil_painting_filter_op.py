import numpy as np
import cv2
from typing import Dict, Any
from .regular_filter_base import RegularFilterOperation


class OilPaintingFilterOp(RegularFilterOperation):
    """油画滤镜操作"""
    
    def __init__(self, brush_size: int = 5, detail_level: int = 3, saturation: float = 1.0):
        """初始化油画滤镜
        
        Args:
            brush_size: 笔触大小
            detail_level: 细节级别
            saturation: 饱和度增强
        """
        super().__init__()
        self.brush_size = max(1, brush_size)
        self.detail_level = max(1, detail_level)
        self.saturation = max(0.1, saturation)
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用油画滤镜"""
        image = self._ensure_valid_image(image)
        h, w = image.shape[:2]
        
        # 应用双边滤波减少细节
        smoothed = cv2.bilateralFilter(image, 15, 80, 80)
        
        # 应用均值偏移分割
        result = cv2.pyrMeanShiftFiltering(
            smoothed, 
            sp=self.brush_size * 2, 
            sr=self.brush_size * 10
        )
        
        # 增强饱和度
        if self.saturation != 1.0:
            hsv = cv2.cvtColor(result, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 1] *= self.saturation
            hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
            result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        
        # 添加纹理效果
        if self.detail_level > 1:
            # 创建纹理核
            kernel_size = self.detail_level * 2 + 1
            kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
            
            # 应用形态学操作增加纹理
            texture = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
            result = cv2.addWeighted(result, 0.7, texture, 0.3, 0)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        """获取操作参数"""
        return {
            "brush_size": self.brush_size,
            "detail_level": self.detail_level,
            "saturation": self.saturation
        }
    
    def serialize(self) -> Dict[str, Any]:
        """序列化操作"""
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }