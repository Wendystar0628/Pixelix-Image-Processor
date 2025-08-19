"""纯配置数据模型"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class AppConfig:
    """应用配置数据类 - 纯数据结构"""
    
    # 窗口配置
    window_geometry: Optional[Dict[str, int]] = None
    window_maximized: bool = False
    
    # UI配置
    show_left_panel: bool = True
    show_analysis_panel: bool = True
    
    # 应用程序设置
    auto_save_interval: int = 300  # 秒
    default_quality: int = 85  # JPEG质量
    proxy_quality_factor: float = 0.75  # 代理图像质量因子，默认为高质量(0.75)
    
    # 渲染模式配置
    rendering_mode: str = "matplotlib"  # 当前渲染模式: "pyqtgraph" 或 "matplotlib"
    default_rendering_mode: str = "matplotlib"  # 默认渲染模式
    
    # 预设配置
    presets: Dict[str, Dict[str, Dict[str, Any]]] = field(default_factory=dict)
    
    # 智能更新配置
    update_debounce_delay: int = 100
    update_max_retry_attempts: int = 3
    update_default_strategy: str = 'smart'
    update_enable_error_recovery: bool = True
    update_error_threshold: int = 5
    update_invisible_delay: int = 300
    
    # 导出路径记忆
    last_batch_export_path: Optional[str] = None  # 批处理导出路径
    last_analysis_export_path: Optional[str] = None  # 数据分析导出路径
    last_image_folder_path: Optional[str] = None  # 图像文件夹路径
    
    def __post_init__(self):
        """初始化后处理 - 只设置默认值"""
        if self.window_geometry is None:
            self.window_geometry = {"x": 100, "y": 100, "width": 1200, "height": 800}
        if self.presets is None:
            self.presets = {}
        
        # 验证智能更新配置
        if self.update_debounce_delay < 0:
            self.update_debounce_delay = 100
        if self.update_max_retry_attempts < 1:
            self.update_max_retry_attempts = 3
        if self.update_error_threshold < 1:
            self.update_error_threshold = 5
        if self.update_invisible_delay < 0:
            self.update_invisible_delay = 300
        
        # 验证更新策略
        valid_strategies = ['immediate', 'debounced', 'visibility', 'throttled', 'smart']
        if self.update_default_strategy not in valid_strategies:
            self.update_default_strategy = 'smart'
        
        # 验证导出路径
        import os
        if self.last_batch_export_path and not os.path.exists(self.last_batch_export_path):
            self.last_batch_export_path = None
        if self.last_analysis_export_path and not os.path.exists(self.last_analysis_export_path):
            self.last_analysis_export_path = None
        if self.last_image_folder_path and not os.path.exists(self.last_image_folder_path):
            self.last_image_folder_path = None