"""
代理图像工具模块

提供用于创建和管理低分辨率代理图像的工具函数。
集成了从文件加载代理和处理内存中图像的功能。
"""

from typing import Tuple, Optional
import numpy as np
import cv2
import os


def create_proxy_image(full_res_image: np.ndarray, quality_factor: float = 0.5) -> Tuple[np.ndarray, float]:
    """
    为高分辨率图像创建一个低分辨率的代理版本，同时保持宽高比。
    此函数处理已加载到内存中的图像。
    
    Args:
        full_res_image: 全分辨率原始图像
        quality_factor: 质量因子，范围0.1-1.0，其中:
                        - 0.1: 极低质量（最快）
                        - 0.25: 低质量
                        - 0.5: 中等质量
                        - 0.75: 高质量
                        - 1.0: 原始质量（最慢，不降采样）
    
    Returns:
        tuple: (代理图像, 缩放因子)
            代理图像: 低分辨率的图像
            缩放因子: 代理图像相对于原始图像的缩放比例 (0.0-1.0)
    """
    # 确保质量因子在有效范围内
    quality_factor = max(0.1, min(1.0, quality_factor))
    
    # 如果质量因子为1.0，则直接返回原图的拷贝
    if quality_factor >= 0.99:
        return full_res_image.copy(), 1.0
    
    # 根据质量因子计算缩放比例
    scale_factor = quality_factor
    
    h, w = full_res_image.shape[:2]
    new_h, new_w = int(h * scale_factor), int(w * scale_factor)
        
    # 使用cv2进行快速缩放
    proxy_image = cv2.resize(
        full_res_image, 
        (new_w, new_h), 
        interpolation=cv2.INTER_AREA
    )
    
    return proxy_image, scale_factor


def load_proxy_from_file(file_path: str, quality_factor: float = 0.25) -> Tuple[Optional[np.ndarray], float]:
    """
    直接从文件加载低分辨率代理图像，避免加载完整图像的开销。
    使用OpenCV的降采样读取功能来提高性能。
    
    Args:
        file_path: 图像文件的路径
        quality_factor: 质量因子，决定了降采样的级别
                        
    Returns:
        tuple: (代理图像, 缩放因子)
            代理图像: 低分辨率的图像，加载失败时为None
            缩放因子: 代理图像相对于原始图像的缩放比例 (0.0-1.0)
    
    Raises:
        FileNotFoundError: 如果文件不存在
        ValueError: 如果文件不是有效图像
    """
    try:
        # 确保文件存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到文件: {file_path}")
        
        # 确保质量因子在有效范围内
        quality_factor = max(0.1, min(1.0, quality_factor))
        scale_factor = quality_factor
        
        # 根据质量因子选择降采样级别
        if quality_factor <= 0.125:
            read_flag = cv2.IMREAD_REDUCED_COLOR_8  # 1/8分辨率
            scale_factor = 0.125
        elif quality_factor <= 0.25:
            read_flag = cv2.IMREAD_REDUCED_COLOR_4  # 1/4分辨率
            scale_factor = 0.25
        elif quality_factor <= 0.5:
            read_flag = cv2.IMREAD_REDUCED_COLOR_2  # 1/2分辨率
            scale_factor = 0.5
        else:
            # 对于高质量代理，使用完整读取
            read_flag = cv2.IMREAD_COLOR
            scale_factor = 1.0

        # 以二进制模式打开文件以支持非ASCII路径
        with open(file_path, "rb") as f:
            file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
            # 使用指定的降采样标志解码图像
            image = cv2.imdecode(file_bytes, read_flag)

            if image is None:
                raise ValueError(f"无法解码图像文件: {file_path}")

            # OpenCV读取的是BGR格式，转换为RGB格式以保持一致性
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            return image, scale_factor
            
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到文件: {file_path}")
    except Exception as e:
        raise ValueError(f"加载代理图像时出错: {str(e)}") 