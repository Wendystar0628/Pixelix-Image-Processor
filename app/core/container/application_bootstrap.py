"""
应用引导器模块 - 重构为纯协调器
"""

import logging
from app.models.app_config import AppConfig
from app.layers.infrastructure.configuration.config_service_interface import ConfigServiceInterface
from .service_manager import ServiceManager
from .service_cleanup_manager import ServiceCleanupManager
from .app_lifecycle_coordinator import AppLifecycleCoordinator
from .application_state import ApplicationState
from .ui_service_factory import UIServiceFactory


class ApplicationBootstrap:
    """应用引导器 - 纯协调器，只负责组装和委托"""
    
    def __init__(self, config: AppConfig, config_service: ConfigServiceInterface):
        self.config = config
        self.config_service = config_service
        
        # 创建专门组件
        self.service_manager = ServiceManager()
        self.cleanup_manager = ServiceCleanupManager()
        self.lifecycle_coordinator = AppLifecycleCoordinator(
            self.service_manager, self.cleanup_manager, config, config_service)
        
        # 保留必要组件
        self.ui_service_factory = UIServiceFactory()
        self.application_state = ApplicationState()
    
    def bootstrap_application(self) -> bool:
        """启动应用 - 委托给生命周期协调器"""
        return self.lifecycle_coordinator.startup_application(self.application_state)
    
    def initialize_all_services(self) -> dict:
        """向后兼容方法 - 返回服务字典"""
        return self.service_manager.get_all_services()
    
    def create_ui_services(self, main_window) -> None:
        """创建UI服务 - 委托给UI服务工厂
        
        注意：UI接口实现的创建已移到main.py层，
        符合分层架构原则
        """
        services = self.service_manager.get_all_services()
        self.ui_service_factory.create_ui_services(main_window, services)

    
    def shutdown(self) -> None:
        """关闭应用 - 委托给生命周期协调器"""
        self.lifecycle_coordinator.shutdown_application(self.application_state)
    
    def cleanup_services(self) -> None:
        """清理服务 - 向后兼容方法"""
        # 获取服务字典
        services = self.service_manager.get_all_services()
        # 传递给清理管理器
        self.cleanup_manager.cleanup_all_services(services)