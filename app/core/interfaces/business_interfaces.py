"""纯业务接口集合"""

# 核心业务接口
from .image_processor_interface import ImageProcessorInterface
from .state_manager_interface import StateManagerInterface
from .app_controller_interface import AppControllerInterface

# 处理器接口
from .handler_interface_base import BaseHandlerInterface, HandlerInterfaceMeta
from .file_handler_interface import FileHandlerInterface
from .processing_handler_interface import ProcessingHandlerInterface
from .preset_handler_interface import PresetHandlerInterface

# UI抽象接口
from .interactive_widget_interface import InteractiveWidgetInterface
from .dialog_manager_interface import DialogManagerInterface
from .ui_service_factory_interface import UIServiceFactoryInterface


class BusinessInterfaces:
    """业务接口集合类 - 提供业务接口的统一视图"""
    
    # 核心业务接口
    IMAGE_PROCESSOR = ImageProcessorInterface
    STATE_MANAGER = StateManagerInterface
    APP_CONTROLLER = AppControllerInterface
    
    # 处理器接口
    BASE_HANDLER = BaseHandlerInterface
    FILE_HANDLER = FileHandlerInterface
    PROCESSING_HANDLER = ProcessingHandlerInterface
    PRESET_HANDLER = PresetHandlerInterface
    
    # UI抽象接口
    INTERACTIVE_WIDGET = InteractiveWidgetInterface
    DIALOG_MANAGER = DialogManagerInterface
    UI_SERVICE_FACTORY = UIServiceFactoryInterface
    
    @classmethod
    def get_core_interfaces(cls):
        """获取核心业务接口列表"""
        return [
            cls.IMAGE_PROCESSOR,
            cls.STATE_MANAGER,
            cls.APP_CONTROLLER,
        ]
    
    @classmethod
    def get_handler_interfaces(cls):
        """获取处理器接口列表"""
        return [
            cls.BASE_HANDLER,
            cls.FILE_HANDLER,
            cls.PROCESSING_HANDLER,
            cls.PRESET_HANDLER,
        ]
    
    @classmethod  
    def get_ui_interfaces(cls):
        """获取UI抽象接口列表"""
        return [
            cls.INTERACTIVE_WIDGET,
            cls.DIALOG_MANAGER,
            cls.UI_SERVICE_FACTORY,
        ]
    
    @classmethod
    def get_all_interfaces(cls):
        """获取所有业务接口列表"""
        return cls.get_core_interfaces() + cls.get_handler_interfaces() + cls.get_ui_interfaces()


__all__ = [
    'BusinessInterfaces',
    # 重新导出所有业务接口
    'ImageProcessorInterface',
    'StateManagerInterface', 
    'AppControllerInterface',
    'BaseHandlerInterface',
    'HandlerInterfaceMeta',
    'FileHandlerInterface',
    'ProcessingHandlerInterface',
    'PresetHandlerInterface',
    'InteractiveWidgetInterface',
    'DialogManagerInterface',
    'UIServiceFactoryInterface',
]