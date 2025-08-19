"""
服务构建器模块
"""

import logging
from typing import Optional

from .simple_container import SimpleDependencyContainer
from ..interfaces import (
    ImageProcessorInterface,
    StateManagerInterface, 
    AppControllerInterface,
    # UI抽象接口
    InteractiveWidgetInterface,
    DialogManagerInterface,
    UIServiceFactoryInterface
)
from .infrastructure_bridge import InfrastructureBridge

logger = logging.getLogger(__name__)


class ServiceBuilder:
    """
    服务构建器
    
    负责配置服务的依赖关系和创建策略，简化ServiceFactory的职责。
    """
    
    def __init__(self, container: SimpleDependencyContainer):
        self.container = container
        self.infrastructure_bridge = InfrastructureBridge(container)
        
    def configure_core_services(self, config_service) -> None:
        """
        配置核心服务的依赖关系
        
        Args:
            config_service: 配置服务接口实现
        """
        logger.info("配置核心服务依赖关系...")
        
        # 通过基础设施桥接器注册配置服务
        self.infrastructure_bridge.register_config_services(config_service)
        
        # 注册图像处理器 - 使用新的业务层实现
        from app.layers.business.processing.image_processor import ImageProcessor
        self.container.register_interface(ImageProcessorInterface, ImageProcessor, singleton=True)
        
        # 注册状态管理器（依赖ImageProcessorInterface）
        from app.core.managers.state_manager import StateManager
        self.container.register_interface(StateManagerInterface, StateManager, singleton=True, dependencies=[ImageProcessorInterface])
        
        logger.info("核心服务依赖关系配置完成")
    
    def configure_ui_services(self, main_window) -> None:
        """
        配置UI相关服务的依赖关系 - 通过桥接适配器访问（无直接导入）
        
        Args:
            main_window: 主窗口实例
        """
        logger.info("配置UI服务依赖关系...")
        
        # 上层服务由DirectServiceInitializer创建并注册到桥接适配器
        # 核心层通过InfrastructureBridge获取上层服务适配器
        # 无需直接导入handlers层实现
        
        logger.info("UI服务依赖关系配置完成")
    
    def configure_batch_services(self) -> None:
        """
        配置批处理服务的依赖关系
        """
        logger.info("配置批处理服务依赖关系...")
        
        # 注册批处理相关服务
        
        logger.info("批处理服务依赖关系配置完成")
    
    def configure_handler_services(self) -> None:
        """
        配置Handler层服务 - 通过桥接适配器访问（无直接导入）
        """
        logger.info("配置Handler服务依赖关系...")
        
        # 上层服务由DirectServiceInitializer创建并注册到桥接适配器
        # 核心层通过InfrastructureBridge获取上层服务适配器
        # 无需直接注册上层服务到依赖注入容器
        
        logger.info("Handler服务依赖关系配置完成")
    

    
    def build_image_processor(self) -> ImageProcessorInterface:
        """构建图像处理器实例"""
        return self.container.resolve(ImageProcessorInterface)
    
    def build_state_manager(self) -> StateManagerInterface:
        """构建状态管理器实例"""
        return self.container.resolve(StateManagerInterface)
    
    def build_config_access(self):
        """构建配置访问接口实例"""
        from ..abstractions.config_access_interface import ConfigAccessInterface
        return self.container.resolve(ConfigAccessInterface)
    
    def build_app_controller(self) -> AppControllerInterface:
        """
        构建应用控制器实例 - 通过桥接适配器获取
        
        Returns:
            应用控制器实例
        """
        # 通过桥接适配器获取上层服务实例
        from ..interfaces.upper_layer_service_interface import UpperLayerServiceInterface
        
        try:
            upper_layer_adapter = self.infrastructure_bridge.get_service(UpperLayerServiceInterface)
            if upper_layer_adapter:
                app_controller = upper_layer_adapter.get_app_controller()
                if app_controller:
                    return app_controller
            
            logger.warning("无法通过桥接适配器获取AppController，可能服务尚未初始化")
            return None
            
        except Exception as e:
            logger.error(f"获取AppController失败: {e}")
            return None