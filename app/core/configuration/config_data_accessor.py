"""
配置数据访问器 - 提供类型安全的配置访问
"""

from typing import Dict, Any, Optional
from .config_data_transfer import ConfigDataTransferObject


class ConfigDataAccessor:
    """配置数据访问器 - 提供类型安全的配置数据访问"""
    
    def __init__(self, config_data: ConfigDataTransferObject):
        """初始化配置访问器
        
        Args:
            config_data: 配置数据传输对象
        """
        self._config_data = config_data
    
    def get_rendering_mode(self) -> str:
        """获取渲染模式"""
        return self._config_data.rendering_mode
    
    def get_proxy_quality_factor(self) -> float:
        """获取代理质量因子"""
        return self._config_data.proxy_quality_factor
    
    def get_analysis_update_config(self) -> Dict[str, Any]:
        """获取分析更新配置"""
        return self._config_data.analysis_update.copy()
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """检查功能是否启用"""
        return self._config_data.features.get(feature_name, False)
    
    def get_window_config(self) -> Dict[str, Any]:
        """获取窗口配置"""
        return self._config_data.window.copy()
    
    def get_export_config(self) -> Dict[str, Any]:
        """获取导出配置"""
        return self._config_data.export.copy()
    
    def get_update_debounce_delay(self) -> int:
        """获取更新防抖延迟"""
        return self._config_data.analysis_update.get('debounce_delay', 100)
    
    def get_update_max_retry_attempts(self) -> int:
        """获取最大重试次数"""
        return self._config_data.analysis_update.get('max_retry_attempts', 3)
    
    def get_update_default_strategy(self) -> str:
        """获取默认更新策略"""
        return self._config_data.analysis_update.get('default_strategy', 'smart')
    
    def is_update_error_recovery_enabled(self) -> bool:
        """检查是否启用错误恢复"""
        return self._config_data.analysis_update.get('enable_error_recovery', True)
    
    def get_update_error_threshold(self) -> int:
        """获取错误阈值"""
        return self._config_data.analysis_update.get('error_threshold', 5)
    
    def get_update_invisible_delay(self) -> int:
        """获取不可见延迟"""
        return self._config_data.analysis_update.get('invisible_delay', 300)
    
    # 新增的配置访问方法
    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置"""
        return {
            'show_left_panel': self._config_data.show_left_panel,
            'show_analysis_panel': self._config_data.show_analysis_panel
        }
    
    def get_processing_config(self) -> Dict[str, Any]:
        """获取处理配置"""
        return {
            'auto_save_interval': self._config_data.auto_save_interval,
            'default_quality': self._config_data.default_quality,
            'proxy_quality_factor': self._config_data.proxy_quality_factor
        }
    
    def get_window_geometry(self) -> Dict[str, int]:
        """获取窗口几何配置"""
        return self._config_data.window.get('geometry', {"x": 100, "y": 100, "width": 1200, "height": 800})
    
    def is_window_maximized(self) -> bool:
        """检查窗口是否最大化"""
        return self._config_data.window.get('maximized', False)
    
    def get_export_quality(self) -> int:
        """获取导出质量"""
        return self._config_data.export.get('quality', 85)
    
    def get_export_format(self) -> str:
        """获取导出格式"""
        return self._config_data.export.get('format', 'PNG')
    
    def get_presets(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """获取预设配置"""
        return self._config_data.presets.copy()
    
    def is_left_panel_visible(self) -> bool:
        """检查左侧面板是否可见"""
        return self._config_data.show_left_panel
    
    def is_analysis_panel_visible(self) -> bool:
        """检查分析面板是否可见"""
        return self._config_data.show_analysis_panel
    
    def get_auto_save_interval(self) -> int:
        """获取自动保存间隔"""
        return self._config_data.auto_save_interval
    
    def get_default_quality(self) -> int:
        """获取默认质量"""
        return self._config_data.default_quality
    
    def get_last_batch_export_path(self) -> Optional[str]:
        """获取上次批处理导出路径"""
        return self._config_data.last_batch_export_path
    
    def get_last_analysis_export_path(self) -> Optional[str]:
        """获取上次数据分析导出路径"""
        return self._config_data.last_analysis_export_path
    
    def get_last_image_folder_path(self) -> Optional[str]:
        """获取上次使用的图像文件夹路径"""
        return self._config_data.last_image_folder_path