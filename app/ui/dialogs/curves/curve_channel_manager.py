"""
曲线通道管理器模块
负责管理不同颜色通道的切换和数据同步
"""

from typing import Dict, List, Callable, Optional
from PyQt6.QtWidgets import QComboBox, QLabel, QHBoxLayout
import numpy as np

from app.ui.dialogs.curves.models.curve_data_model import CurveDataModel


class CurveChannelManager:
    """
    曲线通道管理器
    处理RGB/R/G/B通道的切换、同步和数据传递
    """
    
    def __init__(self, curve_data_model: CurveDataModel):
        """
        初始化通道管理器
        
        Args:
            curve_data_model: 曲线数据模型实例
        """
        self._curve_data = curve_data_model
        self._channel_display_map = {"RGB": "RGB", "R": "红", "G": "绿", "B": "蓝"}
        self._channel_code_map = {"RGB": "RGB", "红": "R", "绿": "G", "蓝": "B"}
        
    def setup_channel_selector(self, layout: QHBoxLayout) -> QComboBox:
        """
        设置通道选择器UI组件
        
        Args:
            layout: 要添加通道选择器的布局
            
        Returns:
            创建的下拉框组件
        """
        # 添加标签
        layout.addWidget(QLabel("通道:"))
        
        # 创建下拉框
        channel_combo = QComboBox()
        channel_combo.addItems(self._channel_display_map.values())
        
        # 设置当前值
        current_channel = self._curve_data.current_channel
        display_name = next(
            (k for k, v in self._channel_code_map.items() if v == current_channel), 
            "RGB"
        )
        channel_combo.setCurrentText(display_name)
        
        # 添加到布局
        layout.addWidget(channel_combo)
        
        return channel_combo
        
    def connect_channel_changed(self, combo: QComboBox, on_channel_changed: Optional[Callable] = None):
        """
        连接通道变更事件
        
        Args:
            combo: 通道选择下拉框
            on_channel_changed: 可选的回调函数，用于通知通道变化
        """
        def _on_index_changed(index: int):
            display_name = combo.itemText(index)
            code_name = self._channel_code_map[display_name]
            
            # 更新数据模型中的当前通道
            self._curve_data.current_channel = code_name
            
            # 如果提供了回调，调用它
            if on_channel_changed:
                on_channel_changed(code_name)
                
        combo.currentIndexChanged.connect(_on_index_changed)
        
    def get_current_channel_name(self) -> str:
        """
        获取当前通道的显示名称
        
        Returns:
            通道显示名称
        """
        code = self._curve_data.current_channel
        return next((k for k, v in self._channel_code_map.items() if v == code), "RGB")
        
    def sync_rgb_to_all_channels(self):
        """同步RGB通道数据到所有单独通道"""
        self._curve_data.sync_all_channels_from_rgb()
        
    def extract_channel_data(self, image: np.ndarray) -> np.ndarray:
        """
        从图像提取当前通道的数据
        
        Args:
            image: 源图像
            
        Returns:
            通道数据
        """
        if image is None or image.ndim != 3:
            return np.zeros((1, 1), dtype=np.uint8)
            
        channel = self._curve_data.current_channel
        
        if channel == "RGB":
            # 计算亮度
            return np.dot(image[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
        else:
            channel_index = {"R": 2, "G": 1, "B": 0}  # OpenCV的BGR顺序
            return image[:, :, channel_index[channel]] 