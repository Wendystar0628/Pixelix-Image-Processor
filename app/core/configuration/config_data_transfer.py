"""
配置数据传输对象 - 纯数据结构
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class ConfigDataTransferObject:
    """配置数据传输对象 - 纯数据结构，不包含业务逻辑"""
    
    # 渲染模式配置
    rendering_mode: str = "matplotlib"
    proxy_quality_factor: float = 0.75
    
    # 分析更新配置
    analysis_update: Dict[str, Any] = None
    
    # 功能特性配置
    features: Dict[str, bool] = None
    
    # 窗口配置
    window: Dict[str, Any] = None
    
    # 导出配置
    export: Dict[str, Any] = None
    
    # UI配置
    show_left_panel: bool = True
    show_analysis_panel: bool = True
    
    # 应用程序设置
    auto_save_interval: int = 300
    default_quality: int = 85
    
    # 预设配置
    presets: Dict[str, Dict[str, Dict[str, Any]]] = None
    
    # 导出路径记忆
    last_batch_export_path: Optional[str] = None
    last_analysis_export_path: Optional[str] = None
    
    def __post_init__(self):
        """初始化默认值"""
        if self.analysis_update is None:
            self.analysis_update = {
                'debounce_delay': 100,
                'max_retry_attempts': 3,
                'default_strategy': 'smart',
                'enable_error_recovery': True,
                'error_threshold': 5,
                'invisible_delay': 300
            }
        if self.features is None:
            self.features = {}
        if self.window is None:
            self.window = {
                'geometry': {"x": 100, "y": 100, "width": 1200, "height": 800},
                'maximized': False
            }
        if self.export is None:
            self.export = {
                'quality': 85,
                'format': 'PNG'
            }
        if self.presets is None:
            self.presets = {}
    
    @classmethod
    def from_app_config(cls, app_config) -> 'ConfigDataTransferObject':
        """从AppConfig创建传输对象"""
        return cls(
            rendering_mode=getattr(app_config, 'rendering_mode', 'matplotlib'),
            proxy_quality_factor=getattr(app_config, 'proxy_quality_factor', 0.75),
            analysis_update={
                'debounce_delay': getattr(app_config, 'update_debounce_delay', 100),
                'max_retry_attempts': getattr(app_config, 'update_max_retry_attempts', 3),
                'default_strategy': getattr(app_config, 'update_default_strategy', 'smart'),
                'enable_error_recovery': getattr(app_config, 'update_enable_error_recovery', True),
                'error_threshold': getattr(app_config, 'update_error_threshold', 5),
                'invisible_delay': getattr(app_config, 'update_invisible_delay', 300)
            },
            features=getattr(app_config, 'features', {}),
            window={
                'geometry': getattr(app_config, 'window_geometry', {"x": 100, "y": 100, "width": 1200, "height": 800}),
                'maximized': getattr(app_config, 'window_maximized', False)
            },
            export={
                'quality': getattr(app_config, 'default_quality', 85),
                'format': getattr(app_config, 'default_format', 'PNG')
            },
            show_left_panel=getattr(app_config, 'show_left_panel', True),
            show_analysis_panel=getattr(app_config, 'show_analysis_panel', True),
            auto_save_interval=getattr(app_config, 'auto_save_interval', 300),
            default_quality=getattr(app_config, 'default_quality', 85),
            presets=getattr(app_config, 'presets', {}),
            last_batch_export_path=getattr(app_config, 'last_batch_export_path', None),
            last_analysis_export_path=getattr(app_config, 'last_analysis_export_path', None)
        )