"""
曲线预设模型模块
管理曲线调整的预设，包括获取预设、应用预设等功能
"""

from typing import Dict, List, Tuple, Any, Optional


class CurvePresetModel:
    """曲线预设模型，管理曲线调整的预设"""
    
    def __init__(self):
        """初始化预设模型"""
        # 加载预设数据
        self._presets = self._load_presets()
        # 当前选择的预设名称
        self._current_preset_name = "线性"
        
    def _load_presets(self) -> Dict[str, Dict[str, Any]]:
        """
        加载预设数据
        注意：这里直接内置了预设，也可以扩展为从文件或数据库加载
        
        Returns:
            预设数据字典
        """
        return {
            "自定义": {
                "description": "自定义曲线。",
                "points": [(0, 0), (255, 255)]  # 初始为线性
            },
            "线性": {
                "description": "线性曲线，保持原始色调分布不变。",
                "points": [(0, 0), (255, 255)]
            },
            "S曲线 (增强对比度)": {
                "description": "S形曲线，增强中间调对比度，同时保持高光和阴影细节。",
                "points": [(0, 0), (64, 32), (192, 224), (255, 255)]
            },
            "反转": {
                "description": "反转色调，创建负片效果。",
                "points": [(0, 255), (255, 0)]
            },
            "明亮化": {
                "description": "提高中间调亮度，保持高光和阴影。",
                "points": [(0, 0), (128, 160), (255, 255)]
            },
            "暗化": {
                "description": "降低中间调亮度，保持高光和阴影。",
                "points": [(0, 0), (128, 96), (255, 255)]
            }
        }
    
    @property
    def preset_names(self) -> List[str]:
        """获取所有预设名称"""
        return list(self._presets.keys())
    
    @property
    def current_preset_name(self) -> str:
        """获取当前预设名称"""
        return self._current_preset_name
    
    @current_preset_name.setter
    def current_preset_name(self, name: str):
        """设置当前预设名称"""
        if name in self._presets:
            self._current_preset_name = name
    
    def get_preset_points(self, preset_name: str) -> Optional[List[Tuple[int, int]]]:
        """
        获取指定预设的控制点
        
        Args:
            preset_name: 预设名称
            
        Returns:
            控制点列表或None（如果预设不存在）
        """
        if preset_name in self._presets:
            return self._presets[preset_name]["points"].copy()
        return None
    
    def get_current_preset_points(self) -> List[Tuple[int, int]]:
        """获取当前预设的控制点"""
        return self._presets[self._current_preset_name]["points"].copy()
    
    def get_preset_description(self, preset_name: str) -> str:
        """
        获取预设描述
        
        Args:
            preset_name: 预设名称
            
        Returns:
            预设描述文本
        """
        if preset_name in self._presets:
            return self._presets[preset_name]["description"]
        return "未知预设。"
    
    def is_custom_preset(self) -> bool:
        """检查当前是否是自定义预设"""
        return self._current_preset_name == "自定义"
    
    def set_to_custom(self):
        """将当前预设设置为自定义"""
        self._current_preset_name = "自定义"
    
    def compare_points_with_preset(
        self, 
        points: List[Tuple[int, int]], 
        preset_name: str, 
        tolerance: int = 0
    ) -> bool:
        """
        比较给定点集与预设点集是否匹配
        
        Args:
            points: 要比较的控制点
            preset_name: 预设名称
            tolerance: 允许的误差
            
        Returns:
            如果匹配返回True，否则False
        """
        if preset_name not in self._presets:
            return False
            
        preset_points = self._presets[preset_name]["points"]
        
        if len(points) != len(preset_points):
            return False
            
        for (x1, y1), (x2, y2) in zip(points, preset_points):
            if abs(x1 - x2) > tolerance or abs(y1 - y2) > tolerance:
                return False
                
        return True 