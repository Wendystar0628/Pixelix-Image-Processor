"""配置访问适配器 - 纯适配器实现"""
from typing import Dict, Any
from ..abstractions.config_access_interface import ConfigAccessInterface
from app.layers.infrastructure.configuration.config_service_interface import ConfigServiceInterface


class ConfigAccessAdapter(ConfigAccessInterface):
    """配置访问适配器"""
    
    def __init__(self, config_service: ConfigServiceInterface):
        self._config_service = config_service
    
    def get_rendering_mode(self) -> str:
        return self._config_service.get_config().rendering_mode
    
    def get_proxy_quality_factor(self) -> float:
        return self._config_service.get_config().proxy_quality_factor
    
    def get_window_geometry(self) -> Dict[str, int]:
        return self._config_service.get_config().window_geometry or {}
    
    def is_feature_enabled(self, feature: str) -> bool:
        features = getattr(self._config_service.get_config(), 'features', {})
        return features.get(feature, False)
    
    def get_update_config(self) -> Dict[str, Any]:
        config = self._config_service.get_config()
        return {
            'debounce_delay': config.update_debounce_delay,
            'max_retry_attempts': config.update_max_retry_attempts,
            'default_strategy': config.update_default_strategy,
            'enable_error_recovery': config.update_enable_error_recovery,
            'error_threshold': config.update_error_threshold,
            'invisible_delay': config.update_invisible_delay,
        }