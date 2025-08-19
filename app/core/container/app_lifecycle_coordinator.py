"""
应用生命周期协调器 - 管理应用启动和关闭流程
"""

import logging
from typing import Dict, Any

from app.models.app_config import AppConfig
from app.layers.infrastructure.configuration.config_service_interface import ConfigServiceInterface
from ..initialization.direct_service_initializer import DirectServiceInitializer
from .service_manager import ServiceManager
from .service_cleanup_manager import ServiceCleanupManager
from .application_state import ApplicationState


class AppLifecycleCoordinator:
    """应用生命周期协调器 - 整合DirectServiceInitializer和服务管理"""
    
    def __init__(self, service_manager: ServiceManager, 
                 cleanup_manager: ServiceCleanupManager,
                 config: AppConfig, config_service: ConfigServiceInterface):
        self.service_manager = service_manager
        self.cleanup_manager = cleanup_manager
        self.config = config
        self.config_service = config_service
        self._logger = logging.getLogger(__name__)
        
        # 创建服务初始化器
        self.direct_initializer = DirectServiceInitializer(config, config_service)
    
    def startup_application(self, application_state: ApplicationState) -> bool:
        """启动应用，协调服务创建和注册"""
        try:
            application_state.set_initializing()
            self._logger.info("开始应用启动协调...")
            
            # 使用现有的DirectServiceInitializer创建服务
            services = self.direct_initializer.initialize_all_services()
            
            # 将服务注册到服务管理器
            for name, service in services.items():
                self.service_manager.register_service(name, service)
            
            # 记录启动信息
            self._logger.info(f"成功创建并注册 {len(services)} 个服务: {list(services.keys())}")
            
            application_state.set_initialized()
            self._logger.info("应用启动协调完成")
            return True
            
        except Exception as e:
            application_state.set_error(str(e))
            self._logger.error(f"应用启动失败: {e}")
            # 清理已创建的服务
            self._cleanup_on_startup_failure()
            return False
    
    def shutdown_application(self, application_state: ApplicationState) -> None:
        """关闭应用，协调服务清理"""
        application_state.set_shutting_down()
        self._logger.info("开始应用关闭协调...")
        
        try:
            # 获取所有服务并清理
            services = self.service_manager.get_all_services()
            self.cleanup_manager.cleanup_all_services(services)
            
            # 清空服务管理器
            self.service_manager.clear_all()
            
            application_state.set_shutdown()
            self._logger.info("应用关闭协调完成")
            
        except Exception as e:
            self._logger.error(f"应用关闭过程中出错: {e}")
    
    def _cleanup_on_startup_failure(self) -> None:
        """启动失败时的清理"""
        try:
            services = self.service_manager.get_all_services()
            if services:
                self.cleanup_manager.cleanup_all_services(services)
                self.service_manager.clear_all()
        except Exception as e:
            self._logger.error(f"启动失败清理时出错: {e}")