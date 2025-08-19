"""配置服务实现 - 基础设施层门面"""
import logging
from typing import Optional
from pathlib import Path

from .config_service_interface import ConfigServiceInterface
from .config_manager import ConfigManager
from app.models.app_config import AppConfig

logger = logging.getLogger(__name__)


class ConfigService(ConfigServiceInterface):
    """配置服务实现 - 基础设施层门面"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """初始化配置服务
        
        Args:
            config_dir: 配置目录路径
        """
        try:
            self._config_manager = ConfigManager(config_dir)
            logger.info("配置服务初始化成功")
        except Exception as e:
            logger.error(f"配置服务初始化失败: {e}")
            raise
    
    def get_config(self) -> AppConfig:
        """获取当前配置"""
        return self._config_manager.get_config()
    
    def update_config(self, **kwargs) -> None:
        """更新配置"""
        self._config_manager.update_config(**kwargs)
    
    def save_config(self) -> None:
        """保存配置"""
        self._config_manager.save_config()
    
    def load_config(self) -> None:
        """重新加载配置"""
        self._config_manager.load_config()
    
    def reset_to_defaults(self) -> None:
        """重置为默认配置"""
        self._config_manager.reset_to_defaults()
    
    def get_config_file_path(self) -> Path:
        """获取配置文件路径"""
        return self._config_manager.get_config_file_path()
    
    def is_config_valid(self) -> bool:
        """检查配置是否有效"""
        try:
            config = self.get_config()
            return config is not None
        except Exception:
            return False