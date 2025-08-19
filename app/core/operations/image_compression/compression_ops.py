"""
图像压缩操作类
"""

import numpy as np
import cv2
from typing import Dict, Any
from PIL import Image
import io

from ..base_operation import ImageOperation


class JpegCompressionOp(ImageOperation):
    """JPEG质量压缩操作"""
    
    def __init__(self, quality: int = 85, algorithm: str = "jpeg", optimize: bool = True, **kwargs):
        self.quality = quality
        self.algorithm = algorithm
        self.optimize = optimize
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用JPEG质量压缩"""
        # 转换为PIL Image
        if len(image.shape) == 3:
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        else:
            pil_image = Image.fromarray(image, mode='L')
        
        # 压缩到内存
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG', quality=self.quality, optimize=self.optimize)
        buffer.seek(0)
        
        # 重新加载
        compressed_image = Image.open(buffer)
        
        # 转换回numpy数组
        if len(image.shape) == 3:
            result = cv2.cvtColor(np.array(compressed_image), cv2.COLOR_RGB2BGR)
        else:
            result = np.array(compressed_image)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "quality": self.quality,
            "algorithm": "jpeg",
            "optimize": self.optimize
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class PngCompressionOp(ImageOperation):
    """PNG压缩级别操作"""
    
    def __init__(self, quality: int = 85, algorithm: str = "png", compress_level: int = 6, **kwargs):
        self.quality = quality
        self.algorithm = algorithm
        self.compress_level = compress_level
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用PNG压缩级别"""
        # 转换为PIL Image
        if len(image.shape) == 3:
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        else:
            pil_image = Image.fromarray(image, mode='L')
        
        # 压缩到内存
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG', compress_level=self.compress_level)
        buffer.seek(0)
        
        # 重新加载
        compressed_image = Image.open(buffer)
        
        # 转换回numpy数组
        if len(image.shape) == 3:
            result = cv2.cvtColor(np.array(compressed_image), cv2.COLOR_RGB2BGR)
        else:
            result = np.array(compressed_image)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "compress_level": self.compress_level,
            "algorithm": "png"
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class WebpCompressionOp(ImageOperation):
    """WebP压缩操作"""
    
    def __init__(self, quality: int = 85, algorithm: str = "webp", lossless: bool = False, **kwargs):
        self.quality = quality
        self.algorithm = algorithm
        self.lossless = lossless
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用WebP压缩"""
        try:
            # 转换为PIL Image
            if len(image.shape) == 3:
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            else:
                pil_image = Image.fromarray(image, mode='L')
            
            # 压缩到内存
            buffer = io.BytesIO()
            pil_image.save(buffer, format='WEBP', quality=self.quality, lossless=self.lossless)
            buffer.seek(0)
            
            # 重新加载
            compressed_image = Image.open(buffer)
            
            # 转换回numpy数组
            if len(image.shape) == 3:
                result = cv2.cvtColor(np.array(compressed_image), cv2.COLOR_RGB2BGR)
            else:
                result = np.array(compressed_image)
            
            return result
        except Exception:
            # 如果WebP不支持，回退到JPEG
            jpeg_op = JpegCompressionOp(self.quality)
            return jpeg_op.apply(image)
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "quality": self.quality,
            "algorithm": "webp",
            "lossless": self.lossless
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class ColorQuantizationOp(ImageOperation):
    """颜色量化压缩操作"""
    
    def __init__(self, quality: int = 85, algorithm: str = "color_quantization", colors: int = 256, dither: bool = True, **kwargs):
        self.quality = quality
        self.algorithm = algorithm
        self.colors = colors
        self.dither = dither
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用颜色量化压缩"""
        # 转换为PIL Image
        if len(image.shape) == 3:
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        else:
            pil_image = Image.fromarray(image, mode='L')
            return image  # 灰度图像不需要颜色量化
        
        # 颜色量化
        dither_method = Image.Dither.FLOYDSTEINBERG if self.dither else Image.Dither.NONE
        quantized = pil_image.quantize(colors=self.colors, dither=dither_method)
        
        # 转换回RGB模式
        rgb_image = quantized.convert('RGB')
        
        # 转换回numpy数组
        result = cv2.cvtColor(np.array(rgb_image), cv2.COLOR_RGB2BGR)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "colors": self.colors,
            "algorithm": "color_quantization",
            "dither": self.dither
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class LossyOptimizationOp(ImageOperation):
    """有损压缩优化操作"""
    
    def __init__(self, quality: int = 85, algorithm: str = "lossy_optimization", target_size_kb: int = 100, max_iterations: int = 10, **kwargs):
        self.quality = quality
        self.algorithm = algorithm
        self.target_size_kb = target_size_kb
        self.max_iterations = max_iterations
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用有损压缩优化"""
        # 转换为PIL Image
        if len(image.shape) == 3:
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        else:
            pil_image = Image.fromarray(image, mode='L')
        
        target_size = self.target_size_kb * 1024
        quality = 95
        best_result = None
        
        # 迭代优化质量参数
        for i in range(self.max_iterations):
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=quality, optimize=True)
            
            if buffer.tell() <= target_size or quality <= 10:
                buffer.seek(0)
                best_result = Image.open(buffer)
                break
            
            # 降低质量
            quality = max(10, quality - 10)
        
        if best_result is None:
            # 如果无法达到目标大小，使用最低质量
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=10, optimize=True)
            buffer.seek(0)
            best_result = Image.open(buffer)
        
        # 转换回numpy数组
        if len(image.shape) == 3:
            result = cv2.cvtColor(np.array(best_result), cv2.COLOR_RGB2BGR)
        else:
            result = np.array(best_result)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "target_size_kb": self.target_size_kb,
            "algorithm": "lossy_optimization",
            "max_iterations": self.max_iterations
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }