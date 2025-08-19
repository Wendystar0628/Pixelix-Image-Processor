"""
新增滤镜操作类模块

包含10个新增的常规滤镜操作类实现
"""

import numpy as np
import cv2
from typing import Dict, Any
from .regular_filter_base import RegularFilterOperation


class WatercolorFilterOp(RegularFilterOperation):
    """水彩画滤镜操作"""
    
    def __init__(self, flow_intensity: float = 0.5, penetration: float = 0.3):
        super().__init__()
        self.flow_intensity = np.clip(flow_intensity, 0.0, 1.0)
        self.penetration = np.clip(penetration, 0.0, 1.0)
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用水彩画滤镜"""
        image = self._ensure_valid_image(image)
        
        # 边缘保持平滑
        smooth = cv2.edgePreservingFilter(image, flags=2, sigma_s=50, sigma_r=0.4)
        
        # 双边滤波增强流动效果
        bilateral = cv2.bilateralFilter(smooth, 15, 80, 80)
        
        # 根据流动强度混合
        flow_result = self._apply_intensity(smooth, bilateral, self.flow_intensity)
        
        # 模拟水彩渗透效果
        kernel = np.ones((3, 3), np.float32) / 9
        penetrated = cv2.filter2D(flow_result, -1, kernel)
        
        # 应用渗透效果
        result = self._apply_intensity(flow_result, penetrated, self.penetration)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "flow_intensity": self.flow_intensity,
            "penetration": self.penetration
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class PencilSketchFilterOp(RegularFilterOperation):
    """铅笔画滤镜操作"""
    
    def __init__(self, line_thickness: float = 1.0, shadow_intensity: float = 0.5):
        super().__init__()
        self.line_thickness = np.clip(line_thickness, 0.1, 3.0)
        self.shadow_intensity = np.clip(shadow_intensity, 0.0, 1.0)
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用铅笔画滤镜"""
        image = self._ensure_valid_image(image)
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 高斯模糊
        blur_size = max(3, int(self.line_thickness * 3))
        if blur_size % 2 == 0:
            blur_size += 1
        blurred = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)
        
        # 创建铅笔效果
        pencil = cv2.divide(gray, blurred, scale=256.0)
        
        # 增强对比度
        pencil = cv2.convertScaleAbs(pencil, alpha=1.2, beta=10)
        
        # 应用阴影效果
        shadow = cv2.GaussianBlur(pencil, (5, 5), 0)
        shadow = cv2.convertScaleAbs(shadow, alpha=0.7, beta=0)
        
        # 混合阴影
        result_gray = self._apply_intensity(pencil, shadow, self.shadow_intensity)
        
        # 转换回3通道
        result = np.stack([result_gray] * 3, axis=-1)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "line_thickness": self.line_thickness,
            "shadow_intensity": self.shadow_intensity
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class CartoonFilterOp(RegularFilterOperation):
    """卡通化滤镜操作"""
    
    def __init__(self, color_simplification: float = 0.7, edge_enhancement: float = 0.8):
        super().__init__()
        self.color_simplification = np.clip(color_simplification, 0.0, 1.0)
        self.edge_enhancement = np.clip(edge_enhancement, 0.0, 1.0)
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用卡通化滤镜"""
        image = self._ensure_valid_image(image)
        
        # 双边滤波平滑色彩
        smooth = cv2.bilateralFilter(image, 15, 80, 80)
        
        # K-means色彩量化
        k = max(2, int(8 * (1 - self.color_simplification) + 2))
        data = smooth.reshape((-1, 3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # 重建图像
        centers = np.uint8(centers)
        quantized = centers[labels.flatten()]
        quantized = quantized.reshape(smooth.shape)
        
        # 边缘检测
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 7)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        
        # 应用边缘增强
        if self.edge_enhancement > 0:
            edges_mask = edges / 255.0
            result = quantized * edges_mask
            result = self._apply_intensity(quantized, result.astype(np.uint8), self.edge_enhancement)
        else:
            result = quantized
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "color_simplification": self.color_simplification,
            "edge_enhancement": self.edge_enhancement
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class WarmToneFilterOp(RegularFilterOperation):
    """暖色调滤镜操作"""
    
    def __init__(self, warmth_intensity: float = 0.5, temperature_shift: float = 0.3):
        super().__init__()
        self.warmth_intensity = np.clip(warmth_intensity, 0.0, 1.0)
        self.temperature_shift = np.clip(temperature_shift, 0.0, 1.0)
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用暖色调滤镜"""
        image = self._ensure_valid_image(image)
        
        # 转换到HSV色彩空间
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype(np.float32)
        
        # 增强暖色调
        h, s, v = cv2.split(hsv)
        
        # 色相调整 - 向红橙色调偏移
        h_shift = self.temperature_shift * 10  # 色相偏移量
        h = (h - h_shift) % 180
        
        # 饱和度增强
        s = np.clip(s * (1 + self.warmth_intensity * 0.3), 0, 255)
        
        # 重新组合
        hsv_adjusted = cv2.merge([h, s, v])
        result = cv2.cvtColor(hsv_adjusted.astype(np.uint8), cv2.COLOR_HSV2RGB)
        
        # 在RGB空间进一步增强暖色
        warm_boost = np.array([1.0 + self.warmth_intensity * 0.2, 
                              1.0 + self.warmth_intensity * 0.1, 
                              1.0 - self.warmth_intensity * 0.1])
        result = np.clip(result * warm_boost, 0, 255).astype(np.uint8)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "warmth_intensity": self.warmth_intensity,
            "temperature_shift": self.temperature_shift
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class CoolToneFilterOp(RegularFilterOperation):
    """冷色调滤镜操作"""
    
    def __init__(self, coolness_intensity: float = 0.5, temperature_shift: float = 0.3):
        super().__init__()
        self.coolness_intensity = np.clip(coolness_intensity, 0.0, 1.0)
        self.temperature_shift = np.clip(temperature_shift, 0.0, 1.0)
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用冷色调滤镜"""
        image = self._ensure_valid_image(image)
        
        # 转换到HSV色彩空间
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype(np.float32)
        
        # 增强冷色调
        h, s, v = cv2.split(hsv)
        
        # 色相调整 - 向蓝青色调偏移
        h_shift = self.temperature_shift * 15  # 色相偏移量
        h = (h + h_shift) % 180
        
        # 饱和度调整
        s = np.clip(s * (1 + self.coolness_intensity * 0.2), 0, 255)
        
        # 重新组合
        hsv_adjusted = cv2.merge([h, s, v])
        result = cv2.cvtColor(hsv_adjusted.astype(np.uint8), cv2.COLOR_HSV2RGB)
        
        # 在RGB空间进一步增强冷色
        cool_boost = np.array([1.0 - self.coolness_intensity * 0.1, 
                              1.0 + self.coolness_intensity * 0.05, 
                              1.0 + self.coolness_intensity * 0.2])
        result = np.clip(result * cool_boost, 0, 255).astype(np.uint8)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "coolness_intensity": self.coolness_intensity,
            "temperature_shift": self.temperature_shift
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class FilmGrainFilterOp(RegularFilterOperation):
    """黑白胶片滤镜操作"""
    
    def __init__(self, grain_intensity: float = 0.5, contrast_boost: float = 0.3):
        super().__init__()
        self.grain_intensity = np.clip(grain_intensity, 0.0, 1.0)
        self.contrast_boost = np.clip(contrast_boost, 0.0, 1.0)
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用黑白胶片滤镜"""
        image = self._ensure_valid_image(image)
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 增强对比度
        alpha = 1.0 + self.contrast_boost
        beta = -self.contrast_boost * 50
        contrasted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
        
        # 添加胶片颗粒
        if self.grain_intensity > 0:
            noise = np.random.normal(0, self.grain_intensity * 25, gray.shape).astype(np.float32)
            grainy = np.clip(contrasted.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        else:
            grainy = contrasted
        
        # 模拟胶片特性曲线
        lut = np.arange(256, dtype=np.float32)
        lut = 255 * np.power(lut / 255, 0.8)  # 轻微的伽马调整
        grainy = cv2.LUT(grainy, lut.astype(np.uint8))
        
        # 转换回3通道
        result = np.stack([grainy] * 3, axis=-1)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "grain_intensity": self.grain_intensity,
            "contrast_boost": self.contrast_boost
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class NoiseFilterOp(RegularFilterOperation):
    """噪点滤镜操作"""
    
    def __init__(self, noise_type: int = 0, noise_intensity: float = 0.1):
        super().__init__()
        self.noise_type = max(0, min(2, noise_type))  # 0:高斯 1:椒盐 2:泊松
        self.noise_intensity = np.clip(noise_intensity, 0.0, 1.0)
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用噪点滤镜"""
        image = self._ensure_valid_image(image)
        
        if self.noise_intensity == 0:
            return image
        
        result = image.astype(np.float32)
        
        if self.noise_type == 0:  # 高斯噪声
            noise = np.random.normal(0, self.noise_intensity * 30, image.shape)
            result = result + noise
        elif self.noise_type == 1:  # 椒盐噪声
            prob = self.noise_intensity * 0.1
            mask = np.random.random(image.shape[:2])
            result[mask < prob/2] = 0  # 椒噪声
            result[mask > 1 - prob/2] = 255  # 盐噪声
        else:  # 泊松噪声
            # 泊松噪声基于图像强度
            result = np.random.poisson(result * self.noise_intensity * 0.1) / (self.noise_intensity * 0.1)
        
        result = np.clip(result, 0, 255).astype(np.uint8)
        return result
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "noise_type": self.noise_type,
            "noise_intensity": self.noise_intensity
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class FrostedGlassFilterOp(RegularFilterOperation):
    """磨砂玻璃滤镜操作"""
    
    def __init__(self, blur_amount: float = 0.5, distortion_strength: float = 0.3):
        super().__init__()
        self.blur_amount = np.clip(blur_amount, 0.0, 1.0)
        self.distortion_strength = np.clip(distortion_strength, 0.0, 1.0)
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用磨砂玻璃滤镜"""
        image = self._ensure_valid_image(image)
        h, w = image.shape[:2]
        
        # 创建扭曲映射
        if self.distortion_strength > 0:
            # 生成随机位移
            displacement = self.distortion_strength * 10
            map_x = np.float32(np.mgrid[0:h, 0:w][1])
            map_y = np.float32(np.mgrid[0:h, 0:w][0])
            
            # 添加随机扭曲
            noise_x = np.random.normal(0, displacement, (h, w)).astype(np.float32)
            noise_y = np.random.normal(0, displacement, (h, w)).astype(np.float32)
            
            map_x = np.clip(map_x + noise_x, 0, w-1)
            map_y = np.clip(map_y + noise_y, 0, h-1)
            
            # 应用扭曲
            distorted = cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR)
        else:
            distorted = image
        
        # 应用模糊
        if self.blur_amount > 0:
            blur_size = max(3, int(self.blur_amount * 15))
            if blur_size % 2 == 0:
                blur_size += 1
            result = cv2.GaussianBlur(distorted, (blur_size, blur_size), 0)
        else:
            result = distorted
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "blur_amount": self.blur_amount,
            "distortion_strength": self.distortion_strength
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class FabricTextureFilterOp(RegularFilterOperation):
    """织物纹理滤镜操作"""
    
    def __init__(self, fabric_type: int = 0, texture_intensity: float = 0.5):
        super().__init__()
        self.fabric_type = max(0, min(2, fabric_type))  # 0:帆布 1:丝绸 2:麻布
        self.texture_intensity = np.clip(texture_intensity, 0.0, 1.0)
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用织物纹理滤镜"""
        image = self._ensure_valid_image(image)
        h, w = image.shape[:2]
        
        if self.texture_intensity == 0:
            return image
        
        # 生成纹理图案
        if self.fabric_type == 0:  # 帆布纹理
            pattern = self._create_canvas_pattern(h, w)
        elif self.fabric_type == 1:  # 丝绸纹理
            pattern = self._create_silk_pattern(h, w)
        else:  # 麻布纹理
            pattern = self._create_linen_pattern(h, w)
        
        # 应用纹理
        pattern_normalized = pattern / 255.0
        textured = image.astype(np.float32)
        
        for c in range(3):
            textured[:, :, c] = textured[:, :, c] * (1 - self.texture_intensity * 0.3 + 
                                                   pattern_normalized * self.texture_intensity * 0.6)
        
        result = np.clip(textured, 0, 255).astype(np.uint8)
        return result
    
    def _create_canvas_pattern(self, h: int, w: int) -> np.ndarray:
        """创建帆布纹理图案"""
        pattern = np.zeros((h, w), dtype=np.uint8)
        for i in range(0, h, 4):
            pattern[i:i+2, :] = 200
        for j in range(0, w, 4):
            pattern[:, j:j+2] = np.maximum(pattern[:, j:j+2], 180)
        return pattern
    
    def _create_silk_pattern(self, h: int, w: int) -> np.ndarray:
        """创建丝绸纹理图案"""
        x = np.arange(w)
        y = np.arange(h)
        X, Y = np.meshgrid(x, y)
        pattern = 128 + 30 * np.sin(X * 0.1) * np.sin(Y * 0.15)
        return np.clip(pattern, 0, 255).astype(np.uint8)
    
    def _create_linen_pattern(self, h: int, w: int) -> np.ndarray:
        """创建麻布纹理图案"""
        pattern = np.random.normal(128, 20, (h, w))
        # 添加纤维方向性
        for i in range(0, h, 6):
            pattern[i:i+3, :] += 15
        for j in range(0, w, 8):
            pattern[:, j:j+2] += 10
        return np.clip(pattern, 0, 255).astype(np.uint8)
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "fabric_type": self.fabric_type,
            "texture_intensity": self.texture_intensity
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }


class VignetteFilterOp(RegularFilterOperation):
    """暗角滤镜操作"""
    
    def __init__(self, vignette_strength: float = 0.5, gradient_range: float = 0.7):
        super().__init__()
        self.vignette_strength = np.clip(vignette_strength, 0.0, 1.0)
        self.gradient_range = np.clip(gradient_range, 0.1, 1.0)
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用暗角滤镜"""
        image = self._ensure_valid_image(image)
        h, w = image.shape[:2]
        
        if self.vignette_strength == 0:
            return image
        
        # 创建暗角遮罩
        center_x, center_y = w // 2, h // 2
        max_distance = np.sqrt(center_x**2 + center_y**2)
        
        y, x = np.ogrid[:h, :w]
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # 计算暗角强度
        normalized_distance = distance / max_distance
        vignette_mask = 1 - self.vignette_strength * np.power(
            np.clip(normalized_distance / self.gradient_range, 0, 1), 2)
        
        # 应用暗角效果
        result = image.astype(np.float32)
        for c in range(3):
            result[:, :, c] *= vignette_mask
        
        result = np.clip(result, 0, 255).astype(np.uint8)
        return result
    
    def get_params(self) -> Dict[str, Any]:
        return {
            "vignette_strength": self.vignette_strength,
            "gradient_range": self.gradient_range
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }