"""向后兼容性导出层"""
from app.models.app_config import AppConfig
from app.layers.infrastructure.configuration.config_manager import ConfigManager

# 向后兼容导出，不包含任何实现
__all__ = ['AppConfig', 'ConfigManager']
