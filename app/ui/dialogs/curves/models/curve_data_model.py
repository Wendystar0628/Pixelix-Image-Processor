"""
曲线数据模型模块
负责曲线控制点数据的管理和处理
"""

from typing import List, Tuple, Dict, Optional, Any
import numpy as np
from scipy import interpolate


class CurveDataModel:
    """
    曲线数据模型，管理和处理曲线控制点数据
    提供曲线操作和数据转换的核心功能
    """

    def __init__(self):
        # 初始化各通道曲线控制点
        self._channel_points = {
            "RGB": [(0, 0), (255, 255)],  # 线性曲线作为默认值
            "R": [(0, 0), (255, 255)],
            "G": [(0, 0), (255, 255)],
            "B": [(0, 0), (255, 255)],
        }
        self._current_channel = "RGB"

    @property
    def channel_points(self) -> Dict[str, List[Tuple[int, int]]]:
        """获取所有通道的控制点"""
        return self._channel_points

    @property
    def current_channel(self) -> str:
        """获取当前活动通道"""
        return self._current_channel

    @current_channel.setter
    def current_channel(self, channel: str):
        """设置当前活动通道"""
        if channel in self._channel_points:
            self._current_channel = channel

    def get_current_points(self) -> List[Tuple[int, int]]:
        """获取当前通道的控制点"""
        return self._channel_points[self._current_channel].copy()

    def set_current_points(self, points: List[Tuple[int, int]]):
        """设置当前通道的控制点"""
        if points:
            # 确保点按x坐标排序
            sorted_points = sorted(points, key=lambda p: p[0])
            self._channel_points[self._current_channel] = sorted_points

    def set_channel_points(self, channel: str, points: List[Tuple[int, int]]):
        """设置指定通道的控制点"""
        if channel in self._channel_points and points:
            # 确保点按x坐标排序
            sorted_points = sorted(points, key=lambda p: p[0])
            self._channel_points[channel] = sorted_points

    def sync_all_channels_from_rgb(self):
        """将RGB通道的控制点同步到所有单独的通道"""
        rgb_points = self._channel_points["RGB"]
        self._channel_points["R"] = rgb_points.copy()
        self._channel_points["G"] = rgb_points.copy()
        self._channel_points["B"] = rgb_points.copy()

    def reset_to_linear(self, channel: Optional[str] = None):
        """将指定通道或所有通道重置为线性曲线"""
        linear_points = [(0, 0), (255, 255)]
        
        if channel:
            if channel in self._channel_points:
                self._channel_points[channel] = linear_points.copy()
        else:
            # 重置所有通道
            for ch in self._channel_points:
                self._channel_points[ch] = linear_points.copy()

    def apply_preset(self, preset_points: List[Tuple[int, int]]):
        """应用预设曲线到所有通道"""
        for channel in self._channel_points:
            self._channel_points[channel] = preset_points.copy()

    @staticmethod
    def create_lookup_table(control_points: List[Tuple[int, int]]) -> np.ndarray:
        """
        根据给定的控制点创建256级查找表
        
        Args:
            control_points: 控制点列表，每个点是(x,y)坐标元组
            
        Returns:
            numpy数组，表示0-255的映射结果
        """
        # 确保控制点按x坐标排序
        sorted_points = sorted(control_points, key=lambda p: p[0])
        
        x_points = np.array([p[0] for p in sorted_points])
        y_points = np.array([p[1] for p in sorted_points])
        
        # 默认使用线性插值
        lut = np.interp(np.arange(256), x_points, y_points)

        # 如果有足够多的点，尝试使用三次样条插值
        if len(sorted_points) > 2:
            try:
                cs = interpolate.CubicSpline(x_points, y_points)
                smooth_lut = cs(np.arange(256))
                lut = np.clip(smooth_lut, 0, 255)
            except Exception:
                pass  # 插值失败则保留线性结果
                
        return lut.astype(np.uint8)

    def get_serializable_data(self) -> Dict[str, Any]:
        """获取可序列化的数据，用于保存或传递给操作类"""
        return {
            "points_rgb": self._channel_points["RGB"],
            "points_r": self._channel_points["R"],
            "points_g": self._channel_points["G"],
            "points_b": self._channel_points["B"],
        }
    
    def load_from_params(self, params: Dict[str, Any]):
        """从参数字典加载数据"""
        if "points_rgb" in params:
            self._channel_points["RGB"] = params["points_rgb"]
        if "points_r" in params:
            self._channel_points["R"] = params["points_r"]
        if "points_g" in params:
            self._channel_points["G"] = params["points_g"]
        if "points_b" in params:
            self._channel_points["B"] = params["points_b"] 