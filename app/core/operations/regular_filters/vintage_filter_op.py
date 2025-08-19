import numpy as np
import cv2
from typing import Dict, Any
from .regular_filter_base import RegularFilterOperation


class VintageFilterOp(RegularFilterOperation):
    """怀旧滤镜操作"""
    
    def __init__(self, intensity: float = 0.5, temperature: float = 0.0, vignette: float = 0.3):
        """初始化怀旧滤镜
        
        Args:
            intensity: 怀旧强度
            temperature: 色温调节 (-1.0 到 1.0)
            vignette: 暗角强度
        """
        super().__init__()
        self.intensity = max(0.0, min(1.0, intensity))
        self.temperature = max(-1.0, min(1.0, temperature))
        self.vignette = max(0.0, min(1.0, vignette))
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用怀旧滤镜"""
        image = self._ensure_valid_image(image)
        result = image.astype(np.float32)
        h, w = image.shape[:2]
        
        # 应用怀旧色调矩阵
        vintage_matrix = np.array([
            [0.393, 0.769, 0.189],  # R
            [0.349, 0.686, 0.168],  # G
            [0.272, 0.534, 0.131]   # B
        ])
        
        # 重塑图像以便矩阵运算
        reshaped = result.reshape(-1, 3)
        vintage_result = np.dot(reshaped, vintage_matrix.T)
        vintage_result = vintage_result.reshape(h, w, 3)
        
        # 应用色温调节
        if self.temperature != 0.0:
            if self.temperature > 0:
                # 暖色调
                vintage_result[:, :, 0] *= (1 + self.temperature * 0.3)  # 增加红色
                vintage_result[:, :, 1] *= (1 + self.temperature * 0.1)  # 略增绿色
                vintage_result[:, :, 2] *= (1 - self.temperature * 0.2)  # 减少蓝色
            else:
                # 冷色调
                temp = abs(self.temperature)
                vintage_result[:, :, 0] *= (1 - temp * 0.2)  # 减少红色
                vintage_result[:, :, 1] *= (1 - temp * 0.1)  # 略减绿色
                vintage_result[:, :, 2] *= (1 + temp * 0.3)  # 增加蓝色
        
        # 应用暗角效果
        if self.vignette > 0:
            center_x, center_y = w // 2, h // 2
            max_dist = np.sqrt(center_x**2 + center_y**2)
            
            y, x = np.ogrid[:h, :w]
            dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            
            # 创建暗角掩码
            vignette_mask = 1 - (dist / max_dist) * self.vignette
            vignette_mask = np.clip(vignette_mask, 0.3, 1.0)
            vignette_mask = np.stack([vignette_mask] * 3, axis=-1)
            
            vintage_result *= vignette_mask
        
        # 裁剪到有效范围
        vintage_result = np.clip(vintage_result, 0, 255)
        
        # 根据强度混合原图和效果图
        result = self._apply_intensity(image, vintage_result.astype(np.uint8), self.intensity)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        """获取操作参数"""
        return {
            "intensity": self.intensity,
            "temperature": self.temperature,
            "vignette": self.vignette
        }
    
    def serialize(self) -> Dict[str, Any]:
        """序列化操作"""
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }