import numpy as np
import cv2
from typing import Dict, Any
from .regular_filter_base import RegularFilterOperation


class MosaicFilterOp(RegularFilterOperation):
    """马赛克滤镜操作"""
    
    def __init__(self, block_size: int = 10, preserve_edges: bool = False):
        """初始化马赛克滤镜
        
        Args:
            block_size: 马赛克块大小
            preserve_edges: 是否保持边缘
        """
        super().__init__()
        self.block_size = max(2, block_size)
        self.preserve_edges = preserve_edges
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        """应用马赛克滤镜"""
        image = self._ensure_valid_image(image)
        h, w = image.shape[:2]
        
        # 创建马赛克效果
        result = image.copy()
        
        for y in range(0, h, self.block_size):
            for x in range(0, w, self.block_size):
                # 计算块的边界
                y_end = min(y + self.block_size, h)
                x_end = min(x + self.block_size, w)
                
                # 获取块区域
                block = image[y:y_end, x:x_end]
                
                if block.size > 0:
                    # 计算块的平均颜色
                    avg_color = np.mean(block, axis=(0, 1)).astype(np.uint8)
                    
                    # 填充整个块
                    result[y:y_end, x:x_end] = avg_color
        
        # 如果需要保持边缘，进行边缘检测并混合
        if self.preserve_edges:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edges = np.stack([edges] * 3, axis=-1) / 255.0
            
            # 在边缘处保持原图
            result = (result * (1 - edges) + image * edges).astype(np.uint8)
        
        return result
    
    def get_params(self) -> Dict[str, Any]:
        """获取操作参数"""
        return {
            "block_size": self.block_size,
            "preserve_edges": self.preserve_edges
        }
    
    def serialize(self) -> Dict[str, Any]:
        """序列化操作"""
        return {
            "operation_name": self.__class__.__name__,
            "parameters": self.get_params()
        }