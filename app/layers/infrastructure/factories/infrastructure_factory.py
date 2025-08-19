"""基础设施服务工厂"""
import logging
from typing import Optional
from pathlib import Path

from ..configuration.config_service import ConfigService
from ..configuration.config_service_interface import ConfigServiceInterface

logger = logging.getLogger(__name__)


class InfrastructureFactory:
    """基础设施服务工厂"""
    
    def __init__(self):
        self._config_service: Optional[ConfigServiceInterface] = None
    
    def create_config_service(self, config_dir: Optional[Path] = None) -> ConfigServiceInterface:
        """创建配置服务
        
        Args:
            config_dir: 配置目录路径
            
        Returns:
            配置服务实例
        """
        if self._config_service is None:
            try:
                self._config_service = ConfigService(config_dir)
                logger.info("配置服务创建成功")
            except Exception as e:
                logger.error(f"创建配置服务失败: {e}")
                raise
        
        return self._config_service
    
    def get_config_service(self) -> Optional[ConfigServiceInterface]:
        """获取已创建的配置服务"""
        return self._config_service
    
    def reset_services(self) -> None:
        """重置所有服务（用于测试）"""
        self._config_service = None
        logger.debug("基础设施服务已重置")