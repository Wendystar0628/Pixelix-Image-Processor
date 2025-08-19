import numpy as np
import cv2
from typing import Dict, Any
from .regular_filter_base import RegularFilterOperation


class SketchFilterOp(RegularFilterOperation):
    """素描滤镜操作"""
    
    def __init__(self, line_strength: float = 1.0, contrast: float = 1.0, background_color: int = 255):
        """初始化素描滤镜
        
        Args:
            line_strength: 线条强度
            contrast: 对比度
            background_color: 背景色 (0-255)
        """
        super().__init__()
        self.line_strength = max(0.1, line_strength)
        self.contrast = max(0.1, contrast)
        self.background_color = max(0, min(255, background_color))
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用素描滤镜"""
        image = self._ensure_valid_image(image)
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 高斯模糊
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # 创建素描效果：原图除以模糊图的反相
        inverted_blur = 255 - blurred
        sketch = cv2.divide(gray, inverted_blur, scale=256.0)
        
        # 应用线条强度
        if self.line_strength != 1.0:
            sketch = sketch.astype(np.float32)
            sketch = np.power(sketch / 255.0, 1.0 / self.line_strength) * 255.0
            sketch = np.clip(sketch, 0, 255).astype(np.uint8)
        
        # 应用对比度
        if self.contrast != 1.0:
            sketch = sketch.astype(np.float32)
            sketch = (sketch - 128) * self.contrast + 128
            sketch = np.clip(sketch, 0, 255).astype(np.uint8)
        
        # 设置背景色
        if self.background_color != 255:
            # 将白色背景替换为指定颜色
            mask = sketch > 240
            sketch[mask] = self.background_color
        
        # 转换回3通道
        result = np.stack([sketch] * 3, axis=-1)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        """获取操作参数"""
        return {
            "line_strength": self.line_strength,
            "contrast": self.contrast,
            "background_color": self.background_color
        }
    
    def serialize(self) -> Dict[str, Any]:
        """序列化操作"""
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }