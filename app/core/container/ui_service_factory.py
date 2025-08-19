"""UI服务工厂实现"""

import logging
from typing import Optional, Any

from ..interfaces.ui_service_factory_interface import UIServiceFactoryInterface
from ..interfaces import DialogManagerInterface, InteractiveWidgetInterface

logger = logging.getLogger(__name__)


class UIServiceFactory(UIServiceFactoryInterface):
    """UI服务工厂，负责创建和配置UI相关服务"""
    
    def __init__(self):
        self._dialog_manager: Optional[Any] = None
        self._app_controller: Optional[Any] = None
    
    def create_ui_services(self, main_window, services) -> None:
        """创建UI相关服务"""
        logger.info("创建UI服务...")
        
        # 配置UI依赖关系
        self.configure_ui_dependencies(main_window)
        
        # 获取核心服务
        state_manager = services.get('state_manager')
        processing_handler = services.get('processing_handler')
        file_handler = services.get('file_handler')
        batch_processing_handler = services.get('batch_processing_handler')
        
        # 注意：DialogManager的创建已移到InterfaceIntegrationManager
        # Core层不再直接创建UI组件，符合分层架构原则
        logger.info("UI组件创建将由UI层的InterfaceIntegrationManager处理")
        
        logger.info("UI服务创建完成")
    
    def configure_ui_dependencies(self, main_window) -> None:
        """配置UI相关的依赖关系"""
        logger.info("配置UI依赖关系...")
        # UI依赖关系配置逻辑
        logger.info("UI依赖关系配置完成")
    
    def get_dialog_manager(self) -> Optional[Any]:
        """获取对话框管理器"""
        return self._dialog_manager
    
    def get_app_controller(self) -> Optional[Any]:
        """获取应用控制器"""
        return self._app_controller
    
    def create_dialog_manager(self) -> 'DialogManagerInterface':
        """创建对话框管理器接口实现
        
        注意：此方法应该由外部依赖注入系统调用，
        具体的接口包装由ApplicationBootstrap负责
        
        Returns:
            DialogManagerInterface: 对话框管理器接口实现（需外部注入）
        """
        # 这个方法的实现已转移到ApplicationBootstrap
        # UIServiceFactory不再直接创建接口包装器
        logger.warning("create_dialog_manager应该由ApplicationBootstrap调用")
        return None
    
    def create_interactive_widget(self) -> 'InteractiveWidgetInterface':
        """创建交互组件接口实现
        
        Returns:
            InteractiveWidgetInterface: 交互组件接口实现
        """
        # 这个方法暂时返回None，因为交互组件需要在UI创建后才能获取
        # 实际的交互组件创建将在ApplicationBootstrap中处理
        logger.warning("create_interactive_widget方法暂未实现，需要在UI创建后获取")
        return None
