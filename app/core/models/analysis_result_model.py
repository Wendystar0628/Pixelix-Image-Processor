"""
分析结果模型模块

定义了图像分析结果的数据模型，用于表示各种分析计算的结果。
"""
from typing import Dict, Any, List, Optional, Union
import numpy as np


class AnalysisResultModel:
    """
    分析结果模型，表示图像分析计算的结果数据。
    
    包含了各种分析结果，如直方图、RGB波形图、色相饱和度等。
    """
    
    def __init__(self):
        """
        初始化一个空的分析结果模型。
        """
        self.histogram: Optional[List[np.ndarray]] = None
        self.rgb_parade: Optional[List[np.ndarray]] = None
        self.hue_histogram: Optional[np.ndarray] = None
        self.sat_histogram: Optional[np.ndarray] = None
        self.image_properties: Dict[str, Any] = {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        将分析结果转换为字典，用于序列化。
        
        注意：NumPy数组会被转换为列表。
        
        Returns:
            Dict[str, Any]: 包含分析结果数据的字典
        """
        result = {}
        
        if self.histogram is not None:
            result["histogram"] = [h.tolist() if h is not None else None for h in self.histogram]
            
        if self.rgb_parade is not None:
            result["rgb_parade"] = [p.tolist() if p is not None else None for p in self.rgb_parade]
            
        if self.hue_histogram is not None:
            result["hue_histogram"] = self.hue_histogram.tolist()
            
        if self.sat_histogram is not None:
            result["sat_histogram"] = self.sat_histogram.tolist()
            
        if self.image_properties:
            result["image_properties"] = self.image_properties
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResultModel':
        """
        从字典创建分析结果实例。
        
        Args:
            data: 包含分析结果数据的字典
            
        Returns:
            AnalysisResultModel: 创建的分析结果实例
        """
        result = cls()
        
        if "histogram" in data:
            result.histogram = [np.array(h) if h is not None else None for h in data["histogram"]]
            
        if "rgb_parade" in data:
            result.rgb_parade = [np.array(p) if p is not None else None for p in data["rgb_parade"]]
            
        if "hue_histogram" in data:
            result.hue_histogram = np.array(data["hue_histogram"])
            
        if "sat_histogram" in data:
            result.sat_histogram = np.array(data["sat_histogram"])
            
        if "image_properties" in data:
            result.image_properties = data["image_properties"]
            
        return result 